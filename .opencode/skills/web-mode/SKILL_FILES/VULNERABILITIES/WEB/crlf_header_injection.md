# CRLF and HTTP Header Injection — prove the injected boundary first

Use this guide when attacker-controlled data may become a header value, request target, upstream header, or response header after decoding/rewriting. Keep response-header injection, upstream request-header injection, splitting, and persistent desync as separate claims.

## Model the transformation

Write the invariant: user data must remain data rather than terminating or introducing an HTTP field/message boundary.

Map input bytes -> outer HTTP parser -> URL/body decoding -> application/proxy interpolation -> upstream/response serialization -> receiving parser. Identify whether a library refuses control characters and whether a rewrite uses raw or normalized values.

For response injection, choose a non-cached test response and a harmless header marker. For upstream injection, prefer a local lab or explicitly permitted echo fixture with raw upstream logs. A `%0d%0a` displayed as text, generic 400, or proxy log escaping does not prove header injection.

Modern desync research shows meaningful downstream effects can follow a small primitive, but shared-connection experiments can affect unrelated users. Do not automatically proceed from a new header to request splitting or queue poisoning. Establish a permitted isolated environment for any framing transition.

## Cheap discovery

1. Find fields observed in response headers or upstream construction: download filenames, redirects, tracking fields, path rewrites, and configured proxy metadata.
2. Capture a valid ordinary control and a marker-only control.
3. Compare a single encoded line break with an ordinary separator and inspect raw headers/logs, not rendered text.
4. If the client refuses literal CR/LF, preserve that fact. An encoded request parameter can exercise a different decode/interpolation path; do not bypass client restrictions by assuming the target accepts equivalent bytes.
5. If only malformed syntax causes a status change, retain a parser hypothesis and seek a discriminating fixture trace before declaring success.

## Differential experiments

| Hypothesis | Minimal probe/control | Decisive observation / benign alternative |
|---|---|---|
| Response value permits CRLF | Marker followed by encoded CRLF and a harmless `X-Audit-Marker` field, versus marker plus ordinary spaces | A distinct response field appears; same text inside one escaped value is not injection |
| One decoder introduces control bytes after validation | Compare `%0d%0a` and `%250d%250a` at the same insertion point | Trace identifies the decode stage and separate field; blind double encoding is not proof |
| Path rewrite injects an upstream field | In a lab, compare ordinary path marker and encoded line-break path | Upstream raw request contains a new field without changing the outer request's own headers |
| LF-only and CRLF handling differ | In an isolated fixture compare encoded LF, CR, and CRLF with equal markers | Receiving parser accepts a new field; generic reject/normalize is a narrow negative |
| A value is normalized before internal URL generation | Compare source/config's raw versus normalized path assumptions using a marker | Exact field construction is established, not inferred from a vendor banner |
| Injection changes a security-relevant consumer | After field insertion is proven, select the nearest approved redirect/cache/policy boundary | Consumer actually interprets the injected value; presence alone does not establish impact |

Use one hypothesis at a time. Separate detection from an exploit that changes content length, transfer coding, cookies, CSP, or request count.

## Context-specific payloads

Illustrative outer query values, requiring the feature to decode and place the value into a header:

```text
name=AUDIT_MARKER
name=AUDIT_MARKER%20X-Audit-Marker%3A%20AUDIT_ID
name=AUDIT_MARKER%0d%0aX-Audit-Marker%3A%20AUDIT_ID
```

The second line is a non-line-break control. Inspect whether the third creates a new raw field. `%0d%0a` only becomes CRLF if the relevant component decodes it.

Decode-depth comparison:

```text
name=AUDIT_MARKER%250d%250aX-Audit-Marker%253A%2520AUDIT_ID
```

Do not claim this bypasses any control without showing both stages. It may simply remain literal percent-encoded text.

A laboratory upstream request-line interpolation test, adapted in shape from research but using a harmless marker field:

```text
/audit%20HTTP/1.1%0d%0aX-Audit-Marker:%20AUDIT_ID%0d%0aX-Audit-Tail:%20x
```

This requires a specific rewrite that decodes and interpolates the path into an upstream HTTP/1 request. Save exact outer and upstream bytes. Use it only with the controlled upstream fixture: status differences against a production site are not a substitute for isolation or proof.

## Bridge to modern desync only when warranted

After upstream header injection is confirmed, identify whether the primitive can change message boundaries, how the proxy associates responses, and whether connections are reusable. Consult `http_request_smuggling.md` for CL/TE/0/H2 meanings.

A missing upstream field in the final browser-visible response does not disprove request injection; the origin may consume it without echoing it. Conversely, a reflected new response field says nothing about upstream request splitting. Request tunnelling, connection-locked desync, IP-locked behavior, and cross-user response poisoning require different reachability proof.

Use a bounded harmless canary request in an isolated lab if a framing proof is permitted. Never demonstrate a worm, force unrelated users into a test account, or wait for another user's response to increase the finding's apparent severity.

## Falsification and evidence

Try escaped header display, multiline logging formats, canonicalization by tooling, application reflection, error-page templates, upstream security rejection, and a response already cached from another experiment as benign explanations.

Save normal and changed inputs, exact encoding layers, separate raw fields, upstream trace if available, request/response count, connection handling, and the smallest final consumer effect. Mark inference where upstream traces are unavailable. A controlled header insertion can be a valid primitive even when broader impact is unresolved; eligibility is a separate policy decision.

A transient injected policy/redirect/action may be meaningful even if a later request is corrected. Scope negative conclusions to the insertion point, transport, decoder, and receiver. Reopen for a different rewrite variable, serializer, protocol downgrade, or newly observed internal header construction.

## Sources and version limits

Source review: 2026-11-13. Examples are conditional parser/serialization tests. New research case studies do not establish a vulnerability in every Nginx/CDN deployment.

- [PortSwigger — HTTP response header injection](https://portswigger.net/kb/issues/00200200_http-response-header-injection): response-field boundary and potential consumer effects.
- [PortSwigger — CRLF-powered desync attacks](https://portswigger.net/research/crlf-powered-desync-attacks): 2026 upstream header injection research, rewriting preconditions, and connection-locked variants.
- [HTTPWG — RFC 9112](https://httpwg.org/specs/rfc9112.html): HTTP/1 message/field parsing and response-splitting concerns.
- [MITRE — CWE-113](https://cwe.mitre.org/data/definitions/113.html): weakness definition for unneutralized CRLF in HTTP headers.
