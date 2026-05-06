# ResearchArchitect Sponsor Deck Technical Revision 2026-05-06

status: RESOLVED
created_at: 2026-05-06
updated_at_utc: 2026-05-06T04:54:12Z
deck: `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`
worktree: `/private/tmp/research-anomaly-sponsor-deck-review-20260506`
branch: `codex/researcharchitect-sponsor-deck-review-20260506`

## User Feedback Addressed

| Feedback | Deck response |
| --- | --- |
| `ファイル名を守るという話はどこから来た？` | Removed the file-name-protection framing. Slide 1 now starts from block-I/O flow and the storage observation boundary. |
| `技術的な話はほしい` | Added concrete input tensor, feature contract, AE operator roles, planning parameter counts, MNN parity, memory accounting, and scheduling gates. |
| `ブロックストレージに組み込むという話も盛り込んでほしい` | Slide 1 is now a block-storage integration diagram with host, controller, protected volumes, collector, feature ring, and AE score path. |
| `MLに与えられるリソースが限られているという話もほしい` | Slide 4 is now a resource-budget slide covering 500 KB per-volume detector data, retained input state, transient scratch, `V ~= 2000`, inference slots, and 10-second CPU window. |

## Revised Slide Spine

| Slide | Revised role |
| --- | --- |
| 1 | Technical scope: lightweight anomaly detector embedded in the block-I/O path. |
| 2 | Input contract: cheap 10-second block-storage statistics to fixed-shape ML input. |
| 3 | Model candidates: AE-01..05 as technical hypothesis tests and operator-role comparisons. |
| 4 | Resource budget: persistent detector data, shared runtime separation, transient scratch, and scheduling constraints. |
| 5 | Evaluation gates: offline comparison, MNN score parity, detector-data measurement, and 10-second scheduling. |

## QA

```text
PPTX output: paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx
size: 38272 bytes
slide count: 5
layout quality: PASS, 0 errors, 0 warnings
render/contact sheet: PASS
text extraction: PASS, 5 slides
```

Claim audit:

```text
No "ファイル名を守る" framing remains.
The deck includes ブロックストレージ, ML, MNN, and 500 KB resource framing.
No support-request wording remains.
No performance, SOTA, MNN readiness, 500 KB fit, or deployment-readiness claim is promoted.
```
