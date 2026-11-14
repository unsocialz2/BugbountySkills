# API Mass Assignment — writable-field authority reasoning guide

Use this file when an API accepts object-like input and may bind client-supplied fields directly to server-side models or state.

## Goal

Determine whether the client can write a field whose value should be **derived, protected, role-gated, server-owned, or immutable**.

Do not equate “undocumented field accepted” with a vulnerability unless it changes protected state or authority.

## Model the object boundary

For the relevant resource, identify:

- fields the client is expected to control,
- fields returned but intended read-only,
- server-derived identity/tenant/owner fields,
- role/security/status/financial fields,
- create-only vs update-only vs immutable fields,
- schema/OpenAPI/GraphQL hints where available,
- authoritative post-write state.

## Minimal hunt loop

1. Capture a normal create/update request and response.
2. Compare visible response/schema fields with writable input fields.
3. Select one field whose authority is security-relevant and plausibly mapped by the backend.
4. Add/change that field while keeping the request otherwise valid.
5. Re-read the resource independently to confirm authoritative state.
6. Falsify ignored/echo-only fields, client-side display artifacts, asynchronous rollback, or a field the current actor is legitimately allowed to set.

## High-signal questions

- Does the server derive owner/tenant/role/status, or accept a client interpretation?
- Are read-only fields actually write-protected?
- Do create, PUT, PATCH, and bulk-update paths expose different writable sets?
- Does nested input update related objects or security-sensitive subfields unexpectedly?
- Do GraphQL input types or alternate API versions expose fields hidden by the normal client?

## Evidence contract

A strong finding should preserve:

1. actor/resource context,
2. protected field and intended authority,
3. normal control request,
4. altered request,
5. authoritative persisted state,
6. resulting capability/impact,
7. negative/falsification control.

Numeric severity belongs to `reporting-mode`.

## Stop conditions

Reject or narrow when:

- the field is ignored or only echoed,
- the actor is intended to control the field,
- the change does not persist or affect authoritative state,
- only cosmetic/client-local behavior changes.

## Cross-skill use

Use `api_authorization_bypass.md` when the primary issue is which actor may mutate the object, and `business_logic_bugs.md` when the field change violates a broader workflow/business invariant.

## Discovery and experiment payloads — Input authority, including nested objects

Examples below are synthetic request shapes, not discovered target endpoints.
Read policy first, substitute existing owned resources, and start with a normal
successful operation. A cheap discriminating discovery probe does not require a
previously confirmed vulnerability. No example has been replayed against an
external target by this revision.

| Question | Minimal control / probe | Protected or benign outcome to discriminate |
|---|---|---|
| Echo vs authority | Update a normal display field, then append one known read-only field | Use an independent GET/action to distinguish reflected input from authoritative changes. |
| Read-only security flag | Known own fixture verified=false control vs verified=true with the same normal update | Prove the actual entitlement or verification-gated action; a JSON echo is insufficient. |
| Create vs update | Observed create and PATCH input shapes for the same record type | A create-only field may legitimately be immutable on update; identify the intended guarantee. |
| Nested relationship | A-owned attachment owner field vs B-owned relationship reference | Do not mistake a nested BOLA issue for mere extra-field acceptance; record each binding. |
| Bulk/upsert drift | Single normal update vs a documented bulk/upsert of one owned record | Test one record first. Validate returned success against actual state and lifecycle restrictions. |

### Payload context

```json
{"display_name":"AUDIT_MARKER"}
```
```json
{"display_name":"AUDIT_MARKER","verified":true}
```
`verified` is a synthetic example, not a field to inject everywhere. Use a real
schema/response hint. First test the field's current value, then one meaningful
change only if allowed. Keep balance/role mutations in a disposable fixture or
explicit program-approved test workflow. BOPLA also includes over-readable
properties; response-field exposure belongs to authorization analysis.

### Evidence and reopening

Keep actor/role/tenant, exact request bytes, successful normal control, probe
response, authoritative readback or transient protected result, strongest benign
explanation, and remaining gap. Close only the tested relationship/representation;
reopen for an observed alternate consumer, changed lifecycle, repaired control, or
new source evidence. Absence of output is not evidence that processing never ran.

### Primary sources and applicability

Sources checked 2026-11-13 for mechanism/design support; they are not target
version or exploitability attestations. The experiment matrix is a synthesis.

- [PortSwigger API testing](https://portswigger.net/web-security/api-testing) — hidden fields and mass assignment.
- [OWASP mass assignment](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html) — binders, DTOs and allowed input properties.
- [OWASP API3](https://api-security.owasp.org/editions/2023/en/0xa3-broken-object-property-level-authorization/) — read/write object-property authorization.
