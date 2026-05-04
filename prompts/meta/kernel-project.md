# kernel-project.md - Project-Specific Profile v1.1.0
# ABSTRACT LAYER - PROJECT: rules, conventions, and constraints specific to THIS research project.
# This file is the SINGLE SOURCE OF TRUTH for project-specific rules.
#
# Separation principle:
#   - kernel-constitution.md -> Universal axioms - valid for ANY project
#   - kernel-domains.md      -> Generic research domain framework
#   - kernel-project.md      -> THIS file: project-type + project-instance rules
#
# Derived output: docs/03_PROJECT_RULES.md
# FOUNDATION: kernel-constitution.md §AXIOMS

<meta_section id="META-PROJECT" version="1.1.0" axiom_refs="phi6,A7,A10">
<purpose>Project-specific profile for AI-assisted research on storage-embedded anomaly detection of ransomware behavior, supported by a deployable research-agent workflow.</purpose>
<authority>The Root Admin (ResearchArchitect) edits this file when onboarding or changing project-specific acceptance rules. All other agents consult `docs/03_PROJECT_RULES.md`.</authority>
<rules>
- MUST NOT place project-specific rules in kernel-constitution.md, kernel-domains.md, kernel-ops.md, kernel-workflow.md, or kernel-antipatterns.md.
- MUST regenerate `docs/03_PROJECT_RULES.md` after any PR-{N} edit.
- MUST treat this repository as AI/ML anomaly detection research for block-storage ransomware behavior, not as a product firmware implementation.
- MUST preserve source papers, dataset references, raw traces, experiment configs, model code, run logs, metrics, figures, manuscript drafts, and critique artifacts as external memory.
- MUST NOT promote model-performance, novelty, device-fit, MNN-readiness, or deployment-readiness claims without traceable evidence.
- MUST keep the deployed detector assumption explicit: 10-second statistics, cheap block-I/O telemetry, and a conservative rounded 500 KB per-volume detector-data budget for model weights plus input statistics/state, derived from roughly 1 GB across roughly 2000 volumes and excluding shared MNN runtime/library memory.
</rules>
<see_also>docs/03_PROJECT_RULES.md, docs/01_PROJECT_MAP.md, docs/interface/ResearchBrief.md</see_also>

--------------------------------------------------------
# § PROJECT IDENTITY

| Field | Value |
|-------|-------|
| Repository | `git@github.com:t0m0h1r0/research-anomaly.git` |
| Local project | `/Users/tomohiro/Documents/New project 3` |
| Project type | Storage-embedded AI anomaly detection research + deployable research-agent workflow |
| Research target | Detect ransomware-like block-storage behavior using AI anomaly detection over time-series I/O statistics |
| Observation boundary | SCSI/NVMe-style block I/O metadata: timestamp, read/write operation, LBA or offset, transfer length, optional cheap entropy/compression telemetry |
| Deployed input | Fixed-shape sequences of 10-second statistics, not raw per-I/O event streams |
| Candidate model family | Memory-aware AutoEncoder models: MLP AE, GRU AE, temporal convolution AE, and tiny CNN-GRU AE only if justified |
| Embedded runtime target | Alibaba MNN CPU inference path, with parity testing against offline scores before implementation claims |
| Detector-data budget | conservative rounded 500 KB per volume for model weight information plus retained input statistics/state, excluding shared MNN runtime/library memory |
| Primary datasets | RanSAP first; RanSMAP, SNIA IOTTA, UMass storage traces, and other registered traces as compatibility evidence |
| Research artifacts | Research brief, literature notes, dataset cards, model specs, code, configs, experiment results, figures, and manuscript drafts |
| Primary objective | Decide whether storage-local AI anomaly detection for ransomware is credible, reproducible, and device-feasible |
| Secondary objective | Improve the reusable AI-agent research workflow through traceable lessons |

--------------------------------------------------------
# § PR - Project-Specific Rules

