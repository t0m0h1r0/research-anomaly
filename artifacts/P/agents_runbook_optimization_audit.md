# AGENTS Runbook Optimization Audit

owner: ResearchArchitect
branch: codex/optimize-codex-config
worktree: /private/tmp/research-anomaly-codex-config
date: 2026-05-04
status: PASS

## PLAN

- Make `AGENTS.md` useful as the first file an external agent reads.
- Keep it short enough to be remembered during execution.
- Avoid duplicating full kernel rules that already live under `prompts/meta/`.

## EXECUTE

- Reorganized `AGENTS.md` around read order, operating loop, source integrity,
  artifact routing, claim gates, Python experiment requirements, and the default
  planning task.
- Updated `prompts/README.md` to list `AGENTS.md` as runtime working memory and
  describe its intended scope.
- Updated `prompts/meta/kernel-deploy.md` with the AGENTS profile rule and a
  validation check for the runbook.

## VERIFY

Commands run from `/private/tmp/research-anomaly-codex-config`:

- `rg -n "Read First|Operating Loop|Source Integrity|Artifact Routing|Claim Gates|Python Experiments|Default Planning Task" AGENTS.md`
- `rg -n "AGENTS.md|AGENTS profile rule|AGENTS runbook present" prompts/README.md prompts/meta/kernel-deploy.md`
- `git diff --check main..HEAD`

## AUDIT

Verdict: PASS.

- `AGENTS.md` now exposes the repository's high-risk defaults: read the ledger
  first, preserve source/raw data, route artifacts by domain, commit coherent
  checkpoints, and never merge to `main` without explicit user instruction.
- The guide points to source-of-truth files instead of becoming a second full
  rulebook.
- Source directories `paper/source/` and `data/raw/` were not modified.
