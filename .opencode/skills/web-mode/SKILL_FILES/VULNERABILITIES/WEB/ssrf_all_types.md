# SSRF — trace the effective request and the trust it carries

## Boundary and discovery

Use for URL imports, webhooks, document renderers, image proxies, previews, integration validation and background fetch jobs.
A URL field warrants a cheap discovery experiment; do not require a confirmed primitive before investigating it.
The security question is whether attacker input causes a server-side request to cross an intended destination, identity or network boundary.
Intended public URL retrieval is not automatically an SSRF vulnerability.
A callback proves only the interaction actually observed; DNS, TCP, HTTP and response disclosure are separate capabilities.

Map the fetch graph:

1. actor → accepted input and its encoding;
2. parser/normalizer/allowlist → effective URL;
3. resolver/redirect handler → chosen address and hop sequence;
4. component performing the request: frontend, worker, renderer, preview service or third party;
5. method/headers/body/credentials carried to the destination;
6. response parsing, caching and result returned to the actor.

Record which hops and fields are observed versus inferred.
Do not assume that the web request and asynchronous worker have the same network or identity.

## Valid control and canary design

Use an explicitly controlled endpoint permitted by the program; `https://canary.example.invalid/` is a placeholder, not a live service.
Return a tiny stable body such as `AUDIT_MARKER_a1`, a known content type and no external dependencies.
Assign a unique path token per experiment and save controlled server logs with timestamp/method/path.
Keep browser rendering isolated: a callback from the researcher's browser is not server-originated fetch proof.
Compare direct and feature-mediated requests without treating IP reputation as sole attribution.
For blind workflows, correlate a unique token with job creation and use a non-triggering control.

## Payloads and discriminating experiments

Replace placeholders only with permitted controlled destinations. No internal address list is needed to start.

| Question | Probe | Control | Decisive observation / limit |
|---|---|---|---|
| Does a backend fetch the URL? | `https://canary.example.invalid/audit/a1` | Same normal feature with a different controlled token and no browser opening the link | Controlled HTTP log correlates with the job. A DNS-only event proves resolution, not HTTP. |
| Is returned data exposed? | Canary returns `AUDIT_MARKER_a1` | Canary returns `AUDIT_MARKER_b1` | Output tracks canary body; distinguish app parsing from a client directly loading it. |
| Are redirects followed/revalidated? | Controlled `/redirect/a1` returns a redirect to another permitted controlled host | Direct request to the same final host | Log each hop; blocked final hop does not disprove initial server fetch. Never redirect to unapproved networks. |
| Does validation use the same parser as fetch? | Controlled URL with a benign userinfo/path delimiter relevant to observed parser | Canonical equivalent URL | Record actual connected host, not a validator status or string expectation. |
| Does host policy bind to effective destination? | Two controlled aliases with equal content but different permitted policy status | Canonical allowed host | A policy violation requires connecting to a disallowed destination under the stated product policy. |
| Does request authority leak across hops? | Controlled redirect chain recording presence of a synthetic lab-only header | Direct requests to each hop | Only synthetic headers; do not collect real credentials to decorate proof. |
| Are jobs isolated by tenant/lifecycle? | Create an owned URL-import job then remove its permission before consumption | Same job while authorized | Distinguish SSRF destination authority from separate unauthorized job-result access. |

A literal URL containing `$(...)` does not execute a shell by itself.
A JNDI-looking string inside a URL does not prove Log4Shell or SSRF execution.
Scheme support is a property of the actual client and configuration, not a property of a payload list.

## URL and DNS boundaries

Compare validation input and final parsed URL after every actual decode step.
Distinguish hostname allowlisting from resolved-address policy.
A hostname may resolve differently over time, but rebinding is relevant only if validation and connection perform separable resolution.
Observe redirect behavior rather than assuming the library follows every status code.
Use only researcher-controlled DNS/hosts for a lab discriminator; do not rebind toward arbitrary internal services.
Request normalization may differ by method or scheme; change one documented dimension at a time.
If a different URL syntax fails before connection, record parser rejection rather than network protection.

## Internal/cloud and stronger effects

Only test a stronger destination boundary when scope and program rules allow that exact step.
Prefer a program-provided synthetic internal canary or authorized lab mirror over service discovery.
Do not turn this guide into port scanning, metadata credential retrieval or a Redis protocol exploit.
A cloud metadata address in code is not evidence of reachability or accepted authentication.
Method/header restrictions can prevent accessing a metadata service even where HTTP fetching is real.
Record the narrower capability when internal access, response readback or privilege cannot be shown.

## Falsification and evidence

Test scanner/link-preview callbacks, DNS prefetch, cached results, browser-originated requests and unrelated asynchronous processing.
Save request token, normal control, app response/job id, canary logs and exact effective destination evidence.
Separate: accepted input; DNS; HTTP; header/body control; response visibility; restricted destination reached; protected effect.
Preserve a permitted transient action even when the job later fails or rolls back.
A timeout does not identify an internal service; a success page may merely acknowledge queuing.

Close only the tested destination/parser/path when normalization and redirect checks enforce the intended boundary.
Mark missing observability or unexplained callbacks inconclusive.
Reopen for an observed alternate fetcher, renderer, callback consumer or changed URL policy.

## References and freshness

Reviewed 2026-11-13. Canary examples are conditional methodology, not remote-target validation.

- [PortSwigger SSRF](https://portswigger.net/web-security/ssrf) — trust boundaries, fetch contexts and validation differences.
- [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) — allowlisting, DNS and redirect control considerations.
- [Node URL documentation](https://nodejs.org/api/url.html) — parsed URL fields and WHATWG versus legacy APIs; verify the actual fetch library separately.

Use `url_parser_differentials.md` for parser-specific investigation and `file_upload_bypass.md` for renderer/import paths.
