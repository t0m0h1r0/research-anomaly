# Research-Agent Submodule Prompt Sync Audit - f52ae6f

status: PASS
owner: PromptArchitect / PromptAuditor
created_at_utc: 2026-05-16T09:29:59Z
branch: codex/researcharchitect-prompt-submodule-20260516
upstream: git@github.com:t0m0h1r0/research-agent.git
submodule_path: prompts/upstream/research-agent
upstream_revision: f52ae6f
target_env: Codex

## PLAN

The user requested that agent metaprompts be taken in from the upstream
`research-agent` repository as a submodule, then refreshed to the latest
metaprompt revision and redeployed for Codex.

Project-local constraints preserved:

- `prompts/meta/kernel-project.md` remains local and unchanged.
- Upstream provides shared metaprompts only.
- Generated agents, skill capsules, docs, helper scripts, reports, and telemetry
  remain project-local derived outputs.
- No `main` merge was performed.

## EXECUTE

Added `research-agent` as a pinned submodule:

- `.gitmodules`
- `prompts/upstream/research-agent` at `f52ae6f`

Updated the local sync tooling:

- `scripts/sync_research_agent.py` now reads the pinned submodule instead of a
  temporary clone.
- `scripts/validate_prompt_deployment.py` now validates `git-submodule`
  distribution, the submodule path, wiki-packet telemetry, and dynamic agent
  count from `kernel-roles.md`.

Synced shared metaprompts from the submodule. Changed shared kernel files:

- `prompts/meta/kernel-antipatterns.md`
- `prompts/meta/kernel-deploy.md`
- `prompts/meta/kernel-roles.md`

Redeployed Codex-facing prompt artifacts for the new AP-17/wiki-packet audit
discipline:

- `prompts/agents-codex/_base.yaml`
- `prompts/agents-codex/ResearchArchitect.md`
- `prompts/agents-codex/PromptArchitect.md`
- `prompts/agents-codex/PromptAuditor.md`
- `prompts/agents-codex/ConsistencyAuditor.md`
- `prompts/agents-codex/KnowledgeArchitect.md`
- `prompts/agents-codex/Librarian.md`
- `prompts/agents-codex/WikiAuditor.md`
- `prompts/skills/SKILL-PROMPT-AUDIT.md`
- generated runtime docs and reports

## VERIFY

Commands run:

```sh
make prompt-sync-dry-run
make prompt-sync
python3 scripts/validate_prompt_deployment.py --allow-redeploy-marker --expected-revision f52ae6f
make prompt-audit
```

Verification summary:

| Check | Verdict |
|---|---|
| `kernel-project.md` preserved | PASS |
| Submodule present and pinned | PASS |
| `prompts/upstream.toml` records `git-submodule` and `f52ae6f` | PASS |
| Codex agent count matches `kernel-roles.md` profile table | PASS |
| Claude agent count remains valid for existing environment | PASS |
| 9 skill capsules present with required fields | PASS |
| `REDEPLOY_REQUIRED.md` removed only after audit-pass precheck | PASS |
| `schema_resolution_report.json` present | PASS |
| `token_telemetry_report.json` includes `skill_trigger_tokens` and `wiki_static_tokens` | PASS |
| `wiki_knowledge_injection_report.json` present | PASS |

The final `make prompt-audit` status was PASS.

The upstream `kernel-deploy.md` prose says "25 agent files", but
`kernel-roles.md §AGENT PROFILE TABLE` currently contains 24 concrete agent
rows. The local validator therefore treats the profile table as the operative
count and records 24/24 as PASS rather than inventing a non-existent role.

## AUDIT

No registered source PDFs or raw datasets were touched. No model-performance,
novelty, MNN readiness, device-fit, or deployment-readiness claim was promoted.

`docs/wiki/` is absent in this repository, so Stage 1b wiki packet distillation
was recorded as a waiver with `wiki_static_tokens = 0` in
`wiki_knowledge_injection_report.json` and `token_telemetry_report.json`.

The upstream submodule now contains a README recommendation to use a submodule
for receiving projects. This project keeps the submodule at
`prompts/upstream/research-agent` and materializes shared `kernel-*.md` files
into `prompts/meta/` so that the existing local `kernel-project.md` remains
project-owned.