These rules apply to agents working on this project. They are intentionally
portable except for the block-storage ransomware detection topic, active
artifacts, and local project paths.

## PR-1 - Research Outcome and Agent-Workflow Co-Primacy

The agent system exists to advance the storage-embedded ransomware anomaly
detection research. At the same time, substantial tasks should preserve workflow
learning so the research process itself becomes more reliable.

Every substantial research task SHOULD produce two outputs:

| Output | Purpose |
|--------|---------|
| Research artifact | question map, literature note, dataset note, model spec, code patch, experiment package, error analysis, figure, or manuscript patch |
| Workflow artifact | routing lesson, evidence need, prompt limitation, failure mode, reusable task pattern, or audit note |

If these conflict, protect the research evidence first and record the workflow
lesson without delaying a valid research deliverable.

## PR-2 - Source, Dataset, and Experiment Traceability

Agents MUST preserve traceability across source material, public dataset
references, raw traces, processed tensors, code, configs, logs, metrics, figures,
and prose claims. Source papers, raw traces, and immutable data inputs MUST NOT
be overwritten.

Allowed source and derived locations:

| Artifact type | Directory |
|---------------|-----------|
| Source papers and source text | `paper/source/` |
| Immutable/raw datasets or dataset manifests | `data/raw/` |
| Processed datasets with provenance | `data/processed/` |
| Research plans and model audits | `docs/memo/` |
| Literature, benchmark, and citation checks | `docs/evidence/` |
| Interface contracts | `docs/interface/` |
| Reusable model/evaluation code | `src/` |
| Reproducible experiments | `analysis/{study}/` |
| Exploratory notebooks | `notebooks/` |
| Manuscript sections and figures | `paper/sections/`, `paper/figures/`, `artifacts/A/` |
| Workflow lessons | `artifacts/M/` and `docs/02_ACTIVE_LEDGER.md` |

Any performance value, table, figure, detector-data estimate, transient scratch
estimate, or MNN parity value
promoted to writing MUST cite dataset version, split protocol, config path,
command, run log, commit or artifact hash when available, and creation date.

## PR-3 - Model and Claim Rigor Gate

Claims involving ransomware detectability, anomaly-score validity, threshold
design, calibration, robustness, interpretability, memory fit, MNN conversion, or
deployment readiness MUST be independently checked.

Minimum audit standard:

| Check | Acceptance |
|-------|------------|
| Definitions | benign workload, ransomware/anomaly class, unit of observation, alert horizon, and response scope are explicit |
| Observation boundary | host-only, filesystem, process, filename, and signature features are excluded unless scope is formally changed |
| Assumptions | stationarity, contamination, label quality, class imbalance, temporal ordering, encrypted-volume behavior, and operating constraints are stated |
| Baselines | write-ratio, entropy/compression, LBA-spread, simple statistical, and classical anomaly baselines are considered before crediting deep models |
| Metrics | AUROC/AUPRC/F1 or domain metrics are justified; false alarms per volume per day, detection delay, and bytes overwritten before alert are considered when relevant |
| Leakage | train/validation/test boundaries, temporal leakage, workload/family/device leakage, normalization leakage, and threshold tuning leakage are checked |
| Device fit | 10-second statistics, cheap feature collection, 500 KB per-volume detector data for model weights plus input statistics/state, transient scratch per inference slot, scheduled slot count, MNN operator support, and score parity are checked before embedded claims |
| Uncertainty | repeated seeds, confidence intervals, sensitivity analysis, or clearly bounded exploratory status are used for material quantitative claims |
| Failure modes | benign backup/encryption/compression workloads, throttled ransomware, high-entropy benign data, drift, and out-of-distribution behavior are recorded |

Unverified effectiveness, novelty, or device-fit claims remain hypotheses or
audit findings, not paper conclusions.

## PR-4 - Literature, Benchmark, and Citation Hygiene

Agents MUST separate four evidence classes:

