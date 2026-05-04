# AE Public Evaluation

This study implements the first reproducible AutoEncoder evaluation path for
storage-embedded ransomware anomaly detection.

## What It Runs

- Discovers RanSAP-style runs containing `ata_read.csv` and/or `ata_write.csv`.
- Aggregates I/O events into fixed 10-second frames.
- Builds sequence tensors with shape `[N, D=12]` using the scalar-only feature slices in
  `docs/07_ae_implementation_spec.md`.
- Carries a separate loss/score mask so empty-frame statistics, unavailable
  telemetry, and padding do not contribute to normalization, training loss, or
  anomaly scores.
- Trains only on benign sequences.
- Calibrates an anomaly threshold on held-out benign sequences.
- Evaluates held-out benign and attack sequences with:
  - memory-first NumPy MLP AutoEncoder,
  - optional PyTorch GRU/CNN-GRU AutoEncoder code path,
  - write-ratio and mean-write-entropy baselines.
- Writes `manifest.json`, `metrics.json`, `scores.csv`, `model_summary.json`,
  and `run.log`.

## Public RanSAP Run

Acquire RanSAP outside git, preserving the upstream files. The public README says
the dataset can be cloned from GitHub or downloaded from Kaggle, and that some
large CSV files are compressed in zip archives.

```bash
git clone https://github.com/manabu-hirano/RanSAP data/raw/RanSAP
cd data/raw/RanSAP
bash unzip-all.sh
cd ../../..
/Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 analysis/ae_public_eval/run.py --config analysis/ae_public_eval/config.json
```

The runner can also read zip-contained `ata_read.csv` and `ata_write.csv`
without extracting them, but the upstream `unzip-all.sh` path is closer to the
dataset documentation.

## Smoke Run

The fixture is a tiny schema check, not empirical evidence:

```bash
/Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 analysis/ae_public_eval/run.py --config analysis/ae_public_eval/config_smoke.json
```

Current smoke outputs are stored in `results/smoke/` with verdict
`INCONCLUSIVE` and reason `Smoke run on a tiny schema fixture`.

## Model Notes

The default `numpy_mlp` model is the memory-first baseline required before
crediting a heavier model. The optional `torch_gru` and `torch_cnn_gru` paths
implement the proposed temporal AE family when PyTorch is installed on the
experiment machine. In those paths, GRU provides temporal context, Conv1D
extracts local temporal views, and Dense layers provide the bottleneck. Offline
PyTorch results still do not imply MNN readiness;
MNN conversion, score parity, and 500 KB memory measurement remain later gates.

The current deployable profile is scalar-only. LBA and transfer-size histograms
are intentionally not part of this runner's default model input after the latest
main contract update; they should be added only as a separate exploratory
profile with its own fixed shape and manifest.
