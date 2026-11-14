# Email identity parsing — validation, delivery and account binding

## Contents

- Model the identity pipeline
- Discovery and experiment matrix
- Contextual candidate inputs
- Proof, limits and reopening
- Primary sources

## Model the identity pipeline

Use when registration, recovery, invitation, organization membership or linking
makes a security decision from an email address. This is a web identity boundary,
not permission to manipulate third-party mail systems or send unsolicited mail.

Track the exact bytes at input validation, canonicalization, persistence, account
lookup, domain/organization policy, message header/envelope construction, delivery
and verification completion. SMTP envelope mailboxes and message header display
names are different grammars. A browser's email input validation is another layer.

Establish a normal own-account flow with a controlled mail sink or approved test
mailbox. Put a unique synthetic challenge in the message and preserve its intended
account/tenant/purpose. Acceptance of unusual syntax is not itself a bypass.
Neither a displayed address nor SMTP acceptance proves who received the message.

## Discovery and experiment matrix

| Hypothesis | Paired experiment | Protected or benign interpretation |
|---|---|---|
| Validator and sender disagree on domain | Plain mailbox vs one quoted-local-part containing @ in a local sink | Compare parsed policy domain with actual envelope recipient; an RFC-compliant quoted address may legitimately be accepted. |
| Display/header value mistaken for mailbox | Plain addr-spec vs display-name/header-like representation | A mailbox field may correctly reject header syntax; a display label must not become organization proof. |
| Canonicalization collision | Two controlled identities differing in one supported case/Unicode/alias dimension | Verify provider-specific delivery and product intended equivalence. Domain case-insensitivity does not imply every local part is equivalent. |
| Verified old address authorizes new value | Verify A then change to B, then consume A's stale challenge | Completion must bind to intended account/address/purpose and the product lifecycle; observe new authoritative membership. |
| Invitation binding | Invite own B mailbox then alter the supplied email/account hint at acceptance | An unverified hint must not substitute for the intended recipient identity. Possession of a deliberately transferable invite may be by design. |
| Cross-channel comparison drift | Same controlled address through password login, external IdP linking and recovery | Compare issuer/subject/email_verified and stored identity; same display email does not establish equivalent verified subjects. |
| Encoded-word or Unicode parser disagreement | One justified library-specific encoding vs literal/control after identifying actual parsers | Preserve each decoded form. Rejection at transport or mailbox parser is a narrow result, not a global absence of normalization bugs. |
| Length/truncation mismatch | Two bounded own-fixture values straddling a documented field length | A validator, storage field and sender must refer to the same identity; do not flood delivery to discover a length limit. |

## Contextual payloads and candidate inputs

These **reserved-domain synthetic inputs** are for local parser/identity fixtures.
They are not deliverable addresses and are not expected to bypass every validator.
For a permitted real flow use only researcher-controlled, policy-compliant mailboxes.

```text
audit@mail.example.invalid
"audit@staff.example.invalid"@mail.example.invalid
Audit Label <audit@mail.example.invalid>
audit+caseA@mail.example.invalid
AUDIT@mail.example.invalid
```

The quoted local-part contains an @ that is not the domain delimiter. Determine
whether the actual application supports it before comparing parsers. The label
form is a header mailbox representation, not an interchangeable string to accept
in every email input. Plus tags and local-part case are provider-specific; never
claim two accounts are distinct or identical solely from their visual strings.

For verification binding, use an observed shape, for example:

```json
{"challenge_id":"CHALLENGE_FOR_A","code":"OWNED_TEST_CODE","email":"OWNED_B"}
```

Compare against the legitimate A completion and a wrong-code negative control.
If email is not an accepted field, its rejection/ignoring says nothing about
another documented change-address path. Do not alter codes belonging to others.

Where the application applies an email-domain policy, compare the domain it
actually trusts with the address the mail system actually delivers to. Do not
use naive split('@') or a regex as an authoritative RFC mailbox parser in the
harness; that can manufacture the very discrepancy under investigation.

## Proof evidence, limits and reopening

A strong finding shows the intended organization/account constraint, initial
attacker identity, exact representation changes, actual recipient and verification
completion, and resulting unauthorized capability. Source-only comparison of two
libraries is a lead until the product reaches the discrepant paths naturally.

If one service normalizes and another rejects, record the boundary reached; an
error is not authentication success. If the message is undeliverable, do not claim
ownership proof. An address change that requires re-verification may be the
expected defense. Ordinary aliasing is not an account takeover by itself.

Keep synthetic mailbox content, intended and observed identities, transport vs
header interpretation, policy control, resulting account/tenant relationship and
remaining prerequisites. Stop further delivery once minimal proof exists; keep
message recipients and secrets out of shared artifacts. Reopen for another
observed identity channel, parser/version, normalization stage or lifecycle.

## Primary sources

Sources consulted 2026-11-13; syntax standards explain grammar, not the security
policy a particular application must choose or automatic exploitability.

- [PortSwigger Splitting the Email Atom](https://portswigger.net/research/splitting-the-email-atom) — application/mailer parser discrepancies and organization-boundary research.
- [PortSwigger logic examples](https://portswigger.net/web-security/logic-flaws/examples) — web email-domain trust and business-logic context.
- [RFC 5321](https://www.rfc-editor.org/rfc/rfc5321) — SMTP envelope mailbox and delivery semantics.
- [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322) — message header mailbox/display-name grammar.
- [OWASP input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) — email validation and semantic verification limits.
