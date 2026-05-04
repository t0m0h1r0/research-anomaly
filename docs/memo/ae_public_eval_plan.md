# AE Public Evaluation Plan

status: DRAFT
created_at_utc: 2026-05-04T05:09:53Z
owner: ResearchArchitect

## Objective

Implement the first reproducible path from public storage-access traces to
AutoEncoder anomaly scores under the active 10-second statistics contract.

## Implemented Scope

- RanSAP-style CSV and zip discovery.
- Canonical event schema: timestamp, operation, LBA, transfer size, optional
  write entropy.
- Feature tensor: `[N, D=12]` scalar-only sequences with the slice layout frozen in
  `docs/07_ae_implementation_spec.md`.
- Split policy: train on benign runs only, calibrate on held-out benign runs,
  test on held-out benign plus attack runs.
- Default model: memory-first NumPy MLP AutoEncoder over flattened sequences.
- Optional model code: PyTorch GRU and tiny CNN-GRU AutoEncoder candidates.
- Baselines: write-ratio and mean-write-entropy thresholds calibrated on benign
  data.
- Evidence outputs: metrics, scores, model summary, run log, and manifest.

## Deliberate Non-Claims

- The smoke fixture is only a schema and execution check.
- The default MLP AE is a baseline, not proof that CNN-GRU is unnecessary.
- The PyTorch CNN-GRU code path is not MNN readiness evidence.
- No result should support ransomware-detection claims until full public RanSAP
  data is run and independently audited for labels, leakage, and false-positive
  behavior.

## Next Verification Gates

1. Run the public RanSAP config on a local dataset clone or extract.
2. Inspect discovered run labels and add an explicit label map if path inference
   is ambiguous.
3. Run entropy ablation with `feature.include_entropy=false`.
4. Compare `numpy_mlp`, `torch_gru`, and `torch_cnn_gru` where PyTorch is
   available.
5. Add benign false-positive traces from UMass or SNIA before any operational
   false-alarm claim.
6. Promote only audited manifests into research-summary or manuscript claims.