| Class | Examples | Rule |
|-------|----------|------|
| Internal design evidence | feature contract, AE architecture, loss, score function, threshold policy, ablation rationale | Cite exact artifact path and section |
| External literature evidence | storage-level ransomware detection, anomaly detection methods, AutoEncoder time-series detection, computational storage, MNN/device constraints | Verify against bibliographic source before adding claims |
| Dataset/benchmark evidence | RanSAP/RanSMAP dataset card, trace schema, split file, preprocessing, labels, license, caveats | Record provenance and compatibility with the experiment protocol |
| Numerical evidence | scripts, configs, logs, metrics, figures, memory reports, MNN parity outputs | Record command, parameters, output path, and date |

No agent may invent citations, benchmark facts, SOTA claims, dataset properties,
or empirical numbers. If a source is unavailable, mark the claim as needing
source verification. Benchmark comparisons require compatible data splits,
metrics, preprocessing, feature availability, and tuning budgets; otherwise they
are reported as non-comparable context.

## PR-5 - Reproducible Coding and Experiment Standard

Any coding or experiment artifact introduced by agents MUST be reproducible from
repository files plus explicitly registered external data sources.

Required for each promoted experiment:

| Item | Requirement |
|------|-------------|
| Script/notebook | Final evidence uses a non-interactive script under `analysis/{study}/`; notebooks are exploratory unless promoted |
| Inputs | Local files, registered external source, explicit trace manifest, or deterministic synthetic-data generator |
| Config | Stored config or parameter table, including feature schema, model, preprocessing, split, seed, threshold policy, and memory budget assumptions |
| Output | Metrics, logs, figures, and manifest under `analysis/{study}/results/` |
| Command | Captured in the manifest and ledger |
| Interpretation | PASS/FAIL/INCONCLUSIVE with reason and scope |

Standard experiment layout:

```text
analysis/{study}/
  run.py
  README.md
  config.yaml or config.json
  results/
    manifest.json
    metrics.csv or metrics.json
    figures/*.pdf or *.png
    run.log
```

`manifest.json` MUST include: purpose, source_refs, dataset_refs, command,
python_version, package_versions for core dependencies used, parameters,
random_seed or `null`, split protocol, feature schema, metrics, output_files,
created_at_utc, and verdict.

Python scripts MUST be non-interactive, deterministic when randomness is used,
and safe to rerun. Exploratory scratch work may exist temporarily, but only
curated outputs can support manuscript or research-summary claims.

## PR-6 - Paper and Deployment Readiness Standard

Research outputs should move the project toward peer-reviewable anomaly
detection work and a redeployable agent workflow.

Agents MUST prioritize:

1. clear problem setting and ransomware anomaly taxonomy,
2. credible relation to prior storage-level ransomware and time-series anomaly detection work,
3. fair baselines and benchmark protocol,
4. reproducible feature extraction, implementation, and experiments,
5. leakage, threshold, and false-positive analysis,
6. ablation and robustness checks across entropy availability, benign workload shifts, ransomware families, and device conditions,
7. honest limitation and failure-mode reporting,
8. concise academic prose in the chosen manuscript language,
9. explicit MNN conversion, parity, 500 KB per-volume detector-data evidence, transient scratch per slot, and scheduling evidence before embedded claims,
10. deployable prompts, docs, and workflow artifacts.

Stylistic rewrites that do not improve at least one of these points are out of
scope.

--------------------------------------------------------
# § PORTABILITY NOTES

To adapt this system for another research project:

1. Replace only `kernel-project.md` with a new project profile.
2. Keep the generic kernel files unchanged unless a workflow limitation is discovered.
3. Regenerate `docs/03_PROJECT_RULES.md`.
4. Update source-artifact paths and active assumptions in `docs/01_PROJECT_MAP.md`.
5. Run prompt audit for project-specific leakage.

The PR-{N} numbering is local to this file. Universal rules use A-{N}, C-{N},
P-{N}, Q-{N}, AU-{N}, and AP-{N}.
</meta_section>
