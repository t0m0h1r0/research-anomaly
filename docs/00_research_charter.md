# Research Charter

## Research Question

Can a block-storage device detect ransomware early by running an embedded
AutoEncoder over time-series I/O behavior, without relying on host agents,
filesystem paths, process identity, or ransomware signatures?

## Primary Hypothesis

Ransomware that encrypts user data creates a measurable shift in storage I/O
behavior:

- write-heavy bursts,
- changed LBA locality and overwrite patterns,
- changed I/O size distribution,
- increased write-payload entropy or reduced compressibility,
- temporal sequences that differ from normal workload rhythms.

If an AutoEncoder learns normal sequences, the reconstruction error for
ransomware windows should exceed a threshold calibrated on benign workloads.

## Model Hypothesis

A CNN-GRU AutoEncoder remains a candidate architecture because:

- CNN layers can learn local temporal correlations across neighboring
  10-second scalar frames.
- GRU layers can learn temporal transitions between windows without requiring a
  heavy transformer-class model in the storage device.
- A mirrored decoder gives an interpretable reconstruction-error signal per
  feature channel and per time step.

However, the deployed model must fit a 500 KB model-memory budget, excluding the
MNN runtime, and consume only 10-second statistics that are cheap to collect. If
CNN-GRU cannot fit that budget after quantization and MNN conversion, the
research should prefer a smaller AE such as GRU-only, temporal convolution AE,
or MLP bottleneck AE over preserving the original architecture.

## Scope

Included:

- Block storage observation model for SCSI/NVMe style read and write commands.
- Offline feature extraction and model evaluation.
- Public datasets and reproducible synthetic transformations.
- Device-feasibility estimates for inference cost, memory, and telemetry.
- A final implementation path using Alibaba MNN for CPU inference.
- A deployed telemetry model based on 10-second statistics.

Excluded for the initial phase:

- Host endpoint agent design.
- Filesystem or process-level detection.
- Signature-based ransomware classification.
- Production firmware integration.
- Automatic response actions such as write blocking or snapshot rollback.
- Features that require expensive payload scanning, per-block cryptographic
  analysis, or heavy per-I/O computation in the storage device.

## Threat Model

The attacker runs ransomware on a host that has legitimate access to the
protected block device. The storage device sees block commands but does not know
process identity, file names, file extensions, user intent, or application
semantics.

The detector should handle:

- classic encrypt-then-overwrite behavior,
- read-modify-write behavior,
- bursts over many logical addresses,
- BitLocker or already-encrypted volumes where entropy is less discriminative.

The detector is expected to struggle with:

- very slow or throttled ransomware,
- workloads that naturally encrypt, compress, scrub, rehydrate, or backup data,
- small targeted encryption with little LBA coverage,
- benign bulk rewrite jobs that resemble attack behavior.

## Evidence Needed To Continue

Continue the research if offline experiments show all of the following:

- ransomware windows are separable from benign windows at low false-positive
  rates,
- detection time is early enough to matter operationally,
- the signal remains useful when entropy is removed or degraded,
- model memory plausibly fits 500 KB with 10-second statistics and CPU
  inference,
- the final model can be converted to MNN with acceptable score parity,
- false-positive analysis identifies practical allow-listing or calibration
  paths.

Stop or redesign if:

- reconstruction error mostly tracks workload intensity rather than ransomware
  behavior,
- benign backup, compression, encryption, or database maintenance workloads
  dominate the anomaly score,
- public data cannot support entropy/compression evaluation,
- the architecture requires host-only context to be credible.
- the MNN model cannot fit the 500 KB model-memory budget or requires
  unsupported operators.

## Initial Success Criteria

- Detection: high recall at a fixed false-positive budget such as 1 false alarm
  per protected volume per day in offline trace replay.
- Time to detect: alert before a large fraction of the decoy or protected LBA
  range is overwritten.
- Robustness: preserve ranking quality across HDD/SSD, volume size, OS variant,
  and encrypted-volume conditions where public data permits.
- Explainability: report reconstruction error by feature channel so operators can
  see whether the anomaly is address, length, read/write, entropy, or temporal.
- Implementability: keep model weights, model-owned tensors, and input/output
  buffers within 500 KB, excluding the MNN runtime itself.
