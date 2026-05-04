"""Evaluation metrics for calibrated anomaly-score studies."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ThresholdResult:
    threshold: float
    quantile: float
    calibration_count: int


def calibrate_threshold(scores: np.ndarray, quantile: float) -> ThresholdResult:
    if scores.size == 0:
        raise ValueError("cannot calibrate threshold on empty scores")
    return ThresholdResult(float(np.quantile(scores, quantile)), float(quantile), int(scores.size))


def binary_metrics(labels: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float | int]:
    labels = labels.astype(np.int32)
    predictions = (scores >= threshold).astype(np.int32)
    tp = int(np.sum((predictions == 1) & (labels == 1)))
    fp = int(np.sum((predictions == 1) & (labels == 0)))
    tn = int(np.sum((predictions == 0) & (labels == 0)))
    fn = int(np.sum((predictions == 0) & (labels == 1)))
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    fpr = fp / max(fp + tn, 1)
    tnr = tn / max(fp + tn, 1)
    return {
        "threshold": float(threshold),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": float(precision),
        "recall": float(recall),
        "false_positive_rate": float(fpr),
        "true_negative_rate": float(tnr),
    }


def roc_auc(labels: np.ndarray, scores: np.ndarray) -> float | None:
    labels = labels.astype(np.int32)
    positives = scores[labels == 1]
    negatives = scores[labels == 0]
    if positives.size == 0 or negatives.size == 0:
        return None
    combined = np.concatenate([positives, negatives])
    ranks = _average_ranks(combined)
    pos_ranks = ranks[: positives.size]
    auc = (pos_ranks.sum() - positives.size * (positives.size + 1) / 2.0) / (
        positives.size * negatives.size
    )
    return float(auc)


def average_precision(labels: np.ndarray, scores: np.ndarray) -> float | None:
    labels = labels.astype(np.int32)
    positive_count = int(labels.sum())
    if positive_count == 0:
        return None
    order = np.argsort(-scores)
    sorted_labels = labels[order]
    tp = 0
    precision_sum = 0.0
    for idx, label in enumerate(sorted_labels, start=1):
        if label == 1:
            tp += 1
            precision_sum += tp / idx
    return float(precision_sum / positive_count)


def false_alarms_per_day(metrics: dict[str, float | int], window_seconds: float, stride: int) -> float:
    fp = int(metrics["fp"])
    tn = int(metrics["tn"])
    benign_sequences = max(fp + tn, 1)
    sequence_seconds = window_seconds * max(stride, 1)
    sequences_per_day = 86_400.0 / sequence_seconds
    return float((fp / benign_sequences) * sequences_per_day)


def score_summary(scores: np.ndarray) -> dict[str, float | int]:
    if scores.size == 0:
        return {"count": 0}
    return {
        "count": int(scores.size),
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
        "min": float(np.min(scores)),
        "p50": float(np.quantile(scores, 0.5)),
        "p90": float(np.quantile(scores, 0.9)),
        "p99": float(np.quantile(scores, 0.99)),
        "max": float(np.max(scores)),
    }


def _average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty(values.size, dtype=np.float64)
    sorted_values = values[order]
    idx = 0
    while idx < values.size:
        end = idx + 1
        while end < values.size and sorted_values[end] == sorted_values[idx]:
            end += 1
        avg_rank = (idx + 1 + end) / 2.0
        ranks[order[idx:end]] = avg_rank
        idx = end
    return ranks
