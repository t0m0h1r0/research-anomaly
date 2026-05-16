# ResearchArchitect Sponsor Deck Refresh 2026-05-17

status: RESOLVED
created_at_utc: 2026-05-16T22:14:31Z
deck: `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`
deck_project: `paper/presentations/storage_embedded_ransomware_sponsor_brief/`
worktree: `/private/tmp/research-anomaly-presentation-refresh-20260517`
branch: `codex/researcharchitect-presentation-refresh-20260517`

## Scope

Refresh the sponsor-facing presentation, create the final slide deck, and review
and revise until no MAJOR-or-higher finding remains. The revised deck keeps the
Japanese sponsor-facing style but adds a stronger technical decision frame and a
reproducible artifact-tool source project.

## Source Basis

- `docs/interface/ResearchBrief.md`
- `docs/02_ACTIVE_LEDGER.md`
- `docs/03_PROJECT_RULES.md`
- `docs/01_PROJECT_MAP.md`
- `docs/04_embedded_constraints.md`
- `docs/06_memory_aware_ae_candidates.md`
- `docs/memo/500kb_budget_reconciliation.md`
- `docs/evidence/manuscript_claim_gate_matrix.md`
- `paper/sections/05_input_contract.tex`
- `paper/sections/06_autoencoder_candidates.tex`
- `paper/sections/07_evaluation_plan.tex`
- `paper/sections/08_mnn_implementation_plan.tex`

## Revised Slide Spine

| Slide | Role | Core message |
| --- | --- | --- |
| 1 | Technical scope | The research target is lightweight anomaly detection embedded in the block-I/O path. |
| 2 | Decision frame | The deck sets criteria for the next experiment before any adoption decision. |
| 3 | Input contract | The ML input is a fixed-shape sequence of low-cost 10-second statistics. |
| 4 | Candidate ladder | AE-01..05 test whether additional operators are worth evaluating. |
| 5 | Resource budget | Per-volume detector-data, shared runtime, transient scratch, and scheduling must be separated. |
| 6 | Evidence gates | Adoption, shrinking, or rejection depends on offline comparison, MNN parity, memory, and 10-second cadence. |

## Review Findings

| ID | Severity | Finding | Response |
| --- | --- | --- | --- |
| R1-MAJOR-01 | MAJOR | Budget values could be read as measured 500 KB fit. | Labeled them as upper planning targets and added measurement replacement language. |
| R1-MAJOR-02 | MAJOR | The previous deck compressed the decision readout too much. | Added Slide 2 as a decision frame and Slide 6 as the evidence-gate close. |
| R1-MINOR-01 | MINOR | Slide 1 bottom panels were too tight in the first render. | Increased panel dimensions and rerendered. |
| R1-MINOR-02 | MINOR | Slide 3 had an awkward render line break. | Shortened the fixed-shape explanation. |
| R1-MINOR-03 | MINOR | Red non-claim badges could trigger naive positive-claim grep checks. | Reworded them as explicit non-claims. |

## QA

```text
PPTX output: paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx
PPTX size: 46799 bytes
slide count: 6
layout quality: PASS, 0 errors, 0 warnings
text extraction: PASS, 6 slides
claim grep: PASS, no forbidden positive-claim hits
render/contact sheet: PASS
```

Claim audit:

```text
No file-name-protection framing remains.
The deck includes block-storage embedding, technical input details, AE-01..05,
MNN parity, 500 KB detector-data, and 10-second scheduling gates.
No performance, novelty, SOTA, MNN readiness, 500 KB fit, or deployment-readiness claim is promoted.
```

## Flair Revision

After user feedback requesting more `外連味`, the deck was revised with a dark
editorial opening/decision/closing rhythm, stronger lead lines, a circuit-like
block-storage visual frame, and sharper gate language. Claim strength was not
broadened.

## Readability Correction

After follow-up feedback that the background shifts felt unpleasant and slide
claims were unclear, the deck was revised again to use one light editorial
background system across all six slides. Each slide now has an explicit `主張`
line directly under the headline; the darker theatrical treatment is retained
only as local accent/callout styling. Claim strength was not broadened.

## Copy Consistency Correction

After follow-up feedback that Japanese wording and contrast logic felt awkward,
the deck copy was revised to remove ambiguous references such as `この資料は`,
avoid mismatched `AではなくB` pairings, and replace `rawログ` with the more
precise contrast between raw event sequences and 10-second statistics. Claim
strength was not broadened.

## Full Copy Review

After follow-up feedback asking for a full review rather than point fixes, all
slide titles, claim lines, figure labels, table headers, callouts, and guard
badges were re-edited as one copy system. The revision aligns slide-level
claims with proof objects, reduces awkward mixed Japanese/English phrasing, and
standardizes terms such as `10秒間隔`, `ボリューム`, `軽量メタデータ`, and
`score一致`. Claim strength was not broadened.

Final stop condition:

```text
No MAJOR-or-higher finding remained after focused render review and repair.
All generated slides passed layout and claim-gate checks.
No main merge was performed.
```
