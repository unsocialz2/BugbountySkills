# Business Logic Bugs — invariant-driven reasoning guide

## Contents

- Goal
- Evidence contract
- Stop conditions
- Discovery probes and context-bound payloads
- Primary references

Use this file when the application behaves correctly at the HTTP/security-control level but may allow a sequence or state that violates the product's intended business rules.

This skill should **increase creativity**, not reduce the hunt to a list of familiar bug patterns.

## Goal

Discover a state that the product considers impossible, unauthorized, economically invalid, or inconsistent — then prove an attacker can reach it through allowed-looking operations.

Do not begin from payloads. Begin from **actors, assets, state, transitions, and invariants**.

## Build the smallest useful model

For the feature under test, identify:

- **actors** — customer, guest, owner, collaborator, merchant, support/admin, external service, background worker, etc.
- **assets** — account, booking, order, balance, entitlement, collection, coupon, subscription, workflow object, approval, refund, quota, reputation, inventory.
- **states** — only the states relevant to the current flow.
- **transitions** — which action moves the asset from one state to another.
- **authority** — who is supposed to cause each transition.
- **invariants** — statements that should always remain true.

Examples of invariants are useful only as form, not as a checklist:

- an actor can modify only objects they are entitled to control,
- value cannot be created from nothing,
- a completed/revoked object cannot regain capabilities unexpectedly,
- one-time effects happen once,
- a later workflow step implies earlier prerequisites were satisfied,
- changing identity/ownership does not preserve privileges that belonged to the previous identity,
- two individually valid operations should not combine into an invalid state.

Write the target-specific invariant in your own words before testing it.

## Hunt from contradictions

Ask questions that challenge the product's assumptions:

1. What does component B assume component A already validated?
2. Which state is represented differently across frontend, API, worker, cache, payment provider, or another service?
3. Can two valid operations be ordered, repeated, interleaved, or performed by different actors to break an invariant?
4. What remains usable after cancel, revoke, transfer, downgrade, merge, logout, expiration, or completion?
5. Which identifier or state is trusted because the UI normally hides or sequences it?
6. Can a capability survive the lifecycle event that should have destroyed it?
7. Does the server derive ownership/price/role/state, or accept a client-supplied interpretation of it?
8. Are there parallel representations of the same business fact that can drift apart?

Let observed architecture choose the next question. Do not mechanically run negative-number, race, replay, coupon, or step-skip tests unless the flow makes them plausible.

## Minimal experiment design

For each hypothesis:

1. State the invariant you think may be broken.
2. Establish a normal control demonstrating the intended rule.
3. Change the minimum number of variables needed to challenge that rule.
4. Observe authoritative business state and meaningful effects during transient windows, not only the immediate response.
5. Verify downstream consequences from an independent read/view when possible.
6. Try the strongest benign explanation: eventual consistency, idempotent response, UI-only stale state, sandbox behavior, delayed rollback, intended sharing/delegation, or documented product behavior.
7. If state self-corrects, test whether any unauthorized read, completed action, or reusable capability occurred before rollback. Reject the transient-state hypothesis only when no meaningful attacker advantage is demonstrated; unresolved observability remains inconclusive.

## Cross-actor and lifecycle reasoning

Many high-value logic bugs appear at boundaries rather than within one request. Pay special attention when evidence shows:

- ownership changes,
- guest -> registered transitions,
- pre-action -> completed object transitions,
- invited/collaborator -> owner distinctions,
- trial -> paid -> downgraded states,
- pending -> approved/rejected transitions,
- external provider callbacks,
- asynchronous jobs,
- object cloning/import/export,
- account merge/link/unlink,
- cancellation/refund/rebooking flows.

Do not assume these are vulnerable; use them as prompts to inspect where invariants cross components.

## Impact reasoning

Describe impact as the broken business guarantee plus demonstrated attacker advantage:

- unauthorized control/access,
- durable entitlement gain,
- loss/creation/transfer of value,
- bypassed approval or policy state,
- cross-tenant/customer effect,
- irreversible or repeatable workflow corruption.

