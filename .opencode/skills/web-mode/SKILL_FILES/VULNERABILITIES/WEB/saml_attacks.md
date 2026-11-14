# SAML — signed-object consumption and federation boundaries

## Contents

- Model the federation and normal control
- Discovery and verifier map
- Differential experiments and PAYLOADS
- Signature/parser distinctions
- Evidence, closure and source limits

## Model the federation and normal control

Test whether the service provider consumes the exact identity and authorization context
that the trusted identity provider authenticated and signed for this relying party.
SAML is not simply "XML present, try XXE"; signature validation and application consumption
are distinct stages that can disagree even when a signature is cryptographically valid.

Use two researcher-owned accounts and an authorized test federation where available.
Capture one normal SP-initiated login from AuthnRequest through final protected identity.
Also identify whether unsolicited IdP-initiated responses are intentionally supported.
Missing access to a signer is a constraint, not permission to disable signature verification.

Record:

- SP entity ID, ACS endpoint, binding and expected IdP entity/certificate trust;
- response ID, assertion ID, `InResponseTo` and server-side pending request;
- the signed element(s), `Reference URI`, transforms and validated digest;
- the exact verified node returned to application code and the identity/role extraction path;
- `Issuer`, `AudienceRestriction`, `Destination`, `Recipient` and subject confirmation;
- `NotBefore`, `NotOnOrAfter`, accepted clock skew and replay-cache scope;
- `NameID` format/value and authoritative attribute-to-account/tenant mapping;
- RelayState's purpose, integrity and post-login destination.

## Discovery and verifier map

Decode the observed POST form/redirect artifact with the correct binding, preserving original bytes.
Parse an analysis copy without network/entity access; do not pretty-print and re-sign silently.
A decoded assertion is a lead; first establish which library/configuration verifies it at runtime.
Inspect stack/library versions from authorized source where available and verify vendor advisories.
A dependency version or published exploit name alone does not prove an exposed vulnerable flow.

Sketch this path before choosing a mutation:

```text
binding decode -> XML parse -> trust/key lookup -> signature/digest check
-> selected verified assertion -> profile/binding checks -> local account mapping -> session
```

Look for repeated parsing, serialization round trips, multiple candidate elements, ambiguous ID
selection, namespace-dependent XPath, or separate verification and extraction libraries.
These are targeted hypotheses, not reasons to send every XML mutation to every ACS endpoint.

## Differential experiments and PAYLOADS

The values below are owned-fixture placeholders and request shapes, not pre-signed assertions.
A signature-invalid edit normally demonstrates integrity enforcement, not recipient/audience binding.
To isolate a downstream binding, obtain two legitimate appropriately signed test assertions
whose one relevant context differs, or use an authorized local fixture signer.

| Hypothesis | Smallest challenge and matched control | Expected result / interpretation |
|---|---|---|
| Signed node differs from consumed node | In a local/library-matched fixture, retain the signed assertion and introduce a second synthetic assertion with `AUDIT_OTHER_SUBJECT`; compare the verified-node identity. | Reject ambiguity or consume only the verified node. Confirm protected app identity; accepting XML alone is not an auth bypass. |
| SP audience/destination is not bound | Present an intact test assertion issued for owned SP B to SP A, with each SP's normal assertion as control. | Reject wrong relying-party context. A failed signature from an unrelated IdP does not test audience checks. |
| Response is not transaction-bound | Start SP request R1/R2 in separate controlled sessions; exchange intact responses from the same legitimate IdP. | Match the permitted request/session context or explicitly follow the documented unsolicited flow. |
| Recipient or subject confirmation ignored | With test signer, vary `Recipient`/expiry of an otherwise valid assertion independently. | Apply the selected profile's subject-confirmation requirements, not merely the top-level signature. |
| Replay accepted after consumption | Log in with an owned assertion once, then submit it in an isolated new session within the validity window. | Replay handling follows the profile and deployment; prove a new unintended session, not reuse of an existing cookie. |
| Account/tenant mapping trusts weak claim | Compare signed owned identities whose verified issuer/subject differs but an email/display attribute collides under allowed test configuration. | No unintended cross-account link from an untrusted or improperly verified attribute. |
| RelayState changes post-login authority | Change only observed RelayState to an inert owned location, preserving normal signed control. | Preserve permitted navigation/account context; an open redirect is not assertion forgery. |

```xml
<!-- Analysis-only assertion fields; this fragment is NOT a valid signed assertion. -->
<saml:SubjectConfirmationData
  xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
  InResponseTo="OWNED_REQUEST_R2"
  Recipient="https://sp-b.example.invalid/acs"
  NotOnOrAfter="2000-01-01T00:00:00Z" />
```

Use the past timestamp only in a test-signed assertion/local fixture to isolate time validation.
Do not expect a signed assertion with arbitrarily edited expiry to reach that check.
Compare signature failure separately from profile-check rejection using permitted logs/source.

## Signature/parser distinctions

XML canonicalization transforms selected referenced data into digest input; it is misleading
to say that "the whole XML string is signed" or that every comment edit changes signed identity.
For comment/namespace/round-trip candidates, compare the canonicalized signed node and the
consumer's extracted value using the actual deployed parser/version.
Duplicate IDs or multiple assertions may be rejected at schema or library stages; retain that result.
External-entity parsing is a separate boundary: route an evidenced XML fetch question to XXE,
using a harmless controlled marker rather than collecting system files.

Modern research such as SAML roulette demonstrates concrete multi-parser/round-trip problems
in particular library combinations. Do not generalize those exact payloads to all SAML products.
IdP-initiated SSO has no initiating SP request to correlate; absence of `InResponseTo` there is
not by itself a bypass. It still needs appropriate issuer, recipient, audience, time, replay and
local-account checks. Establish product support and threat model before comparing flows.

## Evidence, closure and source limits

Preserve a sanitized normal artifact, altered/intact cross-context artifact, verification stage,
final authenticated subject/tenant, required attacker prerequisites and a negative control.
Prove the natural externally reachable entry; a local signer that controls the victim IdP trust
cannot prove an unprivileged external attack on that deployment.

Close only the tested mutation when it fails at the relevant stage. Reopen for a different parser,
signed-node selection, supported flow or trust configuration when evidence changes.
A changed error page, accepted form POST or redirect to a dashboard is not protected semantic success.
Do not score an unvalidated candidate or claim all federated apps are compromised.

Sources reviewed 2026-11-13. This guide combines profile requirements and original differential
test designs; no production SAML exploit or complete cryptographic fixture was executed here.

## Primary references

- [PortSwigger: SAML roulette](https://portswigger.net/research/saml-roulette-the-hacker-always-wins) — original parser/namespace/round-trip research and library-specific preconditions.
- [OWASP: SAML Security](https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html) — signer/consumer consistency and profile validation.
- [OASIS: SAML 2.0 profiles](https://docs.oasis-open.org/security/saml/v2.0/saml-profiles-2.0-os.pdf) — browser SSO, recipient, correlation, timing and unsolicited-response rules.
