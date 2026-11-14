# JWT Security — verifier and claim-binding reasoning guide

## Contents

- Goal
- Evidence contract
- Stop conditions
- Discovery probes and context-bound payloads
- PAYLOADS — deterministic local HMAC fixture
- Primary references

Use this file when the application relies on JWT/JWS/JWE tokens and evidence suggests the verifier may trust attacker-influenced algorithm, key, header, or claim state incorrectly.

## Goal

Determine whether the server accepts a token whose **integrity, key source, issuer/audience, subject, or privilege claims** were not authorized by the intended trust configuration.

Do not mechanically try every historical JWT trick against every token.

## Map the trust decision

For the token under test, identify:

- token purpose: session, API access, reset, invitation, service-to-service, etc.,
- issuer and audience expectations,
- verification algorithm/family,
- key source and key-selection mechanism,
- relevant header fields that influence verification/key lookup,
- subject/account/tenant/role claims consumed by the application,
- expiry/not-before/issued-at handling,
- where authorization is derived from token claims vs server-side state.

The useful question is: **which attacker-controlled token fields can influence how the verifier chooses trust material or security state?**

## Minimal hunt loop

1. Decode a legitimate token without assuming decoded claims are trusted.
2. Determine which fields the application actually enforces by changing one non-destructive claim/header assumption at a time.
3. Compare rejection/acceptance at the protected action, not only token parsing.
4. Test algorithm/key-source behavior only when the token format/library/deployment suggests that path is relevant.
5. Verify any accepted forged/altered token by observing the resulting server-side identity or capability.
6. Falsify benign explanations such as frontend-only decoding, unsigned display tokens, cached sessions, stale cookies, or an endpoint that ignores the tested claim.

## High-signal questions

- Is the expected algorithm fixed by server configuration or chosen from attacker-controlled token data?
- Is key selection constrained to trusted keys/issuers?
- Can header-controlled key identifiers/URLs change the trust source unexpectedly?
- Are issuer, audience, tenant, subject, and token-purpose boundaries enforced?
- Are privilege claims recomputed server-side or trusted directly from the token?
- Can a token issued for one flow/service/client be replayed in another?
- Are expiry/revocation/security-event expectations enforced where the product relies on them?

## Evidence contract

A strong JWT finding should preserve:

1. token purpose and normal trust configuration as observed,
2. exact attacker-controlled field/assumption,
3. accepted altered/forged token or equivalent verifier failure,
4. protected action/data proving the resulting identity/capability,
5. clean rejection/control case,
6. strongest benign explanation tested and rejected.

Do not assign numeric severity here.

## Stop conditions

Reject or narrow when:

- only local/frontend decoding changes,
- the server rejects the altered token before protected capability is granted,
- the changed claim is not security-relevant or is ignored server-side,
- the token is not intended as an integrity-bearing security artifact,
- the candidate depends on an unverified assumption about the signing key/library.

## References on demand

The contextual token probes and local generator are below. `payloads/references/8-jwt-exploits.md` is only a compatibility lookup back to this guide; do not reload it as an additional source. Use `auth_bypass_all_types.md` or `api-mode` for the surrounding authentication/authorization boundary, and `account_takeover_chains.md` only after a real capability is demonstrated.

## Discovery probes and context-bound payloads

Capture one legitimate token, identify which protected operation consumes it, and remove other
credentials that could mask the result. Do not send signing secrets to online token editors.

| Question | Differential probe / control | Expected protected behavior |
|---|---|---|
| Is the signature actually checked? | Alter one payload byte without recomputing the signature; compare original token on the same action. | Altered token rejected; a public endpoint ignoring both tokens proves nothing. |
| Are token purposes separated? | Present an intact owned ID/reset/invite token at the observed access-token consumer. | Reject wrong token kind even if issuer and signature are valid. |
| Is audience/service binding enforced? | Replay an intact token issued for owned client/service A at observed service B. | B rejects a token not addressed to it; do not edit a signed `aud` and confuse integrity with binding. |
| Is key lookup constrained? | If `kid` is actually used, compare existing benign key ID with `AUDIT_UNKNOWN_KEY`; if `jku` is accepted, use a researcher-controlled inert JWKS fixture. | Unknown/untrusted key source rejected; DNS callback alone does not prove token acceptance. |
| Is algorithm family pinned? | In a local matched verifier fixture, compare configured algorithm with wrong-family token signed by a synthetic test key. | Verifier uses its configured trust model; generation errors are not target rejections. |
| Is security-event state enforced? | Replay the intact owned token after explicit revocation or role removal; compare the documented lifetime policy. | Enforce intended current authority; stateless expiry alone is not necessarily a bug. |

## PAYLOADS — deterministic local HMAC fixture

This creates a **synthetic** HS256 token, not a forged token for a real deployment.
It avoids PyJWT's deliberate refusal to treat PEM public keys as HMAC secrets.
A real RS/HS confusion test needs the exact public-key bytes trusted by a vulnerable verifier,
not an arbitrary re-encoding and not evidence that all current libraries accept it.

```python
import base64, hashlib, hmac, json

def b64u(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=")

def pack(value):
    return b64u(json.dumps(value, separators=(",", ":")).encode())

key = b"AUDIT_SYNTHETIC_KEY_32_BYTES_ONLY!"
header = {"alg": "HS256", "typ": "JWT"}
claims = {"sub": "owned-A", "iss": "https://issuer.example.invalid",
          "aud": "audit-service", "purpose": "audit-fixture"}
message = pack(header) + b"." + pack(claims)
signature = b64u(hmac.new(key, message, hashlib.sha256).digest())
print((message + b"." + signature).decode())
```

Inspect `alg`, `kid`, `jku`, `x5u`, `jwk` only where the verifier consumes them.
A valid own-key token accepted with an attacker-supplied JWK is a different trust failure
from a weak shared secret or an audience error; preserve that distinction in the report.

## Source and version boundaries

Sources reviewed 2026-11-13. The local HMAC construction was executed and its signature checked
independently with PyJWT 2.13.0; that validates fixture generation only, not a target weakness.
Verifier behavior, accepted algorithms and JWKS caches depend on deployed library/configuration.

## Primary references

- [PortSwigger: JWT attacks](https://portswigger.net/web-security/jwt) — signature verification, key selection and algorithm confusion.
- [IETF: RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725) — algorithm, issuer, audience and token-kind separation.
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html) — ID-token validation and identity semantics.

## Scoped closure and reopening

Reopen for another token purpose/audience, actual verifier/key-source evidence, a changed JWKS/configuration or a post-revocation consumer. Failure to generate a token locally is not a target enforcement result.
