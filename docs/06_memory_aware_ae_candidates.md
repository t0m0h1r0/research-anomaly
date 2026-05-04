# Memory-Aware AutoEncoder Candidate Models

status: DRAFT
updated: 2026-05-04

This memo proposes concrete AutoEncoder candidates for the 500 KB per-volume
detector-data budget. The budget is derived from the planning assumption of
roughly 1 GB available across roughly 2000 protected volumes, and it covers
model weight information plus the input statistics/state needed to score one
volume. If the available memory is stated as 1 GiB, the exact quotient is about
524 KiB per volume, so 500 KB is a conservative rounded engineering target. The
current deployable feature contract is scalar-only: it does not
assume LBA or transfer-length histograms unless a target device explicitly
exposes cheap per-window bucket counters.

The estimates below are planning estimates, not MNN measurements. Final claims
still require converted MNN models, identical input parity tests, per-volume
detector-data measurement, and separate transient inference scratch
measurement.

## Sizing Assumptions

Initial input contract:

- one frame is a 10-second statistic vector,
- model input is `N` consecutive frames, or `N * 10` seconds,
- initial comparison values: `N = 6, 12, 24`,
- starting feature dimension: `D = 12` per frame after optional padding,
- initial shape: `[batch=1, N, D]`,
- initial example: `N = 12`, so flattened length `L = N * D = 144`.

`D = 12` covers the scalar statistics that can be emitted from 10-second
window summaries: total intensity, write ratio, mean LBA, mean transfer
length, cheap frame-to-frame deltas, one optional compression/entropy-like
telemetry slot, and four padding/alignment slots.

Weight-size estimates:

```text
FP32 bytes ~= parameter_count * 4
FP16 bytes ~= parameter_count * 2
Int8 bytes ~= parameter_count * 1 + quantization metadata
```

These numbers exclude shared MNN runtime/library memory. They also exclude
transient activation tensors, operator workspace, output tensors, reusable
inference slots, normalization constants, input-statistics buffers, and score
history. The research target should keep weights comfortably below 500 KB so
retained input statistics and per-volume calibration state fit in the same
per-volume detector-data budget.

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
| write ratio | 1 | fixed-point ratio derived from write and total counters |
| mean LBA | 1 | normalized by namespace size or observed range |
| mean transfer length | 1 | log1p-scaled or fixed-point mean |
| frame-to-frame deltas | 2 | absolute changes of mean LBA and mean length |
| optional compression/entropy-like telemetry | 1 | only if cheap telemetry exists |
| padding/alignment | 4 | excluded from loss and score |
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

## Operator Role Policy

The candidate set uses a strict role separation:

- Dense layers are the only intentional information-reducing bottlenecks.
- GRU layers attach temporal context to each frame and must not be the hidden
  place where the sequence is collapsed.
- Conv1D layers expand scalar frame inputs into multiple local temporal views
  and extract short-range patterns. They are feature analysis layers, not the
  compression mechanism.

This keeps the architecture story inspectable: feature extraction and temporal
context happen before the Dense bottleneck; reconstruction happens after it.

## Candidate Summary

The following estimates use `D = 12` and `N = 12`.

| ID | Candidate | Sketch | Params | FP32 weights | FP16 weights | Int8 weights | Main role |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| AE-0 | Linear tiny AE | `144 -> 32 -> 8 -> 32 -> 144` | 9,944 | 39 KB | 20 KB | 10 KB | smallest useful flattened baseline |
| AE-1 | Flat MLP AE | `144 -> 64 -> 16 -> 64 -> 144` | 20,768 | 83 KB | 42 KB | 21 KB | stronger flattened capacity check |
| AE-2 | Two-level dense AE | shared `12 -> 16 -> 8`, sequence `96 -> 24 -> 8`, shared decoder | 5,636 | 23 KB | 12 KB | 6 KB | explicit frame and sequence compression |
| AE-3a | GRU contextual AE, H=24 | GRU context, per-frame dense `24 -> 8`, GRU decoder | 7,052 | 29 KB | 15 KB | 8 KB | first recurrent context model |
| AE-3b | GRU contextual AE, H=32 | GRU context, per-frame dense `32 -> 8`, GRU decoder | 11,700 | 47 KB | 24 KB | 12 KB | stronger recurrent context model |
| AE-4 | Temporal convolution AE | Conv1D temporal feature expansion, per-frame dense `24 -> 8` | 5,684 | 23 KB | 12 KB | 6 KB | predictable MNN-friendly temporal model |
| AE-5 | Tiny CNN-GRU AE | Conv1D local feature expansion, GRU context, per-frame dense `24 -> 8` | 8,804 | 36 KB | 18 KB | 9 KB | constrained CNN-GRU hypothesis test |

