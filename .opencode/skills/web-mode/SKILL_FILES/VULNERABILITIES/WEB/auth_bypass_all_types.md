# Authentication Bypass — reasoning guide

## Contents

- Goal
- Evidence contract
- Stop conditions
- Discovery probes and context-bound payloads
- Primary references

Use this file when evidence suggests the application may accept an unauthenticated or insufficiently authenticated actor as a stronger identity. Do not treat this as a generic 403-bypass or header/payload checklist.

## Goal

Identify the application's **authentication state machine** and determine whether any transition to an authenticated/privileged state can occur without satisfying the intended proof of identity.

Authentication bypass is about a broken identity proof or state transition, not merely receiving HTTP 200.

## Model the flow first

For the specific flow under test, map:

- actor state: logged out, partially authenticated, remembered device, password-verified, MFA-pending, fully authenticated, recovery state, SSO callback state, etc.
- credential/proof presented at each step,
- server-side session/token changes after each step,
- redirect/callback parameters and one-time state,
- which component enforces each check: edge/WAF, frontend, gateway, app, identity provider, backend service,
- the protected action/data that demonstrates successful authentication.

The useful question is: **what fact does the server trust as proof that a prior authentication step really happened?**

## Minimal hunt loop

1. Capture one normal control flow from unauthenticated to the strongest state legitimately available.
2. Identify the server-visible state transition at each step.
3. Change one assumption at a time: omit, replay, reorder, substitute, downgrade, cross-account swap, stale-state reuse, or alternate protocol/path only when the observed architecture makes it plausible.
4. Compare the resulting server-side identity and authorization state, not just status codes.
5. Confirm bypass by accessing an action/data set that genuinely requires the stronger identity.
6. Falsify benign explanations such as public fallback content, cached responses, frontend-only redirects, stale browser state, anonymous sessions, or an error body returned with 200.

## High-signal questions

Prefer questions derived from the application over generic tricks:

- Can step N be reached without a server record proving step N-1?
- Is a password/MFA/recovery result bound to the same account/session that consumes it?
- Can a proof generated for actor A be replayed or attached to actor B?
- Can a stale or parallel authentication flow overwrite a newer security state?
- Does a callback trust user-controlled identity/account fields rather than the verified identity from the IdP?
- Does an alternate endpoint/version enforce a weaker authentication precondition for the same protected action?
- Does the edge enforce something that the origin itself does not, creating a real parser/routing discrepancy?

Only investigate method/header/path/protocol normalization when evidence suggests multiple enforcement layers or routing disagreement. Do not spray bypass headers by default.

## Recovery, MFA, SSO and remembered-state boundaries

Treat these as distinct protocols. Record what binds each artifact to:

- account,
- session/browser,
- challenge,
- nonce/state,
- redirect URI/client,
- device,
- expiration/use count.

A weak binding is a candidate only if it can move an attacker into a stronger identity state.

For MFA, distinguish "primary credential accepted" from "fully authenticated". For SSO, distinguish identity-provider success from application account binding. For recovery, distinguish account discovery from actual control.

## Evidence contract

A validated auth bypass should show:

1. initial attacker state,
2. expected authentication prerequisite,
3. exact altered/missing/replayed transition,
4. server-side evidence of the stronger identity/session,
5. protected action/data proving the bypass,
6. a clean control where the prerequisite is enforced normally,
7. the strongest plausible benign explanation tested and rejected.

Do not score severity here; pass demonstrated access/impact facts to `reporting-mode`.

## Stop conditions

Reject or park when:

- only the HTTP status changes while the protected body/action remains unavailable,
- a frontend route is reachable but backend data/actions remain protected,
- behavior depends on the researcher's already-authenticated browser state,
- an alternate method/path returns generic/public content only,
- the observed difference is solely WAF/CDN behavior with no origin-side privilege change,
- the candidate cannot be reproduced from a clean-enough auth state.

## References on demand

Load protocol-specific material only when needed: OAuth/OIDC -> `oauth_misconfig.md`, SAML -> `saml_attacks.md`, MFA -> `2fa_mfa_bypass.md`, JWT -> `jwt_attacks.md`. Use payload/header/path reference material only after the architecture gives a concrete reason to test that differential.

## Discovery probes and context-bound payloads

A protected normal action is the anchor, not a prerequisite to noticing a suspicious flow.
Browse one successful login/recovery/SSO flow and mark where each proof becomes server state.
Choose the first reachable transition whose binding is unknown. These paths are schematic;
substitute the exact observed request, retain its CSRF/content-type requirements, and use owned accounts.

| Question | Minimal challenge and matched control | Protected result / interpretation |
|---|---|---|
| Does a pre-login session gain authority before final proof? | Save session S0; authenticate normally as control S1; call the same harmless identity/resource read with S0 alone. | S0 must not inherit S1's authenticated identity merely because both originated in one browser. |
| Is a proof bound to its account? | Obtain valid pending flows for owned A and B; send A's proof with B's observed flow ID; compare each normal pair. | Reject mismatch or preserve the proof's actual identity; displaying B in UI is insufficient. |
| Is an old security state accepted after an event? | Retain an owned session, perform explicit revoke/logout-all, then repeat one previously authorized read. | Apply documented revocation scope; distinguish app session, IdP session and access-token lifetime. |
| Does an alternate path enforce the same precondition? | Compare observed `/flow/finish` and a genuinely discovered legacy/mobile callback for the same normal operation. | Equal protected capability needs equivalent proof; different products are not valid controls. |
| Does a client hint select authority? | Change only observed `account_id` or `tenant_id` in a valid completed proof exchange. | Bind authority to verified subject and server-side relationship, not the hint. |

```http
POST /observed/auth/finish HTTP/1.1
Host: app.example.invalid
Content-Type: application/json

{"flow_id":"FLOW_B","proof":"PROOF_A"}
```

This is a binding-test shape, not a known endpoint or generic bypass payload.
Keep successful A/A and B/B controls, plus the mismatched A/B result and final protected read.
If proof is cryptographically bound inside an opaque object, field edits normally invalidate it;
that rejection only tests integrity, while swapping two intact legitimate artifacts tests binding.
A login-CSRF identity switch and authentication as another victim are different claims.
Use the browser flow, including required user action, before describing remote delivery.

## Source and version boundaries

Source guidance was reviewed on 2026-11-13. These experiments are original request-shape designs,
not claims of execution against a specific product. Re-check the deployed identity provider,
cookie policy and session semantics; a public bootstrap endpoint is not a failed auth check.

## Primary references

- [PortSwigger: Authentication](https://portswigger.net/web-security/authentication) — login mechanisms and application-side identity mistakes.
- [OWASP: Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) — reauthentication and recovery requirements.
- [OWASP: Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) — session transitions and invalidation.

## Scoped closure and reopening

Reopen for an observed alternate login/recovery channel, stronger successful control, new identity-binding consumer, or changed gateway/origin routing. A rejected transition only resolves that actor/state/route.
