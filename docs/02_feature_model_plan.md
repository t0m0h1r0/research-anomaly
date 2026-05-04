# Feature And Model Plan

## Observation Boundary

The detector sits at or near a block-storage device. It observes command-level
I/O behavior compatible with SCSI/NVMe block semantics:

- read or write operation,
- logical block address or byte offset,
- transfer length,
- completion timestamp or arrival timestamp,
- optional low-cost telemetry such as compression ratio counters, if the storage
  platform already exposes them.

The deployed detector consumes only 10-second statistics. It should not require
expensive calculations such as per-block Shannon entropy, payload scanning,
sorting large address sets, or maintaining per-LBA state.

NVMe separates the NVM command set from the base specification, and the NVM
command set includes the core read and write commands. Computational-storage
standardization work is also active in SNIA and NVMe, which makes a
storage-adjacent inference path worth evaluating separately from host-agent
detection.

Sources:

- <https://nvmexpress.org/specification/nvm-express-base-specification/>
- <https://nvmexpress.org/specification/nvm-command-set-specification/>
- <https://www.snia.org/computationaltwg>

## Windowing

The deployment window is fixed at 10 seconds. Public per-I/O traces should be
aggregated into the same 10-second schema before model evaluation.

Exploratory event windows may be useful for research intuition, but they must not
be used to support final embedded claims.

The initial tensor should match the deployed cadence:

```text
run -> ordered events -> 10-second statistics -> N-window sequences -> AE input
```

Recommended starting point:

- base window: 10 seconds,
- sequence length: `N` windows, where each model input spans `N * 10` seconds,
- initial `N`: 12 windows for a 2-minute context,
- compare 6, 12, and 24 windows if memory allows,
- stride: 1 window for evaluation; larger stride for training efficiency,
- per-volume normalization of LBA by namespace size when available.

## Feature Tensor

Use the deployable 10-second scalar summaries as the core input:

- total I/O count and total bytes,
- write ratio,
- mean LBA,
- mean transfer length,
- frame-to-frame changes derived from those means,
- entropy or compression-rate scalar, only when cheap telemetry already exists.

Represent each sequence as `N` consecutive 10-second frames:

```text
X shape = [N, D]

N: number of 10-second frames in a sequence
D: scalar features per frame, initially 12
```

Initial feature groups:

| Feature group | Construction |
| --- | --- |
| intensity | total count and total bytes |
| write ratio | writes divided by total I/O count |
| mean LBA | total-count-weighted mean normalized LBA |
| mean transfer length | total-count-weighted mean transfer length |
| frame deltas | changes in mean LBA and mean length from the prior frame |
| compression telemetry | one optional slot, zero-filled and zero-weighted if unavailable |
| padding | four fixed-shape slots, always zero-weighted |

Keep I/O intensity separate in analysis because anomaly scores can otherwise
become "busy workload" detectors.

Histograms require per-I/O bucket counters in the collector. If the deployable
path only emits averages and ratios, LBA/length histograms must remain an
exploratory profile rather than the main embedded claim.

## Normalization

- LBA: normalize mean LBA by observed or declared namespace size.
- Length: log1p-scale mean transfer length.
- Write ratio: `writes / max(total I/O count, 1)`.
- Entropy/compression: use storage-provided compression telemetry if available;
  otherwise omit from the deployed model.
- Counts: use log scaling and robust normalization from benign calibration data.
- Write ratio: prefer host-side or offline normalization for evaluation; embedded
  code can emit raw counters and let the model consume normalized fixed-point
  values after cheap scaling.

All normalization parameters must be learned from the training split only.

## CNN-GRU AutoEncoder

The original architecture is now a constrained candidate, not a fixed decision.
The conservative rounded 500 KB per-volume detector-data budget covers model
weights plus retained input statistics/state and excludes shared MNN
runtime/library memory. That budget, separate transient MNN scratch checks with
scheduled slot counts, and MNN operator support decide whether CNN-GRU survives.

Encoder:

1. Pointwise Conv1D with `kernel_size=1` over the `[N, D]` scalar sequence to
   mix heterogeneous feature channels inside each frame.
