# ResearchArchitect Sponsor Deck Revision Review Log

status: RESOLVED
created_at: 2026-05-05
updated_at_utc: 2026-05-05T09:38:06Z
deck: `paper/presentations/storage_embedded_ransomware_sponsor_brief.pptx`
audience: non-specialist research sponsors
worktree: `/private/tmp/research-anomaly-sponsor-deck-revision`
branch: `codex/researcharchitect-sponsor-deck-revision`

## Scope

Revise the sponsor-facing five-slide research introduction deck so that it
explains the AE-01..05 candidate ladder and the purpose of evaluating each
candidate, while avoiding an overt sponsor-support request. The deck should
frame sponsor value as research judgment and claim discipline rather than as a
funding ask or deployment promise.

## Source Basis

- `docs/interface/ResearchBrief.md`
- `docs/02_ACTIVE_LEDGER.md`
- `docs/03_PROJECT_RULES.md`
- `docs/01_PROJECT_MAP.md`
- `prompts/agents-codex/ResearchArchitect.md`
- `docs/06_memory_aware_ae_candidates.md`
- `paper/sections/01_introduction.tex`
- `paper/sections/03_observation_threat_model.tex`
- `paper/sections/05_input_contract.tex`
- `paper/sections/06_autoencoder_candidates.tex`
- `paper/sections/07_evaluation_plan.tex`
- `paper/sections/08_mnn_implementation_plan.tex`
- `paper/sections/11_roadmap.tex`
- `docs/evidence/manuscript_claim_gate_matrix.md`

## Revised Slide Spine

| Slide | Purpose | Claim discipline |
| --- | --- | --- |
| 1 | Explain why storage-side observation is limited but still worth testing as a last observation point. | No general AI or detection-performance claim. |
| 2 | Show the 10-second scalar-statistic input and AE reconstruction framing. | Payload, signatures, and host context are excluded; entropy is optional only if cheap telemetry exists. |
| 3 | Put AE-01..05 at the center and explain what each candidate evaluates. | The ladder is a complexity test, not an empirical ranking. |
| 4 | Explain that evaluation asks whether AE is necessary against simple baselines and ablations. | Performance values, MNN parity, and 500 KB fit remain unmeasured. |
| 5 | Summarize the current result as a measurable go/no-go design. | No support request or deployment commitment is made. |

## AE Candidate Mapping For Presentation

| Presented ID | Source basis | Evaluation purpose |
| --- | --- | --- |
| AE-01 | AE-0 / AE-1 family | Test whether coarse 10-second statistics contain enough signal under minimal Dense capacity, with width increase only as a capacity check. |
| AE-02 | AE-2 | Test whether shared per-frame Dense encoding plus sequence compression is enough without temporal operators. |
| AE-03 | AE-3a | Test whether frame order and past context add value through the smallest recurrent candidate. |
| AE-04 | AE-4 | Test whether local adjacent-frame temporal changes are enough without GRU state. |
| AE-05 | AE-5 | Test the Tiny CNN-GRU composite only after simpler candidates, using `K=1` Conv for same-frame feature mixing and GRU for context. |

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
size: 36573 bytes
slide count: 5
```

Mechanical checks:

| Check | Result |
| --- | --- |
| PPTX export | PASS |
| rendered slide PNGs | PASS |
| contact sheet render | PASS |
| expected slide count | PASS: 5 |
| layout quality script | PASS: 0 errors, 0 warnings |
| native chart parts | N/A: deck uses editable shapes and text |
| media files | N/A: no external media embedded |

## Review Rounds

| Round | Highest severity | Findings | Response | Verdict |
| --- | --- | --- | --- | --- |
| 1 | MINOR | Slide 4/5 still used sponsor-facing jargon (`training / calibration`, `Isolation Forest`, `channel-wise error`, `MNN変換後score`, `baseline / ablation / claim gate`, `MNN parityと500KB/device-fit`); Slide 4 wrapped `Isolation Forest`; review log omitted Slide 1 footer sources. | Replaced the Slide 4/5 labels with plain Japanese, including `学習・しきい値決め`, `単純比較`, `古典的な異常検出`, `どの特徴がズレたか`, `装置用変換後も同じ点数`, `装置制約への収まり`, and `単純比較・外して試す項目・主張の証拠条件`; removed the awkward `Isolation Forest` wrap; added `paper/sections/01_introduction.tex` and `paper/sections/03_observation_threat_model.tex` to Source Basis. | All findings addressed; no MAJOR-or-higher issue remained. |

Stop condition:

```text
Repeat review and fixes until no MAJOR-or-higher issue remains, or until more
than 10 rounds have been attempted.
```

Final verdict:

```text
No MAJOR-or-higher issue remained after Round 1. All review findings were
addressed before final commit.
```
