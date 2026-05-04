# Data Strategy

## Data Requirements

The minimum event schema for this research is:

| Field | Purpose | Required |
| --- | --- | --- |
| timestamp | Build ordered windows and detection latency | yes |
| operation | Read/write ratio and operation-specific channels | yes |
| LBA or byte offset | Address distribution and spatial locality | yes |
| transfer length | I/O length distribution | yes |
| entropy or compression ratio | Encrypted-write signal | target feature |
| workload or attack label | Supervised evaluation only, not model training | yes |
| device or volume identity | Per-device normalization and split hygiene | yes |

The AutoEncoder should train only on benign windows. Labels are used to evaluate
thresholds, time to detect, and false-positive behavior.

## Public Dataset Candidates

### RanSAP

RanSAP is the best first dataset because it directly targets ransomware storage
access patterns. The public repository states that it contains storage access
patterns for seven ransomware samples, five benign software samples, additional
ransomware variants, OS variation, and BitLocker-enabled storage conditions.

It also exposes the core fields needed here:

- `ata_read.csv`: UNIX seconds, UNIX nanoseconds, LBA, size.
- `ata_write.csv`: UNIX seconds, UNIX nanoseconds, LBA, size, entropy #1,
  entropy #2.

Use it for:

- first offline feasibility experiment,
- entropy-channel ablation,
- HDD/SSD and volume-size sensitivity,
- BitLocker condition stress testing.

Important caveat: RanSAP is close to the target but was collected through a
hypervisor rather than inside a SCSI/NVMe storage device. The feature semantics
are still useful, but device-local observability and overhead remain separate
questions.

Source:

- <https://github.com/manabu-hirano/RanSAP>
- <https://doi.org/10.1016/j.fsidi.2021.301314>

### SNIA IOTTA and Related Block-I/O Traces

SNIA IOTTA is a broad repository for storage I/O traces and tools. Its public
description includes block I/O, HPC summaries, key-value traces, NFS traces,
parallel traces, static snapshots, system-call traces, and workload summaries.

Use it for:

- broad benign workload diversity,
- false-positive evaluation,
- normal workload pretraining,
- stress cases such as enterprise and cloud-like block workloads.

Expected caveat: many block traces include metadata only. They usually help with
timestamp, address, size, and read/write behavior, but not payload entropy or
compression ratio.

Source:

- <https://www.snia.org/educational-library/iotta-repository-2019>
- <https://www.snia.org/blog/2024/just-what-iotta-inquiring-minds-learn-now>

### UMass Storage Trace Repository

The UMass Trace Repository hosts storage traces including OLTP application I/O
from financial institutions and search-engine I/O traces. These are useful
benign traces for testing whether the detector falsely triggers on intense but
non-ransomware storage behavior.

Use it for:

- benign-only pretraining experiments,
- false-positive evaluation,
- workload shift tests across OLTP and search traces.

Expected caveat: these traces should be treated as normal workload traces, not
ransomware evidence.

Source:

- <https://traces.cs.umass.edu/docs/traces/storage/>

### NapierOne

NapierOne is not a block I/O trace dataset. It is a mixed file dataset with more
than 500,000 files across common file types, designed for reproducible security
and forensic analysis. Its documentation explicitly notes naturally high-entropy
file types, which matters for ransomware false positives.

Use it for:

- entropy and compression-ratio calibration,
- controlled replay or synthetic encryption experiments,
- estimating false positives from benign compressed and encrypted file types.

Expected caveat: it must be paired with replay instrumentation to become block
I/O time-series data.

Source:

- <https://registry.opendata.aws/napierone/>

## Feature-Coverage Matrix

| Dataset | Benign | Ransomware | Time | LBA/offset | Length | R/W | Entropy | Main role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RanSAP | yes | yes | yes | yes | yes | yes | write entropy | primary feasibility |
| SNIA IOTTA traces | yes | no | varies | varies | varies | varies | usually no | false positives |
| UMass storage traces | yes | no | yes | likely | likely | likely | no | benign diversity |
| NapierOne | file corpus | no | no | no | file size | no | computable | entropy calibration |

## Data Splitting Rules

- Split by device, workload, ransomware family, and collection condition where
  possible; do not randomly split adjacent windows from the same run into train
  and test.
- Train the AE on benign data only.
- Keep a calibration set of benign windows for threshold selection.
- Reserve ransomware variants and BitLocker conditions for out-of-distribution
  tests.
- Do not redistribute modified datasets unless the source license allows it.
  RanSAP uses CC BY-ND 4.0, so derived public artifacts should contain scripts,
  hashes, and metrics rather than transformed data dumps.

## Data Gaps And Mitigations

### Gap: Public Metadata Traces Often Lack Payload Entropy

Mitigation:

- make entropy an optional channel in the model interface,
- run an ablation with entropy removed,
- derive compression-ratio-like telemetry during controlled replay,
- treat storage-controller compression statistics as a future device signal.

### Gap: Ransomware Behavior Data Is Narrow

Mitigation:

- start with RanSAP, but avoid claiming broad generalization,
- test family holdout rather than only random split,
- inject conservative ransomware-like transformations into benign block traces
  for sensitivity analysis,
- separate "ransomware detection" from "bulk encrypted write detection" in the
  interpretation.

### Gap: Block Storage Cannot See File Semantics

Mitigation:

- evaluate at volume/namespace scope,
- normalize by volume size and baseline workload rhythm,
- report feature-channel contribution rather than a single opaque score,
- explicitly test benign backup, compression, encryption, and database rewrite
  scenarios as false-positive candidates.

## Dataset Decision For Phase 1

Phase 1 should use RanSAP as the primary dataset and produce three results:

1. AE reconstruction-error separation between benign and ransomware windows.
2. Ablation result with entropy removed.
3. False-positive probe by mixing in at least one benign block-I/O trace family
   from UMass or SNIA IOTTA.

