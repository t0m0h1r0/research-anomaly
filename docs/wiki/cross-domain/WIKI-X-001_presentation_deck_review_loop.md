WIKI-ENTRY:
  ref_id: WIKI-X-001
  title: Presentation deck review loop for research briefs
  domain: cross-domain
  status: ACTIVE
  superseded_by: null
  sources:
    - path: paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_2_flair.md
      git_hash: 43929d5
      description: Theatrical treatment review that preserved non-claim guardrails.
    - path: paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_3_visual_consistency.md
      git_hash: 43929d5
      description: Visual consistency review that rejected abrupt background shifts.
    - path: paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_4_copy_consistency.md
      git_hash: 43929d5
      description: Japanese copy review for ambiguous deixis and mismatched contrast pairs.
    - path: paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_5_full_copy_review.md
      git_hash: 43929d5
      description: Whole-deck copy-system review.
    - path: paper/presentations/storage_embedded_ransomware_sponsor_brief/review_reports/round_6_diagram_clarity.md
      git_hash: 43929d5
      description: Diagram clarity review for architecture, AE candidates, and memory accounting.
    - path: docs/memo/researcharchitect_sponsor_deck_refresh_20260517.md
      git_hash: 43929d5
      description: Consolidated presentation refresh memo and QA record.
  consumers:
    - domain: A
      usage: Use before creating or reviewing a sponsor-facing research deck.
    - domain: M
      usage: Use as a workflow lesson for iterative artifact convergence.
  depends_on: []
  compiled_by: KnowledgeArchitect
  verified_by: WikiAuditor
  compiled_at: 2026-05-17
---

# WIKI-X-001 Presentation Deck Review Loop for Research Briefs

## Summary

For sponsor-facing research decks, treat each revision as a claim-and-proof
design problem, not as isolated slide cleanup. A polished deck converges faster
when every slide has one assertion, one proof object, and an explicit boundary
around what is not being claimed.

## Reusable Practices

1. Keep visual flair inside one coherent design system.
   Stronger contrast, larger lead lines, and editorial emphasis can help, but
   sudden full-slide background changes read as a broken narrative unless they
   mark a deliberate chapter break.

2. Put the slide's claim in visible language.
   A slide with attractive components still fails if the audience cannot answer
   "what should I believe after this slide?" in one sentence.

3. Review Japanese as a system, not as local phrases.
   Remove ambiguous demonstratives such as "この資料は" when the referent is not
   immediate. Contrast constructions must use categories that actually oppose
   each other, for example observation versus non-observation, judgment versus
   evidence, or shared weights versus per-volume state.

4. Make architecture diagrams read along one primary path.
   Separate observed inputs, derived features, model scoring, and excluded
   information. Avoid scattered panels that force the reader to infer which
   part of the diagram carries the claim.

5. Present model candidates as diagnostic probes.
   Do not list AE-01..05 as a catalog. State what changes between candidates
   and what each comparison reveals, such as compression sufficiency, need for
   temporal context, local temporal structure, or feature mixing.

6. Separate weights, state, and scratch memory.
   Memory-budget slides should distinguish shared model weights, per-volume
   detector state, shared runtime, and transient inference scratch. Use formulas
   when they clarify which term changes with model choice, volume count, or
   concurrent inference slots.

7. Preserve claim discipline with mechanical checks.
   Use explicit non-claim badges in the deck and grep the exported slide XML for
   forbidden deployment, performance, or readiness claims before final review.

8. Record convergence by round.
   Each review round should name the audience-facing failure mode, the repair,
   the render/layout result, and any remaining risk. Commit at round boundaries.

## Quick Checklist

- Does every slide have exactly one primary assertion?
- Does the main visual prove that assertion without requiring hidden context?
- Are visual mode changes intentional and consistent across the deck?
- Are contrast phrases grammatically and conceptually paired?
- Do diagrams label both the used signal and the excluded signal?
- Do model comparison slides explain what the comparison teaches?
- Do resource slides separate persistent state from transient scratch?
- Did export QA include layout checks and forbidden-claim search?

## Anti-Patterns

- Adding theatrical style by changing the whole background system mid-deck.
- Fixing only the phrases a reviewer named while leaving the same copy smell
  elsewhere.
- Drawing an architecture as many labeled objects instead of one readable path.
- Showing candidate names without explaining the experimental readout.
- Combining "model size", "detector data", and "runtime memory" into one vague
  budget number.
