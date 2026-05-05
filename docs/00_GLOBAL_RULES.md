# GENERATED - do NOT edit directly. Edit prompts/meta/kernel-*.md and regenerate.

# 00_GLOBAL_RULES - Generic Research Agent Kernel

## §A Core Axioms

- Truth before action: agents act on evidence, not belief.
- External memory first: durable state lives in files, git history, and artifacts.
- Fix at source: contradictions are resolved in the owning domain.
- Stateless agents: no result may depend on hidden conversation memory.
- Bounded autonomy: autonomy is earned through evidence and gates.
- Single source of truth: shared rules originate upstream and materialize in
  `prompts/meta/`; project rules live in `prompts/meta/kernel-project.md`.
- Broken symmetry: executor and auditor are separate for material outputs.
- Source integrity: source artifacts are immutable unless the user explicitly replaces them.
- Domain sovereignty: each artifact has one owning domain.
- Diff-first change control: changes should be reviewable and scoped.
- Knowledge-first retrieval: reusable findings are compiled into `docs/wiki/`.

## §C Research Implementation Rules

- C1: Keep reusable research code modular, tested, and documented.
- C2: Preserve existing behavior unless the task explicitly changes it.
- C3: Every numerical or symbolic check must record command, inputs, and outputs.
- C4: Do not substitute a model, approximation, or shortcut without a signed theory/evidence note.
- C5: Test output is evidence; interpretation must cite the output path.
- C6: Inconclusive verification is a valid result when stated precisely.

## §P Paper Rules

- P1: Claims must trace to proof, evidence, or explicit assumption.
- P2: Notation must be consistent across source, memo, and revision.
- P3: Reviewer-facing prose should be concise and defensible.
- P4: Paper edits require a revision brief unless the edit is purely typographic.

## §Q Prompt Rules

- Q1: Agent prompts contain role, scope, STOP conditions, output contract, and JIT refs.
- Q2: Full operation syntax belongs in kernel files or skill capsules.
- Q3: Prompt changes require leakage, upstream-boundary, and token-budget checks.
- Q4: Workflow lessons can justify kernel changes only after evidence is recorded.

## §AU Audit Rules

- AU1: Audit checks artifact evidence, not hidden reasoning.
- AU2: Cross-domain consistency is required before VALIDATED state.
- AU3: Contradiction findings are useful outputs and must not be buried.

## §GIT Lifecycle

Use branch or task isolation for material work. Merge only after owning Gatekeeper
and ConsistencyAuditor pass, or after explicit user approval.

## §P-E-V-A Execution Loop

PLAN -> EXECUTE -> VERIFY -> AUDIT. FAST-TRACK may collapse phases only when no
material claim, evidence, code, or paper section changes.
