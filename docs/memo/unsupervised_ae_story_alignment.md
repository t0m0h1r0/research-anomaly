# Unsupervised AE Story Alignment

status: RESOLVED
created_at_utc: 2026-05-04
target: `paper/sections/*.tex`

## Scope

This memo records the narrative alignment pass requested after the strict review
rounds. The goal was to make the manuscript explain why the design uses
unsupervised anomaly detection, why AutoEncoder is the first deployable
unsupervised candidate, and why per-volume costs matter in storage devices.

## Audit Notes

- The unsupervised rationale is now explicit: the paper is not claiming known
  ransomware family identification as its primary deployment story. It targets
  unknown or variant ransomware as deviation from learned normal block-I/O time
  series.
- AE is now justified as an implementation-oriented unsupervised candidate:
  fixed-shape input and output, external reconstruction-error scoring, and a
  path to MNN CPU operators such as Dense, Conv1D, and GRU.
- The 500 KB budget is now framed as a per-volume detector-data budget for
  model weights plus retained input statistics/state, not as shared runtime or
  all transient inference memory.
- The manuscript now requires aggregate memory and CPU measurement when the
  same detector is applied across many volumes or namespaces, because per-volume
  buffers, thresholds, calibration state, and score history can dominate total
  device cost.

## Verification

- `make -B` in `paper/` succeeds and writes `paper/build/main.pdf`.
- The final log scan reports no TeX errors, LaTeX/package warnings, Overfull
  boxes, undefined references, fatal errors, or emergency stops.
- `git diff --check` reports no whitespace errors.
