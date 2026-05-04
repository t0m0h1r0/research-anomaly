# Literature Survey: Ransomware Detection From Storage Behavior

## Scope

This survey focuses on prior work relevant to a storage-embedded ransomware
detector with these constraints:

- block storage observation boundary: SCSI/NVMe-like I/O metadata;
- final input: 10-second statistics, not raw event streams;
- final implementation: Alibaba MNN on CPU;
- per-volume detector-data budget: 500 KB for model weights plus retained input
  statistics/state, excluding shared MNN runtime/library memory;
- expensive features such as per-block Shannon entropy are not assumed unless
  existing hardware or firmware telemetry already exposes them;
- target model family: AutoEncoder-based anomaly detection, compared against
  simpler baselines.

The most important finding is that storage-level ransomware detection is a real
research line, but existing strong results mostly use supervised decision-tree
style models, entropy or payload-derived statistics, or richer host/filesystem
context. A small storage-local AutoEncoder remains a plausible research gap, but
it must be evaluated against storage-specific baselines and harsh
generalization tests.

## Executive Summary

### Most Relevant Prior Work

1. SSD-Insider is the closest firmware-level predecessor. It detects ransomware
   inside SSD firmware using block I/O request headers rather than payload, with
   10-second detection and SSD-native recovery. This directly supports the idea
   that storage-device-local detection is plausible, but its detector is a
   lightweight supervised/rule-like model, not an AutoEncoder.

2. IBM's storage-system work and the 2024 generalizability study are the closest
   block-storage ML predecessors. They emphasize computationally light I/O
   features, computational storage devices, decision-tree/XGBoost models, and
   the difficulty of generalizing across filesystem, volume state, encryption,
   virtualization, and benign database workloads.

3. RanSAP is the best initial public dataset because it includes ransomware and
   benign storage access patterns with timestamp, LBA, size, read/write, and
   write entropy. RanSMAP is a newer successor that adds memory access patterns
   and mixed benign/ransomware executions; for this project, its storage-only
   subset is useful, while memory features are outside scope.

4. DeftPunk is important because it targets cloud block stores and combines a
   two-layer classifier with pre-/post-attack snapshots. It shows that block
   storage ransomware protection can be practical at cloud scale, but its
   recovery mechanism and deployment assumptions differ from an embedded device.

5. Filesystem and endpoint systems such as UNVEIL, CryptoDrop, ShieldFS,
   Redemption, Peeler, and XRan show that behavioral ransomware detection works
   better than signatures for variants, but they rely on host-visible semantics,
   API calls, process identity, file paths, file content deltas, or kernel events
   that a block device cannot observe.

6. Time-series AutoEncoder research supports reconstruction-error anomaly
   detection, but direct ransomware/storage work using small AE models under
   storage-device constraints is sparse. This is the project's opening.

### Immediate Implications For This Project

- The first baseline should not be CNN-GRU AE. It should be:
  - write ratio / write throughput rules;
  - LBA spread / write-after-read / sequentiality rules;
  - small decision tree or random forest;
  - tiny MLP AE;
  - GRU-only or temporal-convolution AE if the MLP AE fails.
- Entropy is powerful but risky for product fit. It improves detection in many
  papers, yet it is expensive, often unavailable in public block traces, and
  weak on already-encrypted volumes or naturally compressed data.
- Generalization is the central scientific risk. A model trained on one
  filesystem, volume state, or benign workload can show high headline accuracy
  and still fail badly on MySQL/PostgreSQL, BitLocker/LUKS, qcow2, aged volumes,
  or high-utilization devices.
- 10-second windows are defensible: SSD-Insider reports detection within 10 s,
  Hirano-style storage ML uses 10 s windows, and the block-storage
  generalizability study explicitly discusses 1-60 s window trade-offs. The
  project should still measure bytes overwritten before alert.
- The novelty claim should be narrow: "storage-device feasible, MNN-convertible,
  500 KB per-volume detector-data AE over cheap 10-second block-I/O statistics."
  This is distinct from endpoint DL detectors and from storage-level supervised
  classifiers.

## Research Line 1: Storage-Level And Block-I/O Detection

### Storage-Based IDS Before Ransomware

Storage-level intrusion detection predates modern ransomware work.

- Banikazemi, Poff, and Abali proposed storage-based intrusion detection for SANs
  in MSST 2005. The key idea was that storage systems see persistent data
  changes and can detect some intrusions directly at block-storage level. They
  considered both real-time integration in storage management/virtualization and
  appliance-style deployment using point-in-time copy.
