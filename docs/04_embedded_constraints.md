# Embedded Constraints

## Added Assumptions

- A representative storage device may protect roughly 2000 volumes while
  reserving roughly 1 GB for detector data.
- This yields an engineering target of about 500 KB per volume. If the device
  budget is specified as 1 GiB rather than decimal 1 GB, the quotient is about
  524 KiB per volume, so the 500 KB target remains a conservative rounded
  budget.
- The 500 KB budget covers model weight information and the input statistics or
  per-volume detector state needed to score one volume.
- Shared libraries, the MNN runtime itself, and common runtime heap are outside
  the 500 KB budget and are amortized across the many-volume deployment.
- Final embedded inference uses Alibaba MNN on CPU.
- Offline evaluation may use another framework, but final implementation claims
  require MNN conversion and score parity.
- Deployed input is a 10-second statistics vector or tensor.
- The storage device cannot depend on difficult calculations for feature
  collection.

MNN is a reasonable target runtime to evaluate because the official project
describes it as an efficient, lightweight deep-learning framework used for
on-device and embedded inference, with CPU support, ARM optimization,
TensorFlow/Caffe/ONNX/TorchScript conversion, MNN-Compress, and FP16/Int8
quantization support. The same source notes package-size figures that are not
the same as detector-data memory, so this research must still measure converted
model weights, per-volume input statistics, and transient inference scratch
instead of assuming a converted model automatically fits.

Source:

- <https://github.com/alibaba/MNN>

## Detector-Data Budget

Treat 500 KB as a per-volume persistent detector-data budget derived from the
planning assumption of roughly 1 GB available across roughly 2000 protected
volumes. The budget covers model weight information and input statistics/state
for one volume. It excludes shared MNN runtime code, common libraries, and
common runtime heap. Transient inference scratch such as activation tensors,
operator workspace, output tensors, and reusable inference slots must still be
measured for device fit, but it is tracked separately from the 500 KB budget
because it need not be replicated for every volume at rest.

Initial budget target:

| Component | Target |
| --- | ---: |
| model weights and quantization metadata | <= 360 KB |
| retained 10-second input statistics and sequence buffers | <= 64 KB |
| normalization constants, thresholds, and calibration state | <= 24 KB |
| score history and alert explanation state | <= 16 KB |
| volume metadata, alignment, and implementation margin | <= 36 KB |
| total | <= 500 KB |

Use this accounting model:

```text
B_volume = 500 KB
V = protected volume count
Q = simultaneously allocated inference scratch slots
```

Persistent detector data:

```text
M_persistent(V) =
  M_shared_runtime
  + M_shared_weights
  + V * (M_volume_weights + M_volume_state)
```

Per-volume detector-data gates:

```text
shared-weight view:     (M_shared_weights / V) + M_volume_state <= B_volume
replicated-weight view: M_volume_weights + M_volume_state <= B_volume
```

Peak device-fit check:

```text
M_peak(V, Q) = M_persistent(V) + Q * M_transient_scratch
```

The target scale is `V ~= 2000`; smaller sweeps are useful for plots but are not
the final many-volume device-fit condition. The schedule must justify `Q`,
because multiple reusable inference slots may be needed to score all volumes
within each 10-second cadence.

## Feature Collection Rules

Allowed in the embedded collector:

- incrementing counters,
- adding transfer lengths,
- maintaining per-window sums for mean LBA and mean transfer length,
- deriving write ratio from counters,
- comparing current 10-second scalar summaries with the prior summary,
- cheap fixed-point scaling,
- reading existing compression or entropy-like hardware counters.

Avoid in the embedded collector:

- per-block Shannon entropy,
- payload scans,
- large sort or unique-LBA sets,
- per-LBA maps,
- histograms unless the target device already has cheap bucket counters,
- floating-point-heavy preprocessing,
- compression trial runs done only for detection.

## 10-Second Statistic Contract

The production input should be a fixed-shape sequence of 10-second frames. A
starting contract is:

```text
frame_10s = {
  total_count,
  total_bytes,
  write_ratio,
  mean_lba,
  mean_length,
  delta_mean_lba,
  delta_mean_length,
  optional_compression_signal,
  padding[4]
}
```

The model input is `N` consecutive frames, so the temporal context is
`N * 10` seconds. An initial `N = 12` gives roughly two minutes of context.
The exact sequence length, feature count, and hidden size should be reduced
before model work if the MNN memory harness shows pressure.

## Model Implications

CNN-GRU is no longer the default architecture. It is one candidate that must earn
its place against smaller alternatives.

Preferred evaluation order:

1. Linear tiny AE as the smallest flattened baseline.
2. Two-level dense AE as the smallest deployable candidate.
3. 1D temporal convolution AE that expands local temporal views and compresses
   only through Dense.
4. GRU contextual AE with a small hidden state and explicit Dense bottleneck.
5. Tiny CNN-GRU AE only if the first four are insufficient.

Selection criteria:

- detection quality at low false-positive budgets,
- alert timing at 10-second cadence,
- per-volume detector data under 500 KB for model weights plus input
  statistics/state,
- acceptable transient MNN scratch and inference-slot scheduling at the target
  volume count,
- no unsupported MNN operators,
- acceptable score parity after MNN conversion and quantization.

## MNN Implementation Path

1. Train and evaluate candidate models offline.
2. Freeze the input contract and normalization constants.
3. Export the chosen model through ONNX or another MNN-supported route.
4. Convert to MNN with fixed input shapes.
5. Apply MNN compression or Int8 quantization if accuracy permits.
6. Run a parity suite comparing offline scores and MNN scores on identical
   benign and ransomware windows.
7. Measure persistent detector data for model weights, quantization metadata,
   retained input statistics, normalization constants, thresholds, and score
   history.
8. Separately measure transient activation tensors, operator workspace,
   reusable inference slots, and CPU scheduling at the target volume count.
9. Reject the model if weight plus input-statistics/state data exceeds 500 KB
   per volume, or if aggregate memory/CPU at roughly 2000 volumes cannot fit the
   device budget.

## Open Questions

- Is model storage in flash separate from RAM, or is the `.mnn` model copied into
  RAM before inference?
- Is fixed-point preprocessing acceptable before MNN inference?
- Does the storage controller already expose compression ratio or entropy-like
  telemetry?
- What CPU family and clock budget are available for one inference every
  10 seconds?
