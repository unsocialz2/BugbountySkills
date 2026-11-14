# API Rate Limiting — protected-invariant reasoning guide

Use this file when an API relies on request limits, attempt limits, quotas, or velocity controls to protect a concrete security or business invariant.

## Goal

Determine whether the service's **accounting key, bucket, window, or enforcement point** can be bypassed in a way that materially defeats the protection the application relies on.

Do not treat “I can send many requests” as a vulnerability by itself.

## Model the limit

For the action under test, identify:

- what behavior the limit protects: authentication attempts, recovery, enumeration, expensive action, financial/state change, quota, abuse prevention, etc.,
- what entity is counted: account, session, credential, token, IP, device, tenant, route, operation, or combination,
- when the counter increments and resets,
- whether equivalent routes/methods/versions share the same bucket,
- what response/state proves throttling actually occurred,
- whether the control is a documented product/policy requirement or only an assumed best practice.

The key question is: **does an attacker retain the protected capability beyond the limit the product is relying on?**

## Minimal hunt loop

1. Establish a low-volume baseline and observe the first clear throttling condition.
2. Record the counted identity/bucket as best as the evidence supports.
3. Change one accounting dimension at a time only when the architecture suggests it may create a separate bucket.
4. Compare semantic capability after the nominal threshold, not status codes alone.
5. Verify whether the protected operation actually continues to succeed.
6. Falsify benign explanations such as asynchronous counters, grace bursts, documented quotas, per-tenant allocation, client retries, or multiple intentionally independent buckets.

## High-signal questions

- Are equivalent operations counted separately because of route/version/method differences?
- Is the counter bound to a user-controlled identifier rather than the protected account/action?
- Do batched or bulk operations consume one unit while producing multiple protected effects?
- Do refresh/new-session flows reset an account-level security limit unexpectedly?
- Does a distributed/gateway/backend split create inconsistent accounting?
- Are failed and successful attempts accounted for according to the security invariant the product claims to enforce?

Do not flood or brute-force. Use the smallest number of requests needed to establish the accounting behavior, and obey program-specific rate/automation limits.

## Evidence contract

A strong finding should preserve:

1. protected action/invariant,
2. normal throttle baseline,
3. observed bucket/accounting key,
4. exact changed dimension,
5. proof that protected capability continues past the intended limit,
6. repeatability,
7. strongest benign explanation tested and rejected.

Numeric severity belongs to `reporting-mode` and depends on the action the limit protects.

## Stop conditions

Reject or narrow when:

- no concrete security/business action depends on the limit,
- the observed behavior is only a burst allowance or documented quota model,
- alternate buckets are intentionally independent and do not defeat an account/action-level invariant,
- semantic capability is still blocked even if response codes differ,
- confirming the hypothesis would require unsafe/noisy traffic beyond program rules.

## Cross-skill use

Use authentication/recovery skills when rate limiting is only one control inside a larger auth boundary. Use `race_conditions.md` when the issue is simultaneous state transition rather than accounting/velocity. Use GraphQL/gRPC-specific files only when protocol batching/streaming is actually relevant to the same protected operation.

## Discovery and experiment payloads — The protected counter, not request throughput

Examples below are synthetic request shapes, not discovered target endpoints.
Read policy first, substitute existing owned resources, and start with a normal
successful operation. A cheap discriminating discovery probe does not require a
previously confirmed vulnerability. No example has been replayed against an
external target by this revision.

| Question | Minimal control / probe | Protected or benign outcome to discriminate |
|---|---|---|
| Throttled baseline | Observe a known low-limit synthetic fixture before changing any request dimension | If the threshold cannot be established within program limits, mark it blocked; do not manufacture a burst. |
| Equivalent route bucket | After throttle on observed route X, make one equivalent request via documented route Y | Protected operation succeeding despite an intended shared limit matters; independent allocated quotas may be valid. |
| Session-reset accounting | An exhausted own-account bucket before/after a normal session refresh | Changing sessions must not increase guesses against a promised account limit; account rotation alone proves nothing about one victim. |
| Operation vs HTTP count | One operation vs two harmless aliased/batched operations in a fixture | Verify whether two protected effects consume the intended units; HTTP 200/429 alone is not an oracle. |
| Parallel counter window | Sequential smallest pair vs synchronized pair after a clear invariant exists | Use race methodology. Stop at minimum evidence and count committed effects, not success-looking replies. |

### Payload context

```json
{"operation":"redeem_test_credit","resource_id":"OWNED_ONE_USE_FIXTURE"}
```
This payload is a fixture shape. Prefer a sandbox operation whose configured
limit is small and whose effects are reversible. A fabricated forwarding header
must be justified by actual proxy trust evidence. There is no default 100-request
or 1000-request proof, no IP-rotation service requirement, and no brute-force
prescription. One admitted extra operation may prove accounting failure while
its real security impact remains a separate question.

### Evidence and reopening

Keep actor/role/tenant, exact request bytes, successful normal control, probe
response, authoritative readback or transient protected result, strongest benign
explanation, and remaining gap. Close only the tested relationship/representation;
reopen for an observed alternate consumer, changed lifecycle, repaired control, or
new source evidence. Absence of output is not evidence that processing never ran.

### Primary sources and applicability

Sources checked 2026-11-13 for mechanism/design support; they are not target
version or exploitability attestations. The experiment matrix is a synthesis.

- [PortSwigger authentication protections](https://portswigger.net/web-security/authentication/password-based) — attempt controls and authentication effects.
- [GraphQL security](https://graphql.org/learn/security/) — operation cost, breadth/batch and business-layer limits.
- [OWASP API4](https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/) — resource accounting context.
