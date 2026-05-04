# Manuscript Claim Gate Matrix

status: DRAFT
created_at_utc: 2026-05-04
target: `paper/main.tex`

## Purpose

This note records the evidence gates used by the revised manuscript. It is not a
source audit and does not promote any performance, novelty, dataset, or device-fit
claim. It exists to keep future manuscript claims traceable.

## Claim Gates

| Claim class | Promotion requirement | Current status |
|-------------|-----------------------|----------------|
| Literature positioning | DOI or publication URL checked against `docs/evidence/` source notes; no novelty/SOTA language without comparable protocol evidence. | Background only. |
| Dataset usability | Schema, license, run identity, label semantics, timestamp units, operation fields, LBA/offset fields, size fields, entropy availability, and split unit audited. | Candidate only. |
| Feature contract | A reproducible extractor emits the fixed 10-second schema with documented normalization from training data only. | Design only. |
| Performance | `analysis/{study}/results/manifest.json` records command, source refs, split protocol, feature schema, parameters, seed, metrics, outputs, timestamp, and verdict. | Non-claim. |
| Low false positive | Benign workload holdout reports false alarms per volume per day at fixed threshold policy, with tuning split separated from test split. | Non-claim. |
| Entropy-independent detection | Metadata-only profile is evaluated separately from any dataset-provided write entropy or device compression/entropy telemetry. | Non-claim. |
| Unknown or variant threat detection | AE training and calibration use benign data only; ransomware family labels are evaluation-only for AE; supervised references use known-family training and held-out-family testing. Results are reported by family, variant, storage condition, and failure mode. | Proxy protocol only. |
| Architecture choice | AE candidates and rule/classical/supervised references share documented feature availability and tuning budgets. | Protocol only. |
| MNN deployability | Converted MNN model, offline/MNN score parity, converted weight size, operator support, per-volume detector-data size for weights plus retained input statistics/state, transient scratch per inference slot, scheduled scratch slot count `Q`, shared weight versus per-volume state breakdown, and aggregate memory/CPU curves over volume count `V` are measured under fixed input shapes. | Non-claim. |

## Current Manuscript Position

The revised manuscript should be read as a falsifiable protocol paper. It may
claim that the project has a defined observation boundary, feature profile,
evaluation plan, and device-fit gate. It may not claim that AE detection works,
outperforms baselines, generalizes to unknown threats, fits the per-volume
500 KB detector-data budget, satisfies aggregate memory/CPU limits across many volumes, or is
novel against all prior work until the corresponding gates above are satisfied.
