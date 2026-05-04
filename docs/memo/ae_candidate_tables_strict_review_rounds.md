# AE Candidate Tables Strict Review Rounds

status: CLOSED
created_at_utc: 2026-05-04T00:00:00Z
owner: ResearchArchitect
target: AE candidate narrative, notation consistency, and design-space coverage

## Review Standard

This review used a strict reviewer posture. It checked normal manuscript
correctness, but weighted the verdict toward narrative plausibility, notation
consistency, and logical consistency across the AE candidate section, input
contract, anomaly taxonomy, evaluation plan, MNN plan, and roadmap.

The loop stops only when no MAJOR-or-higher finding remains, or after more than
10 rounds. This review stopped after round 2.

## Reviewed Artifacts

- `paper/sections/00_abstract.tex`
- `paper/sections/03_observation_threat_model.tex`
- `paper/sections/04_related_work.tex`
- `paper/sections/05_input_contract.tex`
- `paper/sections/06_autoencoder_candidates.tex`
- `paper/sections/07_evaluation_plan.tex`
- `paper/sections/08_mnn_implementation_plan.tex`
- `paper/sections/11_roadmap.tex`

## Round 1 Findings

| ID | Severity | Finding | Root fix |
| --- | --- | --- | --- |
| AE-TBL-R1-MAJ-001 | MAJOR | The score equation averaged over all `N x |I_g|` entries, while the input contract says padding, unavailable optional telemetry, empty-window ratios, and missing initial deltas must be excluded from loss/score. A reviewer could reject the score definition as inconsistent with the feature contract. | Introduced an explicit active mask `m_{k,i,j}`, active feature groups `G_k^+`, and group normalizer `Z_{k,g}` in the score equation. The notation section now defines the mask and its zero cases. |
| AE-TBL-R1-MAJ-002 | MAJOR | AE-3 prose said it adds GRU context to the AE-2 Dense-only hypothesis, but the fixed layer summary for AE-3 does not include AE-2's pre-frame TD(Dense) plus flattened sequence Dense path. This made the candidate taxonomy look internally inconsistent. | Reframed AE-3 as the minimal recurrent candidate: raw scalar sequence -> GRU context -> TD(Dense) bottleneck. AE-2 remains the two-level Dense bridge, and AE-3 tests temporal context directly. |
| AE-TBL-R1-MAJ-003 | MAJOR | The older "AE candidates" table grouped models by broad family and omitted AE-2 as a first-class candidate, undermining the new coverage table and the "simple-to-complex hypothesis isolation" narrative. | Replaced the family-level table with an ID-level table covering AE-0/1, AE-2, AE-3, AE-4, and AE-5 at the same granularity. |
| AE-TBL-R1-MIN-001 | MINOR | The anomaly taxonomy listed "alert time" as an observed signal for overwrite impact even though alert time is an evaluation result, not a storage observation. | Removed alert time from observed signal and kept time-to-detect / pre-alert damage in the evaluation column. |
| AE-TBL-R1-MIN-002 | MINOR | The ablation row listed AE models in a different order from the implementation order and roadmap. | Reordered the ablation text to AE-0/1, AE-2, AE-4, AE-3, AE-5. |
| AE-TBL-R1-MIN-003 | MINOR | `detector data` and `detector-data` were mixed in paper prose. | Standardized paper-facing prose to `detector-data`. |

## Round 2 Findings

| ID | Severity | Finding | Resolution |
| --- | --- | --- | --- |
| AE-TBL-R2-MIN-001 | MINOR | The first mask-aware score equation produced an overfull line and would have made the PDF less reviewable. | Split the definition with `align` and suppressed the helper-line equation number. |
| AE-TBL-R2-OK-001 | NONE | Re-review found no remaining MAJOR-or-higher issue in the score definition, AE candidate taxonomy, design-space coverage, terminology, anomaly taxonomy, evaluation order, or MNN memory narrative. | Stop after round 2, below the 10-round limit. |

## Final Verdict

No MAJOR-or-higher findings remain. The corrected narrative is:

1. Score computation now matches the feature contract through explicit masks.
2. AE-0/1, AE-2, AE-3, AE-4, and AE-5 are presented at the same granularity.
3. AE-2 is the Dense-only bridge; AE-3 is the minimal recurrent-context test;
   AE-4 is the local temporal Conv1D test; AE-5 is the constrained combined
   pointwise-mixer + GRU test.
4. The design-space coverage table is consistent with the evaluation order and
   ablation plan.
