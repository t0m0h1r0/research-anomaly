# Evaluation Roadmap

## Research Phases

### Phase 0: Feasibility Desk Check

Goal: confirm that public datasets can support the first claim.

Tasks:

- verify RanSAP CSV schema and license handling,
- identify at least one benign block-I/O trace source for false-positive tests,
- define a canonical event schema,
- implement no model yet; only conversion and exploratory statistics.

Exit criteria:

- event schema covers timestamp, op, LBA, size, and optional entropy,
- benign and ransomware runs can be split without leakage,
- missing entropy in non-RanSAP traces is documented as an ablation condition.

### Phase 1: Feature Pipeline

Goal: convert raw traces into stable AE input tensors.

Tasks:

- build time-window and event-window feature extraction,
- generate per-channel histograms and scalars,
- store normalization parameters from benign training data only,
- produce visualization notebooks or reports for sanity checks.

Exit criteria:

- feature tensors are reproducible from source traces,
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

### Phase 3: CNN-GRU AutoEncoder

Goal: test the core hypothesis.

Tasks:

- train AE on benign windows only,
- calibrate threshold on held-out benign data,
- evaluate ransomware windows and full attack timelines,
- report reconstruction error per feature family,
- compare time-window and event-window variants.

Exit criteria:

- reconstruction error separates attack from benign at useful false-positive
  rates,
- detection occurs before most target data is overwritten,
- channel breakdown is intelligible.

### Phase 4: Ablation And Robustness

Goal: understand whether the method survives realistic telemetry loss and
workload variation.

Ablations:

- remove entropy/compression channel,
- remove LBA channel,
- remove length channel,
- replace CNN-GRU with GRU-only AE,
- replace CNN-GRU with CNN-only AE,
- vary window size and sequence length.

Robustness tests:

- ransomware-family holdout,
- storage-device condition holdout,
- BitLocker or already-encrypted volume condition,
- benign workload family holdout,
- high-entropy benign file replay if available.

Exit criteria:

- the detector does not collapse when entropy is unavailable,
- the value of each feature family is measurable,
- the chosen architecture is justified by ablation rather than preference.

### Phase 5: Device-Fit Study

Goal: decide whether "storage embedded" is plausible.

Tasks:

- estimate model parameter count,
- estimate feature-buffer memory,
- estimate inference cadence and latency,
- separate write-path critical work from asynchronous analysis,
- define telemetry required from SCSI/NVMe command processing.

Exit criteria:

- prototype inference can run within a plausible storage-adjacent budget,
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
| E6 | Could this fit near storage? | trained model | size and latency estimate |

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
5. CNN-GRU AE evaluated with ablations.
6. False-positive stress report complete.
7. Device-fit memo complete.
8. Go/no-go review for deeper prototype.

## Go/No-Go Review Template

At the end of Phase 4, answer:

- What is the best false-positive budget achieved?
- How soon does detection occur in attack timelines?
- Which feature channels explain alerts?
- Does performance survive without entropy?
- Which benign workloads still cause false positives?
- What storage-device telemetry is mandatory?
- Is the remaining work a research problem, an engineering problem, or both?

