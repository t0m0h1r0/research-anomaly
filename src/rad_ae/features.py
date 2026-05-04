"""10-second statistic feature extraction for storage-I/O AE inputs."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

from .ransap import IoEvent


FEATURE_SLICES = {
    "intensity": slice(0, 2),
    "write_ratio": slice(2, 3),
    "mean_lba": slice(3, 4),
    "mean_length": slice(4, 5),
    "frame_deltas": slice(5, 7),
    "optional_telemetry": slice(7, 8),
    "padding": slice(8, 12),
}

FEATURE_NAMES = (
    "log_total_count",
    "log_total_bytes",
    "write_ratio",
    "mean_lba",
    "log_mean_length",
    "delta_mean_lba",
    "delta_log_mean_length",
    "optional_entropy_or_compression",
    "padding_0",
    "padding_1",
    "padding_2",
    "padding_3",
)

FEATURE_WEIGHTS = {
    "intensity": 1.0,
    "write_ratio": 1.0,
    "mean_lba": 1.0,
    "mean_length": 1.0,
    "frame_deltas": 0.5,
    "optional_telemetry": 1.0,
    "padding": 0.0,
}


@dataclass(frozen=True)
class FeatureConfig:
    window_seconds: float = 10.0
    sequence_length: int = 12
    stride: int = 1
    include_entropy: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class FrameBuildResult:
    frames: np.ndarray
    score_masks: np.ndarray
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

    def fit(self, x: np.ndarray, masks: np.ndarray | None = None) -> "RobustNormalizer":
        if x.size == 0:
            raise ValueError("cannot fit normalizer on an empty array")
        if masks is not None:
            if masks.shape != x.shape:
                raise ValueError("normalizer masks must have the same shape as x")
            self.center = np.zeros(x.shape[1:], dtype=np.float64)
            self.scale = np.ones(x.shape[1:], dtype=np.float64)
            for feature_index in np.ndindex(x.shape[1:]):
                values = x[(slice(None), *feature_index)]
                valid = masks[(slice(None), *feature_index)] > 0.0
                if not np.any(valid):
                    continue
                valid_values = values[valid]
                center = float(np.median(valid_values))
                mad = float(np.median(np.abs(valid_values - center)))
                std = float(np.std(valid_values))
                scale = 1.4826 * mad if mad > self.epsilon else std
                self.center[feature_index] = center
                self.scale[feature_index] = scale if scale > self.epsilon else 1.0
            return self
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
        return FrameBuildResult(empty, empty.copy(), np.zeros((0,), dtype=np.float64), 0, 0, 0)

    ordered = sorted(events, key=lambda event: event.timestamp)
    max_lba_seen = max(event.lba for event in ordered)
    ns_lba = max(int(namespace_lba or 0), max_lba_seen + 1, 1)
    start = math.floor(ordered[0].timestamp / config.window_seconds) * config.window_seconds
    end = ordered[-1].timestamp
    frame_count = int(math.floor((end - start) / config.window_seconds)) + 1
    frames = np.zeros((frame_count, len(FEATURE_NAMES)), dtype=np.float32)
    total_count_by_frame = np.zeros((frame_count,), dtype=np.float64)
    write_count = np.zeros((frame_count,), dtype=np.float64)
    lba_sum = np.zeros((frame_count,), dtype=np.float64)
    length_sum = np.zeros((frame_count,), dtype=np.float64)
    entropy_sum = np.zeros((frame_count,), dtype=np.float64)
    entropy_count = np.zeros((frame_count,), dtype=np.int64)

    for event in ordered:
        idx = int(math.floor((event.timestamp - start) / config.window_seconds))
        idx = min(max(idx, 0), frame_count - 1)
        frame = frames[idx]
        frame[0] += 1.0
        frame[1] += float(event.size)
        total_count_by_frame[idx] += 1.0
        lba_sum[idx] += float(event.lba)
        length_sum[idx] += float(event.size)

        if event.op != "read":
            write_count[idx] += 1.0
            if config.include_entropy and event.entropy is not None:
                entropy_sum[idx] += float(event.entropy)
                entropy_count[idx] += 1

    mean_lba = np.zeros((frame_count,), dtype=np.float64)
    log_mean_length = np.zeros((frame_count,), dtype=np.float64)
    score_masks = np.zeros_like(frames, dtype=np.float32)
    for idx in range(frame_count):
        total_count = total_count_by_frame[idx]

        frames[idx, 0] = math.log1p(float(frames[idx, 0]))
        frames[idx, 1] = math.log1p(float(frames[idx, 1]))
        score_masks[idx, FEATURE_SLICES["intensity"]] = 1.0
        if total_count > 0.0:
            mean_lba[idx] = lba_sum[idx] / total_count / ns_lba
            log_mean_length[idx] = math.log1p(length_sum[idx] / total_count)
            frames[idx, 2] = write_count[idx] / total_count
            frames[idx, 3] = mean_lba[idx]
            frames[idx, 4] = log_mean_length[idx]
            score_masks[idx, FEATURE_SLICES["write_ratio"]] = 1.0
            score_masks[idx, FEATURE_SLICES["mean_lba"]] = 1.0
            score_masks[idx, FEATURE_SLICES["mean_length"]] = 1.0
        if config.include_entropy and entropy_count[idx]:
            frames[idx, 7] = float(entropy_sum[idx] / entropy_count[idx])
            score_masks[idx, FEATURE_SLICES["optional_telemetry"]] = 1.0

    if frame_count > 1:
        valid_delta = (total_count_by_frame[1:] > 0.0) & (total_count_by_frame[:-1] > 0.0)
        frames[1:, 5] = (np.abs(np.diff(mean_lba)) * valid_delta).astype(np.float32)
        frames[1:, 6] = (np.abs(np.diff(log_mean_length)) * valid_delta).astype(np.float32)
        score_masks[1:, FEATURE_SLICES["frame_deltas"]] = valid_delta[:, np.newaxis].astype(np.float32)

    starts = start + np.arange(frame_count, dtype=np.float64) * config.window_seconds
    return FrameBuildResult(frames, score_masks, starts, ns_lba, len(ordered), int(entropy_count.sum()))


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
        "mask_policy": (
            "Intensity is always valid. Write ratio, mean LBA, and mean length are masked out for empty "
            "frames. Deltas are valid only when both adjacent frames are non-empty. Optional telemetry "
            "is valid only when present. Padding is always masked out."
        ),
        "layout": "Spec-aligned scalar-only [N,D=12]: intensity, write ratio, mean LBA/length, deltas, optional telemetry, pad.",
        "config": config.to_dict(),
    }


def feature_score_weights(config: FeatureConfig) -> np.ndarray:
    weights = np.ones((len(FEATURE_NAMES),), dtype=np.float32)
    for name, feature_slice in FEATURE_SLICES.items():
        weights[feature_slice] = FEATURE_WEIGHTS[name]
    if not config.include_entropy:
        weights[FEATURE_SLICES["optional_telemetry"]] = 0.0
    return weights
