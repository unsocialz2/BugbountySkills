# CSP — evaluate the actual execution policy

## Navigation

Boundary → policy inventory → controlled matrix → architecture-driven chains → evidence.

## Boundary and discovery

CSP is a browser defense around an injection path, not a vulnerability finding by itself.
Investigate a plausible source/sink with inert markers even before an executable primitive exists.
When a reachable injection is blocked, determine which policy and directive deny the particular operation.
Do not treat a policy scanner warning, report-only violation or missing directive as an exploitation result.

## Inventory the effective policy

Capture every enforced `Content-Security-Policy` header and any applicable meta policy from the actual document response.
Keep report-only policies separate; they observe violations without enforcing those restrictions.
Multiple enforced policies all constrain execution; one permissive policy does not neutralize a stricter one.
For the attempted operation resolve directive fallback, such as `script-src-elem`/`script-src-attr` → `script-src` → `default-src`.
Record nonce/hash values and placement, allowed schemes/hosts/paths, `strict-dynamic`, `base-uri`, `object-src`, frame restrictions and Trusted Types.
Do not assume a policy fetched using HEAD is identical to the rendered GET response.

## Controls before bypass work

1. Establish a normal allowed script or renderer action in the document.
2. Establish the exact attacker-controlled insertion context and transformation path.
3. Observe a blocked marker probe and its browser violation/error.
4. Check that the apparent protection is enforced rather than report-only.
5. Preserve the document's policy and browser version alongside the probe.

## PAYLOADS — local policy reasoning matrix

These examples express browser-policy expectations, not a target bypass list.
Run them in a synthetic page first if local execution is available; do not label them tested unless actually executed.
The nonce below is a known fixture value, not a prediction about a victim's nonce.

| Policy fragment | Probe | Expected boundary |
|---|---|---|
| `script-src 'self' 'unsafe-eval'` | `<script>window.__AUDIT_MARKER__=1</script>` | Inline injection remains blocked absent another applicable allowance. |
| `script-src 'nonce-audit123' 'unsafe-inline'` | Same script without nonce. | Nonce-capable browsers ignore this unsafe-inline allowance in the relevant source list. |
| `script-src 'nonce-audit123'` | `<script nonce="audit123">window.__AUDIT_MARKER__=1</script>` | Positive fixture control; a real attacker still needs to satisfy the nonce boundary. |
| `script-src 'unsafe-inline'` with no stronger applicable constraint | Marker inline script. | Inline may execute; identify an actual injection and verify the full effective policy. |
| `script-src 'self'` | `<script src="/owned-marker.js"></script>` | Requires same-origin script content under attacker control and correct serving semantics. |

`unsafe-eval` permits string compilation by already-authorized code; it does not authorize a newly injected inline script tag.
An eval-based path still requires attacker input to reach that authorized code's evaluation sink.
`strict-dynamic` propagates trust from an authorized script to scripts it loads under the supported policy semantics; a host allowlist alone is not the complete decision.
A nonce-looking attribute injected into the DOM is not necessarily the nonce accepted by the enforced header.

## Context-specific experiments

| Hypothesis | Minimal probe / control | What must be proved |
|---|---|---|
| Nonce controlled by request input. | Change one input marker; compare document header and legitimate script nonce. | The attacker can choose/learn and reuse a matching nonce in the same exploitable document, not a different cached response. |
| Trusted same-origin upload executes as script. | Owned `owned-marker.js` containing `window.__AUDIT_MARKER__=1;`; compare inert text upload. | Upload URL, MIME/nosniff/disposition, authentication and script loading all work in the target document. |
| Allowed JSONP/function gadget. | Confirm callback semantics with a marker function in a controlled context. | The endpoint still returns executable content, the real policy permits it, and the callback grammar supports the desired action. |
| Relative trusted script redirected by base URL. | Harmless owned script marker, with and without an injected base. | Actual resolution changes and all script/base policies still allow the final resource. |
| Script-loader gadget under strict-dynamic. | Trace attacker data into an authorized loader's URL/config. | Authorized parent trust, reachable attacker-controlled load and actual execution; no universal DOM-clobbered-nonce claim. |
| Trusted Types policy accepts unsafe input. | Inert HTML marker through the actual policy, then a harmless execution probe. | Data passed the real policy and enforcing sink; policy existence alone proves neither safety nor bypass. |

Use only gadgets present in the observed application/library version.
Do not assume historical Google JSONP endpoints remain live or accept arbitrary JavaScript callbacks.
An open redirect on an allowed host does not automatically bypass CSP: destination and redirect-specific matching still apply.
If a chain needs takeover of another hostname, prove current ownership and scope independently before claiming that step.

## False-positive and false-negative checks

- A console warning is not execution; record marker state and exact executing frame/origin.
- A successfully loaded response may still have a non-executable MIME type or fail strict MIME checks.
- Disabling CSP, adding a permissive extension, or changing the response header is behavior-changing instrumentation.
- A failed payload only closes that code/context/policy path; it does not establish global absence of exploitable injection.
- Different routes can return different policies; compare the actual reader route where the victim consumes input.
- Cached nonce reuse is a hypothesis requiring attacker knowledge and matching response binding, not automatic execution.

## Evidence and stopping

Save the original injection path, full enforced policy set, allowed and blocked controls, loader/gadget source and runtime marker.
Record browser/version and any Trusted Types enforcement or configuration.
Keep HTML injection, CSP bypass, script execution and downstream authority as separate proven steps.
Report the demonstrated XSS capability; do not add arithmetic points to severity for defeating CSP.
Stop a chain when its required load, callback or nonce relation is independently protected.
Reopen for a different real policy, supported gadget, script-serving path or configuration change.

## Primary references

Sources reviewed 2026-11-13; endpoint gadgets and browser support remain version-sensitive.

- [PortSwigger CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy) — evaluating CSP around XSS and gadget-dependent exploitation.
- [MDN CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) — nonce/hash, unsafe-inline/unsafe-eval and strict policy semantics.
- [MDN Trusted Types](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API) — policies, injection sinks and enforcement.
