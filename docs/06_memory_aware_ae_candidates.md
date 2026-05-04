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

## Common Model Contract

All candidates share the same external contract:

```text
input  X     : [1, N, D] normalized 10-second statistic sequence
output X_hat : [1, N, D] reconstructed sequence
score  s     : computed outside the model from X and X_hat
```

The model should reconstruct normalized feature values directly. The embedded
model should not include thresholding, alert logic, per-channel score reduction,
or dynamic normalization. Those steps are easier to audit outside the neural
network and avoid binding operational policy into the MNN graph.

Recommended activation and output policy:

- hidden dense/conv layers: ReLU or clipped ReLU in the first prototype,
- GRU gates: framework default sigmoid/tanh,
- output layer: linear,
- postprocessing: optional clipping to the normalized feature range outside MNN,
- histogram channels: reconstruct normalized histogram bins directly, not a
  softmax distribution in the first prototype.

This means the MNN graph stays small and operator-simple. If histogram
normalization is needed for quality, it should be tested later as an ablation.

## Feature Layout Used In Examples

The initial `D = 40` planning value can be interpreted as:

| Feature group | Dims | Notes |
| --- | ---: | --- |
| read/write counts and bytes | 4 | log-scaled counters |
| read LBA histogram | 8 | normalized bucket counts |
| write LBA histogram | 8 | normalized bucket counts |
| read length histogram | 8 | log-size buckets |
| write length histogram | 8 | log-size buckets |
| sequentiality counters | 2 | read/write sequential estimates |
| optional compression/entropy and pad | 2 | can be removed in metadata-only mode |
| total | 40 | rounded deployment-friendly width |

The exact order should be frozen in the feature extractor and exported with the
MNN parity suite. A candidate may internally reshape the 32 histogram dimensions
as four 8-bin channels, but it must still accept and emit the same `[1, N, D]`
contract.

## Parameter Counting Rules

Dense layer from `A` to `B`:

```text
params = A * B + B
```

GRU layer with input `I` and hidden state `H`, assuming reset/update/new gates
and separate input/recurrent biases:

```text
params = 3 * (I * H + H * H + 2 * H)
```

Conv1D layer with input channels `Cin`, output channels `Cout`, and kernel
width `K`:

```text
params = K * Cin * Cout + Cout
```

MNN-converted files may store metadata and quantization tables, so these formulae
are only planning estimates.

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

Layer flow for `N = 12`, `D = 40`:

```text
Input X                         [1, 12, 40]
Flatten                         [1, 480]
Dense 32 + ReLU                 [1, 32]
Dense 8 + ReLU                  [1, 8]
Dense 32 + ReLU                 [1, 32]
Dense 480 + linear              [1, 480]
Reshape                         [1, 12, 40]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Dense 480 -> 32 | 15,392 |
| Dense 32 -> 8 | 264 |
| Dense 8 -> 32 | 288 |
| Dense 32 -> 480 | 15,840 |
| total | 31,784 |

Interpretation:

- The 8-dimensional bottleneck is the entire compressed representation of the
  two-minute sequence.
- The model can learn correlations between any feature at any time step, but
  only through a flattened vector.
- If this model performs well, the signal is likely dominated by coarse
  sequence-level distribution shifts rather than fine temporal dynamics.

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

Layer flow for `N = 12`, `D = 40`:

```text
Input X                         [1, 12, 40]
Flatten                         [1, 480]
Dense 64 + ReLU                 [1, 64]
Dense 16 + ReLU                 [1, 16]
Dense 4 + ReLU                  [1, 4]
Dense 16 + ReLU                 [1, 16]
Dense 64 + ReLU                 [1, 64]
Dense 480 + linear              [1, 480]
Reshape                         [1, 12, 40]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Dense 480 -> 64 | 30,784 |
| Dense 64 -> 16 | 1,040 |
| Dense 16 -> 4 | 68 |
| Dense 4 -> 16 | 80 |
| Dense 16 -> 64 | 1,088 |
| Dense 64 -> 480 | 31,200 |
| total | 64,260 |

Interpretation:

- The 4-dimensional central bottleneck forces a very strong compression.
- The larger outer layers make it a stronger flattened baseline than AE-0.
- FP32 weights already exceed the initial 240 KB weight target, so this model is
  mainly useful if FP16/Int8 parity is acceptable.

Memory note:

- At `N = 12`, FP32 weights are already about 251 KB.
- This is slightly above the initial 240 KB weight target but still plausible
  under FP16 or Int8.
- At `N = 24`, this architecture becomes unattractive unless quantized.

Expected role:

- Use as the strongest flattened AE before adding temporal operators.
- Reject if it does not materially beat AE-0 or simple baselines.

## AE-2: Shared-Frame Bottleneck AE

Layer flow for `N = 12`, `D = 40`:

```text
Input X                         [1, 12, 40]
TimeDistributed Dense 24 + ReLU  [1, 12, 24]
TimeDistributed Dense 12 + ReLU  [1, 12, 12]
Flatten                         [1, 144]
Dense 32 + ReLU                 [1, 32]
Dense 8 + ReLU                  [1, 8]
Dense 32 + ReLU                 [1, 32]
Dense 144 + ReLU                [1, 144]
Reshape                         [1, 12, 12]
TimeDistributed Dense 24 + ReLU  [1, 12, 24]
TimeDistributed Dense 40 linear  [1, 12, 40]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| shared Dense 40 -> 24 | 984 |
| shared Dense 24 -> 12 | 300 |
| Dense 144 -> 32 | 4,640 |
| Dense 32 -> 8 | 264 |
| Dense 8 -> 32 | 288 |
| Dense 32 -> 144 | 4,752 |
| shared Dense 12 -> 24 | 312 |
| shared Dense 24 -> 40 | 1,000 |
| total | 12,540 |

Interpretation:

- Each 10-second frame is first compressed from 40 dimensions to 12 dimensions
  using the same small encoder.
- The whole 12-frame sequence is then compressed through an 8-dimensional
  sequence bottleneck.
- The decoder expands the sequence bottleneck back to per-frame embeddings and
  then reconstructs each frame.
- This is a good "deployment-first" model because it preserves frame structure
  while staying dense-only.

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

Layer flow for `H = 24`, `N = 12`, `D = 40`:

```text
Input X                         [1, 12, 40]
GRU encoder, return last state   [1, 24]
Repeat context N times           [1, 12, 24]
GRU decoder, return sequence     [1, 12, 24]
TimeDistributed Dense 40 linear  [1, 12, 40]
```

Parameter detail for `H = 24`:

| Layer | Params |
| --- | ---: |
| encoder GRU, I=40, H=24 | 4,752 |
| decoder GRU, I=24, H=24 | 3,600 |
| output Dense 24 -> 40 | 1,000 |
| total | 9,352 |

Parameter detail for `H = 32`:

| Layer | Params |
| --- | ---: |
| encoder GRU, I=40, H=32 | 7,104 |
| decoder GRU, I=32, H=32 | 6,336 |
| output Dense 32 -> 40 | 1,320 |
| total | 14,760 |

Interpretation:

- The encoder reads the `N` frames in order and compresses the whole history
  into the final hidden state.
- The decoder receives that hidden state repeated across `N` steps and learns to
  reconstruct the original sequence.
- This tests whether ransomware is better represented as a temporal rhythm shift
  than as a flattened distribution shift.

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

Layer flow for `N = 12`, `D = 40`:

```text
Input X                         [1, 12, 40]
Conv1D K=3, C=24 + ReLU          [1, 12, 24]
Conv1D K=3, C=24 + ReLU          [1, 12, 24]
Pointwise Conv1D C=8 + ReLU      [1, 12, 8]
Pointwise Conv1D C=24 + ReLU     [1, 12, 24]
Conv1D K=3, C=24 + ReLU          [1, 12, 24]
Conv1D K=3, C=40 linear          [1, 12, 40]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Conv1D K=3, 40 -> 24 | 2,904 |
| Conv1D K=3, 24 -> 24 | 1,752 |
| Conv1D K=1, 24 -> 8 | 200 |
| Conv1D K=1, 8 -> 24 | 216 |
| Conv1D K=3, 24 -> 24 | 1,752 |
| Conv1D K=3, 24 -> 40 | 2,920 |
| total | 9,744 |

Interpretation:

- The model reconstructs each frame using nearby frames, so it can learn local
  temporal motifs such as burst onset, sustained write-heavy periods, and
  recovery to normal.
- Weight count is almost independent of `N`; increasing `N` mainly increases
  activation memory.
- This is likely the cleanest temporal model for MNN if recurrent operators are
  awkward or memory-hungry.

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

Layer flow for one concrete variant:

```text
Input X                                  [1, 12, 40]
Reshape per frame                        [1, 12, 5, 8]
TimeDistributed Conv1D over 8 buckets     [1, 12, 5, 8]
Flatten per-frame feature map             [1, 12, 40]
TimeDistributed Dense 16 + ReLU           [1, 12, 16]
GRU encoder hidden 24                     [1, 24]
Repeat context N times                    [1, 12, 24]
GRU decoder hidden 24                     [1, 12, 24]
TimeDistributed Dense 40 linear           [1, 12, 40]
```

Possible feature-family reshape:

| Family | Width |
| --- | ---: |
| read LBA histogram | 8 |
| write LBA histogram | 8 |
| read length histogram | 8 |
| write length histogram | 8 |
| scalar/padded group | 8 |

Interpretation:

- The per-frame CNN only looks across neighboring buckets inside each feature
  family. It is meant to learn local spatial structure such as adjacent LBA
  buckets or nearby I/O size buckets.
- The per-frame dense layer converts CNN features into a compact embedding.
- The GRU handles temporal ordering across the `N` frames.
- This is the closest model to the original CNN-GRU hypothesis, but it relies on
  a somewhat artificial 5-by-8 layout for scalar channels.

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

Layer flow for one concrete variant:

```text
Input X                                      [1, 12, 40]
Split histogram channels                     [1, 12, 32]
Split scalar channels                        [1, 12, 8]
Histogram branch Dense/Conv embedding         [1, 12, 16]
Scalar branch Dense embedding                 [1, 12, 8]
Concatenate embeddings                        [1, 12, 24]
Temporal trunk, GRU or Conv1D                 [1, 12, 24]
Histogram reconstruction head                 [1, 12, 32]
Scalar reconstruction head                    [1, 12, 8]
Concatenate outputs                           [1, 12, 40]
```

Interpretation:

- Histograms and scalar counters are reconstructed by separate heads.
- This makes per-channel error reporting cleaner and lets the training loss
  weight histograms differently from counters and ratios.
- It is useful if single-head models either overfit counters or underfit
  histogram shape.

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