- Allalouf et al. proposed IDStor in MSST 2010. IDStor listens to block storage
  traffic out of the I/O path, maintains block-to-file mappings, and infers
  file-level commands from block reads/writes.

Relevance:

- These works establish the storage controller as a defensible security boundary.
- They also show the fundamental trade-off: pure block storage lacks filesystem
  semantics. Either infer them, maintain mappings, or accept a weaker but more
  universal signal.
- Our project chooses the weaker but universal path: no block-to-file mapping,
  no filesystem parsing, no host trust.

Sources:

- IBM Research, "Storage-based intrusion detection for Storage Area Networks
  (SANs)": <https://research.ibm.com/publications/storage-based-intrusion-detection-for-storage-area-networks-sans>
- IBM Research, "Block storage listener for detecting file-level intrusions":
  <https://research.ibm.com/publications/block-storage-listener-for-detecting-file-level-intrusions>

### SSD-Insider: Firmware-Level SSD Defense

SSD-Insider is the strongest predecessor for "inside storage" ransomware
defense. It runs inside NAND flash-based SSD firmware, uses lightweight
behavioral features over ransomware overwriting patterns, and relies only on
block I/O request headers rather than payload. It also uses SSD delayed deletion
to recover overwritten data.

Reported results from the publication page:

- implemented on an open-channel SSD prototype;
- evaluated with eight real-world and two in-house ransomware samples;
- used multiple background applications;
- achieved 0% FRR/FAR in most scenarios and 5% FAR under heavy overwriting
  resembling data wiping;
- detected activity within 10 seconds;
- recovered an infected SSD within 1 second with no data loss;
- added very small per-I/O software overhead relative to NAND latency.

Relevance:

- Directly supports storage-device-local ransomware detection.
- Supports 10-second cadence.
- Supports payload-free detection from I/O headers.
- Recovery design is SSD-specific and not portable to all block storage.
- The detector is not AE-based; it appears closer to lightweight behavior
  features plus supervised decision-tree classification.

Implication:

- SSD-Insider should be a primary baseline and discussion point.
- Our model should include overwrite/write-after-read/sequentiality-like cheap
  features where feasible.
- If a tiny AE cannot beat or complement a decision tree under the 500 KB
  detector-data budget, the AE
  hypothesis weakens.

Source:

- Baek et al., "SSD-Insider: Internal defense of solid-state drive against
  ransomware with perfect data recovery": <https://doi.org/10.1109/ICDCS.2018.00089>
- DGIST publication page:
  <https://dgist.elsevierpure.com/en/publications/ssd-insider-internal-defense-of-solid-state-drive-against-ransomw/>

### IBM / Computational Storage ML Work

IBM Research's FMS 2023 work asks whether information extracted from I/O
operations is sufficient for efficient ransomware detection in storage systems.
The architecture uses storage access patterns, feature extraction, and ML
inference directly in the storage system, leveraging computational storage
device capabilities at controller level.

Relevance:

- Very close to the project thesis: feature extraction and inference inside the
  storage stack with no user impact.
- Emphasizes "unseen ransomware" and generalizability to different storage
  setups.
- Uses storage access patterns and ML, but available public metadata suggests a
  supervised ML pipeline rather than AE anomaly detection.

Source:

- IBM Research, "Efficient ransomware detection with machine learning in storage
  systems": <https://research.ibm.com/publications/efficient-ransomware-detection-with-machine-learning-in-storage-systems>

### Generalizability In Block Storage

Reategui, Pletka, and Diamantopoulos (arXiv 2024) is essential for this project.
It studies whether ML ransomware detection from block I/O generalizes across
realistic configurations.

Key points:

- Recent storage-level ransomware detection is promising but hard because block
  I/O lacks semantic information.
- Their framework extracts minimal I/O information: entropy of writes, LBA,
  operation type, transfer size, and timestamp.
- It computes 79 lightweight features over second-range windows.
- It studies filesystem type, volume utilization, file-system aging, copy-on-
  write VM images, device encryption, and benign workloads.
- It reports that models trained on one setup can fail on others. A model trained
  on NTFS showed much lower F1 on EXT4/XFS; benign database workloads such as
  PostgreSQL could create extreme false-positive rates.
- It notes that LBA-derived features can be valuable in medium-utilization
  setups but unreliable for aged, fragmented, high-utilization, or different-
  capacity devices.
