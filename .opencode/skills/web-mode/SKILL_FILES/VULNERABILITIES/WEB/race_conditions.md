# Race Conditions — concurrency and invariant reasoning guide

## Contents

- Goal
- Evidence contract
- Stop conditions
- Discovery probes and context-bound payloads
- Primary references

Use this file when a security/business invariant may depend on the ordering or atomicity of two or more valid operations.

## Goal

Determine whether concurrent execution can produce a state that **cannot be produced by the same operations sequentially** and that gives a meaningful attacker advantage.

Do not assume every check-then-act flow is exploitable, and do not default to a fixed number of parallel requests or a specific transport trick.

## Identify the invariant first

Write the expected rule in target-specific terms, for example:

- one capability can be consumed once,
- balance/inventory/quota cannot be spent twice,
- only one conflicting state transition may commit,
- ownership/role checks and mutation must refer to the same authoritative state.

Then identify the operations that may contend on that invariant.

## Minimal hunt loop

1. Establish a stable **sequential control** showing the intended result.
2. Identify the smallest pair/group of operations that could overlap on the same state.
3. Synchronize only enough to test that specific overlap.
4. Compare final authoritative state and any meaningful effect during the window with both relevant sequential orderings.
5. Repeat to establish reproducibility and distinguish a real race window from retries/eventual consistency.
6. Verify downstream effect from an independent read or ledger/state view when possible.
7. Falsify benign explanations such as idempotent responses, duplicate UI messages, delayed rollback, queue retries, non-authoritative caches, or intentionally multi-use capabilities.

## Concurrency model

Choose synchronization based on the observed stack rather than habit:

- same connection vs multiple connections,
- HTTP/1.1 vs HTTP/2,
- browser/UI concurrency,
- asynchronous jobs or webhook delivery,
- two different actors/sessions,
- read-check-write vs write-write conflicts.

The transport technique is secondary; the security claim is the broken invariant.

## Sub-state / TOCTOU reasoning

High-signal questions include:

- Is authorization/eligibility checked before the state that it depends on can change?
- Can one operation invalidate a condition while another still commits based on the old state?
- Are two services/transactions using different snapshots of the same business fact?
- Does a temporary intermediate state expose a capability that should not be externally reachable?

## Evidence contract

A strong race finding should preserve:

1. target-specific invariant,
2. sequential control,
3. concurrent operation set and synchronization method,
4. authoritative final state or a captured transient disclosure/unauthorized action,
5. attacker advantage,
6. reproducibility rate or enough repeated evidence to establish the condition,
7. strongest benign explanation tested and rejected.

Do not assign numeric severity here.

## Stop conditions

Reject or narrow when:

- only response ordering changes while authoritative state remains correct,
- duplicate responses map to one committed effect,
- state self-corrects before any attacker advantage exists,
- the behavior is explained by documented eventual consistency,
- the result cannot be reproduced beyond ordinary network/retry noise.

## Tools on demand

Use synchronized-request tooling only after the invariant and control are clear. The exact tool or transport should be chosen to match the observed application stack; it is not part of the vulnerability definition.

## Discovery probes and context-bound payloads

Notice coupled operations while browsing normally: check→write, reserve→confirm, generate→send,
create→initialize and revoke→consume. A known primitive is not required to form a race hypothesis.
Choose one concrete invariant and a controlled fixture before scheduling concurrent requests.

| Candidate window | Smallest discriminating experiment | Control / false-positive test |
|---|---|---|
| Single-use capability consumption | Send two valid consumes together on an owned synthetic capability. | Sequential consumes should produce one effect; count committed effects rather than success-looking replies. |
| Multi-endpoint authorization change | Coordinate revoke and preview on one owned fixture with two controlled actors. | Run both sequential orders; access completed before revocation can be legitimate, so demonstrate an invalid linearization or defined revocation breach. |
| Approval then mutation | Coordinate content update R1→R2 with publish using approval for R1. | Compare fixed R1/R1 and invalid sequential R2/R1; inspect actual published revision. |
| Partial construction | Create a harmless account/object while requesting its already observed capability before initialization finishes. | Prove ordinary initialized policy and ensure temporary default does not intentionally grant that capability. |
| Async proof delivery | On owned email/test sink, overlap two change-confirmation flows with distinct markers. | Verify which address/account receives each proof, then which state it actually authorizes. |
| Retry-key race | Concurrently submit one logical operation under same versus different idempotency keys. | Same-key dedup can work while resource-level once-only semantics fail under fresh keys; establish both requirements. |

```json
{"fixture_id":"OWNED_FIXTURE","request_key":"AUDIT_K1"}
```

Use the exact observed request twice initially, changing the key only in a separate experiment.
Warm connections when transport setup dominates; choose HTTP/2 single-packet synchronization,
last-byte synchronization or small grouped requests according to the stack. HTTP/2 multiplexing
alone does not prove simultaneous backend execution, and a chosen request count is not universal.
Respect the program's concurrency/volume limits; do not solve timing uncertainty with a flood.

Save request IDs/timestamps and the independent state or event trace that reveals the conflict.
A race can disclose a secret or authorize an action during a temporary state even if the final
state repairs itself. Capture that bounded semantic effect; permanent mutation is not mandatory.
If no observable effect distinguishes the tested ordering, mark that experiment inconclusive;
reopen for a different valid actor/transition/window rather than declaring all races absent.

## Source and version boundaries

Sources reviewed 2026-11-13. Synchronization is a technique, not an exploit result.
The probes are original fixture designs; they were not executed against an external target here.

## Primary references

- [PortSwigger: Race conditions](https://portswigger.net/web-security/race-conditions) — prediction, probing and controlled concurrent experiments.
- [PortSwigger: Smashing the state machine](https://portswigger.net/research/smashing-the-state-machine) — multi-endpoint and partial-construction races.
- [OWASP: Business Logic Security](https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html) — atomicity and one-time business effects.
