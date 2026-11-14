# URL Parser Differentials — compare validation with actual consumption

## Contents

- Define the invariant
- Cheap discovery
- Differential experiment families
- Context-specific payloads and matched outcomes
- Consumer-specific reasoning
- Falsification and evidence
- Sources and version limits


Use this guide when two components parse, decode, resolve, normalize, or navigate the same attacker-influenced URL differently. This is a shared reasoning layer for redirects, SSRF, CORS matching, proxy routing, and cache paths; it is not a list of universal bypass strings.

## Define the invariant

Write what the validator intends to constrain: scheme, canonical hostname, port, origin, registrable domain, resolved address, path subtree, redirect destination, or complete URL. These are different policies.

Map the full transformation chain:

```text
raw input -> outer transport decoding -> validation parser/normalizer
          -> serialization or string concatenation -> consumer parser
          -> DNS/resolution -> redirect handling -> final connection/navigation
```

Record exact libraries, runtime versions, base URLs for relative parsing, Unicode/IDNA handling, DNS timing, and each decode. Do not grant an attacker control of a host merely because it appears somewhere in the URL text.

## Cheap discovery

1. Obtain a normal accepted URL and a normal rejected URL for the real feature.
2. Identify observable output: canonical URL, browser navigation, harmless callback, fixture destination, or a route marker.
3. Compare two harmless controlled destinations or `.invalid` parser-only values before testing private/internal destinations.
4. Record which component rejects input and whether any request occurs first. Local parsing and static validation alone do not demonstrate target consumption.
5. Pick a differential from the actual validator/consumer pair. If no behavior/source suggests the pair, use a small discovery probe rather than a broad bypass sheet.

## Differential experiment families

| Boundary | Minimal comparison | What is meaningful |
|---|---|---|
| Userinfo versus host | `https://allowed.example.invalid@audit.example.invalid/` and reversed names | Validator accepts one authority while the actual consumer reaches the other; string reflection is not enough |
| Backslash handling | Ordinary slash and `https://allowed.example.invalid\@audit.example.invalid/` | WHATWG special-URL parsing and another parser may disagree; record both actual outputs |
| Relative URL resolution | `/audit/A`, `//audit.example.invalid/A`, `audit/A`, with an explicit base | A supposedly same-origin value resolves to another origin or escapes a path constraint |
| Decode depth/path delimiter | `/owned%2fchild`, `/owned%252fchild`, and ordinary `/owned/child` | The authorization/cache check and final route consume different paths |
| Fragment/query interpretation | `https://audit.example.invalid/#allowed.example.invalid` versus ordinary path/query | Fragment content is not an HTTP request path; a text matcher may nevertheless trust it |
| Host canonicalization | Case, a trailing dot, explicit default port, and permitted IDNA test names | Equivalent or non-equivalent authorities are treated inconsistently at a protected boundary |
| DNS and redirects | Two controlled hosts with stable fixture DNS; approved redirect to another controlled host | Validation checks one location but fetching reaches an unvalidated final destination |
| Host suffix comparison | Exact host versus `notallowed.example.invalid` or `allowed.example.invalid.audit.invalid` | A missing label boundary is bypassed; an anchored correct regex is not bypassed by merely appending a suffix |

Use URL parser/accessor APIs to inspect components. `endsWith` can be used safely only with a policy-aware label boundary and canonicalization; `includes` is not a host-identity test. An exact allowlist still needs correct parsing and redirect/DNS enforcement for its purpose.

## Context-specific payloads and matched outcomes

These examples are parser fixtures. They do not resolve DNS or contact a target:

