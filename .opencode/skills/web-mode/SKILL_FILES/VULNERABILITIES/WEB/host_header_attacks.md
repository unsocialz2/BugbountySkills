# Host and Forwarded Authority — URL construction, routing, and trust

Use this guide when a client-influenced authority reaches URL generation, tenant selection, access control, or upstream routing. An accepted alternate Host or a reflected hostname is not automatically a vulnerability.

## Model authority before testing

Write the expected authority source for the operation: configured canonical host, validated request authority, trusted proxy metadata, or a tenant mapping. Record TLS SNI, HTTP/1 Host or HTTP/2 `:authority`, absolute-form request target if relevant, forwarded headers, and which hop is permitted to set them.

Distinguish:
- client authority selecting the intended public virtual host;
- a gateway overwriting a trusted upstream host/proto field;
- application code trusting client-supplied forwarding metadata;
- URL construction versus routing to a different service;
- cache key selection versus origin tenant selection.

Use an owned account, test email inbox if recovery is involved, and an approved test route. Confirm normal tenant/host behavior and capture the actual generated link or protected response. Do not use real users' recovery mail.

## Cheap discovery

1. Inspect normal absolute URLs in redirects, canonical links, asset references, emails, and callbacks.
2. On a non-cached test object, change one authority field to `audit-marker.example.invalid` and observe whether output changes.
3. Compare a valid approved authority, an invalid ordinary authority, and the marker. Record whether rejection happens at the edge or app when knowable.
4. If routing changes, establish what service/tenant is reached before sending any credential or sensitive operation.
5. Follow an effect only when there is a concrete trust boundary; accepting an arbitrary Host to serve a generic error/default page is not enough.

## Differential experiments

| Hypothesis | Small experiment and control | What must be proved |
|---|---|---|
| URL builder uses untrusted Host | Compare generated link under canonical Host and marker Host on owned request | A sensitive link's authority changes; plain reflected text is a narrower observation |
| Forwarded host bypasses canonical validation | Keep Host constant; vary only observed `X-Forwarded-Host` or standardized Forwarded field | Client controls a field the app treats as trusted URL authority |
| Proto handling downgrades a sensitive link | Compare intended HTTPS with one proto metadata change on an isolated flow | Actual link/callback security changes, not just a cosmetic scheme string |
| Frontend and backend choose different tenants/vhosts | Compare approved tenant A/B controls and the suspect authority relationship | An actor gains data/action across the tenant boundary; branding differences are insufficient |
| Cache keys omit an authority-selection input | Prime only an isolated test key and retrieve without altered input | Clean consumer receives changed authority-dependent representation; use cache guide |
| Connection-specific routing trusts a prior host | In a lab/approved fixture compare same and new connections with equivalent ordinary requests | Routing follows unintended prior state; do not involve other users' connections |

Duplicate Host, absolute-form, and HTTP/2 authority experiments require evidence of an intermediary disagreement and raw-wire controls. Many compliant servers reject them. Do not assume a particular duplicate selection rule.

## Context-specific payloads

Test only a forwarding family the deployment actually uses:

```http
GET /audit/AUDIT_ID HTTP/1.1
Host: app.example.invalid
X-Forwarded-Host: audit-marker.example.invalid
```

```http
GET /audit/AUDIT_ID HTTP/1.1
Host: app.example.invalid
Forwarded: host="audit-marker.example.invalid";proto=https
```

Matched controls omit the forwarding field or set it to the legitimate canonical host. A proxy may strip or replace it; prove what the application consumes.

For a normal recovery flow, preserve the real method/body/CSRF requirements and change only the authority input. Example data must identify the researcher's account:

```json
{"email":"owned-recovery-account@example.invalid"}
```

This placeholder is deliberately non-deliverable. Use the program-approved researcher inbox in an actual permitted workflow. Inspect the full original email and URL without sending a real token to an untrusted third party.

For origin routing, `curl --resolve` can preserve SNI and Host while selecting a specific approved IP:

```bash
curl --resolve 'app.example.invalid:443:192.0.2.10' \
  'https://app.example.invalid/audit/AUDIT_ID'
```

The address is documentation-only. Replace it only after origin ownership/scope is established. Do not disable TLS verification merely to declare an IP equivalent to the protected service.

## Validate the nearest effect

A poisoned reset URL is strong evidence of URL construction. Account control needs additional permitted evidence that the token is usable for that account and that realistic delivery gives an attacker the token. A test inbox click is a controlled delivery experiment, not proof every real victim will click.

For routing, verify protected semantic success from the claimed starting role and preserve a normal allowed/denied comparison. For SSRF-like host routing, establish the reached destination or synthetic internal fixture response without guessing internal services. For caches, show clean retrieval rather than direct reflection.

Do not rely on a CNAME or a string containing two hosts as a general bypass. DNS aliasing does not change HTTP authority validation by itself.

## Falsification, evidence, and closure

Test generic/default virtual hosts, intentional multi-domain support, canonical-host rewriting, forwarded-field stripping, public content, stale cache, and a callback/token exchange that rejects the changed URL. A public route under a different Host may be intentional.

Save the exact authority/SNI/proxy inputs, normal control, generated links or response, owned identities, routing attribution, and final effect. State whether the modified host was accepted, used, and security-relevant as three separate facts.

Stop when the app consistently uses a configured canonical authority or when no unauthorized capability follows. Scope that result to the tested operation and metadata path. Reopen for a distinct builder, recovery email template, service gateway, tenant route, or protocol path. Cleanup owned recovery artifacts and test objects; do not report automatic account takeover.

## Sources and version limits

Source review: 2026-11-13. Header examples are conditional canaries, not accepted syntax on every proxy.

- [PortSwigger — HTTP Host header attacks](https://portswigger.net/web-security/host-header): authority-dependent attack surfaces and trust boundaries.
- [PortSwigger — Identifying and exploiting Host header flaws](https://portswigger.net/web-security/host-header/exploiting): URL construction, routing, and ambiguous-request considerations.
- [HTTPWG — RFC 9110](https://httpwg.org/specs/rfc9110.html): authority/Host semantics and request routing context.
- [Cloudflare — Protect your origin](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/): direct-origin reachability needs independent enforcement; reachability is not a global authorization bypass.
