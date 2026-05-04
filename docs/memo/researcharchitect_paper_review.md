# ResearchArchitect Paper Review

status: RESOLVED
created_at_utc: 2026-05-04
reviewer: ResearchArchitect
target: `paper/main.tex`

## Scope

This memo records a strict reviewer-style audit of the provisional manuscript on
storage-embedded AutoEncoder ransomware detection. The review emphasizes
narrative coherence, notation consistency, claim discipline, and traceability.

## Verdict

Major revision completed. The manuscript now presents itself as a falsifiable
research protocol rather than an empirical result paper. Its central question is
whether a memory-bounded AE provides incremental value over cheap storage-level
rules under a fixed observation boundary, feature contract, evidence gate, and
MNN device-fit constraint.

## Findings And Required Fixes

| ID | Severity | Finding | Required fix | Status |
|----|----------|---------|--------------|--------|
| RA-PR-001 | High | The narrative does not yet separate the paper's present contribution from future empirical claims. The title, abstract, contribution section, and conclusion still read partly like a proposal and partly like a paper awaiting results. | Reframe the manuscript as a protocol/positioned hypothesis paper. State the current contribution, the falsification criteria, and the future evidence gates in the abstract, introduction, contribution section, and conclusion. | RESOLVED |
| RA-PR-002 | High | The ransomware anomaly taxonomy is implicit. Threat model prose lists likely behaviors, but the paper lacks a compact taxonomy connecting storage-observable anomalies, confounders, and evaluation tests. | Add a taxonomy table early in the paper and use it to motivate feature groups, ablations, and false-positive tests. | RESOLVED |
| RA-PR-003 | High | Notation is inconsistent. The same `\tau` role is used for sequence index and threshold; `N`, `D`, frame, sequence, batch size, and score notation are not defined once and reused consistently. | Add a notation paragraph or table. Use a non-conflicting threshold symbol such as `\gamma`, reserve `k` or `i` for frame time, and keep batch size notation separate from feature dimension. | RESOLVED |
| RA-PR-004 | High | The feature schema has a hidden dimensional mismatch. The text moved between histogram-style metadata features, optional entropy/compression, and padded examples without proving that histogram counters are deployable. | Define fixed scalar feature profiles from 10-second summaries. Tie all model examples to the padded `D=12` contract while treating histograms as a separate future profile only if the target device exposes cheap bucket counters. | RESOLVED |
| RA-PR-005 | High | Entropy is treated too smoothly. RanSAP write entropy is useful for feasibility, but per-write entropy is not automatically a cheap embedded feature. A reviewer could see a scope leak from dataset convenience into deployment claims. | Separate dataset-provided write entropy from deployable compression/entropy-like counters. Treat write entropy as an upper-bound or ablation signal unless a target device exposes cheap telemetry. | RESOLVED |
| RA-PR-006 | Medium | Baseline fairness is under-specified. The paper lists supervised classifiers beside one-class AE baselines without explaining which comparisons answer which scientific question. | Split baselines into rule, unsupervised/classical, and supervised oracle/reference groups. State that label-trained models cannot be used to validate the one-class deployment claim without protocol caveats. | RESOLVED |
| RA-PR-007 | Medium | Related work omits two storage-relevant threads already present in the survey: cloud block-store detection/recovery and safe ransomware emulation. | Add short, disciplined discussion of DeftPunk and WannaLaugh, without overclaiming comparability to the embedded AE setting. | RESOLVED |
| RA-PR-008 | Medium | Claim traceability gates are not visible enough inside the manuscript. Source audit, dataset schema/license checks, experiment manifests, and MNN memory/parity evidence appear in docs but not as paper-level gates. | Add a claim discipline subsection or table that maps claim classes to required evidence before promotion. | RESOLVED |
| RA-PR-009 | Low | Terminology and typography are uneven: `500KB` vs `500 KB`, `AutoEncoder` vs `AE`, English/Japanese labels, `false positive` vs operational false alarms, and raw backticks in LaTeX text. | Normalize key terms and LaTeX typography where the manuscript is touched. | RESOLVED |

## Resolution Summary

- Reframed `paper/main.tex` as a verification protocol with explicit non-claims
  for performance, SOTA, MNN fit, and 500 KB achievement.
- Added paper-level claim gates and a companion evidence matrix at
  `docs/evidence/manuscript_claim_gate_matrix.md`.
- Added a storage-observable ransomware anomaly taxonomy linking signals,
  confounders, and required tests.
- Introduced consistent notation for frames, sequences, feature groups, batch
  size, score, and threshold.
- Made feature profiles explicit: scalar-only P0, frame-delta P1, and padded
  telemetry P2, with unavailable optional slots zero-filled and masked from
  loss/score.
- Separated dataset-provided write entropy from deployable cheap telemetry.
- Split baselines into rule, unsupervised, and supervised reference groups.
- Added DeftPunk and WannaLaugh discussion and citations.

## Resolution Policy

All fixes should be made in the manuscript or a companion evidence memo, not by
weakening language superficially. If an empirical or deployment claim cannot be
supported by registered evidence, the revision must convert it into a testable
gate or explicit non-claim.
