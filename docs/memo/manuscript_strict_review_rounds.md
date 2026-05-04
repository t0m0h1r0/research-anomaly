# Manuscript Strict Review Rounds

status: CLOSED
updated: 2026-05-04
scope: paper manuscript only; code review excluded by user request.

## Protocol

The manuscript was reviewed as a strict reviewer would read it, prioritizing
claim boundaries, narrative coherence, notation consistency, and logical
separation between detector inputs and offline evaluation quantities. The loop
stops when no MAJOR-or-higher manuscript finding remains, or after more than
10 rounds.

Severity rule used here:

- MAJOR: a reader could reasonably misunderstand the proposed detector,
  feature contract, evidence level, or evaluation claim.
- MINOR: wording or formatting polish that does not change the scientific
  contract.

## Findings And Resolution

| Round | ID | Severity | Finding | Root fix | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | R1-MAJ-001 | MAJOR | `\maketitle` appeared both in `paper/main.tex` and the abstract section after the TeX split. | Removed the section-local `\maketitle` so the manuscript has one title point. | RESOLVED |
| 1 | R1-MAJ-002 | MAJOR | The feature contract still implied read/write-specific mean LBA and mean transfer length, which exceeded the 10-second scalar summaries assumed in the narrative. | Reframed the main contract as total count, total bytes, write ratio, mean LBA, mean length, frame deltas, optional telemetry, and padding. Read/write-specific means are now only a separate profile if a target device explicitly emits them. | RESOLVED |
| 1 | R1-MAJ-003 | MAJOR | Overwritten bytes, affected LBA fraction, and file-level encryption progress were too easy to read as detector-observed features. | Clarified that these are estimated offline from raw trace and attack labels for evaluation, not used as scalar detector inputs. | RESOLVED |
| 1 | R1-MAJ-004 | MAJOR | The manuscript alternated between `read/write ratio`, `R/W ratio`, and `write ratio`, while the actual fixed contract uses one write-ratio scalar. | Standardized the detector feature wording to `write ratio`; retained `read/write` only for command type or dataset schema. | RESOLVED |
| 1 | R1-MAJ-005 | MAJOR | The fixed-width `D=12` table used variable-looking dimensions for optional telemetry and padding, making the slot count ambiguous. | Made the table fixed: 7 required scalars, 1 optional telemetry slot, 4 padding slots, total `D=12`; unavailable telemetry is zero-filled and zero-weighted. | RESOLVED |
| 2 | R2-MAJ-NONE | NONE | Second manuscript-only review found no remaining MAJOR-or-higher issue in narrative, notation, or detector/evaluation logic. | No further manuscript fix required. | CLOSED |

## Verification

- `make -B` under `paper/` completed and produced `paper/build/main.pdf`.
- Log scan found no TeX errors, undefined references, or overfull boxes.
- Stale-contract scan found no remaining `read/write ratio`, `R/W ratio`,
  `D=38`, `D=40`, or variable optional/padding dimensions in the manuscript.

