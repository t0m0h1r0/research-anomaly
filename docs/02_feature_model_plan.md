# Feature And Model Plan

## Observation Boundary

The detector sits at or near a block-storage device. It observes command-level
I/O behavior compatible with SCSI/NVMe block semantics:

- read or write operation,
- logical block address or byte offset,
- transfer length,
- completion timestamp or arrival timestamp,
- optional payload-derived telemetry such as entropy or compression ratio.

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

Use two window modes and compare them early:

| Mode | Example | Strength | Risk |
| --- | --- | --- | --- |
| time window | 1 s, 5 s, 10 s | maps to detection latency | sparse during idle periods |
| event window | 256, 512, 1024 I/Os | stable tensor density | latency varies with workload rate |

The initial tensor should keep both modes possible:

```text
run -> ordered events -> windows -> T-window sequences -> AE input tensor
```

Recommended starting point:

- base window: 1 second,
- sequence length: 32 windows,
- stride: 1 to 4 windows for evaluation; larger stride for training efficiency,
- per-volume normalization of LBA by namespace size when available.

## Feature Tensor

Use the user-proposed feature families as the core input:

- address distribution,
- I/O length distribution,
- read/write ratio,
- entropy or compression-rate distribution.

Represent each sequence as:

```text
X shape = [T, C, B]

T: number of windows in a sequence
C: feature channels
B: histogram buckets or scalar-broadcast width
```

Initial channels:

| Channel | Construction |
| --- | --- |
| read LBA histogram | bucket normalized LBA for reads |
| write LBA histogram | bucket normalized LBA for writes |
| read length histogram | bucket log2 transfer lengths for reads |
| write length histogram | bucket log2 transfer lengths for writes |
| read/write ratio | scalar per window, broadcast or appended after CNN |
| write entropy histogram | bucket entropy or compression ratio for writes |
| I/O intensity | event count and byte count, used as auxiliary scalar |

Keep I/O intensity separate in analysis because anomaly scores can otherwise
become "busy workload" detectors.

## Normalization

- LBA: normalize by observed or declared namespace size, then histogram.
- Length: log2 bucket by bytes or logical blocks.
- Read/write ratio: `writes / max(reads + writes, 1)`.
- Entropy: bucket by Shannon entropy per block or compression ratio if available.
- Counts: use log scaling and robust normalization from benign calibration data.

All normalization parameters must be learned from the training split only.

## CNN-GRU AutoEncoder

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

## Explainability Output

Every alert should carry:

- total anomaly score,
- per-channel reconstruction error,
- top contributing windows,
- approximate affected LBA span,
- read/write and entropy summaries for the alert interval.

This prevents the system from becoming a black-box "AE says bad" detector and
helps distinguish ransomware-like encryption from benign maintenance jobs.

