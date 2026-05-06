# SKILL-PRESENTATION-DECK

id: SKILL-PRESENTATION-DECK
purpose: Create research-grounded editable decks through staged planning, source-mapped slide messages, render review, talk-track alignment, and traceable explanatory visuals.
trigger:
- PresentationWriter receives a slide deck, talk deck, or paper-to-presentation task
- Paper/RevisionBrief/EvidencePackage must become audience-facing slides
- PaperReviewer reviews rendered presentation output
minimal_instruction: Build a PresentationDeckPlan first: audience context, source scope, narrative spine, reference schema, slide plan, editable production plan, and render-review checks. Give each slide one sourced lead message and use speaker notes as spoken complement rather than duplicate text.
full_ref: prompts/meta/kernel-ops.md §PRESENTATION-GEN-01
input_contract:
- paper/source or paper/sections paths
- signed RevisionBrief or EvidencePackage when claims go beyond source summary
- audience, venue/language, and slide/time budget when known
output_contract:
- deck outline/source under `paper/presentations/{deck_id}/`
- PresentationDeckPlan with source_scope, narrative_spine, slide_plan, production_plan, and render_review
- narrative spine: audience problem -> paper insight -> evidence -> implication
- slide source map, lead list, visual plan, speaker-note intent, and message budget
- rendered-review notes covering content fidelity, design coherence, readability, cognitive load, talk-track alignment, and source trace
best_practices:
- start from audience context, preference/template signals, and source scope
- enforce slide/time budget; move derivations, caveats, and secondary details to notes/backup
- one claim per slide; lead is larger than labels/captions/notes
- visual hierarchy: lead -> visual -> labels -> source note
- prefer editable/programmatic slide sources; avoid flattening the entire deck into images unless explicitly requested
- prefer diagrams/charts/timelines/mechanisms/comparisons over dense bullets
- preserve uncertainty, assumptions, limits, and cited quantitative/novelty/benchmark claims
- audience check: what remains after 30 seconds, 5 minutes, and the ending?
review_criteria:
- content fidelity, design coherence, readability, cognitive load, talk-track alignment, source trace, and audience recall
forbidden_context:
- claims remembered from conversation but not present in artifacts
- unverified SOTA, novelty, benchmark, or numerical claims
success_metric:
- each slide has lead, visual, source refs, one message, and a role in the spine
token_target: 220
