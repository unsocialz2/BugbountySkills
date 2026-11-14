# CORS — prove cross-origin read authority

## Navigation

Boundary → controls → origin probes → browser proof → falsification → evidence.

## Boundary and discovery

Investigate whether a weaker origin can read a response protected by credentials, network position, or another trust relationship.
CORS is a browser response-read policy, not server authentication and not a general prohibition on cross-site requests.
A curl request with a fabricated Origin is a cheap discovery probe; it cannot establish browser exploitability.
Start with one real endpoint whose response contains a harmless synthetic marker in an owned account.
Identify how credentials arrive: ambient cookies, HTTP authentication, or a bearer token unavailable to attacker-origin script.
Record origin as scheme + host + port; distinguish it from schemeful site and registrable domain.

## Controls

1. Load the endpoint normally as account A and verify the synthetic marker is returned.
2. Load it unauthenticated and record whether the marker is protected.
3. Send the normal request with one foreign Origin to characterize policy.
4. Confirm from a real attacker-origin browser page whether the required credentials are sent and the body is script-readable.
5. Compare a negative origin using the same method/content type and browser state.

## PAYLOADS — origin decision probes

Replace these reserved hostnames with owned permitted origins when executing.
Send only origins relevant to the observed matching rule; not all examples are valid browser origins.

```http
Origin: https://probe.example.invalid
Origin: https://app.example.invalid.probe.invalid
Origin: https://app.example.invalid:8443
Origin: null
```

| Observed rule hypothesis | Positive control | Boundary candidate |
|---|---|---|
| Exact origin allowlist | Registered origin. | A distinct owned origin; scheme and port matter. |
| Unanchored substring check | Intended origin containing the expected hostname. | A hostname containing that string outside the allowed domain boundary. |
| Suffix check without dot boundary | Intended subdomain. | Distinct hostname ending with the same letters, only if that is what code/behavior suggests. |
| Special opaque-origin trust | Normal intended workflow. | A sandboxed document producing `Origin: null` under the real browser. |
| Version/method drift | Allowed operation on the current path. | Equivalent sensitive response through a discovered alternate path. |

An anchored host regex must be tested as written; `^https?://.*\.example\.invalid$` does not accept `https://example.invalid.probe.invalid`.
A literal `Origin: https://user@host/` is not a normal serialized browser origin.
A browser normally prevents arbitrary script modification of Origin; a server accepting a hand-built impossible header is not enough.

## Browser read proof

Use a page served from an owned attacker origin, not DevTools executed in the target's origin.
The target path below is illustrative: recover the actual read-only path from normal traffic.

```html
<pre id="result">waiting</pre>
<script>
fetch('https://app.example.invalid/api/audit-marker', {
  credentials: 'include'
}).then(async response => {
  const body = await response.text();
  document.querySelector('#result').textContent =
    JSON.stringify({status: response.status,
                    hasMarker: body.includes('AUDIT_MARKER_7e31')});
}).catch(error => {
  document.querySelector('#result').textContent = error.name;
});
</script>
```

Do not transfer the response to an external collector.
A rejected Promise, an opaque response, or a readable public login page does not prove a sensitive read.
`credentials: 'include'` requests credential use but does not override SameSite, partitioning or third-party-cookie restrictions.
A custom Authorization header cannot be filled with a victim token the attacker does not possess.

## Opaque-origin branch

For a realistic `null`-origin candidate, use `sandbox="allow-scripts"` without `allow-same-origin` around a synthetic read PoC.
Unsandboxed srcdoc normally inherits its creator's origin; srcdoc alone is not a null-origin primitive.
Record the actual request Origin and cookie behavior; do not infer them from the markup.
Any postMessage proof channel should send only a boolean marker and validate `event.source`; it does not grant parent-origin authority.

## Distinguishing the possible outcomes

| Observation | Interpretation |
|---|---|
| ACAO reflects an origin, no protected browser-readable response. | Policy anomaly/lead, not demonstrated data exposure. |
| ACAO `*`, credentialed request. | Browsers do not treat wildcard ACAO as authorization for a credentialed read. |
| Successful preflight, actual response fails CORS. | Read remains blocked. |
| Actual response readable only without victim credentials, data public. | No protected read demonstrated. |
| Sensitive response readable from an unauthorized origin using browser-supplied authority. | Boundary failure supported within the tested context. |

CORS without cookies can still matter for a network-restricted service or a different authority model; state that model explicitly.
Inspect preflight and actual response separately, including redirects and exposed headers needed by the attack.
If policy varies with Origin, investigate cache variation only when actual shared-cache behavior supports that hypothesis.

## Evidence, stop and reopen

Save normal/unauthenticated controls, attacker origin, browser request credentials, actual response CORS headers and marker readability.
Preserve browser version, cookie policy and top-level site/partition; localhost ports alone do not model arbitrary cross-site hosting.
Narrow the claim to data actually readable; do not infer account takeover from `/me` metadata.
Park browser-blocked reads with the exact blocking condition; reopen for a new credible origin, credential context or response path.
Use `csrf_all_types.md` for state changes that do not require reading responses.

## Primary references

Sources reviewed 2026-11-13; reproduce browser-sensitive behavior on the actual browser/version.

- [PortSwigger CORS](https://portswigger.net/web-security/cors) — misconfigured origin trust and null-origin cases.
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS) — credentialed reads, preflight and wildcard restrictions.
- [MDN iframe](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe) — sandbox origin behavior.
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) — SameSite and partitioned-cookie prerequisites.
