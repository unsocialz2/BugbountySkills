# Capability links — sharing, invitations and scoped bearer authority

## Contents

- Distinguish discovery, identity and bearer authority
- Build owned capabilities and normal controls
- Differential experiments and PAYLOADS
- Reachability, disclosure and lifecycle evidence
- Source and version boundaries

## Distinguish discovery, identity and bearer authority

A share/download/reset/invitation link may intentionally grant authority to whoever possesses it.
Absence of login on such a link is not automatically missing authentication or IDOR.
Test whether the capability can be obtained, widened, substituted, retained or consumed outside
its intended object, action, identity, tenant, time or lifecycle scope.

Separate three claims:

1. **Discovery:** how an attacker naturally obtains the exact high-entropy capability.
2. **Authority:** what possession is intended to allow and which checks still apply.
3. **Misuse:** a demonstrated action outside that intended grant or a separate unauthorized disclosure.

Guessing a random nonexistent token and getting 404 tests neither entropy nor authorization.
Manually gifting yourself another user's token establishes possession, not attacker discovery.
A policy may accept certain public disclosures without replay; preserve that scope rather than
inventing a possession path or using a credential against policy.

## Build owned capabilities and normal controls

Use owned A/B resources with distinct `AUDIT_A`/`AUDIT_B` content.
Create a capability through the normal UI and record its grant parameters and consuming request.
Where supported, create view-only versus edit, single-object versus collection, invite versus download,
expiring versus indefinite, recipient-specific versus anyone-with-link variants.

Record:

- issuing actor, tenant and object; intended consumer and action;
- artifact type, opaque/signed fields and downstream redirects;
- creation, acceptance/consumption, expiration, revoke, membership and ownership events;
- cache/download behavior and whether material is intentionally a fixed snapshot;
- rate/usage limits only where they are part of the grant.

Use a fresh browser/client for possession-only controls and a valid intended recipient for
identity-bound controls. Preserve ordinary object ACL behavior separately from share-link behavior.

## Differential experiments and PAYLOADS

| Hypothesis | Minimal experiment and matched control | Expected protected behavior |
|---|---|---|
| Object substitution | Retain A's intact capability and change only a separate observed resource ID to owned B. | Capability cannot authorize B unless its documented scope includes B. |
| Action amplification | Use a view-only capability on a discovered update/comment/export action with a harmless marker. | Consumer enforces granted action, not merely token presence. |
| Parent/child scope escape | Use a collection/document grant with a child belonging to another owned parent. | Enforce containment or explicit relationship-based grant. |
| Invitation recipient binding | A issues invite to controlled mailbox B; attempt acceptance as owned C without B's required proof. | Apply product's recipient/account policy; some invitations are intentionally transferable bearer links. |
| Revoke/use boundary | Revoke an owned grant then consume it from a fresh isolated client. | Honor the advertised revocation semantics; an intentionally previously downloaded copy cannot be revoked. |
| Ownership or tenant change | Transfer an owned object or remove a member, then use the old grant. | Re-evaluate according to intended capability policy; member removal need not revoke all public shares. |
| Expiry or one-time use | Compare a fresh capability with an expired/consumed one on the same owned action. | Reject beyond the promised lifetime/usage; browser-cached content is not necessarily a new server disclosure. |
| Cross-purpose substitution | Submit an intact own invitation artifact at a discovered recovery/download consumer. | Reject wrong-purpose artifact even if signing keys or token format are shared. |

```http
GET /observed/download?object=OWNED_B&grant=INTACT_GRANT_FOR_A HTTP/1.1
Host: app.example.invalid
```

Change separate binding dimensions independently. An edited signed token usually fails its MAC;
that is not evidence about authorization of an intact grant to a different object.
For a view-only fixture, use an ordinary harmless title/comment marker as a permitted write probe;
verify the owner's authoritative view and restore it afterward.

```json
{"object_id":"OWNED_B","grant":"INTACT_VIEW_GRANT_A","title":"AUDIT_MARKER"}
```

Only use this shape when the observed application already accepts those fields for an actual action.
A reflected `title` without stored mutation or usable privilege is not action amplification.

## Reachability, disclosure and lifecycle evidence

If a capability appears in search/list/log/export output, prove which lower-privileged actor can
read that output and whether the capability still grants protected authority.
A source map mentioning a URL format does not reveal a real valid token.
A deliberate public share indexed by search may be intended; compare product settings and controls.

For claimed Referer leakage, capture the actual browser request and effective Referrer-Policy.
Modern cross-origin defaults often omit the path/query. Do not infer full-token leakage from an
external image/link alone. A server log sink needs demonstrated access by the claimed attacker.
Do not export live tokens to third-party collection services merely to create evidence.

Revocation, acceptance and export can race; inspect effects during the window as well as final state.
If a file was returned before revoke committed, establish ordering and the intended linearization point.
Route a concrete ordering hypothesis to `race_conditions.md`; do not call every delayed rejection a race.

## Evidence, closure and source boundaries

Preserve issuing/consuming context, intended grant, normal controls, exact cross-boundary request,
object/actor markers, final or transient semantic result and realistic token-discovery facts.
Report capability disclosure and scope enforcement as separate issues when only one is demonstrated.

Close only the tested grant kind/lifecycle/action. Reopen for another observed consumer or state.
Do not claim account takeover from a share link unless an independent account-control chain works.

Sources reviewed 2026-11-13. Capability semantics remain product-specific; these are original
synthetic differential designs, not claims that a particular token format is vulnerable.

## Primary references

- [PortSwigger: Access control](https://portswigger.net/web-security/access-control) — object and context-dependent authorization.
- [PortSwigger: Other authentication mechanisms](https://portswigger.net/web-security/authentication/other-mechanisms) — recovery artifacts as authentication capabilities.
- [OWASP: Forgot Password](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html) — expiry, one-time consumption, account binding and disclosure safeguards.
- [OWASP: Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) — scope/relationship checks independent of identifier format.
