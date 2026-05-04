# Evaluation Roadmap

## Research Phases

### Phase 0: Feasibility Desk Check

Goal: confirm that public datasets can support the first claim.

Tasks:

- verify RanSAP CSV schema and license handling,
- identify at least one benign block-I/O trace source for false-positive tests,
- define a canonical event schema,
- define the deployed 10-second statistic schema,
- implement no model yet; only conversion and exploratory statistics.

Exit criteria:

- event schema covers timestamp, op, LBA, size, and optional entropy,
- deployed schema covers only cheap 10-second statistics,
- benign and ransomware runs can be split without leakage,
- missing entropy in non-RanSAP traces is documented as an ablation condition.

### Phase 1: Feature Pipeline

Goal: convert raw traces into stable AE input tensors.

Tasks:

- build the production-shaped 10-second statistics extractor,
- keep any event-window or sub-10-second feature extraction as exploratory
  scripts outside the final embedded claim,
- generate scalar feature channels and any exploratory histogram profile separately,
- store normalization parameters from benign training data only,
- produce visualization notebooks or reports for sanity checks.

Exit criteria:

- feature tensors are reproducible from source traces,
- tensors match the final fixed-shape embedded input contract,
- idle periods and sparse windows are handled consistently,
- no label information leaks into training normalization.

### Phase 2: Simple Baselines

Goal: know whether the deep model beats obvious rules.

Baselines:

- write-ratio threshold,
- entropy threshold,
- write-ratio plus entropy threshold,
- rolling z-score over bytes written and LBA coverage,
- Isolation Forest or one-class SVM over window summaries.

Exit criteria:

- baseline precision/recall and false-positive curves are available,
- AE is not credited for merely rediscovering a trivial threshold.

### Phase 3: Tiny AutoEncoder Candidates

Goal: test the core hypothesis.

Tasks:

- train memory-aware AE candidates on benign 10-second statistic windows only,
- calibrate threshold on held-out benign data,
- evaluate ransomware windows and full attack timelines,
- report reconstruction error per feature family,
- compare MLP AE, GRU-only AE, temporal convolution AE, and tiny CNN-GRU AE.

Exit criteria:

- reconstruction error separates attack from benign at useful false-positive
  rates,
- detection occurs before most target data is overwritten,
- channel breakdown is intelligible,
- at least one candidate has a plausible path to 500 KB per-volume detector
  data for model weights plus retained input statistics/state, excluding shared
  MNN runtime/library memory.

### Phase 4: Ablation And Robustness

Goal: understand whether the method survives realistic telemetry loss and
workload variation.

Ablations:

- remove entropy/compression channel,
- remove mean LBA channel,
- remove mean length channel,
- replace CNN-GRU with GRU-only AE,
- replace CNN-GRU with CNN-only AE,
- vary 10-second sequence length.

Robustness tests:

- ransomware-family holdout,
- storage-device condition holdout,
- BitLocker or already-encrypted volume condition,
- benign workload family holdout,
- high-entropy benign file replay if available.

Exit criteria:

- the detector does not collapse when entropy is unavailable,
- the value of each feature family is measurable,
- the chosen architecture is justified by ablation rather than preference,
- detection remains useful at 10-second cadence.

### Phase 5: MNN Device-Fit Study

Goal: decide whether "storage embedded with MNN and 500 KB per-volume detector
data" is plausible under a many-volume deployment assumption.

Tasks:

- estimate model parameter count,
- estimate retained input-statistics/state memory,
- estimate inference cadence and latency,
- separate write-path critical work from asynchronous analysis,
- define telemetry required from SCSI/NVMe command processing,
- convert the chosen model to MNN,
- measure or estimate converted weight representation and per-volume retained
  input statistics/state,
- separately measure transient tensors, operator workspace, reusable inference
  slots, and CPU scheduling at the target volume count,
- compare MNN scores with the offline evaluation framework.

Exit criteria:

- model weights plus retained input statistics/state fit within 500 KB per
  volume, excluding shared MNN runtime/library memory,
