"""10-second statistic feature extraction for storage-I/O AE inputs."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

from .ransap import IoEvent


SCALAR_NAMES = (
    "log_read_count",
    "log_write_count",
    "log_read_bytes",
    "log_write_bytes",
    "write_ratio",
    "log_seq_read_count",
    "log_seq_write_count",
    "mean_write_entropy",
)

CHANNEL_NAMES = (
    "read_lba_hist",
    "write_lba_hist",
    "read_len_hist",
    "write_len_hist",
    "scalar_summary",
)


@dataclass(frozen=True)
class FeatureConfig:
    window_seconds: float = 10.0
    sequence_length: int = 12
    stride: int = 1
    bucket_count: int = 8
    logical_block_bytes: int = 512
    length_bucket_min_log2: int = 9
    include_entropy: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class FrameBuildResult:
    frames: np.ndarray
    window_starts: np.ndarray
    namespace_lba: int
    event_count: int
    entropy_event_count: int


class RobustNormalizer:
    """Feature-wise median/MAD normalizer fitted only on training data."""

    def __init__(self, epsilon: float = 1e-6) -> None:
        self.epsilon = epsilon
        self.center: np.ndarray | None = None
        self.scale: np.ndarray | None = None

    def fit(self, x: np.ndarray) -> "RobustNormalizer":
        if x.size == 0:
            raise ValueError("cannot fit normalizer on an empty array")
        self.center = np.median(x, axis=0)
        mad = np.median(np.abs(x - self.center), axis=0)
        std = np.std(x, axis=0)
        self.scale = np.where(mad > self.epsilon, 1.4826 * mad, std)
        self.scale = np.where(self.scale > self.epsilon, self.scale, 1.0)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.center is None or self.scale is None:
            raise ValueError("normalizer has not been fitted")
        return ((x - self.center) / self.scale).astype(np.float32)

    def to_dict(self) -> dict[str, object]:
        if self.center is None or self.scale is None:
            return {}
        return {
            "method": "median_mad_with_std_fallback",
            "epsilon": self.epsilon,
            "center_shape": list(self.center.shape),
            "scale_shape": list(self.scale.shape),
        }


def build_frames(
    events: Sequence[IoEvent],
    config: FeatureConfig,
    namespace_lba: int | None = None,
) -> FrameBuildResult:
    """Aggregate sorted or unsorted events into fixed-shape 10-second frames."""

    if not events:
        empty = np.zeros((0, len(CHANNEL_NAMES), config.bucket_count), dtype=np.float32)
        return FrameBuildResult(empty, np.zeros((0,), dtype=np.float64), 0, 0, 0)

    ordered = sorted(events, key=lambda event: event.timestamp)
    max_lba_seen = max(event.lba for event in ordered)
    ns_lba = max(int(namespace_lba or 0), max_lba_seen + 1, 1)
    start = math.floor(ordered[0].timestamp / config.window_seconds) * config.window_seconds
    end = ordered[-1].timestamp
    frame_count = int(math.floor((end - start) / config.window_seconds)) + 1
    frames = np.zeros((frame_count, len(CHANNEL_NAMES), config.bucket_count), dtype=np.float32)
    entropy_sum = np.zeros((frame_count,), dtype=np.float64)
    entropy_count = np.zeros((frame_count,), dtype=np.int64)
    previous_end_by_op: dict[str, int] = {}

    for event in ordered:
        idx = int(math.floor((event.timestamp - start) / config.window_seconds))
        idx = min(max(idx, 0), frame_count - 1)
        lba_bucket = _lba_bucket(event.lba, ns_lba, config.bucket_count)
        len_bucket = _length_bucket(event.size, config.length_bucket_min_log2, config.bucket_count)
        scalar = frames[idx, 4]
        size_blocks = max(1, math.ceil(event.size / config.logical_block_bytes))
        is_seq = previous_end_by_op.get(event.op) == event.lba
        previous_end_by_op[event.op] = event.lba + size_blocks

        if event.op == "read":
            frames[idx, 0, lba_bucket] += 1.0
            frames[idx, 2, len_bucket] += 1.0
            scalar[0] += 1.0
            scalar[2] += float(event.size)
            if is_seq:
                scalar[5] += 1.0
        else:
            frames[idx, 1, lba_bucket] += 1.0
            frames[idx, 3, len_bucket] += 1.0
            scalar[1] += 1.0
            scalar[3] += float(event.size)
            if is_seq:
                scalar[6] += 1.0
            if config.include_entropy and event.entropy is not None:
                entropy_sum[idx] += float(event.entropy)
                entropy_count[idx] += 1

    for idx in range(frame_count):
        for channel in range(4):
            total = float(frames[idx, channel].sum())
            if total > 0.0:
                frames[idx, channel] /= total

        scalar = frames[idx, 4]
        read_count = float(scalar[0])
        write_count = float(scalar[1])
        scalar[4] = write_count / max(read_count + write_count, 1.0)
        for pos in (0, 1, 2, 3, 5, 6):
            scalar[pos] = math.log1p(float(scalar[pos]))
        scalar[7] = float(entropy_sum[idx] / entropy_count[idx]) if entropy_count[idx] else 0.0

    starts = start + np.arange(frame_count, dtype=np.float64) * config.window_seconds
    return FrameBuildResult(frames, starts, ns_lba, len(ordered), int(entropy_count.sum()))


def make_sequences(frames: np.ndarray, sequence_length: int, stride: int) -> np.ndarray:
    if frames.shape[0] < sequence_length:
        return np.zeros((0, sequence_length, *frames.shape[1:]), dtype=np.float32)
    starts = range(0, frames.shape[0] - sequence_length + 1, max(1, stride))
    return np.stack([frames[start : start + sequence_length] for start in starts]).astype(np.float32)


def flatten_sequences(x: np.ndarray) -> np.ndarray:
    return x.reshape((x.shape[0], int(np.prod(x.shape[1:])))).astype(np.float32)


def feature_schema(config: FeatureConfig) -> dict[str, object]:
    return {
        "input_shape": [
            config.sequence_length,
            len(CHANNEL_NAMES),
            config.bucket_count,
        ],
        "window_seconds": config.window_seconds,
        "channel_names": list(CHANNEL_NAMES),
        "scalar_channel_positions": list(SCALAR_NAMES),
        "histogram_channels_are_per_frame_normalized": True,
        "scalar_channel": "log-scaled counts/bytes, write ratio, optional mean write entropy",
        "config": config.to_dict(),
    }


def _lba_bucket(lba: int, namespace_lba: int, bucket_count: int) -> int:
    if namespace_lba <= 0:
        return 0
    bucket = int((max(lba, 0) / namespace_lba) * bucket_count)
    return min(max(bucket, 0), bucket_count - 1)


def _length_bucket(size: int, min_log2: int, bucket_count: int) -> int:
    if size <= 0:
        return 0
    bucket = int(math.floor(math.log2(size))) - min_log2
    return min(max(bucket, 0), bucket_count - 1)
