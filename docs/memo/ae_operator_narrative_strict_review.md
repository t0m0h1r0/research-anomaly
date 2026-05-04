# AE Operator Narrative Strict Review

Date: 2026-05-04

## Scope

This review treats the AE candidate story as if it were under external review.
The focus is narrative coherence, notation consistency, operator-role discipline,
and traceability between the paper, design docs, implementation skeleton, and
tests.

Reviewed artifacts:

- `paper/sections/06_autoencoder_candidates.tex`
- `paper/sections/07_evaluation_plan.tex`
- `paper/sections/11_roadmap.tex`
- `docs/00_research_charter.md`
- `docs/02_feature_model_plan.md`
- `docs/06_memory_aware_ae_candidates.md`
- `docs/07_ae_implementation_spec.md`
- `analysis/ae_public_eval/README.md`
- `src/rad_ae/torch_models.py`
- `tests/test_torch_models.py`

## Review Rounds

| Round | ID | Severity | Finding | Resolution | Status |
| ---: | --- | --- | --- | --- | --- |
| 1 | AE-NARR-R1-MAJ-001 | MAJOR | The manuscript described AE-5 as a time-axis Conv1D while also claiming `K=1` only mixes same-frame heterogeneous features. A reviewer could read this as a contradiction about whether CNN or GRU owns temporal modeling. | The paper and specs now separate implementation axis from semantics: Conv1D is applied to the sequence layout, but `kernel_size=1` cannot inspect neighboring frames and is therefore a shared per-frame channel mixer. GRU remains the temporal-context operator. | RESOLVED |
| 1 | AE-NARR-R1-MAJ-002 | MAJOR | The paper used the metatextual phrase "user hypothesis" and did not define the difference between `[1,N,D]`, `[B,N,D]`, and framework `None`, making the manuscript feel like a working note rather than a reviewable paper. | The paper now uses "initial CNN-GRU hypothesis" and defines `X in R^{B_batch x N x D}`, `[1,N,D]` as single-volume embedded inference, and `None` as offline batch notation. | RESOLVED |
| 1 | AE-NARR-R1-MAJ-003 | MAJOR | AE-2 was central to the evaluation order in the candidate section but disappeared from the roadmap, feature-model alternatives, and ablation wording. That made the model family look ad hoc and weakened the "simpler models first" narrative. | The roadmap, feature-model plan, research charter, and evaluation ablation now explicitly include AE-2 two-level Dense between flattened MLP and temporal operators. | RESOLVED |
| 1 | AE-NARR-R1-MIN-001 | MINOR | The implementation named the AE-5 `K=1` Conv1D block `temporal_cnn`, contradicting the paper's pointwise-mixer role even though the parameterization was correct. | The PyTorch module and implementation spec now call the block `pointwise_mixer`, and the test checks the kernel size and channel dimensions. | RESOLVED |
| 2 | AE-NARR-R2-OK-001 | NONE | After the above fixes, no MAJOR-or-higher narrative, notation, operator-role, or implementation-traceability issue remains in scope. | Remaining risk is empirical: whether AE-5 improves low-false-positive detection enough to justify conversion and scratch-memory costs. | CLOSED |

## Current Verdict

No MAJOR-or-higher findings remain after Round 2. The corrected story is:

1. Dense layers own denoising, explicit bottlenecks, and information selection.
2. Conv1D `K=3` owns local temporal feature extraction in AE-4.
3. Conv1D `K=1` owns same-frame cross-feature mixing in AE-5 and does not model
   neighboring-frame context.
4. GRU owns temporal context while preserving the sequence.
5. AE-2 remains the necessary Dense-only bridge between flattened MLP baselines
   and temporal operators.
