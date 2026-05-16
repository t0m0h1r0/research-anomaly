# GENERATED - live state file. Append rather than rewrite during normal agent work.

# 02_ACTIVE_LEDGER

## §ACTIVE_STATE

| Field | Value |
|-------|-------|
| phase | PRESENTATION_REFRESH |
| branch | codex/researcharchitect-presentation-refresh-20260517 |
| current_objective | Holistically revise sponsor deck copy, labels, and claim-to-proof alignment |
| active_brief | `docs/interface/ResearchBrief.md` |
| source_artifact | `git@github.com:t0m0h1r0/research-agent.git` remote snapshot @ `ed38873`, materialized into `prompts/meta/` |
| next_action | Await user review or explicit main no-ff merge instruction; do not merge to `main` otherwise |
| updated_at_utc | 2026-05-16T23:00:55Z |

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
| CHK-RAD-024 | DONE | T/R/A | `docs/06_memory_aware_ae_candidates.md`, `docs/07_ae_implementation_spec.md`, `paper/sections/06_autoencoder_candidates.tex`, `src/rad_ae/torch_models.py` | refined AE-5 to use `K=1` Conv1D for cross-feature mixing, pre-GRU TD Dense frame denoising, GRU context, and post-GRU Dense bottleneck selection | 2026-05-04 |
| CHK-RAD-025 | DONE | A/T/R | `docs/memo/ae_operator_narrative_strict_review.md`, `paper/sections/`, `docs/`, `src/rad_ae/torch_models.py`, `tests/test_torch_models.py` | completed strict AE operator-narrative review; resolved pointwise Conv1D axis ambiguity, AE-2 roadmap omission, manuscript notation, and implementation naming consistency | 2026-05-04 |
| CHK-CODEXOPTI-001 | DONE | P | `prompts/agents-codex/_base.yaml`, `prompts/meta/kernel-deploy.md`, `artifacts/P/codex_config_optimization_audit.md` | optimized Codex shared runtime/git/prompt-budget defaults and recorded prompt audit checks | 2026-05-04 |
| CHK-CODEXOPTI-002 | DONE | P | `AGENTS.md`, `prompts/README.md`, `prompts/meta/kernel-deploy.md`, `artifacts/P/agents_runbook_optimization_audit.md` | optimized external-agent runbook for read order, source integrity, artifact routing, claim gates, experiments, and merge discipline | 2026-05-04 |
| CHK-UPPROMPT-001 | DONE | P | `prompts/upstream.toml`, `scripts/sync_research_agent.py`, `prompts/meta/`, `prompts/agents-*`, `prompts/skills/` | synced shared research-agent kernel revision `4459e3e`, added local refresh wrapper, and preserved `prompts/meta/kernel-project.md` by hash | 2026-05-05 |
| CHK-RAD-026 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `docs/memo/researcharchitect_sponsor_deck_review.md` | created sponsor-facing five-slide research introduction deck; resolved review after 3 rounds with no MAJOR-or-higher findings | 2026-05-05 |
| CHK-RAD-027 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `docs/memo/researcharchitect_sponsor_deck_revision_review.md` | revised sponsor deck to foreground AE-01..05 overview and evaluation purpose while avoiding an overt support request; addressed all review findings with no MAJOR-or-higher findings after 1 round | 2026-05-05 |
| CHK-UPPROMPT-002 | DONE | P | `prompts/upstream.toml`, `prompts/upstream-managed.json`, `prompts/meta/`, `prompts/agents-*`, `prompts/skills/`, `scripts/` | synced upstream metaprompt-only revision `8abd3a7`, preserved `kernel-project.md`, redeployed local agents/helpers, and passed prompt audit | 2026-05-05 |
| CHK-UPPROMPT-003 | DONE | P | `prompts/upstream.toml`, `prompts/upstream-managed.json`, `prompts/meta/`, `prompts/agents-*`, `prompts/skills/`, `scripts/validate_prompt_deployment.py`, `artifacts/P/research_agent_upstream_sync_audit_c985b65.md` | synced upstream metaprompt-only revision `c985b65`, preserved `kernel-project.md`, redeployed 24 Codex + 24 Claude prompts and 9 local skill capsules, removed redeploy marker after prompt audit PASS | 2026-05-06 |
| CHK-RAD-028 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `docs/memo/researcharchitect_sponsor_deck_review_20260506.md` | completed strict sponsor deck review in a new worktree; addressed 5 MAJOR, 5 MINOR, and 1 NIT finding, then re-reviewed with no MAJOR-or-higher findings after 2 rounds | 2026-05-06 |
| CHK-RAD-029 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `docs/memo/researcharchitect_sponsor_deck_zero_base_review_20260506.md` | recreated sponsor deck from a blank narrative; addressed 6 MAJOR, 5 MINOR, and 1 NIT finding, then re-reviewed with no MAJOR-or-higher findings after 2 rounds | 2026-05-06 |
| CHK-RAD-030 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `docs/memo/researcharchitect_sponsor_deck_technical_revision_20260506.md` | revised sponsor deck to remove file-name-protection framing and foreground block-storage embedding, technical AE/input details, and constrained ML resources | 2026-05-06 |
| CHK-UPPROMPT-004 | DONE | P | `.gitmodules`, `prompts/upstream/research-agent`, `prompts/upstream.toml`, `prompts/upstream-managed.json`, `prompts/meta/`, `prompts/agents-codex/`, `prompts/skills/SKILL-PROMPT-AUDIT.md`, `wiki_knowledge_injection_report.json`, `artifacts/P/research_agent_submodule_prompt_sync_f52ae6f.md` | added research-agent as a pinned submodule, synced shared metaprompts at `f52ae6f`, preserved `kernel-project.md`, redeployed Codex prompt artifacts for AP-17/wiki-packet audit discipline, and passed prompt audit | 2026-05-16 |
| CHK-UPPROMPT-005 | DONE | P | `scripts/sync_research_agent.py`, `scripts/deploy_prompt_system.py`, `scripts/validate_prompt_deployment.py`, `prompts/upstream.toml`, `prompts/upstream-managed.json`, `prompts/meta/`, `prompts/agents-*`, `prompts/skills/`, `token_roi_report.json`, `artifacts/P/research_agent_remote_snapshot_prompt_sync_ed38873.md` | discontinued persistent `prompts/upstream/` submodule, synced latest remote metaprompt snapshot `ed38873`, preserved `kernel-project.md`, zero-base regenerated local agents/skills/docs/reports, and passed prompt audit with Q3-16 token-ROI reporting | 2026-05-17 |
| CHK-RAD-031 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `paper/presentations/storage_embedded_ransomware_sponsor_brief/`, `docs/memo/researcharchitect_sponsor_deck_refresh_20260517.md` | refreshed sponsor-facing presentation into a six-slide technical decision narrative; added editable artifact-tool source and resolved render/claim review with 0 layout errors/warnings | 2026-05-17 |
| CHK-RAD-032 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_2_flair.md` | revised the sponsor deck for stronger editorial contrast and more theatrical lead lines while preserving non-claim gates; rerendered with 0 layout errors/warnings | 2026-05-17 |
| CHK-RAD-033 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_3_visual_consistency.md` | corrected abrupt background shifts by returning all slides to one light editorial system and adding explicit `主張` lines; rerendered with 0 layout errors/warnings | 2026-05-17 |
| CHK-RAD-034 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_4_copy_consistency.md` | tightened Japanese copy, removed ambiguous `この資料は` framing, and corrected mismatched contrast pairs; rerendered with 0 layout errors/warnings | 2026-05-17 |
| CHK-RAD-035 | DONE | A | `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`, `paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_5_full_copy_review.md` | reviewed all slide titles, claim lines, figure labels, tables, callouts, and guard badges as one copy system; rerendered with 0 layout errors/warnings | 2026-05-17 |

## §ASSUMPTIONS

| ID | Status | Statement | Owner |
|----|--------|-----------|-------|
| ASM-RAD-001 | OPEN | The current repository scaffold defines the active domain as storage-embedded ransomware anomaly detection. | M |
| ASM-RAD-002 | OPEN | RanSAP is the first candidate dataset but must be source-verified before empirical work. | M/E |
| ASM-RAD-003 | OPEN | CNN-GRU AE is a candidate, not a default; smaller AE baselines must be tested first. | T/L |
| ASM-RAD-004 | OPEN | MNN conversion and 500 KB detector-data fit are deployment-readiness claims, not assumptions. | L/E |
| ASM-RAD-005 | OPEN | Existing T/L/E/A domains can route model design, implementation, evaluation, and writing without generic kernel changes. | Q |
| ASM-RAD-006 | OPEN | The 500 KB budget is a per-volume detector-data target derived from roughly 1 GB over roughly 2000 volumes; it covers model weights plus input statistics/state and excludes shared runtime/library memory. | M/L/E |
| ASM-RAD-007 | OPEN | AE candidates should keep operator roles explicit: Dense compresses or denoises, GRU contextualizes, AE-4 Conv1D extracts local temporal features, and AE-5 `K=1` Conv1D mixes heterogeneous per-frame features. | T/L/A |

## §LESSONS

| ID | Status | Lesson | Artifact |
|----|--------|--------|----------|
| LES-RAD-001 | ACTIVE | Project retargeting should change `kernel-project.md` and generated runtime docs while keeping the generic kernel stable. | `prompts/meta/kernel-project.md` |
| LES-RAD-002 | ACTIVE | Storage-ransomware anomaly detection needs explicit gates for observation boundary, leakage, thresholding, benign false positives, MNN parity, and memory fit. | `docs/03_PROJECT_RULES.md` |
| LES-RAD-003 | ACTIVE | Shared prompt refreshes should come from upstream `research-agent`, with `kernel-project.md` treated as project-local and verified unchanged before accepting sync output. | `scripts/sync_research_agent.py` |
| LES-RAD-004 | ACTIVE | Upstream now distributes metaprompts only; skills, helper scripts, templates, and agent prompts must be regenerated and audited inside each receiving project. | `prompts/upstream.toml` |
| LES-RAD-005 | ACTIVE | Upstream revision `c985b65` changes implementation-domain notation from `R` to `L` and adds role-triggered scheme/code, paper-writing, deck, and illustration/readback skill loops; local prompt audit must check the 9-capsule manifest and Q3b `skill_trigger_tokens`. | `artifacts/P/research_agent_upstream_sync_audit_c985b65.md` |
| LES-RAD-006 | SUPERSEDED | Shared metaprompt updates were temporarily pinned through `prompts/upstream/research-agent`; this was replaced by remote-snapshot sync in LES-RAD-007. | `artifacts/P/research_agent_submodule_prompt_sync_f52ae6f.md` |
| LES-RAD-007 | ACTIVE | Persistent upstream checkouts are unnecessary for this receiving project; shared metaprompts should be pulled from an ephemeral remote snapshot, materialized into `prompts/meta/`, and followed by zero-base local deployment while preserving `kernel-project.md`. | `artifacts/P/research_agent_remote_snapshot_prompt_sync_ed38873.md` |

## §REPLAN_LOG

| ID | Date | Trigger | Decision |
|----|------|---------|----------|
| RPL-RAD-001 | 2026-05-04 | User requested AI anomaly detection research agents and provided `research-anomaly` repository | Deploy generic research agents and retarget project rules to the existing storage-embedded ransomware anomaly-detection scaffold |
| RPL-RAD-002 | 2026-05-05 | User moved latest meta/agent prompts to `git@github.com:t0m0h1r0/research-agent.git` | Import shared kernel/skills/generated agents from upstream while keeping this project's `kernel-project.md` local |
| RPL-RAD-003 | 2026-05-05 | Upstream revision `8abd3a7` changed the distribution contract | Import only shared metaprompts from upstream, preserve the local project profile, and regenerate project-local agents, skills, docs, and helper scripts |
| RPL-RAD-004 | 2026-05-06 | Upstream revision `c985b65` added scheme/code, paper-writing, presentation-generation, and visual-concept prompt operations | Import shared metaprompts only, preserve the local project profile, redeploy project-local prompts/skills/docs, and require 9-skill + Q3b telemetry audit before removing the redeploy marker |
| RPL-RAD-005 | 2026-05-16 | User requested research-agent metaprompts be taken in as a submodule and latest Codex agents redeployed | Add `research-agent` as a pinned submodule, sync shared kernel files from the submodule, preserve the local project profile, and redeploy/audit Codex prompt artifacts with AP-17 wiki-packet checks |
| RPL-RAD-006 | 2026-05-17 | User requested preserving `kernel-project.md`, taking in latest metaprompts, discontinuing the `upstream` directory, and deploying from zero base | Remove the persistent submodule checkout, sync shared kernel files from the remote snapshot only, preserve the local project profile by hash, regenerate all local derived prompt artifacts, and audit Q3-16 token ROI |

## §4 BRANCH_LOCK_REGISTRY

| ID | Branch | Worktree | Objective | Status | Updated |
|----|--------|----------|-----------|--------|---------|
| BLK-RAD-001 | codex/researcharchitect-ae-public-eval | `/private/tmp/new-project-3-researcharchitect-ae-eval` | continue AE evaluation implementation after main merge and scalar-only D=12 contract update | ACTIVE | 2026-05-04 |
| RAD-RA-PR | codex/researcharchitect-paper-review | `/private/tmp/new-project-3-researcharchitect-paper-review` | reviewer-grade manuscript/code audit and root-cause revision | ACTIVE | 2026-05-04 |
| RAD-RA-500KB | codex/researcharchitect-500kb-memory | `/private/tmp/new-project-3-researcharchitect-500kb-memory` | correct 500 KB detector-data budget rationale and align docs/manuscript gates | ACTIVE | 2026-05-04 |
| RAD-CODEXCFG | codex/optimize-codex-config | `/private/tmp/research-anomaly-codex-config` | optimize Codex prompt configuration and audit compactness/trust boundaries | ACTIVE | 2026-05-04 |
| RAD-UPPROMPT | codex/external-research-agent-prompts | `/Users/tomohiro/Documents/research-anomaly` | adapt project to upstream research-agent prompt sync and preserve local project profile | ACTIVE | 2026-05-05 |
| RAD-RA-SPONSORDECK | codex/researcharchitect-sponsor-deck | `/private/tmp/research-anomaly-sponsor-deck` | create and review sponsor-facing five-slide research introduction deck | ACTIVE | 2026-05-05 |
| RAD-RA-SPONSORDECK-REV | codex/researcharchitect-sponsor-deck-revision | `/private/tmp/research-anomaly-sponsor-deck-revision` | revise sponsor deck around AE-01..05 candidate overview and review until no MAJOR-or-higher findings remain | ACTIVE | 2026-05-05 |
| RAD-UPPROMPT2 | codex/researcharchitect-prompt-refresh | `/private/tmp/research-anomaly-prompt-refresh` | sync upstream metaprompt-only revision `8abd3a7` and redeploy local prompt artifacts | ACTIVE | 2026-05-05 |
| RAD-UPPROMPT3 | codex/researcharchitect-prompt-refresh-20260506 | `/private/tmp/research-anomaly-prompt-refresh-20260506` | sync upstream metaprompt-only revision `c985b65` and redeploy local prompt artifacts | ACTIVE | 2026-05-06 |
| RAD-RA-SPONSORDECK-REVIEW-20260506 | codex/researcharchitect-sponsor-deck-review-20260506 | `/private/tmp/research-anomaly-sponsor-deck-review-20260506` | strict review and zero-base revision of sponsor deck until no MAJOR-or-higher findings remain | ACTIVE | 2026-05-06 |
| RAD-UPPROMPT4 | codex/researcharchitect-prompt-submodule-20260516 | `/private/tmp/research-anomaly-prompt-submodule-20260516` | add research-agent as a submodule, sync latest shared metaprompts, and redeploy Codex prompt artifacts | ACTIVE | 2026-05-16 |
| RAD-UPPROMPT5 | codex/researcharchitect-zero-base-prompt-deploy-20260517 | `/Users/tomohiro/Documents/research-anomaly` | sync latest shared metaprompts from remote snapshot, remove persistent upstream directory, and zero-base redeploy local prompt artifacts | ACTIVE | 2026-05-17 |
| RAD-RA-PRESREFRESH-20260517 | codex/researcharchitect-presentation-refresh-20260517 | `/private/tmp/research-anomaly-presentation-refresh-20260517` | refresh sponsor-facing presentation, create editable deck source/PPTX, and review until no MAJOR-or-higher findings remain | ACTIVE | 2026-05-17 |