- It shows entropy-only detection is not enough under encryption, and encrypted
  workloads require representative training data.
- It argues for computationally light features and CSD-style offload.

Relevance:

- This is the warning label for the entire project.
- Our evaluation must split by filesystem, volume state, encryption, and benign
  workload family.
- LBA histograms should be treated as environment-sensitive, not universally
  stable.
- Entropy/compression should be optional and ablated.
- A low false-positive objective matters more than headline AUROC/F1.

Source:

- Reategui et al., "On the Generalizability of Machine Learning-based
  Ransomware Detection in Block Storage": <https://arxiv.org/abs/2412.21084>

### WannaLaugh Ransomware Emulator

WannaLaugh is a configurable ransomware emulator intended to safely mimic
ransomware behavior and generate malicious storage traces without running real
malware. The SYSTOR 2024 publication page says experiments show it can mimic six
real ransomware with high accuracy.

Relevance:

- Useful for safe trace expansion after initial public-data evaluation.
- Helps explore evasion-like parameter sweeps: file ordering, write methods,
  partial encryption, throttling, extension filters, and mixed workloads.
- It can help build the "unknown ransomware behavior" test set without live
  malware.

Risk:

- Emulator traces can overfit detector assumptions if they are generated using
  the same behavioral model we hope to detect.
- Use emulator traces as stress tests and augmentation, not as the only evidence.

Sources:

- IBM Research, "WannaLaugh: A Configurable Ransomware Emulator":
  <https://research.ibm.com/publications/wannalaugh-a-configurable-ransomware-simulator-learning-to-mimic-malicious-storage-traces>
- DOI: <https://doi.org/10.1145/3688351.3689163>

### DeftPunk: Cloud Block Store Detection And Recovery

DeftPunk, published at OSDI 2024 by Alibaba Group authors, targets ransomware
protection for cloud block stores. The USENIX page says the authors first tried
to adapt existing methods, then identified cloud block-store-specific I/O
characteristics and built a block-level detection and recovery system.

Key points from the USENIX summary:

- cloud block-store focus;
- two-layer classifier for fast and accurate detection;
- pre-/post-attack snapshots to avoid data loss;
- log-structured support for low-overhead recovery;
- nearly 100% recall across 13 ransomware types in large-scale benchmarks;
- low runtime overhead.

Relevance:

- It is one of the strongest practical systems in the same broad "block storage"
  family.
- The two-layer classifier is a useful architecture pattern: cheap first-level
  screening, expensive second-level confirmation.
- Snapshot/recovery design is cloud-block-store specific and not directly the
  same as SCSI/NVMe embedded device inference.
- The project should consider whether a tiny AE is best used as first-level
  anomaly scoring, second-level confirmation, or a companion score to a decision
  tree.

Source:

- Wang et al., "Ransom Access Memories: Achieving Practical Ransomware
  Protection in Cloud with DeftPunk":
  <https://www.usenix.org/conference/osdi24/presentation/wang-zhongyu>

### Rcryptect: Block-Level Cryptographic Function Detection

Rcryptect monitors block-level writes through a FUSE filesystem to detect
cryptographic operations using statistical rules. It is not a block-device
firmware system, but it is relevant because it focuses on block-level encrypted
data signals and real-time behavior.

Key points from the abstract:

- static analysis is weak against obfuscation;
- dynamic analysis can be platform-bound and slow;
- Rcryptect uses block-level monitoring to detect potentially malicious
  cryptographic operations;
- it distinguishes normal and encrypted blocks using statistical heuristic
  rules;
- it uses FUSE to avoid kernel modification;
- it reports about 13% overhead.

Relevance:

- Reinforces entropy/statistical randomness as an effective signal.
- Also reinforces why entropy may be too expensive or intrusive for our final
  storage-device design unless hardware telemetry exists.

Source:

- Lee et al., "Rcryptect: Real-time detection of cryptographic function in the
  user-space filesystem": <https://doi.org/10.1016/j.cose.2021.102512>

### Commercial Storage Signals

Vendor materials are not peer-reviewed evidence, but they show that storage
vendors are already productizing I/O anomaly signals.

Examples:

- Dell PowerMax monitors device-level I/O pattern deviations, including Track
  Flip (reducible data rewritten as unreducible) and Write After Read (WAR).
- IBM FlashSystem marketing states that FlashCore Module technology monitors
  statistics from every I/O and uses ML to detect ransomware-like anomalies in
  less than a minute.

Relevance:

