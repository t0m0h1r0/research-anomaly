# Memory-Aware AutoEncoder Candidate Models

status: DRAFT
updated: 2026-05-04

This memo proposes concrete AutoEncoder candidates for the 500 KB model-memory
budget. The estimates are intentionally conservative design estimates, not MNN
measurements. Final claims still require converted MNN models, identical input
parity tests, and peak model-owned memory measurement.

## Sizing Assumptions

Initial input contract:

- one frame is a 10-second statistic vector,
- model input is `N` consecutive frames, or `N * 10` seconds,
- initial comparison values: `N = 6, 12, 24`,
- starting feature dimension: `D = 40` per frame after padding/alignment,
- initial shape: `[batch=1, N, D]`,
- initial example: `N = 12`, so flattened length `L = N * D = 480`.

`D = 40` is a rounded planning value. It covers the current 38 required cheap
features plus optional compression/entropy-like telemetry and padding. The
metadata-only model should still be evaluated separately with the optional
channel removed.

Weight-size estimates:

```text
FP32 bytes ~= parameter_count * 4
FP16 bytes ~= parameter_count * 2
Int8 bytes ~= parameter_count * 1 + quantization metadata
```

These numbers exclude MNN runtime memory. They also exclude MNN allocator
overhead, operator workspace, input/output buffers, and score history. The
research target should keep weights well below 240 KB so that tensor/workspace
memory has room inside the 500 KB model-owned peak budget.

## Candidate Summary

The following estimates use `D = 40` and `N = 12`.

| ID | Candidate | Sketch | Params | FP32 weights | FP16 weights | Int8 weights | Main role |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| AE-0 | Linear tiny AE | `480 -> 32 -> 8 -> 32 -> 480` | 31,784 | 124 KB | 62 KB | 31 KB | smallest useful flattened baseline |
| AE-1 | Flat MLP AE | `480 -> 64 -> 16 -> 4 -> 16 -> 64 -> 480` | 64,260 | 251 KB | 126 KB | 63 KB | stronger flattened AE baseline |
| AE-2 | Shared-frame bottleneck AE | shared `40 -> 24 -> 12`, sequence `144 -> 32 -> 8`, shared decoder | 12,540 | 49 KB | 25 KB | 12 KB | very small deployable candidate |
| AE-3a | GRU seq2seq AE, H=24 | encoder GRU, decoder GRU, per-frame dense head | 9,352 | 37 KB | 18 KB | 9 KB | first temporal AE candidate |
| AE-3b | GRU seq2seq AE, H=32 | encoder GRU, decoder GRU, per-frame dense head | 14,760 | 58 KB | 29 KB | 14 KB | stronger temporal AE candidate |
| AE-4 | Temporal convolution AE | Conv1D temporal encoder/decoder, 24 channels, 8-channel bottleneck | 9,744 | 38 KB | 19 KB | 10 KB | predictable MNN-friendly temporal model |
| AE-5 | Tiny CNN-GRU AE | per-frame feature CNN, GRU H=24, per-frame dense decoder | 9,000-30,000 | 35-117 KB | 18-59 KB | 9-29 KB | closest to original CNN-GRU hypothesis |
| AE-6 | Split hist/scalar AE | separate histogram and scalar heads with shared temporal trunk | 20,000-50,000 | 78-195 KB | 39-98 KB | 20-49 KB | explainability and loss balancing |

`AE-5` and `AE-6` are ranges because their exact parameter count depends on the
feature-family reshape and decoder-head choice.

## AE-0: Linear Tiny AE

Shape:

```text
Input [1, N, D]
  -> flatten [1, N*D]
  -> Dense 32
  -> Dense 8
  -> Dense 32
  -> Dense N*D
  -> reshape [1, N, D]
```

Why it matters:

- It is the smallest nontrivial AE baseline.
- It has no recurrent or convolution operator risk.
- Its weights scale linearly with `N` through the two large `L <-> 32` layers.
- It is a useful sanity check against simple PCA-like compression.

Expected weakness:

- It has no temporal inductive bias beyond flattening order.
- It may detect workload intensity rather than ransomware-like temporal shape.

Recommendation:

- Run first as the memory floor and as a leakage/split sanity check.
- Keep it even if stronger models win, because it shows whether temporal
  modeling actually buys anything.

## AE-1: Flat MLP AE

Shape:

```text
Input [1, N, D]
  -> flatten [1, 480]
  -> Dense 64
  -> Dense 16
  -> Dense 4
  -> Dense 16
  -> Dense 64
  -> Dense 480
  -> reshape [1, N, D]
```

Memory note:

- At `N = 12`, FP32 weights are already about 251 KB.
- This is slightly above the initial 240 KB weight target but still plausible
  under FP16 or Int8.
- At `N = 24`, this architecture becomes unattractive unless quantized.

Expected role:

- Use as the strongest flattened AE before adding temporal operators.
- Reject if it does not materially beat AE-0 or simple baselines.

## AE-2: Shared-Frame Bottleneck AE

Shape:

```text
Input [1, N, D]
  -> TimeDistributed Dense 24
  -> TimeDistributed Dense 12
  -> flatten [1, N*12]
  -> Dense 32
  -> Dense 8
  -> Dense 32
  -> Dense N*12
  -> TimeDistributed Dense 24
  -> TimeDistributed Dense D
```

Why it matters:

- It keeps per-frame encoding shared across time.
- It is much smaller than flat MLP while still compressing the whole sequence.
- It avoids GRU workspace risk.
- Parameter growth with `N` is limited to the sequence bottleneck layers.

Expected weakness:

- It may be too weak for slow temporal patterns.
- The temporal bottleneck is still a flattened sequence compression, not a true
  recurrent model.

Recommendation:

