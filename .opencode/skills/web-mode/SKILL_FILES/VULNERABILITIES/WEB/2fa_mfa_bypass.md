# 2FA / MFA Bypass — state and binding reasoning guide

## Contents

- Goal
- Evidence contract
- Stop conditions
- Discovery probes and context-bound payloads
- Primary references

Use this file when the product has a distinct multi-factor or step-up authentication state and evidence suggests that state may not be enforced consistently.

MFA bypass is not "find any endpoint that works before OTP." The question is whether the server accepts an action that should require a stronger authentication state without the intended second factor.

## Goal

Model how the application represents MFA state, what the second factor is bound to, and which actions require that state.

A valid attacker model can be a party who already has the primary credential/session but **does not possess the required second factor**. Testing with a controlled account is sufficient to demonstrate that boundary; a second test account is not inherently required.

## Map the MFA state machine

For the relevant flow, record:

- primary-authenticated but MFA-pending state,
- fully authenticated state,
- remembered/trusted device state if present,
- step-up state for especially sensitive actions,
- recovery/fallback state,
- session/token/cookie changes between these states,
- what account/challenge/session/device each verification artifact is bound to.

The key question is: **what server-side evidence proves that this exact session/account completed the required factor?**

## Minimal hunt loop

1. Capture one normal MFA flow and note all server-visible state changes.
2. Identify one protected action that demonstrably requires the stronger state.
3. Change one assumption at a time: skip, replay, reorder, cross-session swap, stale-state reuse, alternate login path, or recovery/fallback path only when the architecture makes it plausible.
4. Verify whether the server-side authentication state actually changes or whether only the UI changes.
5. Confirm the result by performing the protected action from the tested state.
6. Falsify benign explanations such as remembered-device policy, grace periods, already-elevated sessions, account-specific MFA exemptions, or cached frontend state.

## Binding questions

High-signal questions include:

- Is the factor result bound to the same account that consumes it?
- Is it bound to the same session/browser/challenge?
- Can a proof from one parallel login flow affect another?
- Does verification upgrade only one token/session, or are weaker sessions accidentally treated as upgraded too?
- Are alternate login methods subject to the same MFA policy?
- Does disabling/changing MFA require a state at least as strong as enabling it?
- Are recovery/fallback flows equivalent in assurance to the normal MFA path?
- Are step-up requirements checked server-side on the sensitive action itself?

Do not brute-force or flood verification endpoints unless program rules explicitly allow it and the security question actually depends on rate limiting. Prefer low-volume evidence about binding and state enforcement first.

## Recovery and fallback

Treat backup codes, support recovery, trusted devices, alternate identity providers, and phone/email fallback as separate authentication protocols. Analyze their guarantees directly instead of assuming they are weaker.

A fallback path is only a bypass if it grants the same protected state without satisfying the product's intended assurance level.

## Evidence contract

A validated MFA bypass should show:

1. starting auth state,
2. factor normally required,
3. exact altered/skipped/replayed transition,
4. resulting server-side auth state,
5. protected action proving the stronger state was accepted,
6. normal control path where the factor is enforced,
7. account/session/challenge binding evidence,
8. strongest benign explanation tested and rejected.

Do not jump directly to ATO. If the bypass only grants a narrower action, record that narrower impact. Use `account_takeover_chains.md` only when an evidence-backed account-control path remains.

## Stop conditions

Reject or narrow when:

- only client-side navigation changes,
- the sensitive backend action still enforces MFA/step-up,
- the tested session was already trusted/elevated before the test,
- alternate login is intentionally exempt by documented policy and does not weaken another boundary,
- a stale code/session response does not result in stronger server-side capability,
- the tested state gains no capability beyond what the intended primary-authenticated/MFA-pending state is supposed to have.

## Cross-skill use

Use `auth_bypass_all_types.md` for the wider login state machine, `rate_limiting_bypass.md` only when rate limiting is the actual boundary under test, OAuth/SAML/JWT files for protocol-specific questions, and `account_takeover_chains.md` only after a real primitive is confirmed.

## Discovery probes and context-bound payloads

Start with owned credentials and a single harmless action whose normal successful control
requires the product's stronger assurance. An endpoint existing before OTP can be intentional.
Classify primary-login MFA, action-specific step-up, device remembrance and recovery separately.

| Question | Minimal challenge and matched control | Expected protected behavior |
|---|---|---|
| Can a pending session access a post-MFA resource? | Replay the captured read with pending S0 versus completed S1; omit all other session credentials. | Only S1 gains the stronger capability; a public response is not a bypass. |
| Is a verification result flow-bound? | Create two pending flows A1/A2 on the same owned account; pair valid proof P1 with flow A2 once. | No unintended upgrade of a different pending transaction. Some factors are account-scoped: prove the product's actual guarantee. |
| Can a code be consumed twice? | Complete a controlled challenge once, then replay its exact accepted verification request in a new flow. | No new stronger session from a consumed proof; distinguish TOTP time-window semantics from challenge single-use. |
| Is an enrollment result applied to the correct account? | With owned A/B, substitute only the enrollment/challenge ID while retaining A's session. | B's factor must not be registered or confirmed by A's authority. |
| Does fallback bypass intended assurance? | Compare normal recovery/backup-code completion with normal MFA, then inspect resulting allowed actions. | A documented recovery protocol can be legitimate; find the missing prerequisite, not merely a different factor. |
| Does step-up expire where it matters? | After the product's stated step-up lifetime, repeat the exact harmless protected action with old session. | Sensitive action checks current required assurance server-side, not a cached UI badge. |

```json
{"challenge_id":"CHALLENGE_2","code":"VALID_OWNED_CODE_FOR_1"}
```

Do not generate guessed codes or treat `verified:true` in an altered browser response as server proof.
Use a real accepted normal challenge as control; prove the exact granted capability afterward.
A remembered-device cookie created after valid MFA is not automatically a bypass when reused.
For WebAuthn, the UV bit and server policy matter; an external authenticator's existence does
not imply hardware-only assurance. See `webauthn_passkeys.md` for assertion/ceremony boundaries.

## Source and version boundaries

Sources reviewed 2026-11-13. Factor vendors differ in challenge scope, TOTP reuse handling,
trusted-device lifetime and step-up policy. Treat undocumented behavior as a question and
preserve controls; these request shapes have not been executed against a live target.

## Primary references

- [PortSwigger: Multi-factor authentication](https://portswigger.net/web-security/authentication/multi-factor) — MFA state and verification-flow mistakes.
- [OWASP: Multifactor Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html) — factor replacement, recovery and trust decisions.
- [W3C: WebAuthn Level 2](https://www.w3.org/TR/webauthn-2/) — user presence/verification and assertion validation.

## Scoped closure and reopening

Reopen for a supported fallback/trusted-device channel, a fresh partial-authentication token, a role-specific step-up action, or changed challenge binding. Successful MFA enforcement on one action does not certify all pending-session capabilities.
