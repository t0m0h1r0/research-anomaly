# ResearchArchitect Sponsor Deck Review 2026-05-06

status: RESOLVED
created_at: 2026-05-06
updated_at_utc: 2026-05-06T04:24:06Z
deck: `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`
audience: non-specialist research sponsors
worktree: `/private/tmp/research-anomaly-sponsor-deck-review-20260506`
branch: `codex/researcharchitect-sponsor-deck-review-20260506`

## Scope

Review the existing sponsor-facing research presentation in a new worktree,
raise as many issues as practical in one round, address every finding, and
repeat review/fix until no MAJOR-or-higher finding remains or more than 10
rounds have been attempted.

## Source Basis

- `docs/interface/ResearchBrief.md`
- `docs/02_ACTIVE_LEDGER.md`
- `docs/03_PROJECT_RULES.md`
- `docs/01_PROJECT_MAP.md`
- `prompts/agents-codex/PresentationWriter.md`
- `prompts/agents-codex/PaperReviewer.md`
- `docs/06_memory_aware_ae_candidates.md`
- `paper/sections/01_introduction.tex`
- `paper/sections/03_observation_threat_model.tex`
- `paper/sections/05_input_contract.tex`
- `paper/sections/06_autoencoder_candidates.tex`
- `paper/sections/07_evaluation_plan.tex`
- `paper/sections/08_mnn_implementation_plan.tex`
- `paper/sections/11_roadmap.tex`
- `docs/evidence/manuscript_claim_gate_matrix.md`

## Review Round 1 Findings

| ID | Severity | Finding | Response |
| --- | --- | --- | --- |
| MAJOR-01 | MAJOR | Slide 1 did not clearly translate the research need into social significance for non-specialist sponsors. It said the storage view is limited, but not why that limited view matters after host-side defenses fail. | Rebuilt Slide 1 around the last-observation-point story: host context may be unavailable, but block writes still cross the storage boundary. Added explicit social significance, research value, and claim-scope rails. |
| MAJOR-02 | MAJOR | Slides 2, 4, and 5 used too many internal terms for the audience: `D=12`, `N=12`, `mask`, `optional`, `X-hat`, `score`, `benign`, `label`, `false alarm`, `entropy`, `LBA`, `length`, `parity`. | Rewrote visible labels into plain Japanese. Kept `D=12` and `N=12` only as small design-condition chips, and replaced jargon with phrases such as `未提供欄は採点から外す`, `誤警報の少なさ`, and `装置用変換後も同じ点数`. |
| MAJOR-03 | MAJOR | Slide 3 included AE-01..05, but the dense table required sponsors to scan four columns and map source IDs before understanding the purpose of each candidate. | Converted Slide 3 into a five-card ladder. Each AE now has one memorable evaluation question and a quiet source-ID note. |
| MAJOR-04 | MAJOR | The deck did not sufficiently explain why AE might be unnecessary, although rejecting complexity is a core research outcome. | Rebuilt Slide 4 around three gates: `単純規則で足りるか`, `どのAEまで必要か`, and `装置に載せられるか`. |
| MAJOR-05 | MAJOR | The 500 KB constraint was mentioned without context, which could sound like an achieved result or arbitrary number. | Reframed the device constraint as a future gate: one-volume retained detector data must stay small enough for many protected volumes. Removed any implication that device fit has already been measured. |
| MINOR-01 | MINOR | Slide 2 mixed what the device sees with what the model receives. | Separated the input story into `装置境界に残るもの` and `AEに渡す形`. |
| MINOR-02 | MINOR | Slide 5 still had English fragments such as `low false alarm` and technical shorthand. | Replaced them with plain Japanese status rows: `誤警報を低くした時の検知可否`, `装置制約への収まり`, and related terms. |
| MINOR-03 | MINOR | The previous status slide felt defensive because repeated non-claim badges dominated the message. | Reframed Slide 5 as `固定済み` versus `まだ測るもの`, with one decision line at the bottom. |
| MINOR-04 | MINOR | The deck lacked a shared visual language for test gates. | Used a consistent gate/checkpoint language across Slides 3-5. |
| MINOR-05 | MINOR | Source footers needed to remain exact after the rewrite. | Updated per-slide source footers to match the revised claim basis. |
| NIT-01 | NIT | Standalone `AI` phrasing risked sounding hype-like even when negated. | Replaced the visible story with AE/anomaly-detector language and avoided `万能なAI` framing. |

## Review Round 2 Findings

| ID | Severity | Finding | Response |
| --- | --- | --- | --- |
| R2-01 | NONE | Rendered re-review found no MAJOR-or-higher findings and no remaining actionable MINOR/NIT findings. | No additional deck changes required. |

## Build And QA

Tooling:

```text
Node: /Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
Python: /Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
Builder: Presentations skill artifact-tool build_artifact_deck.mjs
Layout check: check_layout_quality.mjs
```

Generated deck:

```text
paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx
size: 35690 bytes
slide count: 5
```

Mechanical checks:

| Check | Result |
| --- | --- |
| PPTX export | PASS |
| rendered slide PNGs | PASS |
| contact sheet render | PASS |
| expected slide count | PASS: 5 |
| PPTX slide XML text extraction | PASS: 5 slides |
| layout quality script | PASS: 0 errors, 0 warnings |
| claim gate audit | PASS: no performance, novelty, SOTA, MNN readiness, device-fit, or deployment-readiness claim promoted |

Final stop condition:

```text
No MAJOR-or-higher finding remained after Round 2.
All Round 1 findings were addressed.
Round limit: 10.
```
