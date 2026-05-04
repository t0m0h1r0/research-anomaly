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
- [Embedded Constraints](docs/04_embedded_constraints.md): 500 KB model memory
  budget, 10-second statistics input, and MNN implementation path.
- [Literature Survey](docs/05_literature_survey.md): prior work on
  storage-level, filesystem-level, dynamic-analysis, and AE-based ransomware
  detection.

## Core Assumptions

- The protected target is block storage exposed through SCSI or NVMe semantics.
- The detector observes block I/O metadata and, where available, data-derived
  entropy or compression-ratio telemetry.
- Inputs are time series built from address distribution, I/O length
  distribution, read/write ratio, and entropy-like features.
- Deployed inputs are 10-second statistics. The device should not depend on
  expensive per-I/O or per-block calculations.
- The embedded model memory budget is 500 KB, excluding the MNN runtime.
- Alibaba MNN is the target runtime for the final embedded implementation.
  Offline evaluation may use another framework, but MNN conversion and parity
  testing are mandatory before implementation claims.
- The model remains an AutoEncoder, but the CNN-GRU design is now a constrained
  candidate rather than a default; it must fit the memory and cheap-feature
  budget.
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
5. Constrain the final model to 10-second statistics and prove that the MNN
   model path fits the 500 KB model-memory budget.
