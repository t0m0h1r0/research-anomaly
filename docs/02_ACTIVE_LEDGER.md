# GENERATED - live state file. Append rather than rewrite during normal agent work.

# 02_ACTIVE_LEDGER

## §ACTIVE_STATE

| Field | Value |
|-------|-------|
| phase | DEPLOYED |
| branch | codex/researcharchitect-ae-public-eval |
| current_objective | Implement and smoke-verify a public RanSAP-style AE evaluation path |
| active_brief | `docs/interface/ResearchBrief.md` |
| source_artifact | none registered yet |
| next_action | Stage public RanSAP under `data/raw/RanSAP/`, run `analysis/ae_public_eval/config.json`, then audit labels, leakage, entropy ablation, and false positives |
| updated_at_utc | 2026-05-04T05:13:45Z |

## §CHECKLIST

| ID | Status | Domain | Artifact | Note | Date |
|----|--------|--------|----------|------|------|
| CHK-RAD-001 | DONE | P | `prompts/meta/kernel-project.md` | retargeted project profile to storage-embedded ransomware anomaly detection | 2026-05-04 |
| CHK-RAD-002 | DONE | P | `docs/03_PROJECT_RULES.md` | regenerated PR-1..PR-6 for the project | 2026-05-04 |
| CHK-RAD-003 | DONE | M | `docs/01_PROJECT_MAP.md` | registered active brief, current docs, directories, and initial task queue | 2026-05-04 |
| CHK-RAD-004 | DONE | M | `docs/interface/ResearchBrief.md` | captured scope as active contract | 2026-05-04 |
| CHK-RAD-005 | DONE | P | `prompts/agents-codex/`, `prompts/agents-claude/` | deployed generated agent files | 2026-05-04 |
| CHK-RAD-006 | READY | M | `docs/memo/ransomware_anomaly_problem_frame.md` | first recommended planning artifact | 2026-05-04 |
| CHK-RAD-007 | DONE | P | `paper/main.tex`, `paper/Makefile`, `Makefile` | drafted provisional XeLaTeX manuscript and make build path | 2026-05-04 |
| CHK-RAD-008 | DONE | P | `paper/main.tex`, `docs/02_feature_model_plan.md`, `docs/04_embedded_constraints.md` | clarified model input as N consecutive 10-second statistic frames | 2026-05-04 |
| CHK-RAD-009 | DONE | T | `docs/06_memory_aware_ae_candidates.md`, `paper/main.tex` | proposed concrete memory-aware AE model examples and rough size estimates | 2026-05-04 |
| CHK-RAD-010 | DONE | T | `docs/06_memory_aware_ae_candidates.md`, `paper/main.tex` | expanded AE candidate internals with layer flow, shapes, decoder behavior, and parameter breakdowns | 2026-05-04 |
| CHK-RAD-011 | DONE | R | `docs/07_ae_implementation_spec.md` | added code-ready AE tensor contracts, feature slices, PyTorch skeletons, scoring, and ONNX export spec | 2026-05-04 |
| CHK-RAD-012 | DONE | R | `src/rad_ae/` | added RanSAP-style readers, 10-second feature extraction, NumPy MLP AE baseline, optional PyTorch GRU/CNN-GRU candidates, and metrics | 2026-05-04 |
| CHK-RAD-013 | DONE | R | `analysis/ae_public_eval/` | added public RanSAP evaluation package with configs, smoke fixture, manifest-backed smoke run, and README | 2026-05-04 |
| CHK-RAD-014 | DONE | E | `docs/evidence/ransap_public_data_note.md` | recorded public RanSAP access, schema, citation, and license facts for evaluation use | 2026-05-04 |

## §ASSUMPTIONS

| ID | Status | Statement | Owner |
|----|--------|-----------|-------|
| ASM-RAD-001 | OPEN | The current repository scaffold defines the active domain as storage-embedded ransomware anomaly detection. | M |
| ASM-RAD-002 | OPEN | RanSAP is the first candidate dataset but must be source-verified before empirical work. | M/E |
| ASM-RAD-003 | OPEN | CNN-GRU AE is a candidate, not a default; smaller AE baselines must be tested first. | T/R |
| ASM-RAD-004 | OPEN | MNN conversion and 500 KB memory fit are deployment-readiness claims, not assumptions. | R/E |
| ASM-RAD-005 | OPEN | Existing T/R/E/A domains can route model design, implementation, evaluation, and writing without generic kernel changes. | Q |

## §LESSONS

| ID | Status | Lesson | Artifact |
|----|--------|--------|----------|
| LES-RAD-001 | ACTIVE | Project retargeting should change `kernel-project.md` and generated runtime docs while keeping the generic kernel stable. | `prompts/meta/kernel-project.md` |
| LES-RAD-002 | ACTIVE | Storage-ransomware anomaly detection needs explicit gates for observation boundary, leakage, thresholding, benign false positives, MNN parity, and memory fit. | `docs/03_PROJECT_RULES.md` |

## §REPLAN_LOG

| ID | Date | Trigger | Decision |
|----|------|---------|----------|
| RPL-RAD-001 | 2026-05-04 | User requested AI anomaly detection research agents and provided `research-anomaly` repository | Deploy generic research agents and retarget project rules to the existing storage-embedded ransomware anomaly-detection scaffold |

## §4 BRANCH_LOCK_REGISTRY

| ID | Branch | Worktree | Objective | Status | Updated |
|----|--------|----------|-----------|--------|---------|
| none | main | n/a | no active branch lock | INACTIVE | 2026-05-04 |
| BLK-RAD-001 | codex/researcharchitect-ae-public-eval | `/private/tmp/new-project-3-researcharchitect-ae-eval` | implement public-data AE evaluation scaffold; do not merge main until user directs | ACTIVE | 2026-05-04 |
