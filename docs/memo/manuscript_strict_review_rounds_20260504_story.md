# Manuscript Strict Review Rounds: Unsupervised AE Story

status: CLOSED
updated: 2026-05-04
scope: paper manuscript and manuscript evidence notes.

## Protocol

The manuscript was reviewed as a strict reviewer would read it after the
unsupervised-AE story revision. The review prioritized narrative coherence,
notation consistency, logical consistency, and whether the paper's evidence
gates match its claimed deployment story. The loop stops when no
MAJOR-or-higher finding remains, or after more than 10 rounds.

Severity rule used here:

- MAJOR: a reader could reasonably misunderstand why the detector is
  unsupervised, what AE is expected to prove, what "unknown threat" means, or
  what device-fit requires.
- MINOR: wording or terminology drift that does not change the scientific
  contract.

## Findings And Resolution

| Round | ID | Severity | Finding | Root fix | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | S2-R1-MAJ-001 | MAJOR | The manuscript said unsupervised AE is useful for unknown or variant ransomware, but the evaluation plan did not define how family holdout acts as a proxy for unknown-threat evaluation. | Added an explicit unknown-threat evaluation subsection: AE training/calibration uses benign data only; ransomware labels are evaluation-only for AE; supervised references use known-family training and held-out-family testing; results are diagnostic rather than a direct win/loss. | RESOLVED |
| 1 | S2-R1-MAJ-002 | MAJOR | The story now depends on many-volume deployment, but claim gates, MNN plan, and roadmap still partly read as single-volume or single-model fit checks. | Promoted device-fit to a two-level gate: per-volume 500 KB peak plus aggregate memory/CPU over volume count `V`; added shared/per-volume cost decomposition and volume-scaling protocol. | RESOLVED |
| 1 | S2-R1-MIN-001 | MINOR | Some sections still used "500 KB" as if it meant standalone model success, weakening notation and claim consistency. | Standardized language to "volume あたり 500 KB" and "aggregate device-fit" where the distinction matters. | RESOLVED |
| 2 | S2-R2-MAJ-NONE | NONE | Second review found no remaining MAJOR-or-higher manuscript issue in the unsupervised rationale, unknown-threat proxy protocol, per-volume memory budget, aggregate volume cost, or evidence gates. | No further manuscript fix required. | CLOSED |

## Verification

- `make -B` under `paper/` completed and produced `paper/build/main.pdf`.
- Final log scan found no TeX errors, LaTeX/package warnings, overfull boxes,
  undefined references, multiply-defined references, fatal errors, or emergency
  stops.
- `git diff --check` reported no whitespace errors.
