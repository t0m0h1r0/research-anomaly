# SKILL-SCHEME-CODE

id: SKILL-SCHEME-CODE
purpose: Guide scientific scheme and code decomposition, SchemeCodePlan creation, executable candidate evaluation, and verifier-gated handoff.
trigger:
- CodeWorkflowCoordinator scopes numerical or research-code work
- CodeArchitect designs or implements computational schemes
- CodeCorrector repairs numerical logic or scientific-code failures
- TestRunner verifies code that changes numerical behavior
minimal_instruction: Before implementation, write or update a SchemeCodePlan with scientific background, input/output contracts, scheme choices, invariants, candidate/evaluator budget, and verification plan. Accept generated code only after unit tests plus at least one scientific verification case when numerical behavior changes.
full_ref: prompts/meta/kernel-ops.md §SCHEME-CODE-01
input_contract:
- task id, equations or source references, assumptions, units, and expected invariants
- implementation paths and forbidden paths
- resource budget for candidate variants and test runs
- acceptance metrics, tolerances, and regression cases
output_contract:
- SchemeCodePlan or verifier report
- bounded implementation diff or diagnosis tied to declared paths
- command logs, tolerance results, residual risks, and PASS/FAIL/INCONCLUSIVE verdict
forbidden_context:
- benchmark-only acceptance without local scientific checks
- unrelated infrastructure optimization while changing numerical logic
- unbounded candidate search without executable evaluator metrics
- generated code accepted by inspection alone
success_metric:
- tests and scientific verification cases support the claimed behavior
- implementation remains within declared diff scope
- verifier report includes commands, tolerances, logs, and residual risks
token_target: 240
