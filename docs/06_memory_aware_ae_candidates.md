# Memory-Aware AutoEncoder Candidate Models

status: DRAFT
updated: 2026-05-04

This memo proposes concrete AutoEncoder candidates for the 500 KB model-memory
budget. The current deployable feature contract is scalar-only: it does not
assume LBA or transfer-length histograms unless a target device explicitly
exposes cheap per-window bucket counters.

The estimates below are planning estimates, not MNN measurements. Final claims
still require converted MNN models, identical input parity tests, and peak
model-owned memory measurement.

## Sizing Assumptions

Initial input contract:

- one frame is a 10-second statistic vector,
- model input is `N` consecutive frames, or `N * 10` seconds,
- initial comparison values: `N = 6, 12, 24`,
- starting feature dimension: `D = 12` per frame after optional padding,
- initial shape: `[batch=1, N, D]`,
- initial example: `N = 12`, so flattened length `L = N * D = 144`.

`D = 12` covers the scalar statistics that can be emitted from 10-second
window summaries: total intensity, read/write ratio, read/write mean LBA,
read/write mean transfer length, cheap frame-to-frame deltas, one optional
compression/entropy-like telemetry slot, and one padding/alignment slot.

Weight-size estimates:

```text
FP32 bytes ~= parameter_count * 4
FP16 bytes ~= parameter_count * 2
Int8 bytes ~= parameter_count * 1 + quantization metadata
```

These numbers exclude MNN runtime memory. They also exclude MNN allocator
overhead, operator workspace, input/output buffers, normalization constants,
and score history. The research target should keep weights well below 240 KB
so tensor/workspace memory has room inside the 500 KB model-owned peak budget.

## Common Model Contract

All candidates share the same external contract:

```text
input  X     : [1, N, 12] normalized 10-second statistic sequence
output X_hat : [1, N, 12] reconstructed sequence
score  s     : computed outside the model from X and X_hat
```

The model should reconstruct normalized scalar feature values directly. The
embedded model should not include thresholding, alert logic, per-channel score
reduction, or dynamic normalization.

Recommended activation and output policy:

- hidden dense/conv layers: ReLU or clipped ReLU in the first prototype,
- GRU gates: framework default sigmoid/tanh,
- output layer: linear,
- postprocessing: optional clipping to the normalized feature range outside MNN.

## Feature Layout Used In Examples

The initial `D = 12` planning value is:

| Feature group | Dims | Notes |
| --- | ---: | --- |
| total count and total bytes | 2 | log-scaled intensity scalars |
| read/write ratio | 2 | fixed-point ratios derived from counters |
| read/write mean LBA | 2 | normalized by namespace size or observed range |
| read/write mean transfer length | 2 | log1p-scaled or fixed-point mean |
| frame-to-frame deltas | 2 | absolute changes of mean LBA and mean length |
| optional compression/entropy-like telemetry | 1 | only if cheap telemetry exists |
| padding/alignment | 1 | excluded from loss and score |
| total | 12 | scalar-only deployment-friendly width |

The exact order must be frozen in the feature extractor and exported with the
MNN parity suite. If a device later supports true bucket counters, that should
be a separate feature profile and not silently mixed with this scalar contract.

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

MNN-converted files may store metadata and quantization tables, so these
formulae are only planning estimates.

## Candidate Summary

The following estimates use `D = 12` and `N = 12`.

