# Anomaly Detection Agent Deployment Report

created_at_utc: 2026-05-04T04:21:54Z
status: SUCCESS

## Summary

The generic research-agent kernel was deployed into this repository and
retargeted to storage-embedded ransomware anomaly detection. The project profile
now binds agent work to the existing research scaffold: block-I/O observation,
10-second statistics, memory-aware AutoEncoder candidates, MNN CPU inference,
and a 500 KB model-side memory budget.

## Produced Artifacts

| Artifact | Status |
|----------|--------|
| `prompts/meta/kernel-project.md` | updated project-specific source of truth |
| `prompts/meta/kernel-*.md` | deployed generic kernel files |
| `prompts/agents-codex/` | deployed Codex agent prompts |
| `prompts/agents-claude/` | deployed Claude agent prompts |
| `prompts/skills/` | deployed skill capsules |
| `docs/00_GLOBAL_RULES.md` | deployed global runtime rules |
| `docs/01_PROJECT_MAP.md` | generated project map |
| `docs/02_ACTIVE_LEDGER.md` | generated live state ledger |
| `docs/03_PROJECT_RULES.md` | generated project rule digest |
| `docs/interface/ResearchBrief.md` | signed active brief |
| `AGENTS.md` | external-agent instructions |
| `schema_resolution_report.json` | deployment schema report |
| `token_telemetry_report.json` | prompt-size telemetry report |

## Validation Summary

| Check | Result |
|-------|--------|
| Project rules count | PASS |
| Agent files per environment | PASS |
| Skill capsule count | PASS |
| HandoffEnvelope reference | PASS |
| Source preservation | PASS, no source PDF or raw dataset registered yet |
| Runtime docs present | PASS |

## Next Action

Dispatch `ASM-RAD-001` to TaskPlanner and produce
`docs/memo/ransomware_anomaly_problem_frame.md`.
