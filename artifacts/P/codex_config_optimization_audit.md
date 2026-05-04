# Codex Config Optimization Audit

owner: ResearchArchitect
branch: codex/optimize-codex-config
worktree: /private/tmp/research-anomaly-codex-config
date: 2026-05-04
status: PASS

## PLAN

- Optimize Codex-side settings without expanding every generated agent prompt.
- Preserve worktree isolation, source integrity, explicit merge gating, and compact prompt inheritance.
- Verify that prompt counts and basic deployment invariants remain intact.

## EXECUTE

- Added `runtime_profile`, `git_policy`, and `prompt_budget_policy` to
  `prompts/agents-codex/_base.yaml`.
- Extended `prompts/meta/kernel-deploy.md` with Codex runtime emphasis and a
  profile rule that keeps shared Codex defaults in `_base.yaml`.
- Left individual generated Codex role prompts unchanged.

## VERIFY

Commands run from `/private/tmp/research-anomaly-codex-config`:

- `ruby -e "require 'yaml'; YAML.load_file('prompts/agents-codex/_base.yaml'); puts 'yaml ok'"` -> `yaml ok`
- `grep -c '^## PR-' docs/03_PROJECT_RULES.md` -> `6`
- Codex generated prompt compactness check -> `files=23`, `max_lines=16`
- Skill capsule count check -> `5`
- `rg` check confirmed `runtime_profile`, `git_policy`, and
  `prompt_budget_policy` are present in Codex base/deploy guidance.

## AUDIT

Verdict: PASS.

- Generated Codex role prompts remain compact and untouched.
- The new defaults encode existing project policy: worktree-first material work,
  coherent checkpoint commits, explicit user approval before main merge, no-ff
  merge method when requested, and continuing in the same worktree after merge.
- Tool and external-output trust boundaries remain active via existing
  `TOOL_TRUST_BOUNDARY`; the optimization does not relax evidence requirements.
- Source integrity is unaffected; no files under `paper/source/` or `data/raw/`
  were modified.

Residual risk: no automated EnvMetaBootstrapper script was present in the repo,
so validation used direct schema/count checks rather than a full regeneration
pipeline.
