# API Versioning — security-drift reasoning guide

Use this file when multiple discovered API versions or compatibility routes implement the same resource/action and may enforce different security guarantees.

## Goal

Determine whether a **reachable alternate version** exposes the same protected capability with weaker authentication, authorization, validation, lifecycle, or business-state enforcement.

Do not brute-force arbitrary version strings as the primary methodology.

## Build a version map from evidence

Prefer versions discovered from:

- current/old clients or mobile apps,
- OpenAPI/Swagger/docs,
- JavaScript bundles,
- traffic/history/archive artifacts,
- response links/errors/headers,
- target-local recon.

For each relevant version, map only the operation needed for the current question.

## Minimal hunt loop

1. Pick one security-sensitive operation that exists in the current version.
2. Establish its normal security behavior.
3. Identify a discovered alternate/legacy version implementing the same or equivalent operation.
4. Replay the minimum semantically equivalent test with the same actor/resource state.
5. Compare the security decision and durable result, not only schema/status differences.
6. Falsify intentionally different product semantics, deprecated read-only endpoints, test/sandbox environments, and unrelated resources sharing similar names.

## High-signal drift

Relevant differences may include:

- missing/weaker authentication,
- inconsistent object/function authorization,
- writable fields protected in the newer version,
- missing step-up or state prerequisites,
- weaker parser/validation path for the same business action,
- stale/revoked capabilities remaining valid only on the old path.

Rate limits or pagination differences are security-relevant only when they protect a concrete invariant or data boundary.

## Evidence contract

A strong finding should preserve:

1. discovered-version evidence,
2. equivalent operation/resource mapping,
3. current-version control,
4. alternate-version test,
5. exact security guarantee that differs,
6. semantic/durable impact,
7. strongest benign explanation tested and rejected.

## Stop conditions

Reject or narrow when:

- the alternate version was guessed but not meaningfully exposed/reachable,
- versions implement different products/resources rather than the same boundary,
- only formatting/schema/pagination differs,
- the legacy path is correctly disabled or preserves the same security decision,
- scope/rules exclude the alternate asset/version.

## Cross-skill use

Once version drift identifies the broken boundary, use the owning skill—authentication, authorization, mass assignment, business logic, parser/injection, or rate limiting—to validate that boundary. This file identifies **where policy drift exists**, not a separate exploit class.

## Discovery and experiment payloads — Equivalent capability across discovered versions

Examples below are synthetic request shapes, not discovered target endpoints.
Read policy first, substitute existing owned resources, and start with a normal
successful operation. A cheap discriminating discovery probe does not require a
previously confirmed vulnerability. No example has been replayed against an
external target by this revision.

| Question | Minimal control / probe | Protected or benign outcome to discriminate |
|---|---|---|
| Authz drift | Current A→D_B denial vs discovered legacy A→the same D_B | Prove resource identity and protected semantics, not just similarly named paths. |
| Writable property drift | Protected field on current PATCH vs observed legacy equivalent | Keep other input valid for each schema; an unsupported body is not an enforcement control. |
| Revocation drift | Revoked own grant/token on current path vs old download/preview endpoint | Record intended capability lifecycle and any result available in a transient window. |
| Alias/content negotiation | Documented version header vs path version with equivalent owned request | Header variants must actually select a different implementation; changed error formatting does not prove drift. |
| Environment confusion | Same record marker and tenant relation vs similarly named sandbox endpoint | An isolated sandbox containing researcher data is not production cross-tenant access. |

### Payload context

```http
GET /api/v2/documents/D_A HTTP/1.1
Host: api.example.invalid
Authorization: Bearer TOKEN_A

```
Compare only with a version actually found in client traffic/schema/archived
source. Translate valid field names while preserving the business action.
Version numbers are discovery hints; a deprecated banner or reachable OpenAPI
file alone is not the security finding. Do not claim applicability of a CVE
without its code/configuration and reachable attacker preconditions.

### Evidence and reopening

Keep actor/role/tenant, exact request bytes, successful normal control, probe
response, authoritative readback or transient protected result, strongest benign
explanation, and remaining gap. Close only the tested relationship/representation;
reopen for an observed alternate consumer, changed lifecycle, repaired control, or
new source evidence. Absence of output is not evidence that processing never ran.

### Primary sources and applicability

Sources checked 2026-11-13 for mechanism/design support; they are not target
version or exploitability attestations. The experiment matrix is a synthesis.

- [PortSwigger API testing](https://portswigger.net/web-security/api-testing) — API documentation and versions.
- [OWASP API9](https://api-security.owasp.org/editions/2023/en/0xa9-improper-inventory-management/) — inventory and deprecated deployments.
- [OWASP REST security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) — consistent endpoint protections.
