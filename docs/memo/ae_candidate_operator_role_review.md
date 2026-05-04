# AE Candidate Operator-Role Review

Date: 2026-05-04

## Scope

This review revisits AE-1 through AE-5 after the design concern that GRU and
CNN/Conv1D should not be used as implicit compression devices. The reviewed
artifacts are:

- `docs/06_memory_aware_ae_candidates.md`
- `docs/07_ae_implementation_spec.md`
- `docs/02_feature_model_plan.md`
- `paper/sections/06_autoencoder_candidates.tex`
- `src/rad_ae/torch_models.py`
- `analysis/ae_public_eval/run.py`

## Design Rule

The candidate family now uses a single role contract:

- Dense layers perform intentional information reduction.
- GRU layers attach temporal context to each frame.
- Conv1D layers expand scalar frame sequences into multiple local temporal
  feature views and extract short-range patterns.

Any candidate that cannot explain its bottleneck under this rule should be
removed or rewritten.

## Candidate Decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| AE-1 | Keep as flat MLP capacity check. | It is a flattened Dense-only control. Its purpose is to separate MLP capacity from temporal operator value. |
| AE-2 | Reframe as two-level dense AE. | It has frame-level Dense compression and sequence-level Dense compression, with no recurrent or convolutional ambiguity. |
| AE-3 | Reframe as GRU contextual AE. | GRU now returns a contextual sequence. A per-frame Dense bottleneck performs compression before the GRU decoder. |
| AE-4 | Reframe as temporal Conv1D expansion AE. | Conv1D expands local temporal views; the bottleneck is TimeDistributed Dense `24 -> 8`. The old `Conv1D(8,1)` compression story is removed. |
| AE-5 | Reframe as constrained CNN-GRU with Dense bottleneck. | Conv1D expands to 24 local-temporal channels, GRU contextualizes, and TimeDistributed Dense `24 -> 8` is the only compression point. |

## Review Rounds

Round 1 finding: MAJOR. AE-3 and AE-5 used final GRU state collapse as the
practical bottleneck, which made GRU responsible for compression.

Resolution: GRU encoders now use `return_sequences=True`; Dense bottlenecks are
applied per frame before decoding.

Round 2 finding: MAJOR. AE-4 still used a 1x1 Conv1D bottleneck, leaving Conv1D
as an implicit compression layer.

Resolution: AE-4 now uses Conv1D only for local temporal feature extraction and
uses TimeDistributed Dense for `24 -> 8 -> 24`.

Round 3 finding: MINOR. AE-5 parameter estimates and prose still reflected a
16-channel Conv1D and an older 32 KB estimate.

Resolution: AE-5 is consistently documented as `Conv1D 12 -> 24`, with 8,804
parameters and roughly 36 KB FP32 weights.

Round 4 result: no MAJOR-or-higher findings remain in the reviewed design
contract. Remaining risk is empirical: whether the added temporal operators
improve low-false-positive detection enough to justify their conversion and
scratch-memory costs.
