# Rate limiting — compatibility route to protected accounting invariants

Use [API rate limiting](../../../../api-mode/SKILL_FILES/VULNERABILITIES/API/api_rate_limiting_bypass.md)
as the canonical methodology for routes, sessions, accounts, batches, quotas and enforcement windows.
A browser login/recovery flow still needs the same accounting model and semantic proof.

## Browser-specific entry

Identify the exact protected behavior: attempts on one account/challenge, recovery message delivery,
expensive generation, resource consumption or another concrete application guarantee.
Observe a low-volume normal control and program-permitted limit behavior before challenging it.
Do not send a fixed 100/1000 requests simply because a guide says so. A success status may be a
throttle acknowledgement, generic anti-enumeration response or failed downstream operation.

## PAYLOADS — one accounting dimension at a time

```json
{"challenge_id":"OWNED_CHALLENGE","code":"KNOWN_INVALID_AUDIT_CODE"}
```

After an observed block under allowed test volume, compare one justified dimension, for example
an independently observed equivalent route or fresh session for the **same** controlled challenge.
Retain the same protected account/action and prove whether the operation is actually accepted.
Use only a small number of owned invalid proofs; this is an accounting test, not an OTP brute force.

Changing to another owned account can test whether a bucket is account-scoped. It does not prove
a per-account limit is bypassed: each account may legitimately have an independent allowance.
Client-IP header mutation is meaningful only if the target actually trusts a forwarding boundary;
never infer a bypass from a different response code without continued protected capability.

RFC 6585's 429 and Retry-After semantics describe HTTP signalling; an application can correctly
limit with other responses, and absence of 429 alone does not establish missing protection.
Use the canonical guide for exact controls, repeatability and scoped stop conditions.

## Sources and limits

Sources reviewed 2026-11-13. Limit thresholds, reset periods, burst allowances and policy scope
are deployment-specific. No traffic/endpoint test was executed for these illustrative payloads.

- [PortSwigger: Password-based login](https://portswigger.net/web-security/authentication/password-based) — login protection accounting pitfalls.
- [OWASP: Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) — throttling in the surrounding authentication threat model.
- [IETF: RFC 6585](https://www.rfc-editor.org/rfc/rfc6585.html) — 429/Retry-After response semantics, not an exploitability checklist.
