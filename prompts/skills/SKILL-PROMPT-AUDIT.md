# SKILL-PROMPT-AUDIT

id: SKILL-PROMPT-AUDIT
purpose: Audit project-local generated prompts for Q3-AUDIT compliance, upstream-only boundary, rule bloat, JIT discipline, and token ROI.
trigger:
- PromptAuditor receives generated prompt artifacts
- EnvMetaBootstrapper Stage 4 or Q3b Token Telemetry Gate
- AP-13 suspicion
minimal_instruction: Verify the 13 Q3-AUDIT items, reject copied upstream generated artifacts, reject duplicated operation bodies, reject broad skill preloading, require role-relevant SkillID/RULE_MANIFEST references, and check static_prompt_tokens, loaded_rule_tokens, and skill_trigger_tokens.
full_ref: prompts/meta/kernel-deploy.md §Stage 4
input_contract:
- generated agent prompt paths
- prompts/skills paths
- prompts/upstream.toml and prompts/upstream-managed.json
- token_telemetry_report.json
forbidden_context:
- PromptArchitect reasoning
- previous generated prompt transcripts
- unlisted draft prompts
success_metric:
- Q3-AUDIT 13-item verdict
- upstream-only distribution boundary recorded
- duplicate-rule scan recorded
- prompt-load ROI verdict recorded
- token telemetry gate result recorded, including skill_trigger_tokens or waiver rationale
token_target: 150
