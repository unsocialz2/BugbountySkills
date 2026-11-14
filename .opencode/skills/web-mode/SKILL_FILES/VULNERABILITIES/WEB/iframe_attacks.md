# Iframes — origin, sandbox, navigation and embedding boundaries

## Navigation

Topology → origin/flags matrix → synthetic probes → real feature validation → evidence.

## Boundary and discovery

Inspect embedded editors, upload previews, user-content frames and third-party widgets when lower-trust content can exercise a stronger capability.
An iframe is a browser context, not a vulnerability class by itself.
Map parent origin, child URL/origin, sandbox attributes, response CSP sandbox, frame-ancestors, credentials and opener/navigation relationships.
Identify the intended isolation guarantee before trying to defeat it.
A cross-origin child executing JavaScript normally remains separated from the parent's DOM by Same-Origin Policy.
Do not turn third-party-widget XSS into parent-origin XSS without a separate demonstrated bridge.

## Origin and flags matrix

| Child configuration | Origin/script consequence | What does not follow |
|---|---|---|
| Unsandboxed srcdoc created by parent. | Normally shares the creator's origin, subject to applicable policy. | Not automatically attacker-controlled or executable. |
| `sandbox="allow-scripts"` without allow-same-origin. | Scripts may run in an opaque origin. | Cannot read the parent's DOM simply because it can run script. |
| `sandbox="allow-same-origin"` without allow-scripts. | Preserves normal origin identity while script execution remains restricted. | Does not itself permit child scripts. |
| Same-origin child with allow-scripts and allow-same-origin. | Can be dangerous if it can access its frame element, remove sandbox and reload. | Not a proof that every sandbox flag is irrelevant at the current instant. |
| Cross-origin child with both tokens. | Scripts and its own origin identity remain available under applicable controls. | Does not merge child and parent origins. |
| Response CSP sandbox plus attribute sandbox. | Effective restrictions combine. | Removing one attribute does not necessarily remove server-enforced sandboxing. |

With allow-same-origin, a same-origin parent may still access the child DOM even when the child cannot run scripts; distinguish parent access from child execution.
Missing allow-top-navigation does not automatically make a flow safe or unsafe; navigation permission and frame embedding are different boundaries.
A sandboxed popup may inherit restrictions unless the applicable escape token and browser semantics allow otherwise.

## Controls

1. Exercise the real preview/embed feature using synthetic inert content.
2. Record actual runtime frame URLs/origins and response policies.
3. Establish a normal allowed action inside the child.
4. Test one isolation property with a harmless marker.
5. Compare with an otherwise identical fixture in which that permission is absent.

## PAYLOADS — local origin observation fixture

The fixture below is for owned synthetic pages, not a target exploit.
It reports whether the child can access a harmless parent property and sends no sensitive data.

```html
<script>
window.addEventListener('message', event => {
  if (event.source !== document.querySelector('#auditFrame').contentWindow) return;
  console.log({senderOrigin: event.origin, result: event.data});
});
</script>
<iframe id="auditFrame" sandbox="allow-scripts"
  srcdoc="<script>let readable=false;try{void parent.document.body;readable=true}catch(e){}parent.postMessage({audit:'AUDIT_MARKER_7e31',parentReadable:readable},'*')</script>">
</iframe>
```

Repeat the local fixture without sandbox only to understand the control; changing the target's sandbox is behavior-changing instrumentation.
Observe event.origin and parent access independently: a child's location.origin display is not always a sufficient observation of an inherited/opaque security origin.
Use real runtime evidence rather than inferring authority from visible URL text.

## Conditional target experiments

| Feature evidence | Discriminating experiment | Secure/benign alternative |
|---|---|---|
| User-controlled HTML is inserted into srcdoc. | Inert marker vs harmless marker-setting code through the real writer path. | Escaping/sanitization/script restriction keeps content inert. |
| Same-origin untrusted frame has both permissions. | Determine whether normal attacker content can reach frameElement and affect a real capability. | Content is not attacker-controlled, policies remain restrictive, or no stronger capability becomes available. |
| Widget replies to parent messages. | Legitimate sender vs distinct owned origin/window. | Correct source/origin/schema binding prevents a bridge. |
| Frame can navigate a stronger context. | Controlled benign destination and actual required gesture. | Browser/sandbox blocks the navigation or only the child moves. |
| Preview offers “open in new tab”. | Same synthetic content embedded vs normal direct-open route. | Separate serving origin or response sandbox preserves intended isolation. |
| Popup escape changes authority. | Normal permitted popup flow vs the suspected flag-dependent branch. | Inherited restrictions remain or no sensitive authority is present. |

Do not silently remove a sandbox, change CSP or use a local file origin to claim production exploitability.
An arbitrary foreign frame being readable in a modified lab page is not evidence of a deployed browser isolation failure.
For sensitive actions, verify server-side authorization rather than interpreting UI access as privilege.

## Frame-related branches

Use `postmessage_attacks.md` for actual message bridges.
Use `clickjacking.md` for misdirected user gestures.
Use `cors_misconfig.md` for attacker-origin response readability.
Use `xss_reflected_stored_dom.md` for an actual executable insertion path.
Use `browser_isolation.md` for COOP/cookies/partitioning relationships.
A bridge must be demonstrated; loading several guides does not make a chain valid.

## Evidence and stopping

Save parent/child URLs, actual origin observation, flags/policies, writer control, normal rendering and minimal capability result.
Record browser/version and whether user interaction or direct-open behavior is required.
A transient forbidden read/action is relevant even if later navigation destroys the frame.
Stop a claim when execution is confined to the intentionally isolated untrusted origin with no escaped capability.
Reopen for a new serving origin, direct-open path, real bridge or configuration change.
Do not report headers or flag combinations alone as a sandbox escape.

## Primary references

Sources reviewed 2026-11-13; browser-sensitive tests require actual deployment reproduction.

- [MDN iframe](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe) — sandbox token and embedding semantics.
- [MDN same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy) — cross-frame restrictions and inherited origins.
- [PortSwigger web messages](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source) — application-level frame bridges.
- [PortSwigger Clickjacking](https://portswigger.net/web-security/clickjacking) — UI interaction is a separate boundary.
