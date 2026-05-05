# Research-Agent Upstream Sync Audit

status: PASS
created_at_utc: 2026-05-05T10:50:00Z
owner: PromptArchitect

## Scope

Adapt this project to upstream revision `8abd3a7`, which distributes only shared
metaprompts. Project-local skill capsules, helper scripts, runtime docs, and
generated agent prompts were redeployed locally while preserving
`prompts/meta/kernel-project.md`.

## Upstream

| Field | Value |
|-------|-------|
| Remote | `git@github.com:t0m0h1r0/research-agent.git` |
| Revision | `8abd3a7` |
| Sync marker | `prompts/upstream.toml` |
| Managed marker | `prompts/upstream-managed.json` |
| Sync wrapper | `scripts/sync_research_agent.py` |
| Default groups | `kernel` |
| Distribution mode | metaprompt-only; generated artifacts are project-local |

## Preservation Check

| File | Before SHA-256 | After SHA-256 | Verdict |
|------|----------------|---------------|---------|
| `prompts/meta/kernel-project.md` | `420eeca84c8d959a733312a33f725f279dbb291e9597b72bfec46ed753b43fa7` | `420eeca84c8d959a733312a33f725f279dbb291e9597b72bfec46ed753b43fa7` | PASS |

The upstream `templates/kernel-project.md` was not copied into the project.

## Verification

| Check | Command | Result |
|-------|---------|--------|
| Sync wrapper dry-run | `make prompt-sync-dry-run` | PASS; fetched revision `8abd3a7`, project profile preserved |
| Wrapper/helper syntax | `python3 -m py_compile scripts/sync_research_agent.py scripts/lock.py scripts/atomic_push.py scripts/validate_prompt_deployment.py` | PASS |
| Codex agents | `find prompts/agents-codex -maxdepth 1 -name '*.md' -type f \| wc -l` | 24 |
| Claude agents | `find prompts/agents-claude -maxdepth 1 -name '*.md' -type f \| wc -l` | 24 |
| Skill capsules | `find prompts/skills -maxdepth 1 -name 'SKILL-*.md' -type f \| wc -l` | 6 |
| Project rules | `rg -c '^## PR-' docs/03_PROJECT_RULES.md` | 6 |
| Project profile diff | `git diff -- prompts/meta/kernel-project.md` | empty |
| Upstream boundary | `make prompt-audit` | PASS; upstream marker says generated artifacts are project-local |
| Redeploy marker | `test ! -e prompts/REDEPLOY_REQUIRED.md` | PASS |

## Notes

- Upstream revision `8abd3a7` emits `prompts/REDEPLOY_REQUIRED.md` after sync;
  it was removed after this local redeploy/audit passed, as instructed by the
  marker.
- The sync wrapper default was changed from `kernel,skills,agents-codex,agents-claude`
  to `kernel`, matching the upstream distribution contract.
- `prompts/README.md`, `AGENTS.md`, `docs/01_PROJECT_MAP.md`,
  `docs/02_ACTIVE_LEDGER.md`, `schema_resolution_report.json`, and
  `token_telemetry_report.json` were updated to reflect the imported upstream
  model.
- `scripts/lock.py`, `scripts/atomic_push.py`, and
  `scripts/validate_prompt_deployment.py` are local helper artifacts; they were
  not copied from upstream.
- Future refreshes should use `make prompt-sync-dry-run` before
  `make prompt-sync`, followed by prompt audit and a coherent commit.
