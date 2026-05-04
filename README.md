# Storage-Embedded AE Ransomware Detection Research

This repository captures the research scaffold for detecting ransomware from a
block-storage device using an embedded AutoEncoder.

The working hypothesis is:

> A storage-device-local AutoEncoder can detect ransomware by reconstructing
> normal time-series I/O behavior and flagging windows whose reconstruction
> error becomes large.

The first research target is not a product implementation. It is to decide
whether the hypothesis is testable with public data, what instrumentation is
missing, and what evidence would be strong enough to continue.

## Entry Points

- [Research Charter](docs/00_research_charter.md): goal, hypotheses, scope, and
  go/no-go criteria.
- [Data Strategy](docs/01_data_strategy.md): public datasets, required feature
  coverage, and known gaps.
- [Feature and Model Plan](docs/02_feature_model_plan.md): feature tensors,
  CNN-GRU AutoEncoder architecture, and inference path.
- [Evaluation Roadmap](docs/03_evaluation_roadmap.md): experiments, baselines,
  metrics, risks, and milestones.

## Core Assumptions

- The protected target is block storage exposed through SCSI or NVMe semantics.
- The detector observes block I/O metadata and, where available, data-derived
  entropy or compression-ratio telemetry.
- Inputs are time series built from address distribution, I/O length
  distribution, read/write ratio, and entropy-like features.
- The model is an AutoEncoder: CNN extracts local correlation and feature
  patterns; GRU compresses temporal behavior; the decoder mirrors that structure.
- Public data must be sufficient for at least a credible offline feasibility
  study.

## Current Research Shape

1. Establish a public-data feasibility baseline using RanSAP as the closest
   ransomware storage-access dataset.
2. Train on benign windows and evaluate whether ransomware windows produce
   higher reconstruction error than benign workload shifts.
3. Add broader benign block-I/O traces to stress false positives across
   enterprise, search, and storage-system workloads.
4. Decide whether entropy/compression signals require controlled replay or
   storage-device instrumentation beyond public trace metadata.

