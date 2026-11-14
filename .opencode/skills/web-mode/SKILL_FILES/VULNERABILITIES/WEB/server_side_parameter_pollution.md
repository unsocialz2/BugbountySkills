# Server-side parameter pollution — track the request the backend constructs

## Boundary and discovery

Use when one application takes user data and constructs a request to another API, service, URL path or structured body.
The attacker may inject a second parameter or alter path/body structure if values are concatenated without the correct encoding.
This is distinct from client duplicate-parameter handling and from JavaScript prototype pollution.
An error after `&` or `#` is only a clue; prove a downstream request or semantic change.
Do not require prior exploit proof before a cheap delimiter probe on an actual proxy/integration feature.

Map:

- browser input bytes and transport encoding;
- frontend decode and validation;
- downstream request construction and target component;
- second parser/decoder and duplicate-field accessor;
- server-owned parameters such as tenant, permission, locale or visibility;
- observable downstream output/action under the original actor.

Keep raw input, decoded value and constructed request separate in notes.
A delimiter encoded once at the browser layer can become literal syntax at the downstream layer after an unsafe concatenation.

## Valid controls

Use an ordinary successful lookup/import/filter operation on researcher-owned fixtures.
Record a known valid key and a known nonmatching key.
Identify harmless supported downstream parameters from exact source/schema or observed normal traffic.
In a lab, use an echo service returning parsed parameters and a protected synthetic policy field.
Do not assume the public frontend supports the same schema as an undocumented internal API.

## Payloads and paired experiments

The examples use `name=AUDIT_ALPHA` as the normal query value. Names and field mappings are synthetic.
They demonstrate first-layer encoding for one decode; verify actual encoders before adapting them.

| Hypothesis | Frontend value/probe | Control | What distinguishes it? |
|---|---|---|---|
| An encoded delimiter becomes a downstream parameter | `AUDIT_ALPHA%26auditMarker=AUDIT_MARKER` in the outer URL value | Literal marker without `%26` | Observed downstream parameter or source-backed behavior; unchanged output alone is ambiguous. |
| A fragment delimiter truncates the constructed URL | `AUDIT_ALPHA%23AUDIT_MARKER` | Same characters encoded an additional time as a literal control where accepted | Trailing downstream parameters disappear; distinguish fragment handling from frontend validation failure. |
| Duplicate names choose a different value | `AUDIT_ALPHA%26name=AUDIT_BETA` | Normal A and normal B lookups | Result tracks effective downstream name. No universal first/last rule applies. |
| Path interpolation changes the target resource | `AUDIT_ALPHA%2F..%2FAUDIT_BETA` | Direct normal A and B requests | Actual downstream normalization reaches a different controlled resource; check object authorization separately. |
| A JSON string is concatenated unsafely | A quote-delimiter canary in a normal string field, first in a local mirror | A safely escaped string with same logical content | Preserve valid constructed JSON and compare parsed fields; generic JSON errors prove only a lead. |
| A server-owned policy is overrideable | One discovered synthetic policy key injected through the proved delimiter | Original valid policy and an inert unknown key | Unauthorized dataset/action occurs, not merely a new echoed parameter. |

A local distinction between unsafe construction and proper encoding:

```python
from urllib.parse import urlencode, parse_qs, urlsplit
value = 'AUDIT_ALPHA&auditMarker=AUDIT_MARKER'
unsafe = 'https://backend.example.invalid/search?name=' + value
safe = 'https://backend.example.invalid/search?' + urlencode({'name': value})
assert 'auditMarker' in parse_qs(urlsplit(unsafe).query)
assert 'auditMarker' not in parse_qs(urlsplit(safe).query)
```

This proves only URL construction semantics, not a remote endpoint's implementation.
For a JSON consumer use its serializer rather than constructing payloads based on URL assumptions.
For XML use XML escaping; a single encoding strategy is not portable across all contexts.

## Duplicate and normalization reasoning

A framework can expose several accessors: first, last, list or application-defined aggregation.
The same language can therefore behave differently in two endpoints.
Capture the accessor/normalizer actually consumed by the security decision.
Do not classify a comma-joined value as successful override without a valid backend action.
If the downstream URL builder encodes values or replaces duplicate keys safely, record the narrow result.
A second decode creates a different hypothesis; establish it rather than spraying nested encodings.
No URL fragment reaches an HTTP server as a fragment, but it can truncate a URL before the downstream HTTP client sends it.

## Nearest security impact

Once structural control is proved, select one server-owned boundary the application actually relies on.
Examples include fixed tenant binding, intended public-only search or an actor-bound object path.
Use controlled objects/accounts to show the difference without enumerating internal resources.
An innocuous locale override is not equivalent to an authorization failure.
A successful internal call can still return data filtered correctly at the frontend; prove what escapes that final gate.
Async jobs need worker-result evidence, not just queue acceptance.
Do not assume server-side parameter pollution grants arbitrary SSRF destinations.

## Falsification and evidence

Save outer raw request, exact decoding assumptions, normal control, downstream evidence and final semantic effect.
Distinguish frontend parsing, WAF handling, internal API validation and final output filtering.
A quote or delimiter may be rejected by intended input validation; that does not prove the unseen downstream parser is secure.
A failed path can be unsupported rather than protected; use known valid fixture routes.
Record transient result exposure even if a subsequent action fails.

Close only the tested construction path when encoding/type-safe serialization or server-owned policy preserves the boundary.
Keep absent downstream visibility, guessed keys and malformed controls inconclusive.
Reopen for another downstream client, serialization format, path representation or decode step.

## References and freshness

Reviewed 2026-11-13. Probe interpretation depends on each actual parser and accessor.

- [PortSwigger server-side parameter pollution](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution) — internal request construction, truncation, duplicates and structured data.
- [Node URL documentation](https://nodejs.org/api/url.html) — URL components and get/getAll semantics; not a universal backend accessor model.
- [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) — consistent parsing/validation of server-constructed destinations and redirect boundaries.

Use `http_parameter_pollution.md` for disagreement between public request parsers and `url_parser_differentials.md` for destination interpretation.
