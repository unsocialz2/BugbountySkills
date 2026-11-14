# API Authorization — actor/resource/action reasoning guide

Use this file when the API authenticates the caller but may enforce ownership, tenant, role, relationship, or function-level permissions incorrectly.

## Goal

Determine whether the server enforces **which authenticated actor may perform which action on which resource**.

Do not reduce BOLA/BFLA testing to changing identifiers or comparing status codes.

## Build the minimum matrix

For the current question, record:

```text
ACTOR A: <role/account/tenant>
ACTOR B: <other role/account/tenant>
RESOURCE A: <owned/accessible by A>
RESOURCE B: <owned/accessible by B>
ACTION: <read/update/delete/export/share/approve/...>
```

Establish normal controls, then change one actor/resource/action relationship at a time.

## Reason from the authorization source

Ask:

- What server-side fact should authorize this action: ownership, membership, tenant, role, capability, relationship, workflow state?
- Where is that fact derived: session/token claims, database relation, route parent, body field, cached relation, service-to-service context?
- Is the decision applied consistently across CRUD actions and alternate representations?
- Do collection/list/export/share endpoints expose or grant a stronger capability than object endpoints?
- Can parent/child identifiers disagree and escape tenant/ownership binding?
- Do old/alternate API versions or GraphQL/gRPC operations reach the same resource through a different policy path?

## Minimal hunt loop

1. Choose one resource/action boundary.
2. Prove allowed behavior for the rightful actor.
3. Change exactly one actor/resource/role relationship.
4. Verify semantic result: protected data returned, state changed, action executed, or capability granted.
5. Re-read authoritative state independently when possible.
6. Falsify public/shared resources, intended collaboration, stale cache, aliases, soft-deleted visibility, or misleading 2xx/error bodies.
7. Expand only when a real boundary failure or shared policy path is established.

## Horizontal, vertical, contextual

Keep distinct:

- **horizontal**: wrong peer owner/tenant,
- **vertical**: weaker role invokes stronger function,
- **contextual**: action allowed only in a particular relationship/workflow state.

The identifier format is secondary; discoverability is not the same as authorization.

## Evidence contract

A strong finding should preserve:

1. actor/resource/action matrix,
2. normal control,
3. cross-boundary request/result,
4. semantic proof of unauthorized capability,
5. ownership/tenant/role evidence,
6. independent state verification where relevant,
7. one falsification/negative control.

Numeric severity belongs to `reporting-mode`.

## Stop conditions

Reject or narrow when:

- the resource/action is intentionally shared/public to that actor,
- only identifier predictability is shown,
- status changes without protected semantic success,
- the actor already has a legitimate relationship granting access,
- an apparent mutation produces no authoritative state change.

## Cross-skill use

Use `api_mass_assignment.md` when the issue is writable fields rather than actor/resource permission, `api_versioning_attacks.md` when policy drift is version-specific, and `business_logic_bugs.md` when workflow invariants—not simple ownership/role—define the boundary.

## Discovery and experiment payloads — Resource graph and tenant authority

Examples below are synthetic request shapes, not discovered target endpoints.
Read policy first, substitute existing owned resources, and start with a normal
successful operation. A cheap discriminating discovery probe does not require a
previously confirmed vulnerability. No example has been replayed against an
external target by this revision.

| Question | Minimal control / probe | Protected or benign outcome to discriminate |
|---|---|---|
| Peer read | A→DOC_A and B→DOC_B controls; A→DOC_B test | Only the rightful actor sees its distinctive synthetic marker; public/shared grants are separate controls. |
| Parent/child conflict | /tenants/T_A/docs/D_A control vs /tenants/T_A/docs/D_B | A child must remain bound to its authoritative owner/tenant, independent of the route hint. |
| Reference substitution on writes | A PATCH to A-owned draft with B-owned attachment ID vs A attachment | Check actual attachment ownership and read back both objects; an ignored field is not a write. |
| Representation asymmetry | Direct protected read vs an observed preview/export/share representation | A previous direct 403 does not answer the other capability. Follow job/result/download if the flow is asynchronous. |
| Permission transition | Before/after share revocation or role downgrade, using the same owned resource | Measure retained capability and product-intended bearer-link semantics; possession of a share token may be deliberate. |
| Collection/filter policy | A exact read denial vs a small list/filter restricted to DOC_B | Filtering and field selection must not widen authorization; one already-public field is not private object disclosure. |

### Payload context

```http
GET /api/tenants/T_A/documents/D_A HTTP/1.1
Host: api.example.invalid
Authorization: Bearer TOKEN_A

```
Use existing owned controls to change only the child to `D_B`, then test an
observed alternate representation. Keep A/B actors and synthetic content
unambiguous. An administrative account is not a low-privilege control.

### Evidence and reopening

Keep actor/role/tenant, exact request bytes, successful normal control, probe
response, authoritative readback or transient protected result, strongest benign
explanation, and remaining gap. Close only the tested relationship/representation;
reopen for an observed alternate consumer, changed lifecycle, repaired control, or
new source evidence. Absence of output is not evidence that processing never ran.

### Primary sources and applicability

Sources checked 2026-11-13 for mechanism/design support; they are not target
version or exploitability attestations. The experiment matrix is a synthesis.

- [PortSwigger access control](https://portswigger.net/web-security/access-control) — horizontal, vertical and contextual boundaries.
- [OWASP API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/) — object-level checks.
- [OWASP REST security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) — endpoint/method access control.
