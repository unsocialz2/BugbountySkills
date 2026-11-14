# Session lifecycle — rotation, revocation and authority continuity

## Contents

- Model credentials and product guarantees
- Discovery and clean controls
- Differential experiments and PAYLOADS
- Browser and distributed-state interpretation
- Evidence and primary references

## Model credentials and product guarantees

Test whether an actor retains, transfers or gains application authority across an event that
should change that authority. Session expiry, logout, token refresh, account recovery, role removal
and IdP logout are different protocols; do not assume they invalidate exactly the same credentials.

Capture normal login, one harmless protected read, explicit logout and subsequent rejection.
Identify each credential separately: app cookie, bearer access token, refresh token, remembered-device
cookie, IdP session, personal access token, API key and signed download capability.
A browser can silently refresh or perform SSO after logout; isolate credentials before interpreting it.

Write the actual guarantee under test, for example:

```text
EVENT: owner explicitly revokes session S1
EXPECTED: S1 may no longer read private fixture AUDIT_A
CONTROL: S1 reads it before revoke; independent S2 remains authorized if revoke is session-specific
TEST: replay exact S1 credential alone after authoritative revoke confirmation
```

A missing "logout all devices" feature is not the same as a broken implemented revoke function.
Do not promote a preference for stricter revocation into a product policy without evidence.

## Discovery and clean controls

Observe cookie/token changes through unauthenticated, primary-authenticated, MFA/step-up,
role-changing and logged-out states as available. Name the authority at each state, not only cookie bytes.
A token staying identical does not prove fixation; the server may change its associated state safely.
Likewise, a rotated token does not prove the old one is invalid.

Use two separate controlled sessions and synthetic data. Retain old credentials only for the
explicit experiment and redact them from evidence exports. Remove accidental fallback credentials
from the replay client. Distinguish successful normal access from cached browser rendering.

## Differential experiments and PAYLOADS

The route shapes are schematic; use actual observed login/session management requests.

| Boundary | Minimal experiment and control | Expected protected behavior |
|---|---|---|
| Fixation across login | Establish whether attacker can implant known S0 by a real supported external path; log owned victim A in; replay S0 alone from isolated client. | No victim authority through attacker-known pre-auth credential. DevTools manually setting A's cookie proves no delivery. |
| Explicit session revoke | Revoke owned S1 via S2, confirm management response/state, repeat a protected read with S1 only. | S1 loses the authority covered by revoke; record any documented propagation window and its consequences. |
| Logout versus refresh | Log S1 out then attempt ordinary refresh with S1's retained refresh credential once. | No re-creation of revoked authority if logout promises that; distinguish short-lived access-token policy. |
| Password recovery | Complete owned password recovery, then compare old app session and old refresh token under stated recovery policy. | Apply intended post-recovery invalidation; a separate retained IdP session is a separate boundary. |
| Role/membership removal | Owner removes viewer B, then B reuses old session and an observed export/WS subscription. | Enforce updated authority on later effects when product policy requires it; snapshot shares may intentionally differ. |
| Step-up lifetime | Perform owned step-up then wait for the documented action-specific expiry; repeat the same harmless protected action. | Reauthenticate or restrict capability as intended, not merely hide UI. |
| Refresh-token rotation | In a controlled fixture, refresh R0 to R1; replay R0 once from a second isolated session. | Enforce configured rotation/reuse-detection policy; not every deployment promises rotating refresh tokens. |
| Session/account binding | Retain owned A's session ID, alter only observed account/tenant hint to owned B. | Backend subject stays bound to A unless A has authorized delegation. |

```http
GET /observed/private-fixture/AUDIT_A HTTP/1.1
Host: app.example.invalid
Cookie: app_session=OWNED_OLD_S1
Cache-Control: no-cache
```

`no-cache` is a test aid, not proof of origin execution. Compare response marker and authoritative
state, inspect relevant cache headers, and use a fresh isolated client as necessary.
Do not attach an Authorization token as well: it could make a revoked-cookie request succeed legitimately.

## Browser and distributed-state interpretation

Cookie `Domain`, `Path`, `Secure`, `HttpOnly`, `SameSite` and partitioning influence reach.
A missing cookie attribute alone is a configuration observation until its actual effect is established.
Two same-name cookies with different paths/domains can reach a server together; identify the server's
actual selection rather than assuming the browser's displayed cookie is authoritative.
Host-only cookies and prefixed cookies have additional rules; verify current browser behavior.

Session revocation may pass through an auth cache, gateway, worker and websocket connection.
Measure observation timestamps and the exact capability that remains available.
A short stale read already returning another user's synthetic secret is not erased by later convergence.
A stale dashboard badge with protected server operations still denied is a different result.
For a job created before removal, establish whether access is intentionally decided at creation or use.

Do not attempt to demonstrate persistence by adding new keys or accounts when a harmless read proves
the boundary. If future independent access is relevant, route to account-control chain validation,
using the minimum permitted security change and explicit cleanup on owned fixtures.

## Evidence and closure

Preserve event type/scope, before/after credential classes, normal protected control, exact replay,
independent state confirmation, elapsed timestamps, refresh/SSO behavior and semantic result.
Document browser/server versions only when observed; do not infer them from source dates.

Close the tested credential/event pair if correctly revoked; keep untouched token types/WS/jobs
marked untested. Reopen when a new representation or propagation boundary is actually observed.
A general session-security certification cannot follow from one logout test.

Sources reviewed 2026-11-13. Requests are original synthetic shapes, not executed target evidence.

## Primary references

- [PortSwigger: Other authentication mechanisms](https://portswigger.net/web-security/authentication/other-mechanisms) — persistent login and recovery surfaces.
- [OWASP: Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) — rotation, lifecycle and server-side session invalidation.
- [MDN: Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) — current cookie scope, prefix, SameSite and partitioned-cookie semantics.
- [IETF: OAuth Security BCP](https://datatracker.ietf.org/doc/html/rfc9700) — refresh-token protection and rotation boundaries where OAuth applies.
