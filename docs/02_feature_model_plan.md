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

Use the user-proposed feature families as the core input:

- address distribution,
- I/O length distribution,
- read/write ratio,
- entropy or compression-rate distribution, only when cheap telemetry already
  exists.

Represent each sequence as `N` consecutive 10-second frames:

```text
X shape = [N, C, B]

N: number of 10-second frames in a sequence
C: feature channels
B: histogram buckets or scalar-broadcast width
```

Initial channels:

| Channel | Construction |
| --- | --- |
| read LBA histogram | small fixed bucket count from shifted normalized LBA |
| write LBA histogram | small fixed bucket count from shifted normalized LBA |
| read length histogram | log2 or lookup-table transfer length buckets |
| write length histogram | log2 or lookup-table transfer length buckets |
| read/write counters | read count, write count, read bytes, write bytes |
| sequentiality estimate | sequential read/write counts if cheap to track |
| compression telemetry | optional scalar or buckets only if already available |

Keep I/O intensity separate in analysis because anomaly scores can otherwise
become "busy workload" detectors.

## Normalization

- LBA: normalize by observed or declared namespace size, then histogram.
- Length: log2 bucket by bytes or logical blocks.
- Read/write ratio: `writes / max(reads + writes, 1)`.
- Entropy/compression: use storage-provided compression telemetry if available;
  otherwise omit from the deployed model.
- Counts: use log scaling and robust normalization from benign calibration data.
- Ratios: prefer host-side or offline normalization for evaluation; embedded
  code can emit raw counters and let the model consume normalized fixed-point
  values after cheap scaling.

All normalization parameters must be learned from the training split only.

## CNN-GRU AutoEncoder

The original architecture is now a constrained candidate, not a fixed decision.
The 500 KB model-memory budget, excluding the MNN runtime, and MNN operator
support decide whether CNN-GRU survives.

Encoder:

1. Per-window CNN over `[C, B]` feature maps.
2. Flatten or pooled embedding per window.
3. GRU over the `T` embeddings.
4. Latent vector or latent sequence.

Decoder:

1. Repeat or initialize decoder GRU from latent state.
2. Produce per-window embeddings.
3. Transposed CNN or MLP heads reconstruct feature channels.
4. Separate heads for histogram channels and scalar channels if needed.

Starting architecture:

```text
Input [T, C, B]
  -> TimeDistributed Conv1D/Conv2D
  -> per-window embedding
  -> GRU encoder
  -> latent z
  -> GRU decoder
  -> TimeDistributed decoder heads
  -> Reconstructed [T, C, B]
```

Loss:

- histogram channels: MSE or Jensen-Shannon divergence after normalization,
- scalar channels: Huber or MSE,
- total loss: weighted sum by feature family,
- anomaly score: rolling reconstruction error with per-channel breakdown.

Memory-first alternatives to evaluate:

| Candidate | Why it may fit better |
| --- | --- |
| MLP bottleneck AE | smallest operator set, easiest MNN conversion |
| GRU-only AE | keeps temporal modeling with fewer activation maps |
| 1D temporal convolution AE | predictable memory, no recurrent state overhead |
| tiny CNN-GRU AE | preserves original idea if quantized memory fits |

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
- model-owned memory stays under 500 KB on the target or a faithful harness.

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