| ID | Candidate | Sketch | Params | FP32 weights | FP16 weights | Int8 weights | Main role |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| AE-0 | Linear tiny AE | `144 -> 32 -> 8 -> 32 -> 144` | 9,944 | 39 KB | 20 KB | 10 KB | smallest useful flattened baseline |
| AE-1 | Flat MLP AE | `144 -> 64 -> 16 -> 4 -> 16 -> 64 -> 144` | 20,916 | 82 KB | 41 KB | 21 KB | stronger flattened AE baseline |
| AE-2 | Shared-frame bottleneck AE | shared `12 -> 24 -> 12`, sequence `144 -> 32 -> 8`, shared decoder | 11,168 | 44 KB | 22 KB | 11 KB | very small deployable candidate |
| AE-3a | GRU seq2seq AE, H=24 | encoder GRU, decoder GRU, per-frame dense head | 6,636 | 26 KB | 13 KB | 7 KB | first temporal AE candidate |
| AE-3b | GRU seq2seq AE, H=32 | encoder GRU, decoder GRU, per-frame dense head | 11,148 | 44 KB | 22 KB | 11 KB | stronger temporal AE candidate |
| AE-4 | Temporal convolution AE | Conv1D temporal encoder/decoder, 24 channels, 8-channel bottleneck | 5,684 | 22 KB | 11 KB | 6 KB | predictable MNN-friendly temporal model |
| AE-5 | Tiny CNN-GRU AE | temporal Conv1D 16 channels, GRU H=24, per-frame dense decoder | 7,516 | 30 KB | 15 KB | 8 KB | constrained CNN-GRU hypothesis test |

All candidates are far below the 500 KB budget in weights. The actual decision
therefore depends on MNN operator workspace, tensor buffers, score parity, and
low-false-positive detection quality.

## AE-0: Linear Tiny AE

Layer flow for `N = 12`, `D = 12`:

```text
Input X                         [1, 12, 12]
Flatten                         [1, 144]
Dense 32 + ReLU                 [1, 32]
Dense 8 + ReLU                  [1, 8]
Dense 32 + ReLU                 [1, 32]
Dense 144 + linear              [1, 144]
Reshape                         [1, 12, 12]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Dense 144 -> 32 | 4,640 |
| Dense 32 -> 8 | 264 |
| Dense 8 -> 32 | 288 |
| Dense 32 -> 144 | 4,752 |
| total | 9,944 |

This is the memory floor and a leakage/split sanity check. If it performs well,
the signal is likely dominated by coarse sequence-level shifts.

## AE-2: Shared-Frame Bottleneck AE

Layer flow for `N = 12`, `D = 12`:

```text
Input X                          [1, 12, 12]
TimeDistributed Dense 24 + ReLU   [1, 12, 24]
TimeDistributed Dense 12 + ReLU   [1, 12, 12]
Flatten                           [1, 144]
Dense 32 + ReLU                   [1, 32]
Dense 8 + ReLU                    [1, 8]
Dense 32 + ReLU                   [1, 32]
Dense 144 + ReLU                  [1, 144]
Reshape                           [1, 12, 12]
TimeDistributed Dense 24 + ReLU   [1, 12, 24]
TimeDistributed Dense 12 linear   [1, 12, 12]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| shared Dense 12 -> 24 | 312 |
| shared Dense 24 -> 12 | 300 |
| Dense 144 -> 32 | 4,640 |
| Dense 32 -> 8 | 264 |
| Dense 8 -> 32 | 288 |
| Dense 32 -> 144 | 4,752 |
| shared Dense 12 -> 24 | 312 |
| shared Dense 24 -> 12 | 300 |
| total | 11,168 |

This candidate keeps per-frame compression explicit while staying operator
simple. It should be one of the first deployable candidates to test.

## AE-3: GRU Seq2Seq AE

Layer flow for `H = 24`, `N = 12`, `D = 12`:

```text
Input X                         [1, 12, 12]
GRU encoder H=24                [1, 24]
RepeatVector 12                 [1, 12, 24]
GRU decoder H=24                [1, 12, 24]
TimeDistributed Dense 12 linear [1, 12, 12]
```

Parameter detail:

| Layer | H=24 params | H=32 params |
| --- | ---: | ---: |
| encoder GRU, I=12 | 2,736 | 4,416 |
| decoder GRU, I=H | 3,600 | 6,336 |
| output Dense H -> 12 | 300 | 396 |
| total | 6,636 | 11,148 |

This is the first recurrent candidate. It tests whether order and temporal
context add value beyond flattened summaries.