- aggregate memory/CPU is plausible at roughly 2000 volumes with shared runtime
  memory and scheduled transient scratch slots accounted for separately,
- fixed-shape MNN inference has acceptable score parity,
- any requirement for payload access or compression hardware is explicit,
- response actions remain out of scope until detection quality is credible.

## Metrics

Primary metrics:

- recall at fixed false-positive budgets,
- false alarms per volume per day,
- time to detect from attack start,
- bytes or LBA fraction overwritten before alert,
- area under precision-recall curve for imbalanced evaluation.

Secondary metrics:

- AUROC,
- per-channel reconstruction-error contribution,
- model size,
- feature extraction CPU cost,
- inference latency,
- memory footprint.
- MNN conversion success and score parity.

Avoid optimizing only for AUROC. Ransomware detection is operationally useful
only if false positives are rare and alerts arrive early.

## Suggested Experiment Table

| ID | Question | Data | Expected output |
| --- | --- | --- | --- |
| E0 | Are the features present? | RanSAP | schema report |
| E1 | Do simple rules work? | RanSAP | threshold baseline |
| E2 | Does AE separate attacks? | RanSAP | score timeline and PR curve |
| E3 | Does entropy dominate? | RanSAP | entropy ablation |
| E4 | Does benign diversity break it? | UMass/SNIA benign traces | false-positive report |
| E5 | Is CNN-GRU necessary? | RanSAP plus benign traces | architecture ablation |
| E6 | Does 10-second cadence still work? | deployed statistic tensors | latency and recall report |
| E7 | Can the MNN detector fit 500 KB per volume? | trained candidate model | MNN detector-data, transient-scratch slot, scheduling, and parity report |

## Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| entropy unavailable in public block traces | weakens one planned feature | make entropy optional and test ablation |
| benign encryption/compression resembles ransomware | high false positives | include high-entropy benign replay and channel attribution |
| AE detects workload intensity, not ransomware | misleading performance | isolate intensity scalars and compare simple baselines |
| random split leaks run-specific patterns | inflated results | split by run, family, device condition, and workload |
| storage device lacks payload access | entropy feature may be impractical | use compression telemetry or metadata-only variant |
| throttled ransomware changes slowly | late detection | evaluate cumulative score and longer temporal horizons |
| public data is too narrow | weak generalization | treat Phase 1 as feasibility, not proof of deployability |
| 500 KB detector-data budget is too small for CNN-GRU | original architecture may not deploy | evaluate MLP, GRU-only, and temporal convolution AE |
| MNN conversion changes scores | offline results may not transfer | require MNN parity before implementation claims |
| 10-second statistics hide early signal | detection may arrive too late | measure bytes overwritten before first alert |

## Safety Rules

- Do not execute live ransomware for the initial research.
- Use public behavioral datasets such as RanSAP for attack traces.
- Use controlled benign encryption simulators for replay experiments.
- Keep raw malware samples out of this repository.
- Store dataset acquisition scripts and hashes, not large or license-restricted
  transformed datasets.

## Milestone Plan

1. Research scaffold complete.
2. Dataset acquisition notes and schema inspection complete.
3. Feature extractor implemented with reproducible tensor output.
4. Baseline rules evaluated.
5. Tiny AE candidates evaluated with ablations.
6. False-positive stress report complete.
7. MNN 500 KB detector-data device-fit memo complete.
8. Go/no-go review for deeper prototype.

## Go/No-Go Review Template

At the end of Phase 4, answer:

- What is the best false-positive budget achieved?
- How soon does detection occur in attack timelines?
- Which feature channels explain alerts?
- Does performance survive without entropy?
- Which benign workloads still cause false positives?
- What storage-device telemetry is mandatory?
- Do model weights plus retained input statistics/state fit 500 KB per volume,
  excluding shared MNN runtime/library memory?
- Does 10-second cadence leave enough response time?
- Is the remaining work a research problem, an engineering problem, or both?
