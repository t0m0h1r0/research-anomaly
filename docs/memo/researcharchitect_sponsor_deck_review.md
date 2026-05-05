# ResearchArchitect Sponsor Deck Review Log

status: IN_PROGRESS
created_at: 2026-05-05
deck: `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`
audience: non-specialist research sponsors

## Scope

Create a roughly five-slide presentation introducing the current manuscript's
research content. The deck must explain the need and social significance of
storage-embedded ransomware anomaly detection while preserving the manuscript's
claim gates.

## Source Basis

- `paper/main.tex`
- `paper/sections/00_abstract.tex`
- `paper/sections/01_introduction.tex`
- `paper/sections/02_claim_gates.tex`
- `paper/sections/03_observation_threat_model.tex`
- `paper/sections/05_input_contract.tex`
- `paper/sections/06_autoencoder_candidates.tex`
- `paper/sections/07_evaluation_plan.tex`
- `paper/sections/08_mnn_implementation_plan.tex`
- `paper/sections/11_roadmap.tex`
- `docs/interface/ResearchBrief.md`
- `docs/04_embedded_constraints.md`
- `docs/evidence/manuscript_claim_gate_matrix.md`

## Slide Spine

| Slide | Claim | Proof object |
| --- | --- | --- |
| 1 | Host-side defenses need a last observation point that remains visible to storage. | Host / block-I/O / storage-detector map. |
| 2 | The study uses cheap 10-second storage statistics, not content inspection. | 10-second statistic pipeline and excluded-feature rail. |
| 3 | The AutoEncoder hypothesis looks for deviation from normal write rhythm, not malware family names. | Normal-only training and reconstruction-error scoring diagram. |
| 4 | The research value is disciplined evidence gating, including failure conditions. | Claim gate matrix. |
| 5 | Sponsor support turns "can this stop ransomware early?" into reproducible go/no-go evidence. | Roadmap and decision-gate timeline. |

## Claim Discipline

- No performance value, SOTA claim, novelty claim, MNN readiness claim, or
  500 KB achievement claim is promoted.
- RanSAP is described only as a candidate/source-audited starting point.
- The 500 KB number is stated as a per-volume detector-data constraint to be
  measured, not a completed result.
- Social impact is framed as a motivation and target benefit, not as a measured
  deployment outcome.

## Build And QA

Tooling:

```text
Node: /Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
Python: /Users/tomohiro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
Builder: Presentations skill artifact-tool build_artifact_deck.mjs
```

Generated deck:

```text
paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx
size: 36100 bytes
slide count: 5
```

Mechanical checks:

| Check | Result |
| --- | --- |
| PPTX export | PASS |
| rendered slide PNGs | PASS |
| contact sheet render | PASS |
| expected slide count in package | PASS: 5 slide XML files |
| layout quality script | PASS: 0 errors, 16 warnings |
| native chart parts | N/A: charts are authored editable primitives |
| media files | N/A: no external media embedded |

Accepted layout warnings:

- Slide 1 and Slide 5: short two-line labels are visually clean in the rendered
  PNGs although the layout checker marks them as tight.
- Slide 3: the bar chart uses direct editable text labels under each bar, which
  the checker marks as split-inline text. This is intentional and visually
  readable in the render.

## Review Rounds

Pending external/second-pass review.
