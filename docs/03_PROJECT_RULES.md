# GENERATED - do NOT edit directly. Edit prompts/meta/kernel-*.md and regenerate.

# 03_PROJECT_RULES

## PR-1 - Research Outcome and Agent-Workflow Co-Primacy

The agent system exists to advance storage-embedded ransomware anomaly detection
research while also capturing workflow lessons. Substantial tasks should produce
a research artifact and, when useful, a workflow artifact.

## PR-2 - Source, Dataset, and Experiment Traceability

Source papers, public dataset references, raw traces, processed tensors, configs,
code, logs, metrics, figures, memory reports, MNN parity outputs, and prose
claims must remain traceable. Source papers and raw traces must not be
overwritten.

## PR-3 - Model and Claim Rigor Gate

Claims about ransomware detectability, anomaly scores, thresholds, calibration,
robustness, interpretability, MNN conversion, 500 KB memory fit, or deployment
readiness require independent checks of definitions, observation boundary,
assumptions, baselines, metrics, leakage, device fit, uncertainty, and failure
modes.

## PR-4 - Literature, Benchmark, and Citation Hygiene

Internal design evidence, external literature, dataset/benchmark evidence, and
numerical evidence must be separated. No invented citations, SOTA claims,
dataset facts, device-fit claims, or empirical numbers are allowed.

## PR-5 - Reproducible Coding and Experiment Standard

Promoted experiments must be runnable from repository files plus registered data
sources. Use `analysis/{study}/run.py`, a stored config, and
`analysis/{study}/results/manifest.json` with command, dependencies, parameters,
seed, split protocol, feature schema, metrics, outputs, timestamp, and verdict.

## PR-6 - Paper and Deployment Readiness Standard

Outputs prioritize problem framing, storage-level ransomware prior work, fair
baselines, reproducible feature extraction and experiments, leakage and
false-positive analysis, ablation and robustness checks, honest limitations,
concise academic prose, MNN parity and 500 KB memory evidence, and redeployable
agent workflow artifacts.
