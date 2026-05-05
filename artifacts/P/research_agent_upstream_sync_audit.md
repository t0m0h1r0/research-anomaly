# Research-Agent Upstream Sync Audit

status: PASS
created_at_utc: 2026-05-05T08:07:00Z
owner: PromptArchitect

## Scope

Adapt this project to import shared meta prompts, JIT skill capsules, and
generated agent prompts from `git@github.com:t0m0h1r0/research-agent.git` while
preserving the project-local profile in `prompts/meta/kernel-project.md`.

## Upstream

| Field | Value |
|-------|-------|
| Remote | `git@github.com:t0m0h1r0/research-agent.git` |
| Revision | `4459e3e` |
| Sync marker | `prompts/upstream.toml` |
| Sync wrapper | `scripts/sync_research_agent.py` |
| Default groups | `kernel,skills,agents-codex,agents-claude` |

## Preservation Check

| File | Before SHA-256 | After SHA-256 | Verdict |
|------|----------------|---------------|---------|
| `prompts/meta/kernel-project.md` | `420eeca84c8d959a733312a33f725f279dbb291e9597b72bfec46ed753b43fa7` | `420eeca84c8d959a733312a33f725f279dbb291e9597b72bfec46ed753b43fa7` | PASS |

The upstream `templates/kernel-project.md` was not copied into the project.

## Verification

| Check | Command | Result |
|-------|---------|--------|
| Sync wrapper dry-run | `python3 scripts/sync_research_agent.py --dry-run` | PASS; fetched revision `4459e3e`, project profile preserved |
| Wrapper syntax | `python3 -m py_compile scripts/sync_research_agent.py` | PASS |
| Codex agents | `find prompts/agents-codex -maxdepth 1 -name '*.md' -type f \| wc -l` | 24 |
| Claude agents | `find prompts/agents-claude -maxdepth 1 -name '*.md' -type f \| wc -l` | 24 |
| Skill capsules | `find prompts/skills -maxdepth 1 -name 'SKILL-*.md' -type f \| wc -l` | 6 |
| Project rules | `rg -c '^## PR-' docs/03_PROJECT_RULES.md` | 6 |
| Project profile diff | `git diff -- prompts/meta/kernel-project.md` | empty |
| Redeploy marker | `test ! -e prompts/REDEPLOY_REQUIRED.md` | PASS |

## Notes

- New upstream assets include `PresentationWriter` for both environments and
  `SKILL-PRESENTATION-DECK.md`.
- Upstream revision `4459e3e` emits `prompts/REDEPLOY_REQUIRED.md` after sync;
  it was removed after this local redeploy/audit passed, as instructed by the
  marker.
- `prompts/README.md`, `AGENTS.md`, `docs/01_PROJECT_MAP.md`,
  `docs/02_ACTIVE_LEDGER.md`, `schema_resolution_report.json`, and
  `token_telemetry_report.json` were updated to reflect the imported upstream
  model.
- Future refreshes should use `make prompt-sync-dry-run` before
  `make prompt-sync`, followed by prompt audit and a coherent commit.
