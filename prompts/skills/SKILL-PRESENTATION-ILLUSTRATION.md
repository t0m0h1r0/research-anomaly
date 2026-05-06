# SKILL-PRESENTATION-ILLUSTRATION

id: SKILL-PRESENTATION-ILLUSTRATION
purpose: Convert supported presentation messages into source-faithful conceptual illustration briefs with reverse-readback fidelity checks.
trigger:
- PresentationWriter needs a conceptual, painting-like, or abstract explanatory visual
- PaperReviewer audits whether a presentation image communicates the intended claim
- A visual draft needs reverse readback before acceptance
minimal_instruction: Start from lead_message and source_refs, then separate abstraction, concretization, illustration language, excluded meanings, and reverse_readback. Revise or downgrade to a diagram if the apparent message does not match the supported slide claim.
full_ref: prompts/meta/kernel-ops.md §VISUAL-CONCEPT-01
input_contract:
- slide id, lead message, and source references
- intended audience takeaway and excluded meanings
- visual role for each subject or scene element
- draft image or prompt when reverse readback is requested
output_contract:
- VisualConceptBrief with abstraction, concretization, positive/negative image language, and reverse_readback
- matches_lead verdict: PASS, PARTIAL, or FAIL
- revision_action: accept, revise_prompt, revise_concept, downgrade_to_diagram, or stop
forbidden_context:
- decorative visuals without claim map
- unsupported quantitative values, mechanisms, citations, dataset facts, or novelty claims
- relying on embedded text labels to carry the core idea
- accepting material FAIL after two revisions
success_metric:
- visual roles map to source elements
- reverse readback matches the slide lead or names residual gaps
- material illustration failures trigger revision or BLOCKED_REPLAN_REQUIRED with STOP-06
token_target: 220
