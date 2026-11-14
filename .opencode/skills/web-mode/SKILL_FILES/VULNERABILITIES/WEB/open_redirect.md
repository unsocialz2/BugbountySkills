# Open redirects — parsing, navigation and downstream bindings

## Navigation

Destination discovery → canonical URL controls → actual navigation → conditional chains → evidence.

## Boundary and discovery

Investigate return/continue/navigation parameters, saved destinations, cookies, postMessage handlers and client router state observed in normal flows.
The security question is whether an attacker can choose a destination outside the product's intended navigation trust boundary.
A redirect may be HTTP Location, meta refresh or a client-side navigation API; Location is not the only evidence.
Start with an inert owned marker path, then an external reserved URL or an owned permitted destination.
Do not send real tokens, user identifiers or customer data to an external destination.

## Map the pipeline

Record raw input bytes → each decode/normalization step → validation parser → storage → navigation sink → final browser URL.
Determine whether the product permits arbitrary destinations intentionally and whether program policy accepts this issue.
Record the base URL used for relative parsing; the same string can resolve differently with a different base or scheme.
Separate display text from the actual href/navigation target.
A validator accepting a URL is not the same as a browser navigating there.

## Controls

1. Capture one normal allowed internal return destination and its final location.
2. Try an ordinary external owned destination to characterize the intended policy.
3. If blocked, choose a parser differential justified by code or observed transforms.
4. Observe final canonical URL in the actual browser and preserve the redirect chain.
5. Repeat from a clean applicable session/state so a saved previous destination does not confound the result.

## PAYLOADS — parser outcomes, not a universal bypass list

Given base `https://app.example.invalid/start`, common WHATWG URL outcomes are:

| Candidate input | Canonical host / relationship | Purpose |
|---|---|---|
| `/AUDIT_MARKER_7e31` | `app.example.invalid` | Internal positive control. |
| `https://probe.example.invalid/AUDIT_MARKER_7e31` | `probe.example.invalid` | Simple external destination control. |
| `//probe.example.invalid/AUDIT_MARKER_7e31` | `probe.example.invalid` | Scheme-relative destination. |
| `https://app.example.invalid@probe.example.invalid/` | `probe.example.invalid` | Userinfo/host distinction if validation confuses them. |
| `https://probe.example.invalid@app.example.invalid/` | `app.example.invalid` | Negative control; this is not an external-host escape. |
| `https://app.example.invalid.probe.invalid/` | `app.example.invalid.probe.invalid` | Host-boundary check only when the observed matcher is textual. |
| `https://probe.example.invalid/#app.example.invalid` | `probe.example.invalid` | Fragment text is not host authorization. |

Do not label `https://app.example.invalid\\@probe.example.invalid` an automatic browser escape; special-scheme backslash normalization can leave the host as app.example.invalid.
Encoded slash/backslash forms require observing the exact decode order and actual final URL, not copying a payload name.
For a local parser check:

```javascript
const base = 'https://app.example.invalid/start';
for (const raw of [
  '/AUDIT_MARKER_7e31',
  '//probe.example.invalid/AUDIT_MARKER_7e31',
  'https://app.example.invalid@probe.example.invalid/',
  'https://probe.example.invalid@app.example.invalid/'
]) {
  const url = new URL(raw, base);
  console.log({raw, origin: url.origin, hostname: url.hostname});
}
```

A local URL result validates that parser example only; the application may use different parsers or reject input before navigation.
Never treat `javascript:` accepted in an HTTP Location header as equivalent to a DOM navigation to that scheme.
Use the XSS guide if an actual script-capable navigation sink is reachable.

## Discriminating experiments

| Hypothesis | Paired comparison | Required proof |
|---|---|---|
| Weak host comparison. | Legitimate host vs owned host matching the actual weak rule. | Navigation reaches an unauthorized host. |
| Validation before decoding. | Original allowed path vs one justified encoded delimiter variant. | Validator and sink interpret the same bytes differently. |
| Persisted previous URL. | Fresh saved internal path vs same flow with marker destination. | Attacker can set the stored value and victim later consumes it. |
| Client-only redirect. | Original HTML response vs runtime navigation with same input. | Browser reaches destination despite no Location header. |
| Relative path confusion. | Same value under recorded base vs altered base controlled by attacker. | Attacker controls the base and final navigation crosses trust. |
| Server forward rather than redirect. | Normal destination vs observed alternate route. | Protected backend action/data, not merely an offsite URL, is reached. |

## Chains must preserve downstream bindings

For OAuth, prove which response artifact reaches the destination and whether client/redirect/PKCE/state/exchange constraints leave it usable.
An open redirect alone is not an OAuth code theft or account takeover.
For SSRF, show that the server fetcher follows the redirect and fails to revalidate the destination; a browser redirect does not establish server fetching.
For CSP, test the final resource and redirect matching under the actual policy; an allowed first hop does not universally authorize an arbitrary final script host.
For referer leakage, capture actual browser referrer policy and outgoing request; modern defaults may omit path/query cross-origin.
No downstream step should require inventing attacker knowledge or victim interaction that the first primitive cannot supply.

## Evidence and stopping

Save entry point, attacker control, exact encoded bytes, storage lifecycle if present, full chain, final browser URL and required interaction.
Use a harmless destination marker; do not publish phishing content for proof.
A visible confirmation/interstitial changes delivery and must be recorded rather than silently clicked away in the PoC description.
State standalone impact and eligibility separately from any proven chain.
Stop a chain when a binding is correctly enforced; report the narrower behavior where policy permits.
Reopen for a new parser stage, stored destination consumer or downstream artifact supported by evidence.

## Primary references

Sources reviewed 2026-11-13; parser and downstream-library behavior are context-sensitive.

- [PortSwigger DOM open redirection](https://portswigger.net/web-security/dom-based/open-redirection) — client-side sources and navigation sinks.
- [WHATWG URL](https://url.spec.whatwg.org/) — host, userinfo, relative resolution and special-scheme parsing.
- [OWASP Redirects and Forwards](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) — intended navigation boundary and validation.
