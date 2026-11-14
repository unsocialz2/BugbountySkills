# WAF and Application Differentials — preserve valid sink semantics

Use this guide when an intermediary blocks a concrete application experiment or when evidence suggests the security layer and consuming parser interpret equivalent input differently. WAF evasion is a technique, not an independent finding or a vendor-wide property.

## Define the question

Write which application boundary is under investigation and which layer currently blocks observation. A blocked payload is not evidence that the origin is vulnerable. Discovery may begin with harmless markers before an executable primitive is known, but escalation must still prove the actual sink and effect.

Map raw bytes, transport decoding, body parser/content type, inspection transformations, gateway rewrites, application normalization, and final consumer (HTML, JavaScript, SQL, template, URL, filesystem). Record WAF/ruleset/config/version only when known. Header fingerprints and vendor names do not identify every rule or runtime setting.

Use a test route and synthetic data. Do not use flooding, slow-drip connections, oversized bodies beyond program policy, or protocol desynchronization as generic ways to get past a block. Prefer a permitted local fixture when inspection details require intrusive testing.

## Cheap discovery and controls

1. Capture a stable successful normal request and response marker.
2. Send a harmless context-specific marker that isolates input parsing from the suspected dangerous syntax.
3. Compare a blocked candidate with a benign lookalike of similar length/shape; distinguish WAF, application validation, auth, and rate-limit responses when possible.
4. Propose one transform the consumer actually understands. Verify locally that it preserves intended semantics before changing the target request.
5. If the transformed request passes the edge, trace it to the real application result. A status change alone only demonstrates a filtering differential.

## Focused differential experiments

| Hypothesis | Probe and paired control | Required result / limiting explanation |
|---|---|---|
| Decoder order differs | Harmless marker encoded once versus twice, compared with raw marker | Application-visible value changes exactly as predicted; escaping that leaves inert text is not execution |
| Parser/content-type mismatch | Equivalent valid body in two content types already supported by the feature | Same business action reaches different validation; an invalid body or unsupported type is not a bypass |
| Duplicate selection differs | Two valid marker values in both orders | Authorized and consumed values differ; use HPP guide rather than assuming first/last behavior |
| Header/path normalization differs | An architecture-supported route representation with the same normal object | Protected semantic action changes, not just a different edge error |
| Inspection size is limited | In a local/approved fixture compare just below/above the documented configured limit with harmless markers | Full body reaches application while relevant inspection does not; oversize Match/deny may correctly stop it |
| Origin route has different controls | Only on an explicitly approved origin, compare the same valid operation with controlled authority | Application boundary is demonstrably weaker; origin exposure alone is not a vulnerability |
| Unicode conversion changes syntax | Match a documented application normalization/conversion with equivalent harmless test characters | The final parser receives a syntactically meaningful value; Unicode appearance or WAF acceptance is insufficient |

Choose the experiment that answers the blocking question. Do not select by a list of vendor payloads.

## Context-specific payloads

Harmless HTML parsing markers distinguish text rendering from tag construction:

```html
<span data-audit="AUDIT_ID">AUDIT_MARKER</span>
```

Compare it to its HTML-escaped form in the actual sink. Rendering a span is HTML injection evidence; it does not prove JavaScript execution.

For an established JavaScript-identifier context, this parser fixture demonstrates valid versus invalid escape placement:

```javascript
// Valid identifier escape; code under test is local and harmless.
const audit = {};
const assign = new Function('audit', String.raw`audit.\u006dark = 'AUDIT_ID';`);
assign(audit);
console.assert(audit.mark === 'AUDIT_ID');
```

JavaScript Unicode escapes in identifiers do not make `\u0028` a substitute for a punctuation token `(`. Percent-encoding inside script text is not automatically decoded by the JavaScript parser. Different outer decoders require separate proof.

For a known form-decoding boundary:

```text
value=AUDIT%5FMARKER
value=AUDIT%255FMARKER
```

Observe whether one or two decodes occur. An input that the WAF ignores but the app stores as literal `%5F` has not preserved the desired semantics.

For body-size reasoning, record the actual protected service, configured limit, oversize behavior, inspected component, and whether the app consumes the trailing marker. Do not assume an arbitrary padding length evades AWS WAF: documented defaults vary by service and can be increased; oversize handling may block the request.

## Prove the application outcome

Use the owning XSS/SQLi/SSRF/auth guide to establish the final boundary. If a harmless canary is sufficient to prove the parser discrepancy, retain that narrow result until a permitted experiment demonstrates the protected capability.

Keep WAF block, bypassed filter decision, backend acceptance, and attacker advantage as separate observations. Validity of one variant does not establish that it works against all rulesets, browsers, encodings, or inputs. Avoid static severity additions for bypassing a defense.

## Falsification and lifecycle

Try cache variance, rate-limiter recovery, a different backend instance, bot challenges, an unsupported request that skipped the real operation, and edge errors with misleading `200` status. Repeat the matched normal control after auth/session changes.

If a bypassed input is later sanitized or rolled back, inspect any permitted transient read/action before dismissing it. If the consumer remains safe, the filter differential alone is not the application finding. Do not keep cycling variants when no new information about the consumer is obtained.

## Evidence and bounded closure

Save original and transformed bytes, local syntax/semantic check, exact decode/context, normal/blocked/transformed controls, tool normalization settings, layer attribution confidence, and final runtime/state evidence. Record uncertain version/config facts as unknown.

A blocked test is blocked coverage. A successful transformed probe with no protected effect is a parser/filter lead. Reopen only for a new observed sink, conversion, supported representation, origin route, or configuration change. Use `url_parser_differentials.md`, `http_parameter_pollution.md`, or `http_request_smuggling.md` for those specific mechanisms; they are not interchangeable bypass knobs.

## Sources and version limits

Source review: 2026-11-13. No claim that a listed vendor accepts these canaries. Verify deployed inspection settings instead of relying on product names.

- [PortSwigger — Unicode overflow research](https://portswigger.net/research/bypassing-character-blocklists-with-unicode-overflows): conversion-specific blocklist gaps; not arbitrary Unicode execution.
- [PortSwigger — Server-side parameter pollution](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution): parser/encoding boundaries with controlled semantic effects.
- [AWS — Oversize request components](https://docs.aws.amazon.com/waf/latest/developerguide/waf-oversize-request-components.html): service-specific body limits and oversize handling choices.
- [Cloudflare — URL normalization](https://developers.cloudflare.com/rules/normalization/): configurable normalization layers and why observed normalization matters.
- [HTTPWG — RFC 9110](https://httpwg.org/specs/rfc9110.html): message semantics and representation metadata; malformed syntax is not equivalent to a normal valid operation.