- WAR and reducibility/compressibility are practical product signals.
- These map well to cheap 10-second counters if the storage platform exposes
  cache/reduction/compression metadata.
- They are likely better product-fit signals than raw Shannon entropy.

Sources:

- Dell PowerMax cybersecurity documentation:
  <https://infohub.delltechnologies.com/en-us/l/dell-powermax-cybersecurity/powermax-2500-and-8500-15/>
- IBM FlashSystem cyber resilience page:
  <https://www.ibm.com/products/flashsystem/cyber-resilience>

## Research Line 2: Public Datasets And Low-Level Behavioral Data

### Hirano 2019: Storage Access Patterns From Live-Forensic Hypervisor

Hirano and Kobayashi collected storage access patterns using WaybackVisor, a
live-forensic hypervisor, and trained Random Forest, SVM, and KNN models. The
ResearchGate-hosted paper summary reports five-dimensional hardware-level I/O
features and an F-measure of 98% on the evaluated setup.

Feature direction:

- average entropy;
- throughput or bytes read/written;
- LBA variance or spread;
- read/write behavior.

Relevance:

- Direct predecessor for storage-access-pattern ML.
- Uses a low-level layer below the OS, which matches defense-in-depth motivation.
- Dataset/setup was narrow in the 2019 paper; RanSAP and later work were created
  partly to address that limitation.

Source:

- Hirano and Kobayashi, "Machine Learning Based Ransomware Detection Using
  Storage Access Patterns Obtained From Live-forensic Hypervisor":
  <https://doi.org/10.1109/IOTSMS48152.2019.8939214>

### RanSAP

RanSAP is the most immediately usable public dataset for our first experiments.
It contains ransomware and benign storage access patterns collected with a thin
hypervisor. The repository exposes read/write CSVs:

- `ata_read.csv`: UNIX seconds, UNIX nanoseconds, LBA, size;
- `ata_write.csv`: UNIX seconds, UNIX nanoseconds, LBA, size, entropy #1,
  entropy #2.

The ScienceDirect page reports:

- seven significant ransomware samples;
- five popular benign software samples;
- ransomware variants;
- OS variation;
- storage-device variation;
- full-drive encryption conditions;
- average F1 of 96.2% for original ransomware detection, 94.1% for variants,
  81.8% on different OS, and 31.0% under full drive encryption.

Relevance:

- Best Phase 1 dataset.
- Provides exactly the raw fields needed to aggregate 10-second storage
  statistics.
- The BitLocker/full-drive encryption result is a major warning: entropy-heavy
  detection may collapse when the volume is already encrypted.

Sources:

- GitHub repository: <https://github.com/manabu-hirano/RanSAP>
- Paper: <https://doi.org/10.1016/j.fsidi.2021.301314>

### RanSMAP

RanSMAP extends RanSAP with storage and memory access patterns. It was created
because storage-only detection could fail under mixed execution, such as
ransomware running while Office applications and browsers are active.

Key points:

- includes six ransomware samples and six benign applications;
- includes seven Conti variants;
- includes simultaneous ransomware plus benign application execution;
- uses multiple CPU/RAM hardware settings;
- reports that low-level memory access patterns improved detection by 2.3%
  compared with storage-only access patterns;
- confirms detection under Office/browser simultaneous execution.

Relevance:

- Useful as a stress dataset for storage-only limitations.
- Memory features are out of scope for a block-storage device unless the product
  boundary expands.
- Its mixed-execution cases should become a required false-negative test.

Sources:

- GitHub repository: <https://github.com/manabu-hirano/RanSMAP>
- Paper: <https://doi.org/10.1016/j.cose.2024.104202>

### NapierOne, GovDocs, UMass, SNIA IOTTA

These are not ransomware storage-access datasets, but they matter for benign
diversity and entropy calibration.

- NapierOne: large mixed file corpus, explicitly includes naturally high-entropy
  file types. Useful for controlled replay and entropy false positives.
- GovDocs/GovDocs1: commonly used decoy file corpus in malware/ransomware
  experiments.
- UMass storage traces: OLTP and search-engine I/O traces. Useful for benign
  block-I/O false positives.
- SNIA IOTTA: broad storage trace repository. Useful for benign workload
  diversity and reproducing storage research baselines.

Relevance:

- They help prove that the model is not just "ransomware vs one Zip program."
- They are essential for false-positive stress.

Sources:

- NapierOne on AWS Open Data:
  <https://registry.opendata.aws/napierone/>