All candidates are far below the 500 KB budget in weights. The actual decision
therefore depends on retained input-statistics state, score parity,
low-false-positive detection quality, and the separate MNN transient
workspace/scheduling check.

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

## AE-1: Flat MLP AE

Layer flow for `N = 12`, `D = 12`:

```text
Input X                         [1, 12, 12]
Flatten                         [1, 144]
Dense 64 + ReLU                 [1, 64]
Dense 16 + ReLU                 [1, 16]
Dense 64 + ReLU                 [1, 64]
Dense 144 + linear              [1, 144]
Reshape                         [1, 12, 12]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Dense 144 -> 64 | 9,280 |
| Dense 64 -> 16 | 1,040 |
| Dense 16 -> 64 | 1,088 |
| Dense 64 -> 144 | 9,360 |
| total | 20,768 |

AE-1 is not a different scientific hypothesis from AE-0. It is a capacity check
for the flattened MLP family: if AE-0 fails only because it is too narrow,
AE-1 tests that before adding temporal operators.

## AE-2: Two-Level Dense AE

Layer flow for `N = 12`, `D = 12`:

```text
Input X                          [1, 12, 12]
TimeDistributed Dense 16 + ReLU   [1, 12, 16]
TimeDistributed Dense 8 + ReLU    [1, 12, 8]
Flatten                           [1, 96]
Dense 24 + ReLU                   [1, 24]
Dense 8 + ReLU                    [1, 8]
Dense 24 + ReLU                   [1, 24]
Dense 96 + ReLU                   [1, 96]
Reshape                           [1, 12, 8]
TimeDistributed Dense 16 + ReLU   [1, 12, 16]
TimeDistributed Dense 12 linear   [1, 12, 12]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| shared Dense 12 -> 16 | 208 |
| shared Dense 16 -> 8 | 136 |
| Dense 96 -> 24 | 2,328 |
| Dense 24 -> 8 | 200 |
| Dense 8 -> 24 | 216 |
| Dense 24 -> 96 | 2,400 |
| shared Dense 8 -> 16 | 144 |
| shared Dense 16 -> 12 | 204 |
| total | 5,636 |

AE-2 has a clear two-stage meaning. The frame-level Dense encoder compresses each
10-second frame from raw scalar features to an 8-dimensional frame code. The
sequence bottleneck then compresses the 12-frame pattern. No recurrent operator
is asked to discard information.

## AE-3: GRU Contextual AE

Layer flow for `H = 24`, `N = 12`, `D = 12`:

```text
Input X                         [1, 12, 12]
GRU context H=24                [1, 12, 24]
TimeDistributed Dense 8 + ReLU  [1, 12, 8]
TimeDistributed Dense 24 + ReLU [1, 12, 24]
GRU decoder H=24                [1, 12, 24]
TimeDistributed Dense 12 linear [1, 12, 12]
```

Parameter detail:

| Layer | H=24 params | H=32 params |
| --- | ---: | ---: |
| context GRU, I=12 | 2,736 | 4,416 |
| bottleneck Dense H -> 8 | 200 | 264 |
| expansion Dense 8 -> H | 216 | 288 |
| decoder GRU, I=H | 3,600 | 6,336 |
| output Dense H -> 12 | 300 | 396 |
| total | 7,052 | 11,700 |

This is the first recurrent candidate. GRU is used only to attach temporal
context to each frame. The information-reducing step is the explicit
TimeDistributed Dense bottleneck, so the model's story remains: temporal
features first, compression second, reconstruction last.

## AE-4: Temporal Conv1D AE

Layer flow for `N = 12`, `D = 12`:

