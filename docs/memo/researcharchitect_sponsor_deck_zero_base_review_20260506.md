# ResearchArchitect Sponsor Deck Zero-Base Review 2026-05-06

status: RESOLVED
created_at: 2026-05-06
updated_at_utc: 2026-05-06T04:42:14Z
deck: `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`
audience: non-specialist research sponsors
worktree: `/private/tmp/research-anomaly-sponsor-deck-review-20260506`
branch: `codex/researcharchitect-sponsor-deck-review-20260506`

## Scope

Recreate the sponsor-facing presentation from a blank narrative, then review it
as aggressively as practical in one round. Address every finding and repeat
review/fix until no MAJOR-or-higher finding remains or more than 10 rounds have
been attempted.

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

## Zero-Base Slide Spine

| Slide | Role | Core message |
| --- | --- | --- |
| 1 | Need and social significance | Ransomware damage still passes through storage as writes, so the storage boundary is a useful last observation point to test. |
| 2 | Observation boundary | Use only cheap 10-second device-side statistics; exclude host identity, file content, signatures, and unavailable expensive features. |
| 3 | AE-01..05 purpose | Treat each AE as a research question about how much temporal/contextual complexity is necessary. |
| 4 | Evaluation plan | Start by trying to reject AE complexity; only move forward after simple rules, ablations, and device constraints are checked. |
| 5 | Sponsor readout | The useful output is a decision branch and next evidence, not a deployment claim or an overt support request. |

## Review Round 1 Findings

| ID | Severity | Finding | Response |
| --- | --- | --- | --- |
| MAJOR-01 | MAJOR | Slide 1 and Slide 2 headlines wrapped awkwardly, including a sentence-ending mark isolated on Slide 1. This made the deck look unfinished even though the content was mostly coherent. | Shortened the headlines, removed headline terminal punctuation, and widened/rebalanced title boxes. |
| MAJOR-02 | MAJOR | The deck still risked sounding like a sponsor support pitch through labels such as `スポンサーへの価値` and direct sponsor-value phrasing. | Reframed the language as `判断への価値` and `共有したい価値`, and removed the explicit `支援要請` phrasing from the visible slide text. |
| MAJOR-03 | MAJOR | AE-01..05 were visible, but the relation to source candidate names such as AE-0/1 and AE-3a was not explicit enough for reviewers comparing against the paper. | Added a plain note that the deck calls the candidates AE-01..05 in explanation order and changed source IDs to `元 AE-*` labels. |
| MAJOR-04 | MAJOR | Slide 2 used `ペイロード` and `高コストな暗号度計算`, which were both too technical and potentially misleading because cheap device counters may still exist for some crypto-like summaries. | Replaced them with `ファイル本文データ` and `安いカウンタがない暗号らしさ推定`. |
| MAJOR-05 | MAJOR | Slide 4 used evaluation jargon such as `ラベル` and `分割単位`, which undercut the non-specialist sponsor brief. | Reworded Gate 0 as checking data source, columns, attack/normal marks, and how training/evaluation are separated. |
| MAJOR-06 | MAJOR | Slide 5 mentioned device readiness in terms that could be read as already achieved, especially around MNN/device fit and 500 KB. | Kept those items in `未主張` and rewrote them as future evidence: conversion parity, retained detector data within 500 KB, and real-operation early warning. |
| MINOR-01 | MINOR | Slide 2's observation story mixed what is not used with what remains, but the retained side needed stronger everyday labels. | Kept the two-column excluded/retained structure and used labels such as `忙しさ`, `偏り`, `場所`, and `大きさ`. |
| MINOR-02 | MINOR | `暗号っぽさ` on Slide 4 was informal in a way that could sound imprecise. | Changed the ablation label to `暗号らしさなし`. |
| MINOR-03 | MINOR | Slide 5's title was longer than needed and repeated the deck goal rather than the sponsor-readable conclusion. | Shortened it to `導入判断ではなく、“次の証拠”を揃える`. |
| MINOR-04 | MINOR | Slide 3's source column was too tight after adding mapping text. | Reduced the source-label type size and widened the source column. |
| MINOR-05 | MINOR | Some headlines ended as full sentences while others were phrase headlines. | Normalized major slide headlines to phrase-style statements for a cleaner spoken presentation. |
| NIT-01 | NIT | The deck needed an auditable text extraction check because visual review alone can miss hidden slide text. | Extracted PPTX slide XML text and confirmed five slides with the intended claim scope. |

## Review Round 2 Findings

| ID | Severity | Finding | Response |
| --- | --- | --- | --- |
| R2-01 | NONE | Re-review after the Round 1 fixes found no MAJOR-or-higher findings and no remaining actionable MINOR/NIT findings. | No additional deck changes required. |

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
size: 35775 bytes
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