Avoid speculative financial numbers or severity labels during hunting. Quantify only what the evidence actually demonstrates.

## Evidence contract

A strong business-logic finding should preserve:

1. target-specific invariant,
2. normal/control flow,
3. minimal violating sequence,
4. actor/object identities relevant to the boundary,
5. authoritative post-condition or captured transient security effect proving the invalid state,
6. strongest benign explanation tested and rejected,
7. real attacker advantage/impact.

## Stop conditions

Park or reject when:

- behavior is documented/clearly intended,
- only the UI is inconsistent while authoritative state remains correct,
- a temporary state is rolled back before any attacker benefit,
- the hypothesis requires an unavailable privileged actor or impossible prerequisite,
- the effect is cosmetic or self-only with no meaningful security/business consequence,
- repeated testing produces no new evidence after the current time-box.

## Inspiration on demand

If the state model stalls, consult `references/business-logic-patterns.md` for historical invariant families as **inspiration only**. Choose a small justified set of families that match observed architecture, rewrite it as a target-specific invariant, and return to the evidence-driven experiment loop. Never treat the examples as the test plan.

## Discovery probes and context-bound payloads

Explore a small representative set of real feature transitions before demanding a known bug class.
A useful hypothesis describes a contradiction, for example: "a cancelled reservation creates more
credit than the original debit" or "a revoked viewer can start a new export." Select the next test
by what it distinguishes, not by its name. Keep multiple competing hypotheses when evidence warrants.

| Invariant and feature evidence | Minimal probe / matched control | Authoritative outcome |
|---|---|---|
| One cancellation causes one refund | On a sandbox/credit fixture, replay the same logical cancellation with the same key, then a fresh key. | One business effect regardless of retry representation; two HTTP successes may be idempotent. |
| Approval applies to the approved content | Approve owned draft revision R1, edit to R2, then perform the ordinary publish step. | Revalidate changed content or preserve approval only for R1; a stale badge alone proves nothing. |
| Owner transfer removes previous authority | Transfer an owned harmless document, then reuse old actor's observed share/export action. | Apply intended post-transfer policy; transfer need not remove separately granted collaboration. |
| Final amount derives from server state | Change one observed editable `quantity` to boundary value 0 on a non-chargeable fixture; compare 1. | Reject or normalize consistently; no actual purchase or speculative financial loss is needed for discovery. |
| Finalized objects cannot regain authority | Finish/cancel an owned workflow, then replay its earlier legitimate confirm request once. | No restored capability contrary to state rules; inspect worker/output as well as response. |
| Tenant move preserves isolation | Clone/import an owned record while changing only an observed parent reference to another owned tenant. | No hidden children/attachments/secrets travel without the corresponding authority. |

```json
{"revision_id":"OWNED_R2","approval_id":"APPROVAL_FOR_OWNED_R1"}
```

This is a revision-binding probe for an observed approve/publish feature, not an endpoint guess.
Use harmless content `AUDIT_MARKER`, read the published revision independently, and compare the
legitimate R1/R1 control. A product may intentionally approve a container rather than a revision;
establish the intended guarantee before calling the resulting publication unauthorized.

Observe both the final state and meaningful effects during intermediate windows.
An eventual rollback does not undo an already delivered private file or completed privileged action.
Conversely, a transient balance displayed in a stale UI without usable value is not financial impact.

## Source and version boundaries

Sources reviewed 2026-11-13. These are original invariant-driven experiment designs.
Use actual product documentation and normal controls for business intent. No finite checklist
establishes that all workflows are secure, and no accepted operation guarantees a bounty.

## Primary references

- [PortSwigger: Business logic](https://portswigger.net/web-security/logic-flaws) — cross-feature assumption and workflow failures.
- [PortSwigger: Smashing the state machine](https://portswigger.net/research/smashing-the-state-machine) — sub-states and cross-request interactions.
- [OWASP: Business Logic Security](https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html) — state machines, replay and authoritative value derivation.

## Scoped closure and reopening

Reopen for an observed retry/async/clone/import/share consumer, another ownership transition or a new state snapshot. A normal final state does not rule out protected reads or completed effects during an intermediate window.