```javascript
const base = 'https://allowed.example.invalid/base/';
const cases = [
  ['https://allowed.example.invalid@audit.example.invalid/', 'audit.example.invalid'],
  ['https://audit.example.invalid@allowed.example.invalid/', 'allowed.example.invalid'],
  [String.raw`https://allowed.example.invalid\@audit.example.invalid/`, 'allowed.example.invalid'],
  ['//audit.example.invalid/audit', 'audit.example.invalid'],
  ['/audit', 'allowed.example.invalid'],
];
for (const [input, expectedHost] of cases) {
  const u = new URL(input, base);
  console.assert(u.hostname === expectedHost, input);
  console.log({input, scheme:u.protocol, host:u.hostname, port:u.port, path:u.pathname});
}
```

The backslash case is deliberately **not** an offsite navigation in this WHATWG parser. It is useful only if a different validation parser disagrees. Test the actual browser/library version before using this observation as evidence.

```python
from urllib.parse import urlsplit
value = r'https://allowed.example.invalid\@audit.example.invalid/'
parts = urlsplit(value)
print(parts.hostname)
```

Compare outputs without assuming Python's parser validates URLs or that every HTTP client uses its result unchanged. Preserve the exact raw string; Markdown escaping, Python literals, shell quoting, and JSON can alter backslash counts.

For an application accepting outer query input:

```text
next=https%3A%2F%2Faudit.example.invalid%2Faudit%2FAUDIT_ID
next=%2F%2Faudit.example.invalid%2Faudit%2FAUDIT_ID
next=%252F%252Faudit.example.invalid%252Faudit%252FAUDIT_ID
```

These compare absolute, scheme-relative after one decode, and possible second-decode behavior. Use `open_redirect.md` to prove browser delivery; use `ssrf_all_types.md` to prove server-originated fetching. `.invalid` is a non-callback placeholder; replace it with a researcher-controlled host only when an actual network observation is permitted.

## Consumer-specific reasoning

- **Redirect:** inspect final browser origin/URL, interaction needed, and whether navigation occurs through HTTP Location, DOM assignment, or a link.
- **SSRF:** distinguish DNS resolution, HTTP connection, request headers/body, response visibility, redirects, and network identity. Local URL parsing proves none of these.
- **CORS:** a browser-origin serialization does not include path or userinfo. A manually forged Origin string may not be producible by a browser.
- **Cache/auth routing:** save the raw path plus every normalized path seen by edge and origin. A `404` difference does not prove another protected route was reached.
- **Filesystem URL/path:** URL semantics and filesystem normalization differ; establish the consuming API before interpreting separators or traversal.

## Falsification and evidence

Try parser rejection, safe reserialization, fixed consumer host, same-origin navigation, deliberate relative-path support, allowlisted subdomain ownership, and redirects revalidated before connection. A string containing `allowed.example.invalid` is not a successful host-boundary bypass.

Keep raw bytes, decoded intermediates, explicit base, parser/library versions, component outputs, actual final destination or harmless fixture result, and valid accepted/rejected controls. Distinguish parser-only findings from demonstrated network/browser effects. Preserve transient unauthorized connection/navigation before any corrective redirect.

Stop with a narrow negative when both actual components enforce the intended constraint. Reopen for a different consumer, additional decode, changed base, redirect stage, DNS resolution path, or alternate serializer. Do not escalate to internal service probing just because a public-host parse discrepancy exists.

## Sources and version limits

Source review: 2026-11-13. WHATWG and language APIs can evolve; run local fixtures using the exact installed runtime and recheck target consumers separately.

- [PortSwigger — URL validation bypass cheat sheet introduction](https://portswigger.net/research/introducing-the-url-validation-bypass-cheat-sheet): context-specific parser and validation research; do not treat generated values as guaranteed bypasses.
- [WHATWG — URL Standard](https://url.spec.whatwg.org/): special-scheme, authority, host, path, base URL, and serialization rules.
- [Node.js — URL API](https://nodejs.org/api/url.html): WHATWG `URL` and component accessors used in the local fixture.
- [Python — urllib.parse](https://docs.python.org/3/library/urllib.parse.html): parsing versus validation and `urljoin`/`urlsplit` behavior; not a browser-navigation specification.
- [PortSwigger — Gotta cache 'em all](https://portswigger.net/research/gotta-cache-em-all): downstream path normalization/delimiter disagreements between caches and applications.
