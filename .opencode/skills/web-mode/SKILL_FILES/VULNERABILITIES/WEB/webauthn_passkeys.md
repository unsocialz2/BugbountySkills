# WebAuthn and passkeys — ceremony, credential and account binding

## Contents

- Model the relying party and legitimate ceremonies
- Discovery and controls
- Differential experiments and PAYLOADS
- Cryptographic and browser constraints
- Evidence, closure and sources

## Model the relying party and legitimate ceremonies

Test whether the application binds a valid authenticator response to the intended ceremony,
challenge, relying party, browser origin, user account and assurance requirement.
An authenticator proving possession of a key is only one part of the application's decision.
Registration/enrollment, authentication, step-up, credential management and recovery are separate flows.

Use two researcher-owned accounts and a supported authenticator or explicitly authorized local
virtual authenticator fixture. Do not change trusted-origin/RP configuration or bypass attestation
and then describe that modified environment as an external browser exploit.

Record the exact server options and verified response fields:

- create versus get ceremony and session/pending transaction;
- challenge generation, lifetime, consumption and account/session association;
- expected RP ID and allowed web origins; origin includes relevant scheme, host and port;
- `clientDataJSON` type/challenge/origin and cross-origin context where applicable;
- `authenticatorData` RP ID hash, user-presence/user-verification flags and extensions;
- allowed algorithms, credential public key, credential ID and user handle/account relation;
- attestation policy when required, rather than assuming every app requires hardware attestation;
- signature-counter interpretation, backup/sync state and credential revocation;
- session/step-up authority created after successful verification.

## Discovery and controls

Capture one successful enrollment and one fresh successful authentication for owned A.
Confirm the newly registered credential is associated with A and final protected identity is A.
Use B's independently registered credential as a cross-account control.
Observe whether login is username-first or discoverable-credential/usernameless; do not assume
a missing username or user handle is invalid in every ceremony.

Check challenge length and uniqueness as inventory. A few non-repeating samples do not prove
entropy; a short challenge is a weakness indicator whose exploitable consequences need analysis.
A browser denial before signing can establish client enforcement but not the server's full verifier.
Inspect authorized server source or a matched local signer/verifier to isolate deeper checks.

## Differential experiments and PAYLOADS

| Binding | Minimal controlled experiment | Protected result / interpretation |
|---|---|---|
| Challenge consumption | Complete one owned assertion, then replay the exact assertion in a fresh pending flow once. | No new unauthorized authority from consumed/stale proof; ensure another existing cookie is not doing the login. |
| Pending session/account | Start separate owned A/B ceremonies, substitute A's intact assertion into B's completion request. | Associate final identity with the verified credential under the intended transaction, not a user-controlled account hint. |
| Credential registration owner | During A enrollment change only observed external `account_id`/`user_id` field to B while keeping A's actual session. | The stored credential must not become an authentication method for B without B's authorized enrollment. |
| Credential ID/account relation | Complete owned A's legitimate assertion but pair with B's observed username/account hint. | Reject mismatch or authenticate only the credential's authorized identity according to the usernameless flow. |
| Origin/RP verification | In an explicitly local matched fixture, generate a correctly signed response for a different controlled origin/RP context. | Verifier rejects wrong expected origin/RP hash; editing signed fields without a new signature only tests integrity. |
| Assurance flags | In a local capable test authenticator, produce valid signatures with UV absent for a server action configured to require UV. | Enforce required assurance server-side; UP and UV are different. A forged bit without valid signature is not a test of UV policy. |
| Ceremony type | Submit an intact legitimate registration response to the observed authentication consumer or vice versa. | Enforce `webauthn.create` versus `webauthn.get`, message structure and pending ceremony binding. |
| Revoked credential | Delete only an owned disposable credential via the legitimate management UI; attempt ordinary login using that credential afterward. | No new session from revoked credential; distinguish a still-active app session. |
| Recovery/enrollment continuity | Complete owned recovery then attempt to add another owned credential from the resulting state. | Enforce the product's intended assurance, ownership and recovery controls at enrollment. |

```json
{"ceremony_id":"OWNED_PENDING_B",
 "account_id":"OWNED_ACCOUNT_B",
 "credential":{"id":"OWNED_CREDENTIAL_A","response":"INTACT_ASSERTION_A"}}
```

This is a schematic transport shape. Browser WebAuthn results normally carry base64url-encoded
binary fields; preserve the actual encoding and wrapper instead of replacing the response with text.
Use intact real captured assertion fields when testing outer account/transaction binding.

## PAYLOADS — decode a synthetic client-data fixture

```python
import base64, json

raw = json.dumps({"type":"webauthn.get","challenge":"AUDIT_CHALLENGE",
                  "origin":"https://rp.example.invalid"}, separators=(",", ":")).encode()
encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
decoded = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
assert json.loads(decoded)["type"] == "webauthn.get"
print(encoded)
```

This demonstrates encoding only. It is not a signed assertion and cannot by itself authenticate.
Changing decoded challenge/origin/type normally changes the signed message's hash and invalidates
its signature. Separate parser/integrity rejection from a missing semantic check.

## Cryptographic and browser constraints

A normal browser constrains which RP IDs/origins an authenticator may use; a fabricated local
response does not prove a malicious website can obtain that response from the victim's authenticator.
For local verifier tests state the extra signing authority explicitly and then assess external reach.
Virtual authenticators are test tooling, not evidence of bypassing a production hardware/attestation policy.

Synced passkeys and authenticators that report zero counters require nuanced counter handling.
`signCount == 0`, backup eligibility or a non-increasing counter alone is not proof of account takeover.
Validate the deployed library's handling and product policy before asserting a cloning/replay flaw.
A legitimate browser's origin allowlist may include multiple supported origins; prove an untrusted
attacker origin is accepted rather than assuming every second origin is malicious.

## Evidence, closure and source limits

Preserve ceremony type, challenge transaction, controlled credential/account mapping, valid signature
control, exact altered outer binding, verifier result and final protected identity/action.
Do not export private keys or unrelated credential inventories into evidence.
Prove the natural attacker path separately from local origin/config/signature capabilities.

Close only the tested ceremony/binding. A rejected assertion does not certify registration owner
checks, recovery safety or all supported origins. Reopen for a distinct observed flow or verifier path.

Sources reviewed 2026-11-13. The base64url fixture was executed locally. No full WebAuthn ceremony
or live service was exercised here. Use the specification level and extensions deployed by the target;
the Level 2 Recommendation below supplies stable baseline verification steps, not a claim that it is latest.

## Primary references

- [PortSwigger: Passkey scanner](https://github.com/portswigger/passkey-scanner) — original tooling and challenge/algorithm checks; scanner flags still require boundary validation.
- [W3C: WebAuthn Level 2](https://www.w3.org/TR/webauthn-2/) — creation/authentication verification, RP/origin/challenge/signature and counter semantics.
- [OWASP: Passkey Security](https://cheatsheetseries.owasp.org/cheatsheets/Passkey_Security_Cheat_Sheet.html) — enrollment, recovery, assurance and relying-party implementation safeguards.
