# GraphQL — compatibility route to schema/resolver security

Use [GraphQL schema and resolver methodology](../../../../api-mode/SKILL_FILES/VULNERABILITIES/API/graphql_introspection_attacks.md)
as the canonical guide. Schema discovery, operation authorization and batching belong there.
This compatibility entry preserves browser-specific distinctions without another payload dump.

## Browser entry and normal controls

Capture one actual query/mutation/subscription with its variables, auth state and effect.
An enabled introspection endpoint is inventory, not automatically sensitive-data exposure.
An `Upload` scalar does not establish unauthorized upload or executable serving.
Two aliases in one request are still subject to whatever object/field checks the resolver performs.

## PAYLOADS — controlled object authorization

Use a query already present in the client and substitute a second owned fixture ID:

```graphql
query Audit($id: ID!) {
  document(id: $id) { id title }
}
```

```json
{"id":"OTHER_OWNED_DOCUMENT"}
```

Prove the legitimate owner reads `AUDIT_B`, then test lower-authority A on the same real resolver.
Adapt names/types to the actual schema; an unknown-field or invalid-ID error is not an ACL control.
Do not request real customer fields to decorate the proof.

## Browser-only boundaries

A GET query returning email is not a demonstrated CSRF state change, and issuing it cross-origin
usually does not let the attacker's script read it. A read disclosure needs its own delivery/read
mechanism such as CORS or a proven cross-origin side channel.

For CSRF, identify a real mutation or other security-relevant side effect, an accepted browser-
producible method/content type, ambient credentials, and a working cross-site delivery PoC.
Servers that execute mutations via GET or simple form content types deserve specific investigation;
GET support or missing CSRF header alone is not sufficient.

Route that boundary to `csrf_all_types.md`; route response readability to `cors_misconfig.md`.
Keep resolver ACL, batch accounting, subscriptions and introspection coverage in the canonical file.

## Sources and limits

Sources reviewed 2026-11-13. The operation above is schematic and not an actual target schema.
Do not assign severity from the existence of GraphQL or claim aliasing itself bypasses authorization.

- [PortSwigger: GraphQL vulnerabilities](https://portswigger.net/web-security/graphql) — schema discovery, aliases, access control and browser delivery considerations.
- [OWASP: GraphQL](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html) — resolver authorization, query controls and batching boundaries.
- [OWASP: Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) — per-action/relationship checks underlying GraphQL operations.
