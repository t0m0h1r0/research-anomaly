# Embedded Constraints

## Added Assumptions

- Model memory available to the detector is 500 KB.
- The MNN runtime itself is outside the 500 KB budget.
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
the same as model memory, so this research must still measure the converted
model, tensor, and workspace footprint instead of assuming a converted model
automatically fits.

Source:

- <https://github.com/alibaba/MNN>

## Model-Memory Budget

Treat 500 KB as the peak memory attributable to the model path. This excludes
the MNN runtime code and common runtime heap, but includes the model file if it
is copied to RAM, model weights, input/output tensors, intermediate tensors,
operator workspace attributable to this model, and score/state buffers owned by
the detector.

Initial budget target:

| Component | Target |
| --- | ---: |
| model file and weights | <= 240 KB |
| model intermediate tensors and operator workspace | <= 160 KB |
| input/output sequence buffers | <= 32 KB |
| recurrent state or score history | <= 24 KB |
| quantization and normalization constants | <= 8 KB |
| safety margin | >= 36 KB |
| total | <= 500 KB |

The 10-second feature counters may live outside this model budget if they are
owned by the storage telemetry path. If they must be charged to the detector,
they should be measured separately and then folded into the safety margin.

## Feature Collection Rules

Allowed in the embedded collector:

- incrementing counters,
- adding transfer lengths,
- updating a small fixed histogram,
- comparing current LBA with the previous command for sequentiality,
- cheap fixed-point scaling,
- reading existing compression or entropy-like hardware counters.

Avoid in the embedded collector:

- per-block Shannon entropy,
- payload scans,
- large sort or unique-LBA sets,
- per-LBA maps,
- floating-point-heavy preprocessing,
- compression trial runs done only for detection.

## 10-Second Statistic Contract

The production input should be a fixed-shape sequence of 10-second frames. A
starting contract is:

```text
frame_10s = {
  read_count,
  write_count,
  read_bytes,
  write_bytes,
  read_lba_hist[8],
  write_lba_hist[8],
  read_len_hist[8],
  write_len_hist[8],
  sequential_read_count,
  sequential_write_count,
  optional_compression_signal
}
```

The model input is `N` consecutive frames, so the temporal context is
`N * 10` seconds. An initial `N = 12` gives roughly two minutes of context.
The exact sequence length and bucket counts should be reduced before model work
if the MNN memory harness shows pressure.

## Model Implications

CNN-GRU is no longer the default architecture. It is one candidate that must earn
its place against smaller alternatives.

Preferred evaluation order:

1. Linear tiny AE as the smallest flattened baseline.
2. Shared-frame bottleneck AE as the smallest deployable candidate.
3. 1D temporal convolution AE with fixed sequence length.
4. GRU-only AE with a small hidden state.
5. Tiny CNN-GRU AE only if the first four are insufficient.

Selection criteria:

- detection quality at low false-positive budgets,
- alert timing at 10-second cadence,
- peak MNN model memory under 500 KB, excluding the runtime,
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
7. Measure peak model memory for model load, tensors, workspace, input buffers,
   and score history, excluding the MNN runtime.
8. Reject the model if the measured model-owned peak exceeds 500 KB.

## Open Questions

- Is model storage in flash separate from RAM, or is the `.mnn` model copied into
  RAM before inference?
- Is fixed-point preprocessing acceptable before MNN inference?
- Does the storage controller already expose compression ratio or entropy-like
  telemetry?
- What CPU family and clock budget are available for one inference every
  10 seconds?
