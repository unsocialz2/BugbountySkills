# Decision checkpoint

Use before marking a hypothesis disproven/confirmed, claiming enforcement, promoting a finding, or producing a session summary. Review only decisive experiments and summary claims; do not require a dossier for every reconnaissance request.

## Evidence that survives the conversation

Link a target-local experiment record or an accessible saved transcript section. `_template/EXPERIMENT.md` is an optional shape. Include actor/role/tenant labels, resource ownership and state, the valid control, exact relevant request/response or runtime evidence, and how the result was interpreted. For source review, retain repository commit, file/line, data flow, and reachability limits. A screenshot can support UI observations but cannot establish unseen server behavior. Redact credentials and unnecessary personal data; scope rules govern what may be retained.

Before cleanup, preserve the permitted minimal proof and the cleanup outcome. Deleted test objects should not erase the only evidence. Never reconstruct missing raw responses from memory; mark historical observations unverified and record what artifact is missing. Retest only if the unresolved decision justifies it and scope permits it.

## Calibrate the conclusion

| Observation | Supported conclusion | What remains unresolved |
|---|---|---|
| Random UUID gives 404 | That request returned not found | Access to an existing controlled resource by the wrong actor |
| Known owned resource succeeds, controlled peer request is denied | Enforcement for that actor/resource/action/state | Other roles, representations, and lifecycle states |
| Unauthenticated request gives explicit session error | Request rejected without a session | Cross-account enforcement and other routes |
| UI shows an upgrade prompt | UI gates this interaction | Server-side entitlement enforcement |
| WAF/challenge prevents reaching application flow | Current test path blocked | Application logic behind the block |
| Marker absent from inspected response | No reflection observed there | Other sinks, stored/DOM behavior, different contexts |
| Metadata marks N workflows public | N workflows are configured as public | How many were reached, executed, or caused an effect |
| Unsigned webhook returns 200 | Handler returned success to that input | Verification, no-op behavior, processing, state effects |
| Scan output is empty | No records in the artifact | Completion, input coverage, tool/template failures |

Do not require a privileged account for every useful observation. Separate what a denial directly proves from what needs a successful control. A meaningful positive control and authoritative outcome are needed for stronger boundary claims.

## Use stable verdicts

Coverage verdicts are `not-tested`, `blocked`, `inconclusive`, `enforced-in-tested-case`, or `boundary-failure`. Put “no reflection observed,” “intended public behavior,” and other observations in the result/reason field, not custom verdicts. For demonstrated intended access with no crossed boundary, explain that the vulnerability hypothesis is disproven; do not pretend that unrestricted access itself demonstrates enforcement. If the experiment does not resolve the specific boundary question, keep its coverage inconclusive and retain the explanation.

Hypothesis status and coverage verdict serve different purposes. A hypothesis may be parked for cost, scope, or access without being disproven. A finding may be closed as out of scope without a claim that the behavior is secure.

## Handoff check

1. Check each material summary claim against an existing evidence location and its valid control.
2. Carry forward exact tested boundaries; remove class-wide negatives unsupported by coverage.
3. Reconcile current access/blockers with later experiments. Preserve old rows with a superseded-by link instead of erasing history.
4. Tie each count to the artifact version/run used. Report missing run provenance explicitly.
5. Keep unresolved hypotheses, why they were parked, and their reopening conditions visible.
6. Choose the next feature/experiment from evidence; state the specific benefit of any requested prerequisite and compare a reachable alternative.

If a check fails, narrow the claim or record the gap. Do not block all useful work, invent evidence, or rerun everything merely to fill a template.
