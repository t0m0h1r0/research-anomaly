# Combined Manuscript And Code Strict Review Rounds

status: CLOSED
updated: 2026-05-04
scope: manuscript, active specs, feature extraction code, evaluation runner,
tests, and smoke outputs after merging latest `origin/main`.

## Protocol

The review loop checked whether the paper narrative, active design documents,
feature extractor, evaluation runner, tests, and manifest-backed smoke outputs
all describe the same deployable detector. The priority was strict consistency
of story, notation, feature availability, and detector-input versus
offline-evaluation boundaries. The loop stops when no MAJOR-or-higher issue
remains, or after more than 10 rounds.

## Findings And Resolution

| Round | ID | Severity | Finding | Root fix | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | C1-MAJ-001 | MAJOR | Latest `main` had a D=12 implementation, but its slots still encoded `read_ratio`, `mean_read_lba`, `mean_write_lba`, `log_mean_read_len`, and `log_mean_write_len`, while the manuscript contract had one `write_ratio`, one `mean_lba`, one `mean_length`, two deltas, one optional telemetry slot, and four padding slots. | Rewrote `src/rad_ae/features.py` to emit the manuscript-aligned fixed `D=12` layout and updated tests, specs, and smoke manifests to the same slice order. | RESOLVED |
| 1 | C1-MAJ-002 | MAJOR | Empty 10-second windows and padding were zero-filled but still participated in normalization, training loss, and anomaly score. This contradicted the paper's mask/zero-weight claim and could make idle gaps look anomalous. | Added per-frame `score_masks`, mask-aware robust normalization, mask-aware NumPy/PyTorch loss, weighted AE scoring, and mask-aware write-ratio/telemetry baselines. | RESOLVED |
| 1 | C1-MAJ-003 | MAJOR | Active design docs still described read/write ratio and read/write-specific means, so readers could not know which contract was authoritative. | Updated data strategy, feature/model plan, embedded constraints, memory-aware candidate memo, and implementation spec to the one-write-ratio scalar contract. | RESOLVED |
| 1 | C1-MAJ-004 | MAJOR | Smoke outputs still recorded stale feature names and slices, making the reproducible evidence point at the wrong contract. | Reran `analysis/ae_public_eval/config_smoke.json` and refreshed manifest, metrics, model summary, and scores. | RESOLVED |
| 2 | C2-MAJ-NONE | NONE | Second combined review found no remaining MAJOR-or-higher mismatch across manuscript, code, active specs, tests, or smoke outputs. | No further fix required. | CLOSED |

## Verification

- Fetched latest `origin/main` and merged it into
  `codex/researcharchitect-paper-review`.
- `/Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests`
  passed.
- `/Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m py_compile src/rad_ae/features.py src/rad_ae/models.py src/rad_ae/torch_models.py analysis/ae_public_eval/run.py`
  passed.
- `/Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 analysis/ae_public_eval/run.py --config analysis/ae_public_eval/config_smoke.json`
  passed and refreshed smoke outputs.
- Manuscript log scan found no TeX errors, undefined references, package
  warnings, or overfull boxes.
