# SKILL-PAPER-WRITING

id: SKILL-PAPER-WRITING
purpose: Guide research-grounded manuscript planning, claim registers, focused feedback, bounded revision, and AI-use transparency.
trigger:
- PaperWriter drafts, expands, rewrites, or substantively revises manuscript prose
- PaperWriter handles related-work, abstract, or response-to-review writing
- PaperReviewer audits manuscript source fidelity or content-focused feedback
minimal_instruction: Create a ManuscriptSectionPlan before drafting or revising: record author key points, source scope, claim register with allowed strength, paragraph outline, focused feedback questions, bounded revision actions, and transparency record.
full_ref: prompts/meta/kernel-ops.md §PAPER-WRITE-01
input_contract:
- target paper/sections path or requested section id
- source materials with line/section scope
- author perspective, key points, venue/audience, and exclusions when available
- signed RevisionBrief or EvidencePackage when claims go beyond background framing
output_contract:
- ManuscriptSectionPlan or concise equivalent in the produced artifact
- bounded prose patch or reviewer findings tied to section/paragraph ids
- claim register entries with source refs, scope limits, and allowed strength
- AI-use transparency record when AI-assisted prose is produced
forbidden_context:
- conversation-only claims
- unsupported broadening of cited work
- style-only feedback when content fidelity is at issue
- silently rewriting neighboring sections outside the dispatched scope
success_metric:
- every material claim is source-mapped, scoped, and no stronger than its evidence
- focused feedback identifies actionable content gaps or unsupported leaps
- revision actions stay within the requested section
token_target: 220