- UMass Storage Trace Repository:
  <https://traces.cs.umass.edu/docs/traces/storage/>
- SNIA IOTTA Repository:
  <https://www.snia.org/educational-library/iotta-repository-2019>

## Research Line 3: Filesystem And Endpoint Behavioral Defenses

These systems often achieve strong detection or recovery, but they are not
directly implementable in a block device. They are still valuable because they
identify robust ransomware behaviors and false-positive cases.

### UNVEIL

UNVEIL is a dynamic analysis system for detecting ransomware by creating an
artificial user environment and monitoring interactions with user files and the
desktop. It targets file-locker and screen-locker behavior. The USENIX page
reports that it found previously unknown evasive ransomware and was evaluated at
large scale.

Relevance:

- Shows the importance of decoy/trigger environments.
- Demonstrates that file tampering is a necessary behavior for many successful
  ransomware attacks.
- Not deployable inside storage because it depends on filesystem and desktop
  observations.

Source:

- Kharaz et al., "UNVEIL: A Large-Scale, Automated Approach to Detecting
  Ransomware": <https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/kharaz>

### CryptoDrop

CryptoDrop monitors suspicious file activity and combines multiple behavior
indicators. Its public abstract reports a median loss of only 10 files out of
about 5,100 available files before stopping ransomware.

Relevance:

- Useful indicator families: bulk modification, entropy changes, extension or
  content changes.
- Strong early-warning framing.
- Uses endpoint/file data not available to block storage.

Source:

- Scaife et al., "CryptoLock (and Drop It): Stopping Ransomware Attacks on User
  Data": <https://doi.org/10.1109/ICDCS.2016.46>

### ShieldFS

ShieldFS is a Windows filesystem add-on driver with copy-on-write recovery. It
profiles low-level filesystem activity and rolls back malicious side effects.
The publication page says it was designed using billions of low-level filesystem
requests from benign applications on real user machines.

Relevance:

- Shows that large benign workload corpora are valuable.
- Copy-on-write response is outside our initial scope, but the detection plus
  recovery architecture is informative.
- Uses process/filesystem models unavailable at pure block layer.

Source:

- Continella et al., "ShieldFS: A Self-healing, Ransomware-aware Filesystem":
  <https://doi.org/10.1145/2991079.2991110>

### Redemption

Redemption is an endpoint real-time protection approach by Kharraz and Kirda.
It is relevant as a continuation of behavior-focused ransomware defense,
especially around stopping and recovering from destructive behavior at the host.

Relevance:

- Reinforces that detection alone is not enough for practical ransomware
  defense.
- Recovery/rollback remains a later stage for this project.

Source:

- Kharraz and Kirda, "Redemption: Real-Time Protection Against Ransomware at
  End-Hosts": <https://doi.org/10.1007/978-3-319-66332-6_5>

### PayBreak

PayBreak hooks cryptographic operations and escrows session keys, enabling
decryption for some ransomware families. Its core insight is cryptographic
rather than storage behavioral.

Relevance:

- Not suitable for storage-device deployment.
- Useful contrast: it protects even after encryption by capturing keys, while
  storage-only systems must infer behavior or recover old data.

Source:

- Kolodenker et al., "PayBreak: Defense Against Cryptographic Ransomware":
  <https://doi.org/10.1145/3052973.3053035>

### Peeler

Peeler profiles kernel-level events to detect ransomware. The arXiv summary
reports over 99% detection, 0.58% false-positive rate, detection after one file
lost for crypto ransomware, and around 9.8 MB memory.

Relevance:

- Shows kernel event sequences are highly informative.
- Memory footprint is much larger than our 500 KB per-volume detector-data
  budget and the signal is not block-device-local.
- Good comparison point for "what host-level context buys you."

Source:

- Ahmed et al., "Peeler: Profiling Kernel-Level Events to Detect Ransomware":
  <https://arxiv.org/abs/2101.12434>

### XRan And Dynamic-Analysis Deep Learning

XRan uses dynamic analysis features such as API call, DLL, and Mutex sequences,
then applies CNN plus explainability methods. The ScienceDirect abstract reports
up to 99.4% true positive rate and emphasizes XAI.

Relevance:

- Strong evidence for sequence-based deep learning on ransomware behavior.
- Not directly portable because API/DLL/Mutex sequences are invisible to block
  storage.
- XAI idea maps to our per-channel reconstruction-error reporting.

Source:

- Gulmez et al., "XRan: Explainable deep learning-based ransomware detection
  using dynamic analysis": <https://doi.org/10.1016/j.cose.2024.103703>

## Research Line 4: Entropy, Compressibility, And High-Entropy False Positives

Entropy is one of the most common ransomware signals because encryption tends to
increase byte randomness. It is also one of the most dangerous features for this
project because it may be unavailable, expensive, or misleading.

Relevant findings:

- Rcryptect uses block-level statistical analysis to detect cryptographic
  operations, but incurs filesystem-level overhead.
- Byte-frequency work argues that whole-file entropy can misclassify naturally
  high-entropy files, and proposes sampling file subareas to reduce overhead.
- Reategui et al. show that entropy-related features are important in many
  storage models, but encrypted volumes and VM images change the detection
  problem.
- RanSAP reports severe degradation under full-drive encryption.
- Dell PowerMax's "Track Flip" signal suggests compressibility/reducibility may
  be more product-realistic than Shannon entropy when storage reduction hardware
  already exists.

Implication:

- Use entropy in offline experiments because RanSAP/RanSMAP provide it.
- Always report no-entropy ablation.
- Prefer cheap compression/reducibility telemetry over new entropy scans in the
  final embedded design.
- Treat naturally compressed/encrypted workloads as first-class false-positive
  tests.

Representative sources:

- Rcryptect: <https://doi.org/10.1016/j.cose.2021.102512>
- Byte-frequency indicators:
  <https://doi.org/10.1007/s11390-021-0263-x>
- RanSAP: <https://doi.org/10.1016/j.fsidi.2021.301314>
- Block-storage generalizability: <https://arxiv.org/abs/2412.21084>

## Research Line 5: AutoEncoders And Time-Series Anomaly Detection

The general time-series anomaly detection literature supports the basic idea:
train a model on normal sequences, reconstruct them, and flag high
reconstruction error. This is not ransomware-specific, but it provides model
families and pitfalls.

### Recurrent AutoEncoders

LSTM/GRU AutoEncoders are common for multivariate time-series anomaly detection.
They can model temporal dependencies, but recurrent decoders can accumulate
errors and may overfit. RAMED, for example, explicitly addresses recurrent
decoder issues with multiresolution ensemble decoding.

Relevance:

- Supports GRU-only AE as a candidate.
- A full LSTM/VAE/GAN model is likely too heavy for 500 KB per-volume
  detector-data memory.
- Threshold selection and reconstruction error calibration must be treated
  carefully.

Sources:

- Niu et al., "LSTM-Based VAE-GAN for Time-Series Anomaly Detection":
  <https://doi.org/10.3390/s20133738>
- Shen et al., "Time Series Anomaly Detection with Multiresolution Ensemble
  Decoding": <https://doi.org/10.1609/aaai.v35i11.17152>

### Temporal Convolutional AutoEncoders

Temporal convolutional AutoEncoders use convolution over time rather than
recurrent state. They can be computationally efficient and fixed-shape, which is
attractive for MNN and embedded deployment.

Relevance:

- A TCN/1D-conv AE is likely a better second candidate than CNN-GRU.
- Fixed input shape and static graph are MNN-friendly.
- Dilated convolutions can capture multi-window context with modest state.

Source:

- Thill et al., "Temporal convolutional autoencoder for unsupervised anomaly
  detection in time series": <https://doi.org/10.1016/j.asoc.2021.107751>

### AE Use In Ransomware Work

Ransomware-specific AE work exists, but most examples operate on file-system,
network, blockchain, static PE, or feature-selection data rather than storage
I/O inside a device. Some recent works use stacked autoencoders for feature
selection or deep classification, not necessarily one-class storage anomaly
detection.

Relevance:

- AE as a ransomware detector is not new in general.
- AE over cheap block-I/O statistics under a 500 KB per-volume detector-data
  budget appears much less explored.
- This supports a scoped novelty claim rather than a broad "AE detects
  ransomware" claim.

Representative sources:

- Ransomware detection using stacked autoencoder for feature selection:
  <https://repository.up.ac.za/handle/2263/98772>
- General malware detection using autoencoder:
  <https://doi.org/10.1109/ACCESS.2022.3155695>

## Baseline Matrix For This Project

