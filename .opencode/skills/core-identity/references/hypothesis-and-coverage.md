# Hypotheses and experiment coverage

Use for a multi-step hunt, session handoff, or an apparent coverage gap. Keep artifacts in the current target workspace. Templates are repository-root `_template/HYPOTHESES.md` and `_template/COVERAGE.md`.

Start from a successful normal flow and identify who controls which object, who should authorize the action, what state changes, and how the result can be independently observed. If unavailable, record the precise prerequisite.

For ambiguous behavior, keep a small set of materially different explanations, including intended behavior. Rank them by evidence, feasible attacker advantage, access, and cost of discriminating tests. A hypothesis may span web/API/background processing; routing must not fragment the end-to-end feature.

An experiment should name its prediction and what result would falsify it. Vary one relationship or state where possible; multi-step logic tests may intentionally vary a sequence. Preserve controls, session validity, resource ownership, raw evidence references, and observed final state. Distinguish failed transport/tooling from a negative security result.

Coverage belongs to the tested tuple: actor/tenant, resource, action/representation, lifecycle state, and relevant version. Record a compact row per meaningful experiment or homogeneous batch; include exceptions instead of duplicating every request. No automatic Cartesian-product testing is required.

Evidence references must resolve to reviewable artifacts, not only conversational summaries. Apply `decision-checkpoint.md` before promotion, closure, or handoff. Keep historical tests, link superseding tests, and refresh current gaps when access changes.

A parked hypothesis needs a reason and reopening trigger: new role, reachable route, changed release, missing artifact, or a genuinely new discriminating test. Resume by reading these records, not re-running an old checklist.
