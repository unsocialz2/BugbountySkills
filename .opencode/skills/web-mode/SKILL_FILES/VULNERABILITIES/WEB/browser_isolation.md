# Browser isolation — origin, site, partition and window authority

## Navigation

Topology → authority model → diagnostic probes → controlled boundary experiments → evidence.

## Purpose and boundary

Use this guide to interpret a concrete browser security hypothesis involving cookies, frames, popups, isolated content or storage.
Missing COOP/COEP/CORP headers or a “weak” cookie attribute is not automatically a reportable vulnerability.
Identify the stronger authority the attacker is trying to exercise: read a protected response, cause an action, receive a message, access a parent, or infer a secret.
Then identify which browser boundary is expected to prevent it.
This guide supports XSS/CORS/CSRF/postMessage/XS-Leak tests; it does not invent a standalone bypass from a header list.

## Model the actual topology

| Concept | Record | Common mistake |
|---|---|---|
| Origin | Scheme, host and port for each context. | Treating sibling hosts or different ports as same-origin. |
| Schemeful site | Scheme plus registrable-domain/public-suffix relationship. | Treating same-site as permission for cross-origin DOM access. |
| Cookie scope | Host-only/Domain, Path, Secure, HttpOnly, SameSite, Partitioned. | Assuming every parent-domain cookie is script-readable or sent in every context. |
| Storage/cache partition | Top-level site, embedded origin and browser policy. | Extrapolating one localhost test to arbitrary public hosting. |
| Browsing context group | Opener/reference availability and COOP decisions. | Assuming a popup handle always survives navigation. |
| Resource embedding | Destination type, CORS mode, CORP/COEP and CSP. | Treating fetch, img, iframe and navigation as equivalent. |

Use an authoritative current public-suffix source when registrable-domain boundaries matter.
A visible URL string may not describe an inherited or opaque security origin completely.
Policy/configuration declarations and browser-observed effects must be kept separate.

## Controls

1. Reproduce the normal feature in a fresh owned test context.
2. Record origins/top-level site, browser version and cookie/storage configuration.
3. Establish a positive control for the browser capability under investigation.
4. Change one topology dimension: origin, site, ancestor, navigation, storage partition or credential state.
5. Observe the specific read/action/reference, not a generic success page.

## PAYLOADS — harmless diagnostics

These observations describe the local executing context; they do not prove an exploit.

```javascript
console.log({
  documentURL: location.href,
  serializedLocationOrigin: location.origin,
  isSecureContext,
  crossOriginIsolated,
  hasOpenerReference: Boolean(window.opener)
});
```

For an owned child context, test parent DOM authority without reading content:

```javascript
let parentDOMReadable = false;
try { void parent.document.body; parentDOMReadable = true; } catch (_) {}
console.log({parentDOMReadable});
```

For cookie analysis, use the browser's network/storage tools on synthetic cookies and requests.
`document.cookie` does not expose HttpOnly cookies and does not prove whether a cookie was sent on a particular request.
A missing opener reference can follow intended isolation or invocation style; compare with the normal control.
`crossOriginIsolated === false` alone is neither a data leak nor an authorization failure.

## Conditional experiment matrix

| Hypothesis | Minimal paired experiment | Required semantic result |
|---|---|---|
| Same-site untrusted sibling can cause a protected action. | Actual sibling-host attacker page vs unrelated-site page, same action. | Credentials and the unauthorized action occur under the claimed hosting capability. |
| Cookie partition escapes tenant/top-level boundary. | Synthetic marker cookie/resource under two real top-level sites. | The wrong partition gains protected authority; header presence alone is not enough. |
| Popup/reference leak. | Normal popup flow with and without the relevant navigation. | Attacker retains an observable allowed property/channel that reveals protected information or grants action. |
| Untrusted preview shares product origin. | Embedded preview vs normal direct-open path with synthetic content. | Attacker-controlled content gains product-origin capability or a real bridge. |
| CORP/COEP difference exposes an oracle. | Controlled resource states and identical embedding mode. | Foreign-origin script can distinguish the protected states in the actual browser. |
| Trusted Types deployment gap. | Enforced route/policy vs alternate actual reader path. | Untrusted input reaches an executable sink without intended transformation. |
| Service-worker persistence path. | Normal allowed registration/resource scope vs attacker-controlled script URL. | Actual attacker-controlled script can register/control a protected scope under supported browser rules. |

Do not “prove” the worker branch by manually installing a service worker with DevTools or weakening response headers.
Service workers require their own origin/scope/serving constraints; arbitrary upload does not automatically meet them.
A resource blocked by one defense may still be requestable via another mode, but that is only useful if it crosses the original invariant.
Do not disable browser security features to turn blocked behavior into a production finding.

## Choose the owning method

- Protected response read: `cors_misconfig.md`.
- Ambient-auth state change: `csrf_all_types.md` or `client_side_csrf.md`.
- Message bridge: `postmessage_attacks.md`.
- Frame isolation: `iframe_attacks.md`.
- Executable insertion/persistence: `xss_reflected_stored_dom.md`.
- Cross-origin inference: `xs_leaks.md`.

Follow one feature across those boundaries when evidence connects them; do not run all guides as a universal checklist.
A failure at one layer can be a useful lead for a different supported mode; it is not permission to fabricate a bypass.

## Evidence and stopping

Preserve actual origin/site/partition topology, policy response, browser/version and capability controls.
If the impact exists only during navigation or before revocation, capture the relevant transient event.
Separate default browser behavior, product-selected supported configuration and behavior-changing lab modifications.
Narrow conclusions to the tested browser/context; another browser is a new hypothesis requiring reproduction.
Stop when the proposed authority is correctly isolated or no attacker-controlled context can reach it.
Reopen for a real hosting change, new supported browser behavior, alternate rendering origin or demonstrated bridge.

## Primary references

Sources reviewed 2026-11-13; isolation defaults/support vary by browser and version.

- [MDN same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy) — origin and window access boundaries.
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) — cookie scope, SameSite and Partitioned semantics.
- [MDN COOP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy) — browsing-context groups and opener isolation.
- [PortSwigger DOM-based vulnerabilities](https://portswigger.net/web-security/dom-based) — attacker sources and security-relevant browser sinks.
- [XS-Leaks Wiki](https://xsleaks.dev/) — partitioning and isolation as observable attack constraints.
