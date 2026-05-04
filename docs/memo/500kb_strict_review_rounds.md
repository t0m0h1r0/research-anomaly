# 500 KB Strict Review Rounds

status: DRAFT
created_at_utc: 2026-05-04T09:22:00Z
owner: ResearchArchitect
target: 500 KB detector-data rationale and manuscript/docs alignment

## Review Standard

This review used a strict reviewer posture. It checked ordinary correctness,
traceability, and buildability, but emphasized narrative plausibility, notation
consistency, and logical consistency around the corrected 500 KB rationale.

## Round 1 Findings

| ID | Severity | Finding | Root fix |
| --- | --- | --- | --- |
| KB-R1-MAJ-001 | MAJOR | The aggregate memory model still reported only shared memory plus per-volume state. Transient scratch was mentioned in prose but absent from the equation, so the device-fit gate could understate peak memory when multiple inference slots are needed to process thousands of volumes every 10 seconds. | Introduce a three-part accounting model: shared runtime/weights, persistent per-volume detector data, and transient inference scratch multiplied by scheduled slot count `Q`. Apply it to the memo, embedded constraints, claim gates, evaluation plan, MNN plan, and implementation checklist. |
| KB-R1-MAJ-002 | MAJOR | `docs/05_literature_survey.md` still presented an old histogram-heavy 38-39 scalar "compromise" frame. This contradicted the signed D=12 scalar-only contract and weakened the story that the deployed input is cheap 10-second statistics. | Replace the stale feature set with the current D=12 scalar contract and explicitly demote histogram counters to a separate profile only when the target device exposes cheap bucket counters. |
| KB-R1-MAJ-003 | MAJOR | The 1 GB / 2000 volumes arithmetic was narratively right but unit-ambiguous. A reviewer could object that binary units produce about 524 KiB rather than exactly 500 KB. | State that 500 KB is a rounded engineering target; if the hardware budget is 1 GiB, the precise quotient is about 524 KiB, so the 500 KB target remains conservative. |
| KB-R1-MIN-001 | MINOR | The new aggregate memory equation was too wide in the PDF build. | Split the equation into aligned lines so the notation is readable and does not produce a new overfull box. |

## Round 1 Resolution

All three MAJOR findings were addressed by root changes rather than local wording:

- memory accounting now defines `B_volume`, shared memory, per-volume detector
  data, transient scratch, and scheduled slot count `Q`;
- feature-contract prose now points to the scalar D=12 contract;
- the unit convention is documented as an engineering budget rather than a
  measured hardware capacity.

## Round 2 Findings

| ID | Severity | Finding | Decision |
| --- | --- | --- | --- |
| KB-R2-MAJ-NONE | NONE | Re-review found no remaining MAJOR-or-higher inconsistency in the 500 KB rationale, feature contract, aggregate memory equation, MNN plan, or claim gates. | Stop after round 2, below the 10-round limit. |

## Verification

- `git diff --check`
- `make -C paper`
- `rg` scan of `paper/build/main.log` found no new overfull boxes, undefined
  references, fatal errors, or emergency stops
- targeted `rg` scans for stale model-memory wording and old 38-39
  feature-contract wording