| Baseline | Why needed | Expected memory | Product fit |
| --- | --- | ---: | --- |
| write ratio / bytes written | simplest ransomware burst detector | tiny | high |
| LBA spread histogram | tests address-distribution hypothesis | tiny | medium, sensitive to fragmentation |
| write-after-read / overwrite proxy | maps to SSD-Insider and Dell WAR | tiny | high if cache/history exists |
| compression/reducibility change | maps to Dell FLIP and storage reduction | tiny if existing telemetry | high if platform supports it |
| decision tree | strong storage-level prior baseline | very small | very high |
| random forest / XGBoost | strong offline baseline | medium | maybe too heavy |
| one-class SVM / Isolation Forest | anomaly baseline | medium | uncertain |
| MLP AE | smallest AE baseline | small | high |
| GRU AE | temporal modeling | small-medium | possible |
| temporal-conv AE | fixed-shape temporal modeling | small-medium | good MNN fit |
| CNN-GRU AE | original architecture | medium-high | must earn its place |

## Feature Lessons

### Features With Strong Prior Support

- write throughput or write bytes per window;
- read throughput;
- read/write ratio;
- LBA variance/spread/histogram;
- write-after-read or overwrite-related behavior;
- entropy/compression/reducibility change;
- transfer-size distribution;
- temporal changes over 10-second windows.

### Features That Conflict With Our Constraints

- per-block Shannon entropy if computed only for detection;
- kurtosis, slope, or higher moments if they require expensive state or
  floating-point-heavy computation;
- per-file content deltas;
- file extension or rename behavior;
- process, API, DLL, Mutex, registry, or kernel event sequences;
- memory-access patterns from hypervisor SLAT/EPT.

### Compromise Feature Set For 10-Second Frames

Use this as the first production-shaped frame:

```text
read_count
write_count
read_bytes_log
write_bytes_log
read_lba_hist[8]
write_lba_hist[8]
read_len_hist[8]
write_len_hist[8]
seq_read_count
seq_write_count
optional_reducibility_or_compression_signal
```

This yields 38-39 scalar values per 10 seconds. With 12 frames, the MLP input is
roughly 456-468 scalars before optional channels.

## Evaluation Lessons

Do not accept a result unless it answers:

- Does it beat SSD-Insider-like cheap behavior rules?
- Does it beat a decision tree on the same 10-second features?
- Does it survive removing entropy/compression?
- Does it survive a different filesystem?
- Does it survive a different volume utilization or aged/fragmented volume?
- Does it survive BitLocker/LUKS or other already-encrypted storage?
- Does it survive benign compression, backup, secure delete, browser, Office,
  MySQL, PostgreSQL, and VM image workloads?
- How many bytes or LBA buckets are overwritten before alert?
- Does the converted MNN model preserve anomaly-score ordering?
- Do model weights plus retained input statistics/state stay under the 500 KB
  per-volume detector-data budget?

## Gaps And Opportunity

### What Existing Work Already Covers

- Storage-local detection is plausible.
- 10-second detection is plausible.
- Block I/O header-only features can work.
- Entropy/compressibility is useful when available.
- Decision-tree-style supervised models are strong.
- Endpoint and filesystem behavior detectors can be highly accurate when they
  see host semantics.

### What Existing Work Does Not Fully Cover

- One-class or unsupervised AE trained only on benign storage workloads under a
  tight embedded memory budget.
- MNN-converted tiny AE inference over fixed 10-second block-I/O statistics.
- A systematic comparison of tiny AE vs SSD-Insider-like rules and decision
  trees under no-entropy constraints.
- Robustness of AE reconstruction error across filesystem type, volume aging,
  encrypted volumes, and database workloads.

### Research Claim To Aim For

The strongest defensible claim is:

> A tiny MNN-deployable AutoEncoder over cheap 10-second block-I/O statistics
> can serve as a storage-local anomaly detector that complements existing
> supervised storage ransomware classifiers, with measured robustness under
> no-entropy and cross-workload conditions.

The claim should not be:

> AutoEncoders are sufficient to detect ransomware from storage I/O in general.

That broader claim is too exposed to generalization, encryption, and benign
workload false positives.

## Annotated Reference List

