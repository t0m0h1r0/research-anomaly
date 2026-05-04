# AE Public Evaluation

This study implements the first reproducible AutoEncoder evaluation path for
storage-embedded ransomware anomaly detection.

## What It Runs

- Discovers RanSAP-style runs containing `ata_read.csv` and/or `ata_write.csv`.
- Aggregates I/O events into fixed 10-second frames.
- Builds sequence tensors with shape `[N, D=40]` using the feature slices in
  `docs/07_ae_implementation_spec.md`.
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
experiment machine. Offline PyTorch results still do not imply MNN readiness;
MNN conversion, score parity, and 500 KB memory measurement remain later gates.
