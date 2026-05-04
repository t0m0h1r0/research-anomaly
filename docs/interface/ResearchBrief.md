# ResearchBrief - Storage-Embedded Ransomware Anomaly Detection

status: SIGNED
signed_by: ResearchArchitect
created_at_utc: 2026-05-04T04:21:54Z

## Objective

Use AI anomaly detection research agents to evaluate whether a block-storage
device can detect ransomware early from cheap 10-second I/O statistics. The
working model family is a memory-aware AutoEncoder, with MNN CPU inference and a
500 KB per-volume detector-data budget as deployment constraints. The 500 KB
target is derived from a planning assumption of roughly 1 GB available across
roughly 2000 protected volumes and covers model weight information plus input
statistics/state, not shared runtime libraries.

## Current Scope

- Domain/application: storage-embedded ransomware detection from block I/O
  behavior.
- Observation boundary: SCSI/NVMe-style metadata such as timestamp, read/write
  operation, LBA or offset, transfer length, and optional cheap
  entropy/compression telemetry.
- Excluded features: host process identity, file paths, filesystem semantics,
  ransomware signatures, and expensive payload scans unless the project scope is
  formally changed.
- Dataset starting point: RanSAP, followed by RanSMAP, SNIA IOTTA, UMass storage
  traces, and other registered benign/ransomware traces as compatibility
  evidence.
- Model candidates: MLP AE, GRU AE, temporal convolution AE, and tiny CNN-GRU AE
  only if simpler models are insufficient.
- Manuscript venue/language: not selected yet.
- Initial mode: research framing, evidence audit, dataset verification, and
  reproducible experiment scaffolding.

## Required Early Outputs

1. Problem frame and ransomware anomaly taxonomy.
2. Dataset/source audit for RanSAP and benign block-I/O traces.
3. Fixed 10-second feature contract and split hygiene policy.
4. Baseline model and evaluation plan, including trivial and classical baselines.
5. Reproducible first experiment scaffold under `analysis/{study}/`.
6. Leakage, thresholding, false-positive, and device-fit risk audit.
7. Paper outline once source and experiment evidence exists.

## Constraints

- Do not claim empirical performance before manifest-backed experiments exist.
- Do not claim novelty, SOTA, MNN readiness, or 500 KB detector-data fit without
  verified literature and comparable protocol or measurement evidence.
- Preserve traceability from claim to source/data/config/code/log.
- Route material work through PLAN -> EXECUTE -> VERIFY -> AUDIT.
