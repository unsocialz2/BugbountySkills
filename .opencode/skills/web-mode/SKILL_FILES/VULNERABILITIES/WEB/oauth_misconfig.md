# OAuth / OIDC Misconfiguration — protocol-binding reasoning guide

## Contents

- Goal
- Evidence contract
- Stop conditions
- Discovery probes and context-bound payloads
- Primary references

Use this file when the application relies on OAuth/OIDC/social login/SSO and evidence suggests a mismatch between authorization artifacts, browser state, client identity, redirect handling, or local account binding.

## Goal

Determine whether the application or authorization server accepts an OAuth/OIDC result outside the **client, redirect, browser flow, identity, scope, audience, or local-account context** it was intended for.

Do not reduce OAuth testing to redirect mutation or assume every protocol weakness ends in account takeover.

## Map the normal flow

Record the smallest useful sequence:

- authorization endpoint / issuer,
- client identifier,
- redirect/callback destination,
- response type / flow,
- state and nonce behavior where applicable,
- PKCE behavior and downgrade protection for the applicable client/flow,
- authorization-code/token exchange component,
- verified identity claims consumed by the application,
- local-account link/merge decision,
- final session/account state created by the application.

The central question is: **what exactly binds the returned authorization result to the browser flow, client, identity, and local account that consumes it?**

## Minimal hunt loop

1. Capture one normal login/authorization flow end to end.
2. Identify one protocol guarantee the application depends on.
3. Change one binding assumption at a time only when the observed deployment makes that change meaningful.
4. Verify the result at the application session/account level, not only at the authorization-server response.
5. Falsify benign explanations such as provider-side rejection, intentionally broad redirect registration, already-linked identity, cached login state, or a callback that fails before session creation.
6. Compare another evidence-backed binding when useful; a correctly protected callback does not establish every binding.

## High-signal boundaries

Reason about these only when present:

- redirect/client binding,
- state/nonce/transaction correlation,
- authorization-code lifecycle,
- PKCE and downgrade protection for the deployed flow,
- issuer/audience/client confusion,
- scope/resource confusion,
- local-account link/merge/unlink behavior,
- alternate mobile/SPA/legacy/enterprise flows,
- email/subject assumptions when mapping an external identity to a local account.

## Account binding

Treat identity-provider success and local-account ownership as separate steps.

Ask:

- Which provider claim is authoritative: issuer+subject, email, phone, tenant, or another identifier?
- Is that claim verified by the provider before the app trusts it?
- Can two different external identities map to the same local account unexpectedly?
- Does linking/unlinking require an appropriately strong existing session?
- Can a stale/parallel authorization flow bind the wrong identity to the current browser session?

## Evidence contract

A strong finding should preserve:

1. normal protocol flow,
2. expected binding/guarantee,
3. exact altered assumption,
4. authorization-server result where relevant,
5. application-side session/account result,
6. actor/account identity evidence,
7. negative/control path,
8. strongest benign explanation tested and rejected.

Numeric severity belongs to `reporting-mode`.

## Stop conditions

Reject or narrow when:

- only a provider error/redirect changes,
- the application never creates or alters a protected session/account state,
- the altered artifact is correctly rejected at exchange/callback time,
- the tested identity was already legitimately linked,
- behavior is intentionally allowed and does not cross a security/account boundary.

## References on demand

Use `references/oauth-oidc-patterns.md` for protocol-family inspiration only after the normal deployment is mapped. Use `account_takeover_chains.md` only if a confirmed protocol weakness creates a real account-control path.

## Discovery probes and context-bound payloads

First identify whether the application is an OAuth client, authorization server, resource server,
or more than one. Follow a normal owned authorization flow through final application identity.
Keep intact artifacts for binding tests; modifying signed identity claims only tests integrity.

| Binding | Minimal challenge and matched control | Expected protected behavior |
|---|---|---|
| Browser transaction | Start owned flows in isolated browsers A/B; deliver an intact callback from A to B once. | No unintended login/link result in B without the mechanism binding that transaction. |
| Code to client | Redeem a code at the observed token endpoint with the other owned registered client, preserving its legitimate auth method. | Reject wrong-client redemption; no confidential secret guessing. |
| PKCE | For a code legitimately issued with S256 challenge, use a wrong verifier versus the real one in separate fresh flows. | Wrong verifier rejected; a code is typically one-use, so do not invalidate the positive control by replaying it. |
| PKCE downgrade | Only where allowed and controlled, compare a no-challenge authorization transaction to the client's normal PKCE transaction. | No acceptance that lets an attacker inject their code into another flow; absent `state` alone is not proof. |
| Issuer mix-up | With two legitimately available issuers, exchange the expected issuer/callback transaction while keeping signed artifacts intact. | Issuer identity and endpoint selection remain bound; arbitrary fake issuer errors are inconclusive. |
| Account linking | Start local A's link flow, consume owned external B's authorization result from a mismatched local session. | Link only to the authorized local account and verified issuer+subject. |
| Scope/resource | Compare intact tokens from two owned grants of different intended scopes/resources. | The protected action checks granted authority, not the client's requested text alone. |

```text
/observed/callback?code=OWNED_CODE_A&state=STATE_B
```

The callback shape is illustrative, not a claim that `state` is the sole protection.
PKCE or OIDC nonce and server-side transaction binding can supply relevant protection in the
correct design; follow RFC 9700 rather than reporting missing parameters in isolation.
Use exact registered researcher-controlled redirect destinations when testing client registration.
A redirect open at one hop does not prove a token reaches it: check code binding, fragment handling,
redirect revalidation, browser behavior and the ability to redeem the actual artifact.

## Source and version boundaries

Sources reviewed 2026-11-13. PKCE guidance applies to web clients as well as native/public clients;
precise requirements vary by flow. OIDC identity requires the applicable ID-token checks, including
issuer, audience and nonce where supplied; email equality is not issuer+subject equivalence.
The matrix is an original test design, not executed product exploit evidence.

## Primary references

- [PortSwigger: OAuth vulnerabilities](https://portswigger.net/web-security/oauth) — callback, redirect and account-binding attack surfaces.
- [IETF: RFC 9700](https://datatracker.ietf.org/doc/html/rfc9700) — PKCE, mix-up, redirect and authorization-response protections.
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html) — issuer, subject, nonce and ID-token validation.

## Scoped closure and reopening

Reopen for another supported client/issuer/response mode, a stale parallel login, a link/unlink transition or a new token consumer. A provider error cannot close an application account-binding question.
