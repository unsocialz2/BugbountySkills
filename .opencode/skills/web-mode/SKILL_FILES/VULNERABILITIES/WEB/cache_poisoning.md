# Web Cache Poisoning — key, storage, and clean-consumer differentials

## Contents

- Model the boundary
- Begin with cheap discovery
- Controls and experiment matrix
- Context-specific payloads
- Prove the consumer effect
- Falsify competing explanations
- Evidence and closure
- Sources and version limits


Use this guide for shared edge, reverse-proxy, application, or framework caches that may reuse an attacker-influenced response for a different request. A reflected header, absent `Vary`, or `HIT` label is a lead, not the finding.

## Model the boundary

Write the suspected invariant: a clean request must not receive an unauthorized representation selected by another request's untrusted input.

Record:
- cache layers observed, which layer emits each status/age header, and whether origin output is separately cached;
- method, normalized URL, host, query, cookies, negotiated headers, and identity dimensions that may enter each key;
- request inputs used to select content, redirects, scripts, links, or business data;
- storage rules, TTL/revalidation, and whether the output is private, public, or intentionally personalized;
- the attacker's ability to prime a cache and the consumer's actual matching request.

Do not infer a key from `Vary` alone. Implementations can add custom key dimensions or ignore parts of request URLs; multiple caches can disagree. `Cache-Control: public` permits particular caching behavior but does not prove that any tested response was stored.

## Begin with cheap discovery

1. Select an approved, researcher-owned, low-impact cacheable resource or isolated lab route; avoid home/login/shared script paths.
2. Establish an identical-request baseline and record body hashes, `Age`, validators, cache status, redirects, and timestamps.
3. Vary a harmless marker in one observed input. Compare whether the marker affects the response and whether that affected output survives in a subsequent clean request.
4. If no safe cache namespace can be isolated, retain the keying hypothesis and request a permitted test mechanism rather than priming a production shared key.
5. Keep discovery separate from exploitation: a marker carried through a cache proves a reuse condition; a security-relevant consumer effect still needs proof.

## Controls and experiment matrix

Use a unique `AUDIT_ID` per experiment, an owned synthetic object, two independent clients when relevant, and a confirmed cache-keyed isolation dimension. A random query parameter is not automatically keyed.

| Hypothesis | Test and matched control | Evidence that distinguishes it |
|---|---|---|
| Response depends on an unkeyed header | Prime a test key with marker header; consume the same key without it; compare a fresh key and a baseline header value | Marker persists only for the primed key in a clean response; origin direct reflection alone is insufficient |
| Query key and application parser disagree | Compare omitted, ordinary, encoded, and duplicate representations of one observed parameter; keep application semantics controlled | Different origin-selected outputs collide at the same effective cache key |
| Host/port normalization differs | Use only approved authorities/ports and an isolated route; compare location/resource URL construction with a baseline host | Clean canonical request receives an output selected by the alternate authority |
| Negotiated representation is incompletely keyed | Compare legitimate HTML/JSON or language variants before priming either | A clean consumer receives the wrong security-relevant type/content, not merely an intended shared translation |
| Internal cache survives edge busting | Change a verified edge-keyed nonce while holding an observed internal key constant | Affected result crosses distinct edge keys; use source/config/log evidence if available to attribute layer |
| Revalidation preserves attacker-selected metadata | Compare fresh fetch, conditional request, expiry, and clean revalidation with distinct markers | A stale harmful representation persists through the actual cache lifecycle; a `304` alone proves no body reuse |

Choose a hypothesis from actual traffic/source/configuration; this is not a universal header spray.

## Context-specific payloads

These are harmless canaries, not automatic exploits. Replace paths and `AUDIT_ID` with the isolated fixture. `.invalid` intentionally does not provide an external callback.

```http
GET /audit-cache/AUDIT_ID/view HTTP/1.1
Host: app.example.invalid
X-Forwarded-Host: audit-marker.example.invalid
```

Run the matching clean consumer without `X-Forwarded-Host`, then a fresh `AUDIT_ID` control. Require proof that this namespace is included in the affected layer's key.

```text
?format=html&probe=AUDIT_MARKER_A
?format=html&probe=AUDIT_MARKER_B
?format=html
```

If the application never reads `probe`, these requests do not test a content-selection boundary. Prefer a real benign field exposed by the feature.

```text
?view=AUDIT_MARKER_A&view=AUDIT_MARKER_B
?view=AUDIT_MARKER_B&view=AUDIT_MARKER_A
```

Duplicates test a parser/key disagreement only if the feature accepts the request and the selected value is observable. Use `http_parameter_pollution.md` to map accessor behavior first.

For framework caches, use a test object whose displayed revision can change from `AUDIT_MARKER_A` to `AUDIT_MARKER_B`; compare authorized reads before/after a normal update and with independent edge-key variations. Never assume a framework name proves a known cache issue is deployed.

## Prove the consumer effect

Keep four facts separate:
1. the input is attacker-controlled and changes origin output;
2. the changed output is actually stored;
3. a clean request with different authority/input receives that output;
4. the reused representation changes data access, executable origin behavior, navigation trust, or another protected capability.

For a redirect, show actual destination handling and any downstream validation. For a resource URL, use a harmless local marker under controlled origins; do not infer script execution from an HTML string. For personal data, use synthetic account records only. A second IP is not inherently required; clean matching requests and independence from injected headers/session state are what matter.

## Falsify competing explanations

- direct reflection on both requests because the client retained an injected header;
- service-worker/browser cache rather than shared cache;
- intentionally varied key, private session cache, or cache miss;
- a stale deployment/replica returning the same content without caching;
- a debugging header that always says `HIT` regardless of response storage;
- benign reflected text with no harmful consumer sink;
- a cache-buster that accidentally selects a different application object.

Repeat only enough to separate these explanations, with a fresh test key when needed. Do not increase impact by affecting unrelated users.

## Evidence and closure

Save exact priming, clean retrieval, and fresh-key control requests/responses, timestamps, hashes, cache/validator headers, isolation proof, attacker/consumer credentials model, and the final observed effect. Document which cache layer is known versus inferred.

Report transient impact if a wrong representation was consumed before expiry/repair; later invalidation does not undo disclosure. If only origin reflection or header oddities were observed, keep a lead. A successful control on one key does not clear every cache layer or representation. Reopen for a different observed key rule, framework path, invalidation transition, or deployment change.

Cleanup only researcher-created objects and permitted test keys; do not purge a whole site's cache. Numeric severity belongs to `reporting-mode` after actual effect and scope are established.

## Sources and version limits

Source review: 2026-11-13. These examples are methodology canaries; no live vendor configuration was exploited during authoring.

- [PortSwigger — Web cache poisoning](https://portswigger.net/web-security/web-cache-poisoning): discovery of unkeyed inputs, harmful output, and storage are distinct stages.
- [PortSwigger — Gotta cache 'em all](https://portswigger.net/research/gotta-cache-em-all): path delimiters, normalization, and layer disagreement; research examples are stack/configuration-specific.
- [HTTPWG — RFC 9111](https://httpwg.org/specs/rfc9111.html): storage, freshness, validation, and `Vary` matching semantics; deployment compliance must be observed.
- [MDN — Vary](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Vary): the response field nominates request headers; its absence is not a complete cache-key inventory.
