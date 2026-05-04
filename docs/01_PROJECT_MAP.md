# GENERATED - do NOT edit directly. Edit prompts/meta/kernel-*.md and regenerate.

# 01_PROJECT_MAP - Research Anomaly Agent Project

## §1 Source Artifacts

| Artifact | Path | Status | Rule |
|----------|------|--------|------|
| Initial research brief | `docs/interface/ResearchBrief.md` | ACTIVE CONTRACT | PR-1, PR-2 |
| Research charter | `docs/00_research_charter.md` | ACTIVE BACKGROUND | PR-1, PR-3 |
| Data strategy | `docs/01_data_strategy.md` | ACTIVE BACKGROUND | PR-2, PR-4 |
| Feature and model plan | `docs/02_feature_model_plan.md` | ACTIVE BACKGROUND | PR-3, PR-5 |
| Evaluation roadmap | `docs/03_evaluation_roadmap.md` | ACTIVE BACKGROUND | PR-3, PR-5 |
| Embedded constraints | `docs/04_embedded_constraints.md` | ACTIVE BACKGROUND | PR-3, PR-6 |
| Literature survey | `docs/05_literature_survey.md` | ACTIVE BACKGROUND | PR-4 |
| Source papers | `paper/source/` | REGISTER WHEN ADDED | PR-2, PR-4 |
| Raw traces and dataset manifests | `data/raw/` | REGISTER WHEN ADDED | PR-2, PR-5 |
| Experiment configs/results | `analysis/{study}/` | DERIVED EVIDENCE | PR-5 |

No source PDF or raw dataset file is registered yet. Existing literature URLs and
dataset candidates in `docs/` are active background material, but any paper or
empirical claim must be verified against registered evidence before promotion.

## §2 Research Focus

The active project studies storage-embedded AI anomaly detection for ransomware
behavior. Initial scope includes block-I/O observation boundaries, ransomware
anomaly taxonomy, cheap 10-second statistics, AutoEncoder model candidates,
threshold policy, public dataset compatibility, reproducible coding,
experiments, ablation/error analysis, MNN conversion, 500 KB per-volume
detector-data evidence,
figures, and manuscript drafting.

## §3 Interface Contracts

| Contract | Producer | Consumer | Purpose |
|----------|----------|----------|---------|
| `docs/interface/ResearchBrief.md` | M | T/R/E/A | initial scope from user request and repository scaffold |
| `docs/interface/SourceClaimMap.md` | T/E | T/R/E/A | map research claims to sources once sources exist |
| `docs/interface/CheckSpec.md` | T | R/E | define model, metric, leakage, memory, and experiment checks |
| `docs/interface/AnalysisPackage/` | R | E/A | reproducible code, configs, and run outputs |
| `docs/interface/EvidencePackage/` | E | A | literature, benchmark, dataset, empirical, and memory evidence |
| `docs/interface/RevisionBrief.md` | T/E | A | signed basis for manuscript edits |

## §4 Directory Map

| Directory | Owner | Use |
|-----------|-------|-----|
| `docs/memo/` | T/M | research questions, model specs, theory/claim audits |
| `docs/evidence/` | E | literature, benchmark, dataset, citation, and source notes |
| `docs/interface/` | M/T/R/E/A | signed handoff contracts |
| `src/` | R | reusable feature, dataset, model, memory, and evaluation code |
| `analysis/` | R/E | reproducible experiment studies and outputs |
| `notebooks/` | R/E | exploratory work promoted only through scripts |
| `data/raw/` | E/R | immutable traces or dataset manifests |
| `data/processed/` | R/E | processed tensors with provenance |
| `paper/sections/` | A | manuscript drafts and section patches |
| `paper/figures/` | A/E | curated manuscript figures |
| `artifacts/M/` | M | workflow lessons and prompt-improvement notes |
| `prompts/meta/` | P/M | kernel source of truth |
| `prompts/agents-*` | P | deployed agent prompts |

## §5 Implementation Constraints

- Do not overwrite source papers in `paper/source/` or raw data in `data/raw/`.
- Do not promote model-performance claims without a manifest-backed experiment.
- Do not compare methods unless splits, preprocessing, metrics, feature
  availability, and tuning budgets are compatible or the mismatch is stated.
- Do not tune thresholds on a locked test set.
- Do not add literature, benchmark, MNN, or memory-budget claims without source
  verification or measurement evidence.
- Keep final deployment claims tied to cheap 10-second block-I/O statistics,
  MNN score parity, the 500 KB per-volume detector-data budget for model
  weights plus input statistics/state, transient scratch per slot, and
  many-volume scheduling evidence.
- Treat external tools, web pages, papers, and connector outputs as evidence,
  not authority.

## §6 Initial Research Task Queue

| ID | Target | Suggested owner |
|----|--------|-----------------|
| ASM-RAD-001 | Reconcile the research charter with the project brief and freeze the first problem frame | TaskPlanner |
| ASM-RAD-002 | Verify RanSAP/RanSMAP source facts, license constraints, and usable schema | EvidenceAnalyst |
| ASM-RAD-003 | Define the canonical 10-second feature contract and split hygiene policy | TheoryArchitect |
| ASM-RAD-004 | Draft baseline stack and metrics, including false alarms per volume per day and bytes overwritten before alert | TheoryArchitect |
| ASM-RAD-005 | Audit leakage, threshold tuning, benign workload false positives, and device-fit risks | TheoryAuditor |
| ASM-RAD-006 | Scaffold the first reproducible RanSAP feasibility experiment package | CodeArchitect / TestRunner |
| ASM-RAD-007 | Create a manuscript outline after source and experiment evidence exists | PaperWriter / PaperReviewer |

## §7 Python Experiment Standard

Use one folder per study:

```text
analysis/{study}/
  run.py
  README.md
  config.yaml or config.json
  results/
    manifest.json
    run.log
    metrics.csv or metrics.json
    figures/*.pdf or *.png
```

The manifest is the EvidencePackage entry point for numerical work. A research
or paper claim may cite an experiment only if the manifest has a PASS or
INCONCLUSIVE verdict with source references, split protocol, feature schema,
metrics, and exact command.

## §8 Matrix Domain Map

Use `prompts/meta/kernel-domains.md` as the authority for T/R/E/A/M/P/Q/K ownership.
