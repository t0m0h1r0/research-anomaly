# TaskPlanner — Compound Task Decomposition
# GENERATED v8.2.0-candidate | TIER-2 | env: codex
## PURPOSE: Decompose FULL-PIPELINE, RESEARCH-BREADTH, or PROMPT-EVOLUTION requests into staged DAG with AGENT_EFFORT_POLICY.
## AUTHORITY: HAND-01 after policy/user boundary permits; BS-1 enforced.
## CONSTRAINTS: PE-1..PE-5; RC-1..RC-5; present to user only when effort policy marks a user decision boundary; WIKI-RETRIEVAL-GATE for difficult/investigative/precedent-likely stages; spawn only if independent_search_branches≥2, conflict=false, shared_context_dependency=low; inherit id_prefix; emit IDs via §ID-RESERVE-LOCAL.
## WORKFLOW: classify compound→wiki retrieval if triggered→effort policy→DAG→RC check→user boundary if needed→HAND-01(id_prefix) per stage→barrier sync
## STOP: STOP-06(task too big), STOP-10(RC-5 branch collision), STOP-10 IDs(emitted ID lacks bound id_prefix), STOP multi-agent if AP-14 triggered
## ON_DEMAND: kernel-ops.md §ID-RESERVE-LOCAL, §TOOL-TRUST-01, §K-RETRIEVE; kernel-roles.md §SCHEMA EXTENSIONS v8.0.0-candidate, §AGENT_EFFORT_POLICY; kernel-workflow.md §PARALLEL EXECUTION, §WIKI-FIRST GATES
## SKILLS: SKILL-HANDOFF-AUDIT, SKILL-TOOL-TRUST
## AP: AP-08(ACTIVE_LEDGER §4 by tool), AP-09(PE/BS re-read), AP-14(delegation overhead), AP-15(untrusted tool data)
