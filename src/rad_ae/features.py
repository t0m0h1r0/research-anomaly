"""10-second statistic feature extraction for storage-I/O AE inputs."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

from .ransap import IoEvent


FEATURE_SLICES = {
    "intensity": slice(0, 2),
    "rw_ratio": slice(2, 4),
    "mean_lba": slice(4, 6),
    "mean_length": slice(6, 8),
    "frame_deltas": slice(8, 10),
    "optional_telemetry": slice(10, 11),
    "padding": slice(11, 12),
}

FEATURE_NAMES = (
    "log_total_count",
    "log_total_bytes",
    "read_ratio",
    "write_ratio",
    "mean_read_lba",
    "mean_write_lba",
    "log_mean_read_len",
    "log_mean_write_len",
    "delta_mean_lba",
    "delta_mean_len",
    "optional_entropy_or_compression",
    "padding",
)

FEATURE_WEIGHTS = {
    "intensity": 1.0,
    "rw_ratio": 1.0,
    "mean_lba": 1.0,
    "mean_length": 1.0,
    "frame_deltas": 0.5,
    "optional_telemetry": 0.0,
    "padding": 0.0,
}


@dataclass(frozen=True)
class FeatureConfig:
    window_seconds: float = 10.0
    sequence_length: int = 12
    stride: int = 1
    logical_block_bytes: int = 512
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
        empty = np.zeros((0, len(FEATURE_NAMES)), dtype=np.float32)
        return FrameBuildResult(empty, np.zeros((0,), dtype=np.float64), 0, 0, 0)

    ordered = sorted(events, key=lambda event: event.timestamp)
    max_lba_seen = max(event.lba for event in ordered)
    ns_lba = max(int(namespace_lba or 0), max_lba_seen + 1, 1)
    start = math.floor(ordered[0].timestamp / config.window_seconds) * config.window_seconds
    end = ordered[-1].timestamp
    frame_count = int(math.floor((end - start) / config.window_seconds)) + 1
    frames = np.zeros((frame_count, len(FEATURE_NAMES)), dtype=np.float32)
    read_count = np.zeros((frame_count,), dtype=np.float64)
    write_count = np.zeros((frame_count,), dtype=np.float64)
    read_lba_sum = np.zeros((frame_count,), dtype=np.float64)
    write_lba_sum = np.zeros((frame_count,), dtype=np.float64)
    read_len_sum = np.zeros((frame_count,), dtype=np.float64)
    write_len_sum = np.zeros((frame_count,), dtype=np.float64)
    entropy_sum = np.zeros((frame_count,), dtype=np.float64)
    entropy_count = np.zeros((frame_count,), dtype=np.int64)

    for event in ordered:
        idx = int(math.floor((event.timestamp - start) / config.window_seconds))
        idx = min(max(idx, 0), frame_count - 1)
        frame = frames[idx]
        frame[0] += 1.0
        frame[1] += float(event.size)

        if event.op == "read":
            read_count[idx] += 1.0
            read_lba_sum[idx] += float(event.lba)
            read_len_sum[idx] += float(event.size)
        else:
            write_count[idx] += 1.0
            write_lba_sum[idx] += float(event.lba)
            write_len_sum[idx] += float(event.size)
            if config.include_entropy and event.entropy is not None:
                entropy_sum[idx] += float(event.entropy)
                entropy_count[idx] += 1

    combined_lba = np.zeros((frame_count,), dtype=np.float64)
    combined_len = np.zeros((frame_count,), dtype=np.float64)
    for idx in range(frame_count):
        total_count = read_count[idx] + write_count[idx]
        total_lba_count = max(total_count, 1.0)
        total_len_count = max(total_count, 1.0)

        read_lba_mean = read_lba_sum[idx] / max(read_count[idx], 1.0)
        write_lba_mean = write_lba_sum[idx] / max(write_count[idx], 1.0)
        read_len_mean = read_len_sum[idx] / max(read_count[idx], 1.0)
        write_len_mean = write_len_sum[idx] / max(write_count[idx], 1.0)
        combined_lba[idx] = (read_lba_sum[idx] + write_lba_sum[idx]) / total_lba_count / ns_lba
        combined_len[idx] = math.log1p((read_len_sum[idx] + write_len_sum[idx]) / total_len_count)

        frames[idx, 0] = math.log1p(float(frames[idx, 0]))
        frames[idx, 1] = math.log1p(float(frames[idx, 1]))
        frames[idx, 2] = read_count[idx] / max(total_count, 1.0)
        frames[idx, 3] = write_count[idx] / max(total_count, 1.0)
        frames[idx, 4] = read_lba_mean / ns_lba
        frames[idx, 5] = write_lba_mean / ns_lba
        frames[idx, 6] = math.log1p(read_len_mean)
        frames[idx, 7] = math.log1p(write_len_mean)
        frames[idx, 10] = float(entropy_sum[idx] / entropy_count[idx]) if entropy_count[idx] else 0.0
        frames[idx, 11] = 0.0

    if frame_count > 1:
        frames[1:, 8] = np.diff(combined_lba).astype(np.float32)
        frames[1:, 9] = np.diff(combined_len).astype(np.float32)

    starts = start + np.arange(frame_count, dtype=np.float64) * config.window_seconds
    return FrameBuildResult(frames, starts, ns_lba, len(ordered), int(entropy_count.sum()))


def make_sequences(frames: np.ndarray, sequence_length: int, stride: int) -> np.ndarray:
    if frames.shape[0] < sequence_length:
        return np.zeros((0, sequence_length, frames.shape[1]), dtype=np.float32)
    starts = range(0, frames.shape[0] - sequence_length + 1, max(1, stride))
    return np.stack([frames[start : start + sequence_length] for start in starts]).astype(np.float32)


def flatten_sequences(x: np.ndarray) -> np.ndarray:
    return x.reshape((x.shape[0], int(np.prod(x.shape[1:])))).astype(np.float32)


def feature_schema(config: FeatureConfig) -> dict[str, object]:
    return {
        "input_shape": [
            config.sequence_length,
            len(FEATURE_NAMES),
        ],
        "window_seconds": config.window_seconds,
        "feature_names": list(FEATURE_NAMES),
        "feature_slices": {name: [value.start, value.stop] for name, value in FEATURE_SLICES.items()},
        "feature_weights_by_group": FEATURE_WEIGHTS,
        "effective_score_weights": feature_score_weights(config).tolist(),
        "layout": "Spec-aligned scalar-only [N,D=12]: intensity, ratios, mean LBA/length, deltas, optional telemetry, pad.",
        "config": config.to_dict(),
    }


def feature_score_weights(config: FeatureConfig) -> np.ndarray:
    weights = np.ones((len(FEATURE_NAMES),), dtype=np.float32)
    for name, feature_slice in FEATURE_SLICES.items():
        weights[feature_slice] = FEATURE_WEIGHTS[name]
    if config.include_entropy:
        weights[FEATURE_SLICES["optional_telemetry"]] = 1.0
    return weights
