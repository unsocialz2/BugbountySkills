# Edge and Origin Enforcement — Cloudflare-aware differential testing

Use this guide when a CDN/WAF-protected hostname may also be served through another approved route. The retained filename is a compatibility path; discovering an origin IP is not a total Cloudflare bypass or a reportable weakness by itself.

## Define the boundary and authorization

Write the protected guarantee: only approved edge requests should reach the origin, or a specific edge-enforced authentication/authorization rule must apply to the same application action.

Separate ownership evidence, scope, route reachability, TLS/authority equivalence, protection difference, and final application effect. A certificate name, favicon, historical IP, ASN, or similar body is attribution evidence; none independently authorizes active requests to that IP or proves it is the current origin.

Before active origin testing, verify the program's scope includes the hostname/IP/route and the intended operation. DNS ownership resemblance is not permission. Prefer program-provided origin addresses or known authorized configuration/source over broad IP scanning.

Record:
- public hostname, TLS SNI, Host/`:authority`, resolved destination, and certificate validation;
- normal edge/auth response and the protected resource/action;
- origin-side ACL, mTLS/Authenticated Origin Pulls, firewall, application auth, and tenant routing when observable;
- whether an alternate path is a public legacy site rather than the same backend;
- caching/replica differences and researcher identity/header requirements on both routes.

## Cheap discovery

1. Review permitted passive DNS/certificate and existing target artifacts for a concrete candidate; retain source and timestamps.
2. Check whether the address is current and in scope before any direct request.
3. Request a harmless approved marker/resource using the same intended SNI and Host.
4. Compare a normal edge request and a normal direct-origin request before testing any protection difference.
5. If the origin rejects requests with a certificate requirement or ACL, preserve that narrow control; do not assume a bypass exists or switch to unrelated IPs.

## Differential experiment matrix

| Hypothesis | Minimal comparison | Meaningful result / benign alternative |
|---|---|---|
| Public origin serves the same app | Edge and approved origin request for a unique owned object/revision | Same marker and object relationship establish equivalence better than a shared logo |
| Origin enforces edge-only identity poorly | Same lower-privilege or unauthenticated request on both routes, with a legitimate privileged control | Direct route grants protected semantic capability; an edge bot challenge versus public origin page alone is insufficient |
| Client forwarding header is trusted | One observed identity/routing header changed on the approved direct route versus omitted/canonical value | Origin authority changes from untrusted data; use auth/Host guides to prove effect |
| Origin route crosses tenant mapping | Approved A/B tenant controls with matched authority and synthetic resources | Wrong tenant's private data/action becomes accessible, not just different branding |
| Security setting is inconsistent across routes | Same owned file/download/callback operation under equivalent state | Direct route changes the protected guarantee; headers that differ without effect are narrower metadata observations |
| mTLS/ACL blocks direct ingress | Legitimate edge result versus direct denied request | Expected origin restriction works in this tested route; no need to attempt credential impersonation |
| Historical address is unrelated/stale | Owned revision/canonical response compared with attribution evidence | No live equivalence means attribution remains unverified, not a hidden bypass |

A direct HTTP request with a changed Host and no matching SNI may select a different virtual host. Keep these variables controlled before interpreting a result.

## Context-specific payloads

The following addresses/names are documentation placeholders and do not identify a live origin:

```bash
# Normal approved hostname route.
curl --max-time 20 'https://app.example.invalid/audit/AUDIT_ID'

# Same TLS SNI and HTTP authority, destination changed to an approved origin.
curl --max-time 20 \
  --resolve 'app.example.invalid:443:192.0.2.10' \
  'https://app.example.invalid/audit/AUDIT_ID'
```

Do not include `-k` by default. If a lab origin intentionally uses a private CA, use the provided CA or record certificate behavior separately. Ignoring certificate errors can help diagnose routing but cannot establish a browser-realistic trusted service.

If the application actually trusts a forwarded-authority family, compare one harmless marker header on the isolated route:

```http
GET /audit/AUDIT_ID HTTP/1.1
Host: app.example.invalid
X-Forwarded-Host: audit-marker.example.invalid
```

This is a trust probe, not proof of bypass. Matching output without a protected state change does not prove authentication weakness. Do not add spoofed Cloudflare identity headers merely because their names are familiar; require evidence that the origin consumes them.

For an owned role-gated object, preserve the normal request shape and credentials. Compare only destination routing first; then test a single missing/changed authorization prerequisite under the owning auth guide. Never send credentials to an unverified address selected from historical data.

## Validation, falsification, and impact

Prove the normal protected operation, equivalent origin route, actual difference in authority/enforcement, and resulting attacker capability. Direct origin access to public content can be expected behavior. Origin-side application auth may correctly protect all sensitive actions even when the edge is bypassed.

Consider independent origin WAF rules, mTLS, source-IP restrictions, private connectivity, cache-only edge responses, stale mirrors, different deployment revisions, and default virtual hosts. Product header fingerprints are not sufficient to assign enforcement to a particular hop.

A briefly accessible action before a firewall rule refresh can matter, but preserve exact timing and avoid repeatedly accessing real protected data. No global bypass claim follows from one route/hostname; origin controls can differ per listener, path, or tenant.

## Evidence, stop, and reopen

Save scope/attribution basis, edge and origin connection details, successful normal controls, actor/resource state, protected semantic result, TLS verification, timestamp/deployment differences, and the strongest rejected benign explanation.

Park when scope is unclear, equivalence is not established, origin enforcement blocks the same operation, or only public/static content is reachable. Reopen for new approved attribution, a new listener/route, a changed enforcement configuration, or a concrete application trust header. Do not compensate for weak evidence with broad origin enumeration.

Use `waf_bypass_all_techniques.md` for filter/consumer parser differences and `host_header_attacks.md` for authority changes. Neither is automatically required by origin discovery.

## Sources and version limits

Source review: 2026-11-13. Cloudflare deployment controls depend on customer configuration; the same hostname can combine several independent protections.

- [Cloudflare — Protect your origin server](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/): origin exposure and independent protection mechanisms.
- [Cloudflare — Authenticated Origin Pulls](https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/): origin-side client-certificate authentication; check actual deployment and certificate policy.
- [PortSwigger — Host header attacks](https://portswigger.net/web-security/host-header/exploiting): controlled authority/routing differentials and proof beyond hostname reflection.
- [HTTPWG — RFC 9110](https://httpwg.org/specs/rfc9110.html): authority and request routing semantics relevant to SNI/Host comparison.