- This should be one of the first two deployability candidates.
- If AE-2 performs close to GRU/TCN, prefer it for implementation simplicity.

## AE-3: GRU Seq2Seq AE

Shape:

```text
Input [1, N, D]
  -> GRU encoder hidden H
  -> repeat/context sequence [1, N, H]
  -> GRU decoder hidden H
  -> TimeDistributed Dense D
```

Recommended hidden sizes:

- `H = 16` for the smallest smoke test,
- `H = 24` as the first serious candidate,
- `H = 32` as the upper small-model candidate.

Why it matters:

- The weights are small because recurrent parameters depend mostly on `D` and
  `H`, not directly on `N`.
- Longer context increases activation/workspace memory but not the core weight
  count.
- It naturally represents temporal rhythm changes.

MNN risk:

- GRU operator support, layout, and workspace behavior must be checked early.
- Quantization can change anomaly-score ranking even when reconstruction looks
  visually similar.

Recommendation:

- `H = 24` is the default recurrent candidate.
- Move to `H = 32` only if `H = 24` underfits and MNN memory remains easy.

## AE-4: Temporal Convolution AE

Shape:

```text
Input [1, N, D]
  -> Conv1D over time, channels 24, kernel 3
  -> Conv1D over time, channels 24, kernel 3
  -> 1x1 bottleneck, channels 8
  -> 1x1 expand, channels 24
  -> Conv1D decoder, channels 24, kernel 3
  -> Conv1D output, channels D, kernel 3
```

Implementation note:

- MNN can usually express this as Conv2D with one spatial dimension.
- Keep padding fixed and avoid dynamic sequence lengths.
- Use fixed `N` per model export.

Why it matters:

- It is often the best memory/control trade-off for embedded time-series AE.
- Weight count is nearly independent of `N`.
- Activation memory grows linearly with `N * channels`.
- It avoids recurrent operator workspace uncertainty.

Recommendation:

- Treat AE-4 as the most promising production candidate unless GRU accuracy is
  clearly better.
- Compare dilation-free and small-dilation variants only after the first
  baseline works.

## AE-5: Tiny CNN-GRU AE

Shape:

```text
Input [1, N, D]
  -> reshape each frame into feature-family buckets, e.g. [families=5, buckets=8]
  -> TimeDistributed small Conv1D over buckets
  -> per-frame embedding, e.g. 16 dims
  -> GRU encoder/decoder H=24
  -> TimeDistributed Dense or small heads back to D
```

Why it matters:

- This is closest to the original hypothesis: CNN captures per-frame feature
  correlations; GRU captures temporal behavior.
- If it beats AE-3 and AE-4, the original CNN-GRU idea earns its complexity.

Risks:

- Feature reshaping may be artificial for scalar channels.
- The decoder may become awkward if histograms and scalars need different
  output treatment.
- It adds more operator types than AE-2/AE-4.

Recommendation:

- Do not make this the first implementation.
- Run it after AE-2, AE-3, and AE-4 define the achievable quality/memory curve.

## AE-6: Split Histogram/Scalar AE

Shape:

```text
Input [1, N, D]
  -> histogram branch for LBA/length distributions
  -> scalar branch for counts, bytes, ratios, sequentiality, optional compression
  -> shared temporal trunk, GRU or Conv1D
  -> histogram reconstruction head
  -> scalar reconstruction head
```

Why it matters:

- Histograms and scalar counters have different loss behavior.
- Separate heads make channel-wise anomaly explanation cleaner.
- Loss weights can be tuned without forcing one large homogeneous output.

Risks:

- More moving pieces in MNN conversion and score parity.
- Easy to overfit the loss weighting before understanding the data.

Recommendation:

- Use only after a single-head AE shows useful signal.
- Consider it for the final paper if explanation quality is weak.

## Recommended Evaluation Order

Run candidates in this order:

1. AE-0 Linear tiny AE.
2. AE-2 Shared-frame bottleneck AE.
3. AE-4 Temporal convolution AE.
4. AE-3a GRU seq2seq AE, `H = 24`.
5. AE-3b GRU seq2seq AE, `H = 32`.
6. AE-5 Tiny CNN-GRU AE.
7. AE-6 Split histogram/scalar AE.

This order intentionally starts with models that are easy to convert and easy to
reject. CNN-GRU should be evaluated, but only after the simpler memory-friendly
models establish the baseline.

## N Trade-Off

`N` controls context length and memory pressure:

| N | Context | Flat dense weight effect | GRU/TCN weight effect | Activation/workspace effect |
| ---: | ---: | --- | --- | --- |
| 6 | 60 s | about half of `N=12` | unchanged | lower |
| 12 | 120 s | baseline estimate | unchanged | baseline |
| 24 | 240 s | about double `N=12` | unchanged | higher |

This favors GRU/TCN-style models if long context is required. Flat MLP models
are attractive only for small `N` or quantized deployments.

## Deployment Rules

- Export fixed-shape models: one `.mnn` per chosen `N` if necessary.
- Use batch size 1.
- Prefer FP16 before Int8 for the first MNN parity test, because anomaly scores
  are sensitive to quantization drift.
- Keep the output linear and compute anomaly score outside the model path.
- Reconstruct normalized feature values directly; do not require softmax over
  histograms in the embedded model unless experiments prove it is necessary.
- Measure model-owned peak memory with input, output, intermediate tensors,
  operator workspace, normalization constants, and score buffers.

## Initial Recommendation

The first serious prototype should implement AE-2 and AE-4. AE-2 gives the
smallest robust non-recurrent design. AE-4 gives temporal modeling with a
predictable MNN operator set. AE-3a should be added if AE-4 misses temporal
patterns. AE-5 should remain the original-hypothesis test, not the default.
