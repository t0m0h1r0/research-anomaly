# Research-Agent Upstream Sync Audit c985b65

status: PASS
created_at_utc: 2026-05-06T03:50:05Z
owner: PromptArchitect

## Scope

Adopt the authoritative upstream metaprompt revision `c985b65` from
`git@github.com:t0m0h1r0/research-agent.git`, preserve the local
`prompts/meta/kernel-project.md`, and redeploy project-local generated prompts,
skill capsules, runtime docs, schema report, and token telemetry.

## Upstream

| Field | Value |
|-------|-------|
| Remote | `git@github.com:t0m0h1r0/research-agent.git` |
| Revision | `c985b65` |
| Upstream HEAD | `origin/HEAD -> origin/main` |
| Sync marker | `prompts/upstream.toml` |
| Managed marker | `prompts/upstream-managed.json` |
| Distribution mode | metaprompt-only; generated artifacts are project-local |

## Preservation Check

| File | SHA-256 | Verdict |
|------|---------|---------|
| `prompts/meta/kernel-project.md` | `420eeca84c8d959a733312a33f725f279dbb291e9597b72bfec46ed753b43fa7` | PASS |

## Verification

| Check | Command | Result |
|-------|---------|--------|
| Sync wrapper dry-run | `make prompt-sync-dry-run` | PASS; fetched revision `c985b65`, project profile preserved |
| Sync wrapper apply | `make prompt-sync` | PASS; synced kernel metaprompts only and emitted redeploy marker |
| Pre-removal audit | `python3 scripts/validate_prompt_deployment.py --allow-redeploy-marker --expected-revision c985b65` | PASS |
| Helper syntax | `python3 -m py_compile scripts/sync_research_agent.py scripts/lock.py scripts/atomic_push.py scripts/validate_prompt_deployment.py` | PASS |
| Prompt audit | `make prompt-audit` | PASS |
| Codex agents | `prompts/agents-codex/*.md` | 24 |
| Claude agents | `prompts/agents-claude/*.md` | 24 |
| Skill capsules | `prompts/skills/SKILL-*.md` | 9 |
| Project rules | `docs/03_PROJECT_RULES.md` | 6 PR rules |
| Redeploy marker | `prompts/REDEPLOY_REQUIRED.md` | removed after audit PASS |

## Redeploy Notes

- New upstream prompt logic renames the implementation domain from `R` to `L`
  and introduces role-relevant JIT skill loops for scheme/code, paper writing,
  presentation generation, and presentation illustration/readback.
- The local skill manifest now contains 9 capsules and all required capsule
  fields passed validation.
- `token_telemetry_report.json` now records Q3b `skill_trigger_tokens` as a
  separate prompt-size proxy.
- No files under `paper/source/` or `data/raw/` were changed.
