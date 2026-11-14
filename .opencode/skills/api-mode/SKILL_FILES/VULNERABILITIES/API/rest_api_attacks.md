# REST API Security — resource and representation reasoning guide

Use this file when the target exposes REST-like resources and the question depends on how HTTP methods, routes, representations, query controls, or resource relationships map to backend security decisions.

## Goal

Understand the **resource/action model** first, then route each security question to the smallest owning methodology.

REST mechanics are not vulnerabilities by themselves. Method, content-type, pagination, filter, and field-selection differences matter only when they cross a real security boundary.

## Map the resource surface

For the current feature, record:

- resource and identifier/relationship,
- routes and discovered versions representing it,
- methods with real semantic meaning,
- accepted request/response representations,
- actor/auth state,
- parent/tenant relationships,
- query controls such as filter/sort/fields/pagination only where they influence protected data/state,
- authoritative read-back path after mutation.

## Minimal hunt loop

1. Capture one legitimate operation.
2. State the security guarantee under test: authentication, authorization, writable fields, workflow invariant, parser differential, version drift, or injection sink.
3. Change one REST dimension only if it can plausibly reach the same backend capability through a different enforcement path.
4. Verify semantic data/state/action, not status codes or response shape alone.
5. Re-read authoritative state after mutations.
6. Falsify documented alternate representations, public data, no-op methods, schema coercion, cached results, and endpoints that only look equivalent.
7. Hand the confirmed hypothesis to the owning deep-dive rather than continuing generic REST fuzzing.

## High-signal differentials

Use only when the architecture supports them:

- equivalent methods with inconsistent middleware,
- JSON/form/XML/multipart paths handled by different parsers,
- parent/child route forms with different authorization context,
- current vs legacy version of the same operation,
- collection vs individual resource views,
- filter/sort/field selection exposing data beyond the actor's authorized set,
- pagination/limits defeating a concrete data/abuse boundary rather than merely allowing a large response.

## Handoff map

- caller identity / missing auth -> `api_authentication_attacks.md`
- ownership/role/tenant/function boundary -> `api_authorization_bypass.md`
- server-owned fields writable by client -> `api_mass_assignment.md`
- old/current policy drift -> `api_versioning_attacks.md`
- focused parser/method/type variation -> `api_fuzzing_methodology.md`
- rate/velocity accounting -> `api_rate_limiting_bypass.md`
- workflow/business invariant -> `web-mode` business-logic methodology when the key boundary is the product state machine
- exact injection payload -> owning injection skill + `payloads` after a concrete sink exists

## Evidence contract

For a REST-specific differential, preserve:

1. same resource/action mapping,
2. control representation/path/method,
3. changed REST dimension,
4. exact security decision that differs,
5. semantic/durable result,
6. strongest benign explanation tested and rejected.

## Stop conditions

Reject or narrow when:

- only response format/status changes,
- routes/methods represent different legitimate operations,
- broader pagination or field selection still respects the actor's authorization boundary,
- content-type differences only change validation/errors,
- no protected data/action/state becomes available.

This file is a router for REST-specific ambiguity, not a generic exploit checklist.

## Discovery and experiment payloads — Representation and operation mapping

Examples below are synthetic request shapes, not discovered target endpoints.
Read policy first, substitute existing owned resources, and start with a normal
successful operation. A cheap discriminating discovery probe does not require a
previously confirmed vulnerability. No example has been replayed against an
external target by this revision.

| Question | Minimal control / probe | Protected or benign outcome to discriminate |
|---|---|---|
| Path vs body relationship | Normal /tenant/T_A/doc/D_A update vs body reference to owned fixture B | Identify which authoritative relation controls the action; record object/parent policy separately. |
| PUT/PATCH semantics | Observed partial update vs full replacement on one disposable record | Omitted fields can legitimately differ; test security defaults/read-only bindings with valid method controls. |
| Representation parser | Normal JSON vs an actually supported form/XML representation | Change body encoding with Content-Type. Wrong Content-Type and invalid bytes test rejection only. |
| List/single read asymmetry | Own list and direct read vs small filter selecting known B-owned fixture | Ensure pagination/filter fields remain within authorized records and distinguish public from private properties. |
| Retries/idempotency | One sandbox transaction vs same key/same payload then same key/different payload | Compare committed state and product key scope. HTTP method idempotence does not require identical response bodies. |

### Payload context

```http
PATCH /api/documents/D_A HTTP/1.1
Host: api.example.invalid
Authorization: Bearer TOKEN_A
Content-Type: application/json

{"title":"AUDIT_MARKER"}
```
Preserve the actual observed valid route/body/authentication. A method advertised
by OPTIONS does not establish that its protected implementation executed. HTTP
200 can contain a business error; HTTP 202 can mean only queued acceptance.
Follow processing to the protected read or final effect without demanding
unnecessary destructive mutation.

### Evidence and reopening

Keep actor/role/tenant, exact request bytes, successful normal control, probe
response, authoritative readback or transient protected result, strongest benign
explanation, and remaining gap. Close only the tested relationship/representation;
reopen for an observed alternate consumer, changed lifecycle, repaired control, or
new source evidence. Absence of output is not evidence that processing never ran.

### Primary sources and applicability

Sources checked 2026-11-13 for mechanism/design support; they are not target
version or exploitability attestations. The experiment matrix is a synthesis.

- [PortSwigger API testing](https://portswigger.net/web-security/api-testing) — methods, formats and endpoint discovery.
- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110) — method semantics, representations and idempotence.
- [OWASP REST security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) — endpoint security and content types.
