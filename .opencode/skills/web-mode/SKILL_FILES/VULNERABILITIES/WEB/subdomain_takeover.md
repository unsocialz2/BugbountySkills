# Subdomain Takeover — dangling dependency, claimability, and actual domain control

## Contents

- Define the dependency and invariant
- Cheap discovery and controls
- Discriminating experiments
- Context-specific payloads and observations
- Trust-chain impact without overclaiming
- Falsification and evidence
- Sources and version limits


Use this guide when an in-scope hostname depends on a third-party resource or domain binding that may no longer be controlled by the owner. A dangling CNAME, NXDOMAIN, `NoSuchBucket`, or provider-branded error is a lead, not proof that a researcher can claim the target hostname.

## Define the dependency and invariant

Write: the organization should retain exclusive authority to serve the intended hostname or verify any new binding before another account can serve it.

Record the complete DNS chain and record type, current provider, custom-domain binding model, resource identifier/region, proof-of-ownership mechanism, certificate requirements, and whether the resource name or the domain binding itself is reclaimable.

Keep distinct:
- dangling resource name;
- available resource identifier;
- third-party account can create the resource;
- third-party account can attach the hostname;
- requests for the hostname reach researcher-controlled content;
- additional trust/cookie/CORS impact.

Provider state is version- and configuration-sensitive. Public fingerprint lists can nominate a hypothesis but cannot substitute for current first-party binding rules or live account-state evidence.

## Cheap discovery and controls

1. Reuse existing scoped DNS inventory and resolve the exact chain; save timestamps and authoritative/recursive differences when relevant.
2. Request only permitted harmless paths and retain Host/SNI/status/body/certificate evidence.
3. Compare the error to current provider documentation. Distinguish DNS failure, resource absence, unknown custom domain, suspended service, private service, and transient provider outage.
4. Establish what creation/binding action would be needed. Do not register a domain, reserve a resource, or attach a hostname solely because a scanner suggests takeover; apply the program's specific resource-claim policy.
5. When claiming is prohibited, preserve the strongest permitted provider evidence and explicitly mark practical control unproven. A policy may accept that narrower report without requiring a claim.

## Discriminating experiments

| Hypothesis | Minimum permitted comparison | Benign alternative / decisive distinction |
|---|---|---|
| A hostname points to a removed named resource | DNS chain plus provider-specific missing-resource response | Private/suspended/wrong-region resources can look missing; error fingerprint alone is insufficient |
| Resource name can be recreated | Provider documentation and permitted availability/account-state check | Reserved names or account ownership may prevent creation even when HTTP says missing |
| Custom-domain binding requires proof | Inspect current TXT/token/account verification requirements before any claim | Verification linked to the legitimate owner can make a dangling dependency non-claimable |
| DNS still routes to a recreated resource | Only after a policy-permitted owned fixture or claim, serve a unique marker at an isolated path | Creating the name does not prove the target's DNS resolves to that account/region |
| HTTPS authority is obtainable | Inspect actual certificate/binding state under the provider's allowed workflow | HTTP-only serving does not prove HTTPS takeover or secure-cookie reach |
| Product trusts the subdomain | Inspect explicit CORS, redirect, script, callback, and cookie policies; test with synthetic owned data only | Parent origin and host-only cookies remain separate; same-site does not mean same-origin |
| Wildcard records create a false candidate | Compare one known legitimate host and a random sibling without claiming either | Wildcard provider errors can produce many apparent hits from one unbound wildcard |

Do not generalize a provider's old verification behavior to its current control plane. Recheck policy when the needed proof action has material external side effects.

## Context-specific payloads and observations

Read-only DNS observations, using documentation-only names:

```bash
dig +noall +answer owned.example.invalid CNAME
dig +noall +answer owned.example.invalid A
dig +noall +answer owned.example.invalid AAAA
```

A missing CNAME response does not exclude A/AAAA, ALIAS flattening, delegation, or other dependency forms. Query actual scope-approved names only.

If policy explicitly permits a minimal claim/marker proof, serve only:

```text
/audit-domain-control/AUDIT_ID
AUDIT_DOMAIN_CONTROL_AUDIT_ID
```

Use a unique path, not the homepage, and avoid active scripts, login pages, branded imitation, cookies, or indexing. Record which researcher-controlled provider account served the marker and the target Host/SNI used. Do not add `Set-Cookie` just to increase impact.

Example request for the proof object:

```http
GET /audit-domain-control/AUDIT_ID HTTP/1.1
Host: owned.example.invalid
```

Matched controls include an unrelated non-existent proof path and the provider's ordinary default response. Keep the claim reversible and follow the program's cleanup/retention instructions; removing a claimed resource while DNS is still dangling may re-expose the problem, so coordinate the permitted handoff rather than silently abandoning it.

## Trust-chain impact without overclaiming

A served marker proves domain content control under the tested protocol and provider state. It does not automatically grant parent-origin JavaScript, parent-domain account control, or all cookies.

Assess only observed relationships:
- a parent-scoped cookie can reach a subdomain only when cookie domain/path/security conditions permit; host-only cookies are different;
- `HttpOnly` changes JavaScript read access but not whether a matching cookie is sent;
- an explicit CORS allowlist trusting this origin can create a separate readable-data boundary if browser credentials/readability are proven;
- a trusted script import or OAuth redirect needs its own request/consumer proof;
- same-site sibling control can affect CSRF defenses without removing same-origin isolation.

Do not harvest cookies or tokens from real visitors. Use the smallest owned fixture that establishes a trust relationship. Keep technical control, program eligibility, and duplicate/submission status separate.

## Falsification and evidence

Try temporary outage, suspended/private service, incorrect region, domain-verification lock, reserved resource name, wildcard response, stale DNS, redirect to a still-owned service, and a default vhost shared across accounts.

Save DNS chain, TTL/timestamps, exact HTTP/TLS evidence, current provider rule links, scope/claim permission basis, account/resource/binding state if permitted, marker path/content and controls, and tested downstream trust facts. Sanitize control-plane screenshots/credentials.

Park if practical binding is blocked or policy prevents decisive verification; label the remaining gap rather than declaring either confirmed takeover or universal safety. Reopen for a documented provider-state change, different binding, ownership token expiry, or owner-approved validation route.

## Sources and version limits

Source review: 2026-11-13. Provider-specific claimability must be rechecked at execution time; no takeover was performed while authoring this guide.

- [OWASP WSTG v4.2 — Subdomain takeover](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover/): historical DNS/dependency discovery patterns; older error-fingerprint examples must be checked against current provider binding rules, not treated as sufficient proof.
- [GitHub — Verify a custom domain for Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages): domain verification can prevent another account from binding a domain; this does not describe all hosting providers.
- [PortSwigger — CORS](https://portswigger.net/web-security/cors): subdomain-origin trust is an additional browser read boundary requiring separate proof.
- [PortSwigger — Host header attacks](https://portswigger.net/web-security/host-header): authority and virtual-host selection; a provider response without the intended Host does not establish control of the target hostname.
