# Web Cache Deception — private representation stored under a public-looking key

Use this guide when a cache and application may interpret a request path differently, causing an authenticated response to be retrievable by a consumer without the original authority. It is not limited to appending `.css`.

## Define the invariant and actors

Write: a private representation for actor A must not become available to actor B/anonymous through shared storage.

Use an owned account A containing a unique non-sensitive marker, a second clean client, and an isolated test URL. Record the legitimate private page/API, its data, authentication mechanism, normal anonymous denial, and the cache's evidence of storage.

Map at least:
- application route matching versus cache static-extension/directory/file rules;
- path decoding, normalization, delimiter handling, and extension/content negotiation;
- cache key dimensions, including query/cookies/auth and redirects;
- actual victim navigation/rendering conditions needed to seed the entry;
- whether output is really private or intentionally public/shareable.

No vendor name or historical patch date certifies the configuration. A dynamic body under a static-looking path is a lead until clean private-data retrieval is shown.

## Cheap discovery without a confirmed primitive

1. Capture A's normal private response containing `AUDIT_PRIVATE_A` and anonymous denial for the exact resource.
2. Append an ordinary random suffix. If both nonexistent paths return the same generic page, fix route controls before testing delimiters.
3. Test one architecture-plausible delimiter or static-path rule with a harmless suffix and observe route identity, status, body marker, content type, and cache signals.
4. Determine application path equivalence independently from caching. Test unprimed variants with a clean client before A seeds them, using distinct identifiers.
5. Seed only isolated keys containing synthetic data. A query nonce is isolation only if it is known to participate in every affected key.

## Differential experiments

| Question | Minimal test | Benign/control explanation |
|---|---|---|
| Does the origin ignore a path suffix? | `/account/AUDIT_ID` versus `/account/AUDIT_ID/audit.css` | If the suffix is a 404 or an actual static object, no private route confusion was established |
| Does a delimiter terminate origin routing? | Ordinary suffix versus `;audit=AUDIT_ID.css` or another delimiter supported by observed stack | An identical SPA shell is not the authenticated response; inspect synthetic private marker |
| Is a static directory rule applied before normalization? | Compare `/assets/AUDIT_ID/..%2faccount` with the normal private route in a lab/approved namespace | Browser, proxy, and server may normalize differently; raw request target must be saved |
| Does a known static filename trigger storage? | Compare an isolated route mapped to a static filename with a non-static suffix | A same-status response is insufficient; prove matching private content and clean cache retrieval |
| Does query/format selection alter cacheability? | Use observed `format` or serializer selectors with clean controls | A genuinely public alternate representation is not a private-data leak |
| Does authentication or ownership change invalidate storage? | Seed an owned marker, then logout/revoke or change visibility normally | A cached public snapshot may be intended; establish the product's revocation guarantee |

Do not combine normalization, delimiter, and auth changes in the first request. Localize which component changes interpretation, then test combinations justified by that model.

## Context-specific payloads

The following are candidate shapes, not a list to enumerate against every URL. `AUDIT_ID` must isolate an approved test object/key.

```text
/account/AUDIT_ID
/account/AUDIT_IDauditsuffix
/account/AUDIT_ID/audit.css
/account/AUDIT_ID;audit=AUDIT_MARKER.css
```

Use the first two as route controls. The semicolon tests matrix-parameter/delimiter behavior only where routing evidence makes it relevant.

```text
/assets/AUDIT_ID/..%2faccount
/assets/AUDIT_ID/%2e%2e%2faccount
```

These are normalization hypotheses requiring exact raw-path transmission. A normal browser or client can normalize a literal dot segment before transmission. In curl, `--path-as-is` preserves particular path forms but does not prevent every parser/proxy rewrite. No protected shared production path should be primed with these examples.

## Proving sequence

Use the following sequence on a fresh isolated variant:

```text
U0: clean anonymous request -> no private marker
A1: authenticated A request -> AUDIT_PRIVATE_A
U2: clean anonymous request, no A cookies/Authorization -> marker unexpectedly present
C3: fresh unprimed variant -> no private marker
```

Record cache indicators and timing for each step. U2 must not contain A's credential or an intended bearer share capability. Repeat using another synthetic marker/key when necessary to attribute shared reuse instead of a public origin endpoint. An authenticated response served only to A does not prove deception.

For a reported browser-delivery attack, show that the supported browser actually requests the crafted URL while authenticated. SameSite, fetch destination, navigation redirects, and the final response's rendering may change reachability. Raw curl with A's cookie demonstrates seeding potential, not necessarily attacker-to-victim delivery.

## Falsification and impact

Reject or narrow when the supposedly private data is public/shareable, the body is an SPA shell, the marker was echoed from the URL, the anonymous response is a live origin authorization defect, or client state accidentally supplies A's credentials.

If the marker is retrieved due to intended shared capability semantics, investigate capability issuance/disclosure/revocation instead of labeling the cache as the root cause. If only a stale marker is public during a short interval, capture that interval; later correction does not negate the disclosure.

Do not obtain real customer information or harvest cached sessions. The finding is the minimum demonstrated cross-authority disclosure, not an assumed account takeover.

## Evidence, stop, and reopen

Preserve raw paths before client normalization, normal A/anonymous controls, pre-seed and post-seed requests, response marker and hashes, storage attribution, key isolation, TTL/expiry observations, and realistic delivery prerequisites.

A blocked/WAF response leaves origin route semantics unknown. A protected suffix is a narrow negative, not proof that static-directory or normalization rules are safe. Reopen when a different cache layer, delimiter, route family, response type, or lifecycle event appears.

Remove permitted test objects after evidence is saved. Do not purge or populate unrelated keys. Use `cache_poisoning.md` if the attacker changes the content rather than causing the cache to store another actor's private representation.

## Sources and version limits

Source review: 2026-11-13. Paths are conditional canaries, not a claim against a currently deployed CDN.

- [PortSwigger — Web cache deception](https://portswigger.net/web-security/web-cache-deception): distinguish path mapping, delimiters, normalization, and storage rules with private-response retrieval.
- [PortSwigger — Gotta cache 'em all](https://portswigger.net/research/gotta-cache-em-all): modern static-directory/file and parser-discrepancy research beyond suffix tests.
- [HTTPWG — RFC 9111](https://httpwg.org/specs/rfc9111.html): shared-cache storage, reuse, and authentication constraints; observe actual implementations.
- [MDN — Vary](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Vary): request-header variation is one keying mechanism, not proof of complete isolation.