## AE-4: Temporal Conv1D AE

Layer flow for `N = 12`, `D = 12`:

```text
Input X                         [1, 12, 12]
Conv1D K=3, C=24 + ReLU         [1, 12, 24]
Conv1D K=3, C=24 + ReLU         [1, 12, 24]
Conv1D K=1, C=8 + ReLU          [1, 12, 8]
Conv1D K=1, C=24 + ReLU         [1, 12, 24]
Conv1D K=3, C=24 + ReLU         [1, 12, 24]
Conv1D K=3, C=12 linear         [1, 12, 12]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Conv1D K=3, 12 -> 24 | 888 |
| Conv1D K=3, 24 -> 24 | 1,752 |
| Conv1D K=1, 24 -> 8 | 200 |
| Conv1D K=1, 8 -> 24 | 216 |
| Conv1D K=3, 24 -> 24 | 1,752 |
| Conv1D K=3, 24 -> 12 | 876 |
| total | 5,684 |

This model is MNN-friendly and captures local temporal changes without recurrent
workspace. It is likely the most predictable temporal baseline.

## AE-5: Tiny CNN-GRU AE

Use this to test the original CNN-GRU hypothesis after simpler candidates. With
scalar-only features, the CNN must operate over time, not over nonexistent LBA
or length buckets.

Layer flow for `N = 12`, `D = 12`, `H = 24`:

```text
Input X                         [1, 12, 12]
Conv1D K=3, C=16 + ReLU         [1, 12, 16]
GRU encoder H=24                [1, 24]
RepeatVector 12                 [1, 12, 24]
GRU decoder H=24                [1, 12, 24]
TimeDistributed Dense 12 linear [1, 12, 12]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Conv1D K=3, 12 -> 16 | 592 |
| encoder GRU, I=16, H=24 | 3,024 |
| decoder GRU, I=24, H=24 | 3,600 |
| output Dense 24 -> 12 | 300 |
| total | 7,516 |

Constraints:

- one temporal Conv1D layer only,
- GRU encoder and decoder are one layer each,
- hidden size fixed to 24 for the first test,
- no Conv2D, transposed convolution, attention, model-side thresholding, or
  distribution softmax,
- output reconstructs the same `[1, N, 12]` scalar sequence.

This stays within roughly 30 KB FP32 weights. The 500 KB question must still be
answered by MNN conversion because operator workspace and tensor buffers can
dominate such a small model.

## Evaluation Order

Recommended order:

1. AE-0 Linear tiny AE.
2. AE-2 Shared-frame bottleneck AE.
3. AE-4 Temporal Conv1D AE.
4. AE-3a GRU seq2seq AE.
5. AE-5 Tiny CNN-GRU AE.
6. AE-1 Flat MLP AE and AE-3b stronger GRU as capacity checks.

AE-5 remains a hypothesis test, not the default. If AE-0 or rule baselines are
already strong, the paper should report that the simple signal is sufficient
rather than promoting a more complex model.

## Sequence Length Sensitivity

`N` controls context length and memory pressure:

| N | Context | Flattened L | Expected memory effect | Detection trade-off |
| ---: | ---: | ---: | --- | --- |
| 6 | 60 s | 72 | lower activations and dense weights | faster, less context |
| 12 | 120 s | 144 | initial reference point | balanced |
| 24 | 240 s | 288 | roughly double sequence buffers | slower, more context |

For GRU and Conv1D models, weights are mostly independent of `N`, but activation
and input/output buffers grow with `N`.

## Output And Scoring Policy

- Reconstruct normalized scalar values directly.
- Compute anomaly score outside MNN as weighted reconstruction error by feature
  group.
- Exclude padding and unavailable optional telemetry from normalization, loss,
  and score.
- Keep thresholding and alert policy outside the model graph.

This keeps the MNN graph small and auditable, and it avoids claiming that the
model sees distributions when only per-window scalar summaries are available.