| Ref | Work | Layer | Method | Useful for this project |
| --- | --- | --- | --- | --- |
| Banikazemi et al. 2005 | Storage-based IDS for SANs | block/SAN | storage IDS + point-in-time copy | storage as security boundary |
| Allalouf et al. 2010 | IDStor | block controller | block-to-file mapping | semantic gap framing |
| Kharaz et al. 2016 | UNVEIL | sandbox/filesystem/desktop | dynamic analysis | ransomware behavior taxonomy |
| Scaife et al. 2016 | CryptoDrop | endpoint/filesystem | behavior indicators | early-warning metrics |
| Continella et al. 2016 | ShieldFS | filesystem driver | adaptive models + copy-on-write | benign workload modeling |
| Kharraz/Kirda 2017 | Redemption | endpoint | real-time protection/recovery | response framing |
| Kolodenker et al. 2017 | PayBreak | endpoint/crypto API | key escrow | contrast with storage-only |
| Baek et al. 2018 | SSD-Insider | SSD firmware | header-only features + recovery | closest firmware baseline |
| Hirano/Kobayashi 2019 | Storage access patterns | hypervisor/storage | RF/SVM/KNN | direct storage ML predecessor |
| Ahmed et al. 2021 | Peeler | kernel events | behavioral event profiling | host context comparison |
| Lee et al. 2022 | Rcryptect | FUSE/block | entropy/statistical heuristics | entropy signal and cost |
| Hirano et al. 2022 | RanSAP | hypervisor/storage | dataset + ML | primary public data |
| Constantinescu/Seshadri 2021 | Sentinel | file storage | ransomware detection algorithms | storage product direction |
| Pletka et al. 2023 | Efficient ML in storage | storage/CSD | storage access ML | CSD architecture |
| Reategui et al. 2024 | Generalizability in block storage | block/CSD | lightweight features + DT/XGBoost | evaluation risks |
| Diamantopoulos et al. 2024 | WannaLaugh | emulator/storage traces | safe ransomware emulation | trace augmentation |
| Wang et al. 2024 | DeftPunk | cloud block storage | two-layer classifier + snapshots | practical block-store recovery architecture |
| Gulmez et al. 2024 | XRan | dynamic analysis | CNN + XAI | sequence/XAI ideas |
| Hirano/Kobayashi 2025 | RanSMAP | hypervisor/storage+memory | dataset + DL | mixed workload stress |
| Thill et al. 2021 | TCN-AE | generic time series | temporal conv AE | embedded-friendly AE candidate |
| Niu et al. 2020 | LSTM VAE-GAN | generic time series | reconstruction + discrimination | AE anomaly framing |
| Shen et al. 2021 | RAMED | generic time series | recurrent AE improvements | recurrent AE pitfalls |

## Source Index

- SSD-Insider:
  <https://dgist.elsevierpure.com/en/publications/ssd-insider-internal-defense-of-solid-state-drive-against-ransomw/>
- IBM storage ML:
  <https://research.ibm.com/publications/efficient-ransomware-detection-with-machine-learning-in-storage-systems>
- Block-storage generalizability:
  <https://arxiv.org/abs/2412.21084>
- WannaLaugh:
  <https://research.ibm.com/publications/wannalaugh-a-configurable-ransomware-simulator-learning-to-mimic-malicious-storage-traces>
- DeftPunk:
  <https://www.usenix.org/conference/osdi24/presentation/wang-zhongyu>
- RanSAP:
  <https://github.com/manabu-hirano/RanSAP>
- RanSAP paper:
  <https://doi.org/10.1016/j.fsidi.2021.301314>
- RanSMAP:
  <https://github.com/manabu-hirano/RanSMAP>
- RanSMAP paper:
  <https://doi.org/10.1016/j.cose.2024.104202>
- Rcryptect:
  <https://doi.org/10.1016/j.cose.2021.102512>
- UNVEIL:
  <https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/kharaz>
- CryptoDrop:
  <https://doi.org/10.1109/ICDCS.2016.46>
- ShieldFS:
  <https://doi.org/10.1145/2991079.2991110>
- Redemption:
  <https://doi.org/10.1007/978-3-319-66332-6_5>
- PayBreak:
  <https://doi.org/10.1145/3052973.3053035>
- Peeler:
  <https://arxiv.org/abs/2101.12434>
- XRan:
  <https://doi.org/10.1016/j.cose.2024.103703>
- TCN-AE:
  <https://doi.org/10.1016/j.asoc.2021.107751>
- LSTM VAE-GAN:
  <https://doi.org/10.3390/s20133738>
- RAMED:
  <https://doi.org/10.1609/aaai.v35i11.17152>
- MNN:
  <https://github.com/alibaba/MNN>
- Dell PowerMax:
  <https://infohub.delltechnologies.com/en-us/l/dell-powermax-cybersecurity/powermax-2500-and-8500-15/>
- IBM FlashSystem:
  <https://www.ibm.com/products/flashsystem/cyber-resilience>
