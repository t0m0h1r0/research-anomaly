# GENERATED - do NOT edit directly. Edit prompts/meta/kernel-*.md and regenerate.

# Prompt System

This prompt system deploys generic research agents for theory/claim audit,
evidence audit, reproducible implementation, experiment evaluation, paper
revision, presentation work, and prompt/workflow evolution.

## Architecture

| Layer | Files | Purpose |
|-------|-------|---------|
| Kernel | `prompts/meta/kernel-*.md` | source of truth |
| Local project profile | `prompts/meta/kernel-project.md` | project-specific rules; preserved across sync |
| Generated agents | `prompts/agents-claude/`, `prompts/agents-codex/` | executable role prompts |
| Skill capsules | `prompts/skills/` | project-local JIT operation details |
| Local helpers | `scripts/sync_research_agent.py`, `scripts/deploy_prompt_system.py`, `scripts/validate_prompt_deployment.py` | sync, zero-base deploy, and prompt-audit helpers |
| Remote metadata | `prompts/upstream.toml`, `prompts/upstream-managed.json` | imported remote snapshot `ed388737ed01` |
| Runtime docs | `AGENTS.md`, `docs/00_GLOBAL_RULES.md`, `docs/01_PROJECT_MAP.md`, `docs/02_ACTIVE_LEDGER.md`, `docs/03_PROJECT_RULES.md` | compact working memory and external-agent runbook |

## Active Project

The active project is storage-embedded AI anomaly detection for ransomware
behavior. The initial scope is registered in
`docs/interface/ResearchBrief.md`; source papers and raw trace files are not yet
registered, while the existing research scaffold in `docs/00_research_charter.md`
through `docs/05_literature_survey.md` is active background material.

## Agent Roster

The deployed roster contains 24 roles per environment. The local skill manifest
contains 9 capsules: handoff audit, git worktree, tool trust, condensation,
prompt audit, scheme/code, paper writing, presentation deck, and presentation
illustration/readback.

## Remote Snapshot Sync

Shared metaprompts are imported from
`git@github.com:t0m0h1r0/research-agent.git` as an ephemeral remote snapshot.
The repository intentionally keeps no `prompts/upstream/` checkout. Generated
agents, skill capsules, templates, docs, and helper scripts are local derived
outputs, not upstream payloads.

Normal refresh:

```sh
make prompt-sync-dry-run
make prompt-sync
make prompt-deploy
make prompt-audit
```

The sync wrapper materializes only shared `kernel-*.md` files into
`prompts/meta/` and verifies that `prompts/meta/kernel-project.md` keeps the
same SHA-256 before and after sync. If sync writes
`prompts/REDEPLOY_REQUIRED.md`, remove it only after zero-base deployment and
prompt audit pass.

## Regeneration

For project retargeting, edit local `prompts/meta/kernel-project.md` and
regenerate `docs/03_PROJECT_RULES.md`, `docs/01_PROJECT_MAP.md`, `AGENTS.md`,
project-local skills/helpers/agents, and validation reports. Do not replace the
project profile unless the project is being intentionally re-onboarded. For
shared workflow changes, change the upstream `research-agent` repository first,
sync metaprompts here, then run prompt audit before using changed agents.
