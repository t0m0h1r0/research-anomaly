# GENERATED - live state file. Append rather than rewrite during normal agent work.

# 02_ACTIVE_LEDGER

## §ACTIVE_STATE

| Field | Value |
|-------|-------|
| phase | REVIEW |
| branch | codex/researcharchitect-500kb-memory |
| current_objective | Complete strict AE candidate review with no MAJOR-or-higher findings in narrative, notation, logic, implementation, or smoke outputs |
| active_brief | `docs/interface/ResearchBrief.md` |
| source_artifact | none registered yet |
| next_action | Run final stale searches, tests, and paper build; commit; do not merge main until explicitly instructed |
| updated_at_utc | 2026-05-04T09:57:56Z |

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
| CHK-RAD-015 | DONE | A | `docs/memo/researcharchitect_paper_review.md`, `paper/main.tex` | strict ResearchArchitect review resolved through manuscript narrative, notation, and claim-discipline revision | 2026-05-04 |
| CHK-RAD-016 | DONE | E/A | `docs/evidence/manuscript_claim_gate_matrix.md`, `paper/main.tex` | added manuscript claim-gate evidence matrix and paper-level evidence gates | 2026-05-04 |
| CHK-RAD-017 | DONE | T/A | `paper/main.tex`, `docs/01_data_strategy.md`, `docs/02_feature_model_plan.md`, `docs/04_embedded_constraints.md`, `docs/06_memory_aware_ae_candidates.md`, `docs/07_ae_implementation_spec.md` | replaced histogram-first feature contract with scalar-only 10-second summaries and recalculated D=12 AE examples | 2026-05-04 |
| CHK-RAD-018 | DONE | R | `src/rad_ae/`, `analysis/ae_public_eval/` | updated implementation from D=40 histogram profile to latest scalar-only D=12 feature contract and refreshed smoke manifest | 2026-05-04 |
| CHK-RAD-019 | DONE | R/A | `src/rad_ae/`, `analysis/ae_public_eval/`, `docs/01_data_strategy.md`, `docs/02_feature_model_plan.md`, `docs/04_embedded_constraints.md`, `docs/06_memory_aware_ae_candidates.md`, `docs/07_ae_implementation_spec.md`, `docs/memo/combined_strict_review_rounds.md` | reconciled code and specs with the manuscript's one-write-ratio D=12 contract, added mask-aware loss/score handling, and reran smoke outputs | 2026-05-04 |
| CHK-RAD-020 | DONE | M/T/A | `docs/memo/500kb_budget_reconciliation.md`, `docs/interface/ResearchBrief.md`, `docs/04_embedded_constraints.md`, `docs/06_memory_aware_ae_candidates.md`, `paper/sections/` | corrected 500 KB rationale to per-volume detector data from roughly 1 GB over roughly 2000 volumes, excluding shared runtime/library memory and separating transient scratch | 2026-05-04 |
| CHK-RAD-021 | DONE | M/T/A | `docs/memo/500kb_strict_review_rounds.md`, `docs/04_embedded_constraints.md`, `docs/05_literature_survey.md`, `paper/sections/07_evaluation_plan.tex`, `paper/sections/08_mnn_implementation_plan.tex` | completed strict review rounds; fixed MAJOR issues in aggregate scratch accounting, stale histogram feature contract, and 500 KB unit convention | 2026-05-04 |
| CHK-RAD-022 | DONE | T/R/A | `docs/memo/ae_candidate_operator_role_review.md`, `docs/06_memory_aware_ae_candidates.md`, `docs/07_ae_implementation_spec.md`, `paper/sections/06_autoencoder_candidates.tex`, `src/rad_ae/torch_models.py` | resolved AE candidate role ambiguity: Dense performs compression, GRU provides temporal context, and Conv1D expands/extracts local temporal features | 2026-05-04 |
| CHK-RAD-023 | DONE | T/R/A | `src/rad_ae/models.py`, `src/rad_ae/torch_models.py`, `analysis/ae_public_eval/`, `docs/memo/ae_candidate_operator_role_review.md` | completed strict AE candidate re-review; aligned NumPy AE-0, added AE-2/AE-4 PyTorch paths, corrected AE-2 parameter arithmetic, and regenerated smoke outputs | 2026-05-04 |

## §ASSUMPTIONS

| ID | Status | Statement | Owner |
|----|--------|-----------|-------|
| ASM-RAD-001 | OPEN | The current repository scaffold defines the active domain as storage-embedded ransomware anomaly detection. | M |
| ASM-RAD-002 | OPEN | RanSAP is the first candidate dataset but must be source-verified before empirical work. | M/E |
| ASM-RAD-003 | OPEN | CNN-GRU AE is a candidate, not a default; smaller AE baselines must be tested first. | T/R |
| ASM-RAD-004 | OPEN | MNN conversion and 500 KB detector-data fit are deployment-readiness claims, not assumptions. | R/E |
| ASM-RAD-005 | OPEN | Existing T/R/E/A domains can route model design, implementation, evaluation, and writing without generic kernel changes. | Q |
| ASM-RAD-006 | OPEN | The 500 KB budget is a per-volume detector-data target derived from roughly 1 GB over roughly 2000 volumes; it covers model weights plus input statistics/state and excludes shared runtime/library memory. | M/R/E |
| ASM-RAD-007 | OPEN | AE candidates should keep operator roles explicit: Dense compresses, GRU contextualizes, and Conv1D expands/extracts local temporal features. | T/R/A |

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
| BLK-RAD-001 | codex/researcharchitect-ae-public-eval | `/private/tmp/new-project-3-researcharchitect-ae-eval` | continue AE evaluation implementation after main merge and scalar-only D=12 contract update | ACTIVE | 2026-05-04 |
| RAD-RA-PR | codex/researcharchitect-paper-review | `/private/tmp/new-project-3-researcharchitect-paper-review` | reviewer-grade manuscript/code audit and root-cause revision | ACTIVE | 2026-05-04 |
| RAD-RA-500KB | codex/researcharchitect-500kb-memory | `/private/tmp/new-project-3-researcharchitect-500kb-memory` | correct 500 KB detector-data budget rationale and align docs/manuscript gates | ACTIVE | 2026-05-04 |
