# Round 6 Diagram Clarity Review

created_at_utc: 2026-05-16T23:12:53Z
trigger: user feedback that architecture, AE-01..05 readout, and weight/state relationship were unclear
artifact: `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`

## Revision

Redesigned the three weakest proof-object slides:

- Slide 1 now has one architecture path: Host / VM -> observation boundary -> 10-second statistics -> AE score.
- Slide 1 explicitly separates used information, verified path, and unused information.
- Slide 4 now explains what AE-01..05 reveal, rather than listing candidates as a table.
- Slide 4 separates the readouts: simple candidates are enough, temporal/local features matter, or the combined candidate deserves MNN/memory checks.
- Slide 5 now separates model weights, per-volume state, detector-data, aggregate memory, and transient scratch.
- Slide 5 states which quantity changes with AE candidate, volume count, and inference-slot count.

## QA

| Check | Result |
| --- | --- |
| PPTX export | PASS |
| Slide count | PASS: 6 |
| Rendered contact sheet | PASS |
| Layout quality | PASS: 0 errors, 0 warnings |
| Claim grep | PASS: no forbidden positive-claim hits |
| Claim discipline | PASS: no performance, novelty, SOTA, MNN readiness, 500 KB fit, or deployment-readiness claim promoted |

## Judgment

PASS. The deck now gives each of the criticized slides one clear proof object
and one intended readout, while preserving the research claim gates.
