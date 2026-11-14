# Account Takeover Chains — evidence-driven impact guide

## Contents

- Goal
- Evidence contract
- Stop conditions
- Candidate discovery and minimal transition probes
- Primary references

Use this file **after** a concrete primitive exists and there is evidence it may cross an account-control boundary. Account takeover is an outcome, not a vulnerability class and not a default escalation target.

## Goal

Determine whether the demonstrated primitive can give an attacker durable or meaningful control over another user's account without assuming missing steps.

Do not start by enumerating known ATO recipes. Start from the capabilities the primitive actually grants.

## Capability map

Record the primitive in concrete terms:

- attacker starting privilege,
- victim interaction required,
- origin/session in which the primitive executes,
- data readable,
- actions writable,
- authentication artifacts accessible or unusable,
- whether sensitive actions require password re-entry, MFA, device approval, email confirmation, or another step-up,
- whether sessions are rotated/revoked after account-security changes.

Then ask which account-control guarantees those capabilities can actually challenge.

## Account-control guarantees

Typical guarantees to test only when relevant to the observed product:

- only the legitimate user can change recovery email/phone,
- reset/recovery artifacts are bound to the intended account and flow,
- linking/unlinking identity providers cannot transfer ownership unexpectedly,
- MFA enrollment/removal requires an appropriately strong prior state,
- session/device management cannot be controlled by a weaker session,
- security-sensitive profile changes do not silently alter recovery ownership,
- account merge/link flows preserve verified identity boundaries,
- existing attacker sessions do not survive a security event that should revoke them.

These are reasoning prompts, not a checklist.

## Minimal chain loop

1. Start from a **confirmed primitive** and state exactly what it grants.
2. Identify the nearest account-control boundary that capability could plausibly influence.
3. Verify the prerequisite for that transition from a normal control flow.
4. Test the smallest chain step needed to cross the boundary.
5. After each step, verify server-side account/security state before proceeding.
6. Stop immediately when a required step is independently protected and the primitive cannot satisfy it.
7. If full takeover is demonstrated, reproduce from a clean-enough state and preserve the exact transition sequence.

Never add hypothetical chain steps to make impact look larger.

## Distinguish levels of impact

Keep these separate:

- **action-as-victim** — transient ability to perform same-origin actions in a victim session,
- **security-setting influence** — ability to alter a recovery/security property but not yet obtain durable login,
- **session compromise** — attacker obtains or controls a usable victim session,
- **durable takeover** — attacker can independently regain account access after the original primitive/session ends,
- **tenant/admin takeover** — demonstrated escalation into a stronger organizational role.

Do not label the first two as ATO unless the remaining control boundary is actually crossed.

## High-signal chain questions

Use only when supported by the current capability map:

- Can the primitive alter a recovery factor and does the service require confirmation from the old factor?
- Can it create a new login method or identity-provider link?
- Can it disable/remove MFA or trusted-device protection?
- Can it create/reveal/replay a recovery artifact bound to the victim?
- Do password/recovery/security changes rotate all relevant sessions and tokens?
- Can an account-link/merge flow confuse verified identities across two actors?
- Does a security-sensitive change become durable without step-up authentication?

## Evidence contract

A claimed takeover chain should show:

1. confirmed starting primitive,
2. each account-security transition with request/runtime evidence,
3. actor/account binding at each step,
4. required victim interaction,
5. final proof of attacker-controlled access,
6. whether access survives logout/session expiry/security changes,
7. one negative/control path showing the intended protection.

Use synthetic/test accounts and the minimum state change needed under program rules.

## Stop conditions

Do not continue or claim ATO when:

- the next step requires a secret/factor the primitive cannot obtain or satisfy,
- a security change requires independent re-authentication/step-up that works correctly,
- the primitive provides only self-account control,
- session/action capability disappears before durable control is established,
- account linking correctly binds to a verified external identity,
- evidence supports only a narrower impact.

Report the narrower demonstrated impact instead of forcing an ATO narrative.

## Cross-skill use

The originating flaw stays in its owning skill (XSS, auth, IDOR/BAC, OAuth, MFA, CSRF, business logic, etc.). This file is only for evidence-based impact chaining. Numeric severity and platform wording belong to `reporting-mode`.

## Candidate discovery and contextual payload sequence

A confirmed primitive is required to claim a chain, not to map the product's normal account controls.
During ordinary use, note which operations create independent future login authority: adding a
passkey/IdP, moving recovery details, issuing a personal token, or creating a new trusted session.
Choose the nearest reachable transition rather than trying every ATO recipe.

| Existing capability | Smallest owned-account experiment | What it can prove |
|---|---|---|
| Authenticated action in A's session | Attempt a permitted recovery-address change to another researcher-controlled address; compare normal reauthentication. | Recovery-setting influence only until possession and future login are actually proven. |
| Link-flow manipulation | Begin linking owned external identity B to local A; substitute the link transaction once while preserving a clean normal pair. | Wrong identity/account binding if the final link and independent login both demonstrate it. |
| Readable reset artifact | Request a reset for owned A; consume only the captured artifact in an isolated session and inspect resulting identity. | Usable recovery authority; do not extrapolate from a token-shaped string or expired link. |
| Stale session after security event | Revoke exactly that owned session, then repeat a harmless protected read and inspect current session list. | Revocation failure within the product's stated scope; not automatic durable account ownership. |
| Weak actor can alter security metadata | Change one allowed fixture field; read authoritative security state independently. | No takeover if the field is echoed but does not change the login/recovery decision. |

```http
POST /observed/account/link/complete HTTP/1.1
Host: app.example.invalid
Content-Type: application/json

{"link_transaction":"TX_A","external_result":"OWNED_RESULT_B"}
```

The route and field names are schematic. Run this only for a real exposed link flow with both
identities under researcher control, and preserve normal A/A linking and unlink cleanup.
Reauthentication checks must be challenged from the exact capability the initial primitive grants.
Do not quietly supply the victim's password or second factor to make the next step work.

A transient action can still have lasting impact, but test the lasting authority separately.
For example, an added login credential must allow a fresh independent login after the original
session ends; a one-time profile edit is a narrower result. Conversely, valid session compromise
can be material without proving access survives every future security event.

## Source and version boundaries

Sources reviewed 2026-11-13. Recovery/linking policy and required assurance are product-specific.
The probes describe how to test a chain boundary; they do not guarantee ATO or platform eligibility.

## Primary references

- [PortSwigger: Other authentication mechanisms](https://portswigger.net/web-security/authentication/other-mechanisms) — password reset and persistent-login boundaries.
- [OWASP: Forgot Password](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html) — recovery token lifecycle and account binding.
- [OWASP: Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) — sensitive changes and reauthentication.

## Scoped closure and reopening

Reopen when the current primitive gains an evidenced new read/action, a supported recovery/linking operation changes, or the previously missing prerequisite becomes naturally reachable. Stop at a protected chain link and preserve the narrower proven result.
