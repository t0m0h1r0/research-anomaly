# GENERATED - do NOT edit directly. Edit prompts/meta/kernel-*.md and regenerate.

# Prompt System

This prompt system deploys generic research agents for theory/claim audit,
evidence audit, reproducible implementation, experiment evaluation, paper
revision, and prompt/workflow evolution.

## Architecture

| Layer | Files | Purpose |
|-------|-------|---------|
| Kernel | `prompts/meta/kernel-*.md` | source of truth |
| Generated agents | `prompts/agents-claude/`, `prompts/agents-codex/` | executable role prompts |
| Skill capsules | `prompts/skills/` | project-local JIT operation details, including scheme/code, paper-writing, deck, and illustration loops |
| Local helpers | `scripts/lock.py`, `scripts/atomic_push.py`, `scripts/validate_prompt_deployment.py` | project-local worktree and prompt-audit helpers |
| Upstream marker | `prompts/upstream.toml` | imported research-agent kernel revision |
| Runtime docs | `AGENTS.md`, `docs/00_GLOBAL_RULES.md`, `docs/01_PROJECT_MAP.md`, `docs/02_ACTIVE_LEDGER.md`, `docs/03_PROJECT_RULES.md` | compact working memory and external-agent runbook |

## Active Project

The active project is storage-embedded AI anomaly detection for ransomware
behavior. The initial scope is registered in
`docs/interface/ResearchBrief.md`; source papers and raw trace files are not yet
registered, while the existing research scaffold in `docs/00_research_charter.md`
through `docs/05_literature_survey.md` is active background material.

Substantial tasks should advance research evidence first and capture workflow
lessons when they improve the agent system.

## Agent Roster

The deployed roster contains 24 roles per environment, including ResearchArchitect,
TaskPlanner, TheoryArchitect, TheoryAuditor, CodeArchitect, TestRunner,
ExperimentRunner, EvidenceAnalyst, PaperWriter, PaperReviewer, ConsistencyAuditor,
PresentationWriter, PromptArchitect, PromptAuditor, KnowledgeArchitect,
WikiAuditor, Librarian, and TraceabilityManager.

The local skill manifest contains 9 capsules: handoff audit, git worktree,
tool trust, condensation, prompt audit, scheme/code, paper writing,
presentation deck, and presentation illustration/readback.

## Upstream Sync

Shared metaprompts are pulled from
`git@github.com:t0m0h1r0/research-agent.git`. Generated agents, skill capsules,
templates, and helper scripts are local derived outputs, not upstream payloads.
For a normal refresh, run:

```sh
make prompt-sync-dry-run
make prompt-sync
make prompt-audit
```

The local wrapper calls upstream `scripts/sync_to_project.py`, writes
`prompts/upstream.toml`, and verifies that `prompts/meta/kernel-project.md` keeps
the same SHA-256 before and after sync. The upstream sync copies only
`kernel/*.md` into `prompts/meta/` and writes
`prompts/upstream-managed.json`. If upstream writes
`prompts/REDEPLOY_REQUIRED.md`, keep it until local deployment docs, skills,
helper-script policy, prompt counts, Q3-AUDIT, and Q3b token telemetry pass;
remove it in the same commit that records the successful redeploy.

## Regeneration

For project retargeting, edit local `prompts/meta/kernel-project.md` and
regenerate `docs/03_PROJECT_RULES.md`, `docs/01_PROJECT_MAP.md`,
`docs/02_ACTIVE_LEDGER.md`, `AGENTS.md`, project-local skills/helpers/agents,
and validation reports. Do not replace the project profile unless the project is
being intentionally re-onboarded. For shared workflow changes, change the
upstream `research-agent` repository first, sync metaprompts here, then run
prompt audit before using changed agents.

`AGENTS.md` should stay short and operational: read-order, worktree/commit
discipline, source integrity, artifact routing, claim gates, and the default
planning task. Full rule bodies belong in `prompts/meta/` or skill capsules.
