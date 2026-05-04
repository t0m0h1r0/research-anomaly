"""Template for reproducible anomaly-detection research checks.

Copy this file to analysis/{study}/run.py and adapt it. The script should be
non-interactive, safe to rerun, and explicit about dataset and split provenance.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path


def package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "example_metric": 0.0,
        "verdict": "INCONCLUSIVE",
        "reason": "Template only; replace with study-specific computation.",
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    command = " ".join([Path(sys.executable).name, *sys.argv])
    manifest = {
        "purpose": "Replace with the anomaly-detection claim being checked.",
        "source_refs": [],
        "dataset_refs": [],
        "command": command,
        "python_version": platform.python_version(),
        "package_versions": {
            "numpy": package_version("numpy"),
            "scipy": package_version("scipy"),
            "pandas": package_version("pandas"),
            "matplotlib": package_version("matplotlib"),
        },
        "parameters": vars(args),
        "random_seed": args.seed,
        "split_protocol": "Replace with train/validation/test split and leakage controls.",
        "feature_schema": "Replace with the 10-second statistic contract used by this study.",
        "metrics": metrics,
        "output_files": ["metrics.json"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": metrics["verdict"],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "run.log").write_text("Template run completed.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