2. TimeDistributed Dense frame code to reduce noisy mixtures into macro
   per-frame features before recurrence.
3. GRU over the frame codes, with `return_sequences=True`.
4. TimeDistributed Dense bottleneck over the contextualized per-frame features.

Decoder:

1. TimeDistributed Dense expansion from the bottleneck.
2. GRU decoder over the expanded sequence.
3. Dense head reconstructs scalar feature channels.

Starting architecture:

```text
Input [N, D]
  -> pointwise Conv1D feature mixer
  -> TimeDistributed Dense frame code
  -> GRU temporal context
  -> TimeDistributed Dense bottleneck z_seq
  -> TimeDistributed Dense expansion
  -> GRU decoder
  -> TimeDistributed Dense head
  -> Reconstructed [N, D]
```

In AE-5, Conv1D is used as a pointwise cross-feature mixer rather than a temporal
compressor. The pre-GRU Dense layer denoises each frame into a macro feature
code. GRU is used as a temporal context extractor. The post-GRU Dense bottleneck
then selects the most important contextual components. The architecture can
therefore explain what is mixed, what is contextualized, and what is compressed.

Loss:

- scalar channels: Huber or MSE,
- total loss: weighted sum by feature family,
- anomaly score: rolling reconstruction error with per-channel breakdown.

Memory-first alternatives to evaluate:

| Candidate | Why it may fit better |
| --- | --- |
| MLP bottleneck AE | smallest operator set, easiest MNN conversion |
| GRU contextual AE | keeps temporal modeling with an explicit Dense bottleneck and fewer activation maps |
| 1D temporal convolution AE | local temporal feature expansion with Dense compression and no recurrent state overhead |
| tiny CNN-GRU AE | preserves original idea if Conv1D/GRU add quality under the Dense bottleneck budget |

Concrete memory-aware model sketches and rough parameter estimates are recorded
in [Memory-Aware AutoEncoder Candidate Models](06_memory_aware_ae_candidates.md).
Code-ready tensor contracts, PyTorch skeletons, scoring functions, and ONNX/MNN
export constraints are recorded in
[Code-Ready AutoEncoder Implementation Spec](07_ae_implementation_spec.md).

The final candidate should prefer fixed input shapes and MNN-supported
operators. Quantized Int8 weights should be tested early; however, the anomaly
score must be validated for quantization drift.

## Thresholding

Start simple:

- choose threshold from benign calibration quantile,
- report results at fixed false-positive budgets,
- smooth scores over a short horizon to reduce single-window noise.

Then test:

- extreme-value tail modeling on benign reconstruction error,
- per-volume adaptive thresholds,
- workload-class thresholds if benign traces are too heterogeneous.

## Inference Placement

Three candidate placements should be evaluated:

| Placement | Description | Research use |
| --- | --- | --- |
| controller firmware path | feature extraction and inference in device | target vision, hardest overhead |
| storage-adjacent processor | device/controller exports telemetry to local compute | realistic prototype |
| offline replay | traces transformed and evaluated outside device | phase 1 feasibility |

For the first research pass, only offline replay is required. Device-local claims
need a later cost model covering RAM, model size, feature-buffer size, inference
latency, and write-path isolation.

The final implementation must run through MNN on CPU. Offline training and
evaluation may use PyTorch, TensorFlow, or ONNX tooling, but the research cannot
claim deployability until:

- the selected model is converted to MNN,
- fixed-shape 10-second statistic tensors are accepted by the MNN model,
- MNN inference scores match offline-framework scores within a defined tolerance,
- model weights plus retained input statistics/state stay under 500 KB per
  volume on the target or a faithful harness,
- transient inference scratch per slot and CPU scheduling fit the target
  many-volume deployment.

## Explainability Output

Every alert should carry:

- total anomaly score,
- per-channel reconstruction error,
- top contributing windows,
- approximate affected LBA span,
- read/write summaries and optional compression or entropy-like telemetry for
  the alert interval.

This prevents the system from becoming a black-box "AE says bad" detector and
helps distinguish ransomware-like encryption from benign maintenance jobs.
