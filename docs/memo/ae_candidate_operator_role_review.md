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
- `src/rad_ae/models.py`
- `src/rad_ae/torch_models.py`
- `analysis/ae_public_eval/run.py`
- `analysis/ae_public_eval/results/smoke/manifest.json`

## Design Rule

The candidate family now uses a single role contract:

- Dense layers perform intentional information reduction.
- GRU layers attach temporal context to each frame.
- Conv1D layers perform feature analysis without owning compression. AE-4 uses
  temporal Conv1D for short-range patterns; AE-5 uses `K=1` Conv1D for
  heterogeneous within-frame feature mixing.

Any candidate that cannot explain its bottleneck under this rule should be
removed or rewritten.

## Candidate Decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| AE-1 | Keep as flat MLP capacity check. | It is a flattened Dense-only control. Its purpose is to separate MLP capacity from temporal operator value. |
| AE-2 | Reframe as two-level dense AE. | It has frame-level Dense compression and sequence-level Dense compression, with no recurrent or convolutional ambiguity. |
| AE-3 | Reframe as GRU contextual AE. | GRU now returns a contextual sequence. A per-frame Dense bottleneck performs compression before the GRU decoder. |
| AE-4 | Reframe as temporal Conv1D expansion AE. | Conv1D expands local temporal views; the bottleneck is TimeDistributed Dense `24 -> 8`. The old `Conv1D(8,1)` compression story is removed. |
| AE-5 | Reframe as constrained CNN-GRU with Dense bottleneck. | `K=1` Conv1D mixes heterogeneous feature channels, pre-GRU Dense forms a denoised frame code, GRU contextualizes, and post-GRU Dense `24 -> 8` selects the integrated bottleneck. |

## Review Rounds

Round 1 finding: MAJOR. AE-3 and AE-5 used final GRU state collapse as the
practical bottleneck, which made GRU responsible for compression.

Resolution: GRU encoders now use `return_sequences=True`; Dense bottlenecks are
applied per frame before decoding.

Round 2 finding: MAJOR. AE-4 still used a 1x1 Conv1D bottleneck, leaving Conv1D
as an implicit compression layer.

Resolution: AE-4 now uses Conv1D only for local temporal feature extraction and
uses TimeDistributed Dense for `24 -> 8 -> 24`.

Round 3 finding: MINOR. AE-5 parameter estimates and prose still reflected an
older Conv1D/channel estimate.

Resolution: AE-5 was made internally consistent at that time; Round 9 records
the later pointwise-mixer redesign.

Round 4 result: no MAJOR-or-higher findings remain in the reviewed design
contract. Remaining risk is empirical: whether the added temporal operators
improve low-false-positive detection enough to justify their conversion and
scratch-memory costs.

Round 5 finding: MAJOR. The dependency-light `numpy_mlp` experiment path did
not implement the documented AE-0/AE-1 family. The memo and paper described
`144 -> hidden -> latent -> hidden -> 144`, while `src/rad_ae/models.py`
implemented only `input -> latent -> output`. This would make the first
evaluation result narratively untraceable to the candidate table.

Resolution: `NumpyMLPAutoEncoder` now implements the flattened Dense family with
`hidden_dim` and `latent_dim`. The default `input_dim=144, hidden_dim=32,
latent_dim=8` parameter count is 9,944, matching AE-0. The public evaluation
runner and configs now record `hidden_dim`, and the smoke manifest was
regenerated.

Round 6 finding: MAJOR. AE-2 and AE-4 were proposed as first-class candidates,
but the optional PyTorch implementation exposed only GRU and CNN-GRU paths. That
made the recommended evaluation order impossible to execute from the code path.

Resolution: `torch_two_level_dense` and `torch_tcn` model paths were added,
alongside shape and parameter-count tests for AE-2, AE-3, AE-4, and AE-5.

Round 7 finding: MAJOR. The AE-2 parameter total was arithmetically wrong:
the layer details sum to 5,836 parameters, not 5,636. This affected the memo,
paper summary table, and expected implementation count.

Resolution: AE-2 totals now use 5,836 parameters and 23,344 raw FP32 weight
bytes. The size columns were changed from rounded KB values to exact raw weight
bytes to avoid unit-rounding ambiguity.

Round 8 result: no MAJOR-or-higher findings remain in the candidate narrative,
operator-role contract, parameter arithmetic, model-selection implementation,
or smoke manifest. Remaining risk is empirical and belongs to future public
dataset and MNN conversion gates.

Round 9 design update: AE-5 was further refined to make the CNN-GRU hypothesis
more meaningful for scalar-only input. The Conv1D layer now uses `K=1` for
within-frame heterogeneous feature mixing, `TD(Dense(16))` denoises that mixture
before GRU, and the post-GRU `TD(Dense(8))` is the integrated contextual
bottleneck. The updated AE-5 has 8,052 parameters and 32,208 raw FP32 weight
bytes. This preserves the rule that Conv1D analyzes, GRU contextualizes, and
Dense performs denoising/compression.
