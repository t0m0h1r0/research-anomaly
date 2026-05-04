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
| Architecture choice | AE candidates and rule/classical/supervised references share documented feature availability and tuning budgets. | Protocol only. |
| MNN deployability | Converted MNN model, offline/MNN score parity, model file size, peak model-owned memory, and operator support are measured under fixed input shapes. | Non-claim. |

## Current Manuscript Position

The revised manuscript should be read as a falsifiable protocol paper. It may
claim that the project has a defined observation boundary, feature profile,
evaluation plan, and device-fit gate. It may not claim that AE detection works,
outperforms baselines, generalizes, fits 500 KB, or is novel against all prior
work until the corresponding gates above are satisfied.
