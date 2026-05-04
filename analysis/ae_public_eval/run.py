"""Run a reproducible public-data AE feasibility evaluation.

The intended public-data target is an unmodified local clone or extract of
RanSAP. The script also supports the small schema fixture in this directory for
smoke checks; fixture results are not empirical ransomware-detection evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from rad_ae.features import FeatureConfig, RobustNormalizer, build_frames, feature_schema, flatten_sequences, make_sequences
from rad_ae.metrics import average_precision, binary_metrics, calibrate_threshold, false_alarms_per_day, roc_auc, score_summary
from rad_ae.models import NumpyMLPAEConfig, NumpyMLPAutoEncoder
from rad_ae.ransap import TraceSource, discover_trace_sources, read_trace_events


@dataclass(frozen=True)
class RunTensor:
    run_id: str
    label: str
    source_kind: str
    event_count: int
    entropy_event_count: int
    frame_count: int
    sequences: np.ndarray


def package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(Path(__file__).with_name("config.json")))
    parser.add_argument("--dataset-root", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--max-runs-per-label", type=int, default=None)
    args = parser.parse_args()

    config_path = Path(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if args.dataset_root is not None:
        config["dataset_root"] = args.dataset_root
    if args.out is not None:
        config["out_dir"] = args.out
    if args.seed is not None:
        config["seed"] = args.seed
    if args.max_runs_per_label is not None:
        config["max_runs_per_label"] = args.max_runs_per_label

    out_dir = Path(config.get("out_dir", "analysis/ae_public_eval/results"))
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []
    dataset_root = Path(str(config["dataset_root"]))
    if not dataset_root.is_absolute():
        dataset_root = REPO_ROOT / dataset_root
    if not dataset_root.exists():
        raise FileNotFoundError(
            f"dataset_root does not exist: {dataset_root}. "
            "For public RanSAP evaluation, clone/extract the dataset under data/raw/RanSAP "
            "or pass --dataset-root."
        )

    seed = int(config.get("seed", 0))
    rng = np.random.default_rng(seed)
    feature_config = FeatureConfig(**config.get("feature", {}))
    label_rules = config.get("label_rules")
    include_unknown = bool(config.get("include_unknown", False))

    sources = discover_trace_sources(dataset_root, label_rules=label_rules, include_unknown=include_unknown)
    sources = _cap_sources_per_label(sources, config.get("max_runs_per_label"))
    if not sources:
        raise RuntimeError(f"no labeled RanSAP-style sources found under {dataset_root}")
    log_lines.append(f"discovered_sources={len(sources)}")

    runs: list[RunTensor] = []
    for source in sources:
        events = read_trace_events(source)
        frames = build_frames(events, feature_config)
        sequences = make_sequences(frames.frames, feature_config.sequence_length, feature_config.stride)
        if sequences.shape[0] == 0:
            log_lines.append(f"skipped_short_run={source.run_id}")
            continue
        runs.append(
            RunTensor(
                run_id=source.run_id,
                label=source.label,
                source_kind=source.kind,
                event_count=frames.event_count,
                entropy_event_count=frames.entropy_event_count,
                frame_count=frames.frames.shape[0],
                sequences=sequences,
            )
        )

    splits = _split_runs(runs, rng, config)
    train_x = _concat_sequences(splits["train"])
    cal_x = _concat_sequences(splits["calibration"])
    test_x, test_labels, test_run_ids = _concat_with_labels(splits["test"])
    if train_x.shape[0] == 0 or cal_x.shape[0] == 0 or test_x.shape[0] == 0:
        raise RuntimeError("train, calibration, and test splits must all contain at least one sequence")

    normalizer = RobustNormalizer().fit(train_x)
    train_norm = normalizer.transform(train_x)
    cal_norm = normalizer.transform(cal_x)
    test_norm = normalizer.transform(test_x)

    model_type = str(config.get("model", {}).get("type", "numpy_mlp"))
    if model_type == "numpy_mlp":
        model, model_scores, model_summary = _train_numpy_mlp(train_norm, cal_norm, test_norm, config, out_dir)
    elif model_type in {"torch_gru", "torch_cnn_gru"}:
        model, model_scores, model_summary = _train_torch_model(model_type, train_norm, cal_norm, test_norm, config)
    else:
        raise ValueError(f"unknown model.type: {model_type}")

    cal_scores = model_scores["calibration"]
    test_scores = model_scores["test"]
    threshold = calibrate_threshold(cal_scores, float(config.get("threshold_quantile", 0.99)))
    ae_metrics = binary_metrics(test_labels, test_scores, threshold.threshold)
    ae_metrics["auroc"] = roc_auc(test_labels, test_scores)
    ae_metrics["average_precision"] = average_precision(test_labels, test_scores)
    ae_metrics["false_alarms_per_day_approx"] = false_alarms_per_day(
        ae_metrics, feature_config.window_seconds, feature_config.stride
    )

    baseline_results = _baseline_results(cal_x, test_x, test_labels, config, feature_config)
    scores_path = out_dir / "scores.csv"
    _write_scores(scores_path, test_run_ids, test_labels, test_scores, baseline_results)

    metrics: dict[str, Any] = {
        "verdict": "INCONCLUSIVE",
        "reason": _verdict_reason(config),
        "source_mode": config.get("source_mode", "public_ransap"),
        "model": {
            "type": model_type,
            "threshold": threshold.__dict__,
            "score_summary": {
                "train": score_summary(model_scores["train"]),
                "calibration": score_summary(cal_scores),
                "test": score_summary(test_scores),
            },
            "metrics_at_threshold": ae_metrics,
        },
        "baselines": baseline_results["metrics"],
        "splits": _split_summary(splits),
        "runs": [_run_summary(run) for run in runs],
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    model_summary["normalizer"] = normalizer.to_dict()
    (out_dir / "model_summary.json").write_text(json.dumps(model_summary, indent=2), encoding="utf-8")

    command = " ".join([Path(sys.executable).name, *sys.argv])
    output_files = ["metrics.json", "model_summary.json", "scores.csv"]
    if (out_dir / "model.npz").exists():
        output_files.append("model.npz")
    manifest = {
        "purpose": "Evaluate memory-aware AutoEncoder candidates on 10-second storage-I/O statistics.",
        "source_refs": [
            "https://github.com/manabu-hirano/RanSAP",
            "https://doi.org/10.1016/j.fsidi.2021.301314",
            "https://www.kaggle.com/datasets/hiranomanabu/ransap-2022-ransomware-behavioral-features/",
        ],
        "dataset_refs": [
            {
                "name": config.get("dataset_name", "RanSAP"),
                "root": str(dataset_root),
                "mode": config.get("source_mode", "public_ransap"),
                "license_note": "RanSAP is distributed under CC BY-ND 4.0 per its public README.",
            }
        ],
        "command": command,
        "python_version": platform.python_version(),
        "package_versions": {
            "numpy": package_version("numpy"),
            "torch": package_version("torch"),
        },
        "parameters": config,
        "random_seed": seed,
        "split_protocol": (
            "Run-level split: train and calibration use benign runs only; test contains held-out benign "
            "runs plus attack runs. No adjacent windows from a run cross train/cal/test unless a user "
            "changes the split policy."
        ),
        "feature_schema": feature_schema(feature_config),
        "metrics": metrics,
        "output_files": output_files,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": metrics["verdict"],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def _cap_sources_per_label(sources: list[TraceSource], max_runs: int | None) -> list[TraceSource]:
    if not max_runs:
        return sources
    counts: dict[str, int] = {}
    capped: list[TraceSource] = []
    for source in sources:
        count = counts.get(source.label, 0)
        if count >= max_runs:
            continue
        capped.append(source)
        counts[source.label] = count + 1
    return capped


def _split_runs(runs: list[RunTensor], rng: np.random.Generator, config: dict[str, Any]) -> dict[str, list[RunTensor]]:
    benign = [run for run in runs if run.label == "benign"]
    attacks = [run for run in runs if run.label == "attack"]
    if len(benign) < 3:
        raise RuntimeError("at least three benign runs are required for run-level train/calibration/test splitting")
    if not attacks:
        raise RuntimeError("at least one attack run is required for evaluation")

    benign_order = list(rng.permutation(len(benign)))
    benign = [benign[idx] for idx in benign_order]
    train_fraction = float(config.get("train_fraction", 0.6))
    calibration_fraction = float(config.get("calibration_fraction", 0.2))
    train_count = max(1, int(round(len(benign) * train_fraction)))
    train_count = min(train_count, len(benign) - 1)
    remaining = len(benign) - train_count
    cal_count = max(1, int(round(len(benign) * calibration_fraction)))
    cal_count = min(cal_count, remaining)
    train = benign[:train_count]
    calibration = benign[train_count : train_count + cal_count]
    test_benign = benign[train_count + cal_count :]
    if not test_benign:
        raise RuntimeError("split policy left no held-out benign test runs; lower train/calibration fractions")
    return {
        "train": train,
        "calibration": calibration,
        "test": test_benign + attacks,
    }


def _concat_sequences(runs: list[RunTensor]) -> np.ndarray:
    if not runs:
        return np.zeros((0, 0, 0, 0), dtype=np.float32)
    return np.concatenate([run.sequences for run in runs], axis=0)


def _concat_with_labels(runs: list[RunTensor]) -> tuple[np.ndarray, np.ndarray, list[str]]:
    x = _concat_sequences(runs)
    labels: list[int] = []
    run_ids: list[str] = []
    for run in runs:
        labels.extend([1 if run.label == "attack" else 0] * run.sequences.shape[0])
        run_ids.extend([run.run_id] * run.sequences.shape[0])
    return x, np.asarray(labels, dtype=np.int32), run_ids


def _train_numpy_mlp(
    train_norm: np.ndarray,
    cal_norm: np.ndarray,
    test_norm: np.ndarray,
    config: dict[str, Any],
    out_dir: Path,
) -> tuple[NumpyMLPAutoEncoder, dict[str, np.ndarray], dict[str, Any]]:
    model_config = config.get("model", {})
    input_dim = int(np.prod(train_norm.shape[1:]))
    ae_config = NumpyMLPAEConfig(
        input_dim=input_dim,
        latent_dim=int(model_config.get("latent_dim", 16)),
        learning_rate=float(model_config.get("learning_rate", 0.001)),
        epochs=int(model_config.get("epochs", 50)),
        batch_size=int(model_config.get("batch_size", 64)),
        seed=int(config.get("seed", 0)),
    )
    model = NumpyMLPAutoEncoder(ae_config).fit(flatten_sequences(train_norm))
    model.save(out_dir / "model.npz")
    scores = {
        "train": model.score(flatten_sequences(train_norm)),
        "calibration": model.score(flatten_sequences(cal_norm)),
        "test": model.score(flatten_sequences(test_norm)),
    }
    return model, scores, {
        "type": "numpy_mlp",
        "config": ae_config.to_dict(),
        "loss_history": model.loss_history,
        "memory_estimate": model.memory_estimate(),
    }


def _train_torch_model(
    model_type: str,
    train_norm: np.ndarray,
    cal_norm: np.ndarray,
    test_norm: np.ndarray,
    config: dict[str, Any],
):
    from rad_ae.torch_models import TorchAEConfig, build_torch_autoencoder, count_torch_parameters, require_torch

    torch, nn = require_torch()
    model_config = config.get("model", {})
    torch_config = TorchAEConfig(
        model_type="gru" if model_type == "torch_gru" else "cnn_gru",
        channels=train_norm.shape[2],
        buckets=train_norm.shape[3],
        sequence_length=train_norm.shape[1],
        latent_dim=int(model_config.get("latent_dim", 16)),
        conv_channels=int(model_config.get("conv_channels", 8)),
        gru_hidden_dim=int(model_config.get("gru_hidden_dim", 16)),
    )
    torch.manual_seed(int(config.get("seed", 0)))
    model = build_torch_autoencoder(torch_config)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(model_config.get("learning_rate", 0.001)))
    loss_fn = nn.MSELoss()
    train_tensor = torch.as_tensor(train_norm, dtype=torch.float32)
    batch_size = int(model_config.get("batch_size", 64))
    losses: list[float] = []
    model.train()
    for _epoch in range(int(model_config.get("epochs", 50))):
        epoch_losses: list[float] = []
        order = torch.randperm(train_tensor.shape[0])
        for start in range(0, train_tensor.shape[0], batch_size):
            batch = train_tensor[order[start : start + batch_size]]
            optimizer.zero_grad()
            recon = model(batch)
            loss = loss_fn(recon, batch)
            loss.backward()
            optimizer.step()
            epoch_losses.append(float(loss.detach().cpu()))
        losses.append(float(np.mean(epoch_losses)))

    def score(x: np.ndarray) -> np.ndarray:
        model.eval()
        with torch.no_grad():
            tensor = torch.as_tensor(x, dtype=torch.float32)
            recon = model(tensor).cpu().numpy()
        return np.mean((recon - x) ** 2, axis=(1, 2, 3))

    scores = {
        "train": score(train_norm),
        "calibration": score(cal_norm),
        "test": score(test_norm),
    }
    parameter_count = count_torch_parameters(model)
    return model, scores, {
        "type": model_type,
        "config": torch_config.__dict__,
        "loss_history": losses,
        "memory_estimate": {
            "parameter_count": parameter_count,
            "weight_bytes_fp32": parameter_count * 4,
            "weight_bytes_int8": parameter_count,
        },
    }


def _baseline_results(
    cal_x: np.ndarray,
    test_x: np.ndarray,
    labels: np.ndarray,
    config: dict[str, Any],
    feature_config: FeatureConfig,
) -> dict[str, Any]:
    quantile = float(config.get("threshold_quantile", 0.99))
    raw_scores = {
        "write_ratio": (_scalar_score(cal_x, 4), _scalar_score(test_x, 4)),
        "mean_write_entropy": (_scalar_score(cal_x, 7), _scalar_score(test_x, 7)),
    }
    metrics: dict[str, Any] = {}
    test_score_columns: dict[str, np.ndarray] = {}
    for name, (cal_scores, test_scores) in raw_scores.items():
        threshold = calibrate_threshold(cal_scores, quantile)
        at_threshold = binary_metrics(labels, test_scores, threshold.threshold)
        at_threshold["auroc"] = roc_auc(labels, test_scores)
        at_threshold["average_precision"] = average_precision(labels, test_scores)
        at_threshold["false_alarms_per_day_approx"] = false_alarms_per_day(
            at_threshold, feature_config.window_seconds, feature_config.stride
        )
        metrics[name] = {
            "threshold": threshold.__dict__,
            "score_summary": {
                "calibration": score_summary(cal_scores),
                "test": score_summary(test_scores),
            },
            "metrics_at_threshold": at_threshold,
        }
        test_score_columns[name] = test_scores
    return {"metrics": metrics, "test_scores": test_score_columns}


def _scalar_score(x: np.ndarray, scalar_position: int) -> np.ndarray:
    return np.mean(x[:, :, 4, scalar_position], axis=1)


def _write_scores(
    path: Path,
    run_ids: list[str],
    labels: np.ndarray,
    ae_scores: np.ndarray,
    baseline_results: dict[str, Any],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["run_id", "label", "sequence_index", "ae_score", "write_ratio_score", "entropy_score"])
        write_ratio = baseline_results["test_scores"]["write_ratio"]
        entropy = baseline_results["test_scores"]["mean_write_entropy"]
        for idx, (run_id, label, ae_score) in enumerate(zip(run_ids, labels, ae_scores)):
            writer.writerow(
                [
                    run_id,
                    "attack" if int(label) == 1 else "benign",
                    idx,
                    float(ae_score),
                    float(write_ratio[idx]),
                    float(entropy[idx]),
                ]
            )


def _split_summary(splits: dict[str, list[RunTensor]]) -> dict[str, Any]:
    return {
        name: {
            "run_count": len(runs),
            "sequence_count": int(sum(run.sequences.shape[0] for run in runs)),
            "run_ids": [run.run_id for run in runs],
        }
        for name, runs in splits.items()
    }


def _run_summary(run: RunTensor) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "label": run.label,
        "source_kind": run.source_kind,
        "event_count": run.event_count,
        "entropy_event_count": run.entropy_event_count,
        "frame_count": run.frame_count,
        "sequence_count": int(run.sequences.shape[0]),
    }


def _verdict_reason(config: dict[str, Any]) -> str:
    if config.get("source_mode") == "fixture":
        return "Smoke run on a tiny schema fixture; not empirical evidence."
    return "Feasibility experiment completed, but claims require review of dataset coverage, splits, and baselines."


if __name__ == "__main__":
    main()
