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
- [Embedded Constraints](docs/04_embedded_constraints.md): 500 KB per-volume
  detector-data budget, 10-second statistics input, and MNN implementation path.
- [Literature Survey](docs/05_literature_survey.md): prior work on
  storage-level, filesystem-level, dynamic-analysis, and AE-based ransomware
  detection.
- [Memory-Aware AE Candidates](docs/06_memory_aware_ae_candidates.md): concrete
  small AutoEncoder examples and rough memory estimates.
- [AE Implementation Spec](docs/07_ae_implementation_spec.md): code-ready
  tensor contracts, feature slices, PyTorch skeletons, scoring, and ONNX export
  constraints.

## Core Assumptions

- The protected target is block storage exposed through SCSI or NVMe semantics.
- The detector observes block I/O metadata and, where available, data-derived
  entropy or compression-ratio telemetry.
- Inputs are time series made by collecting 10-second statistics and feeding
  `N` consecutive frames, i.e. `N * 10` seconds of context, to the model.
  Feature families include address distribution, I/O length distribution,
  read/write ratio, and optional entropy-like features.
- Deployed inputs are 10-second statistics. The device should not depend on
  expensive per-I/O or per-block calculations.
- The embedded detector-data budget is 500 KB per volume for model weights plus
  retained input statistics/state. It is derived from a planning assumption of
  roughly 1 GB across roughly 2000 volumes and excludes shared MNN
  runtime/library memory. If the target budget is stated as 1 GiB, 500 KB is a
  conservative rounded target rather than an exact quotient.
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
5. Constrain the final model to 10-second statistics and prove that MNN weights
   plus retained input statistics/state fit the 500 KB per-volume
   detector-data budget, with transient scratch measured separately.