```text
Input X                         [1, 12, 12]
Conv1D K=3, C=24 + ReLU         [1, 12, 24]
Conv1D K=3, C=24 + ReLU         [1, 12, 24]
TimeDistributed Dense 8 + ReLU  [1, 12, 8]
TimeDistributed Dense 24 + ReLU [1, 12, 24]
Conv1D K=3, C=24 + ReLU         [1, 12, 24]
Conv1D K=3, C=12 linear         [1, 12, 12]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Conv1D K=3, 12 -> 24 | 888 |
| Conv1D K=3, 24 -> 24 | 1,752 |
| bottleneck Dense 24 -> 8 | 200 |
| expansion Dense 8 -> 24 | 216 |
| Conv1D K=3, 24 -> 24 | 1,752 |
| Conv1D K=3, 24 -> 12 | 876 |
| total | 5,684 |

This model is MNN-friendly and captures local temporal changes without recurrent
workspace. The temporal Conv1D layers expand the scalar input into multiple
local temporal views. They are not treated as the compression step. The
information-reducing step is the explicit per-frame Dense bottleneck, and the
remaining Dense/Conv1D layers decode that bottleneck. It is likely the most
predictable temporal baseline.

## AE-5: Tiny CNN-GRU AE

Use this to test the original CNN-GRU hypothesis after simpler candidates. With
scalar-only features, the CNN must operate over time, not over nonexistent LBA
or length buckets.

Layer flow for `N = 12`, `D = 12`, `H = 24`:

```text
Input X                         [1, 12, 12]
Conv1D K=3, C=24 + ReLU         [1, 12, 24]
GRU context H=24                [1, 12, 24]
TimeDistributed Dense 8 + ReLU  [1, 12, 8]
TimeDistributed Dense 24 + ReLU [1, 12, 24]
GRU decoder H=24                [1, 12, 24]
TimeDistributed Dense 12 linear [1, 12, 12]
```

Parameter detail:

| Layer | Params |
| --- | ---: |
| Conv1D K=3, 12 -> 24 | 888 |
| context GRU, I=24, H=24 | 3,600 |
| bottleneck Dense 24 -> 8 | 200 |
| expansion Dense 8 -> 24 | 216 |
| decoder GRU, I=24, H=24 | 3,600 |
| output Dense 24 -> 12 | 300 |
| total | 8,804 |

Constraints:

- one temporal Conv1D layer only,
- Conv1D expands the scalar frame into 24 local-temporal channels,
- GRU encoder and decoder are one layer each,
- hidden size fixed to 24 for the first test,
- information reduction is done by the TimeDistributed Dense bottleneck, not by
  collapsing the GRU state to one vector,
- no Conv2D, transposed convolution, attention, model-side thresholding, or
  distribution softmax,
- output reconstructs the same `[1, N, 12]` scalar sequence.

This stays within roughly 36 KB FP32 weights. The 500 KB question must still be
answered by measuring the converted weight representation together with the
retained input statistics/state for one volume. Operator workspace and tensor
buffers remain a separate transient device-fit measurement.

## Evaluation Order

Recommended order:

1. AE-0 Linear tiny AE.
2. AE-2 Two-level dense AE.
3. AE-4 Temporal Conv1D AE.
4. AE-3a GRU contextual AE.
5. AE-5 Tiny CNN-GRU AE.
6. AE-1 Flat MLP AE and AE-3b stronger GRU as capacity checks.

AE-5 remains a hypothesis test, not the default. If AE-0 or rule baselines are
already strong, the paper should report that the simple signal is sufficient
rather than promoting a more complex model.

## Sequence Length Sensitivity

`N` controls context length and detector-data pressure:

| N | Context | Flattened L | Expected memory effect | Detection trade-off |
| ---: | ---: | ---: | --- | --- |
| 6 | 60 s | 72 | smaller retained sequence statistics and lower dense weights | faster, less context |
| 12 | 120 s | 144 | initial reference point | balanced |
| 24 | 240 s | 288 | roughly double retained sequence statistics | slower, more context |

For GRU and Conv1D models, weights are mostly independent of `N`, but activation
scratch and retained input statistics grow with `N`.

## Output And Scoring Policy

- Reconstruct normalized scalar values directly.
- Compute anomaly score outside MNN as weighted reconstruction error by feature
  group.
- Exclude padding and unavailable optional telemetry from normalization, loss,
  and score.
- Keep thresholding and alert policy outside the model graph.

This keeps the MNN graph small and auditable, and it avoids claiming that the
model sees distributions when only per-window scalar summaries are available.
