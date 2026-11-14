# DOM Clobbering — named properties into real consumers

## Navigation

HTML control → named-property control → consumer/gadget → execution/authority → evidence.

## Boundary and discovery

Investigate when a lower-trust writer can supply HTML with id/name attributes and application code reads named DOM/global properties.
An inert marker element is a valid discovery probe; a complete XSS primitive need not exist first.
Clobbering is property/name resolution confusion, distinct from JavaScript prototype pollution.
The impact depends on what a reachable consumer does with the resulting element, collection or string.
HTML injection alone and a clobberable global alone do not prove an exploitable chain.

## Model the lookup

Record whether the code reads `window.config`, `document.forms`, a named form property, a lexical local variable or an explicitly queried node.
A closure that reads `window.config` still reads the window property; being inside a closure does not protect that lookup.
A separately initialized lexical `const config = {...}` is a different binding.
Document existing globals/descriptors, parser context, insertion timing and whether the consumer runs before or after the injection.
Identify sanitizer version/configuration, allowed elements and any id/name rewriting.
A shadow root and a main-document named lookup have different visibility; do not generalize one to the other.

## Controls

1. Capture the normal page and the exact value the consumer reads without injected HTML.
2. Add a harmless marker element through the real lower-trust input.
3. Inspect whether the intended lookup changed, without manually overwriting the global in DevTools.
4. Observe the actual consumer action or a synthetic marker effect.
5. Repeat with an id/name that cannot match the consumer to exclude unrelated layout/timing effects.

## PAYLOADS — name/shape probes

These are candidate shapes, not guaranteed to shadow any arbitrary built-in or existing global.
Use the identifier the observed code actually reads; the names below are synthetic fixtures.

```html
<a id="auditConfig" href="https://probe.example.invalid/AUDIT_MARKER_7e31"></a>
```

In a controlled browser, observe `window.auditConfig` and the consumer's read.
For a consumer expecting `.url`, a same-id collection is one historical shape worth testing if the browser/parser and sanitizer permit it:

```html
<a id="auditConfig"></a>
<a id="auditConfig" name="url"
   href="https://probe.example.invalid/AUDIT_MARKER_7e31"></a>
```

For a form consumer, distinguish the element from its `.value` and from string coercion:

```html
<form id="auditForm">
  <input name="auditField" value="AUDIT_MARKER_7e31">
</form>
```

Do not assume `<input id=isAdmin value=true>` sets a boolean privilege flag.
Inspect the exact value/type consumed; an HTMLInputElement is not boolean true merely because its value attribute says true.
Use an inert allowed URL first; external script loading requires a separately owned, in-scope marker resource and policy permission.

## Discriminating experiments

| Hypothesis | Minimal comparison | Expected secure/benign outcome |
|---|---|---|
| Global named-property fallback. | Matching id vs nonmatching id before consumer runs. | Explicit lexical object or guarded lookup stays unchanged. |
| Multi-level property chain. | Single anchor vs same-id collection with observed property name. | Shape/type mismatch rejected or named lookup not available. |
| Sanitizer allows dangerous named properties. | Same HTML before/after sanitizer, then actual insertion. | Names stripped/prefixed or no consumer resolves them. |
| String coercion reaches URL sink. | Harmless URL marker vs plain inert element. | Consumer validates canonical URL/type or never loads it. |
| Script-loader gadget. | Benign resource marker from a legitimate URL vs clobbered URL. | Required policy/URL check blocks foreign content. |
| Timing/lifecycle dependency. | Inject before normal consumer event vs after. | Late injection cannot affect already-captured safe binding. |

Do not call a standalone console-created element a target vulnerability; demonstrate injection through the real feature and normal victim rendering.
DOMPurify configuration can isolate named properties; preserve the actual configuration instead of naming a historical bypass as universal.
A sanitizer that preserves some id/name attributes may still prevent the specific collision or remove the elements needed for a gadget.
Inspect transformations after sanitization too.

## From clobbering to impact

For a URL consumer, prove which canonical URL is loaded and under which document origin/CSP.
For an authorization-looking client flag, verify a server-side protected action; frontend UI changes alone are not privilege escalation.
For XSS, use a marker such as `window.__AUDIT_MARKER__='7e31'` in the actual executing context; do not export cookies.
A nonce gadget must satisfy the actual enforced policy and script-loader flow; no general strict-CSP bypass follows from a clobbered value.
Trace each transition independently and stop where a required step remains protected.

## Evidence, stop and reopen

Preserve injected HTML, sanitized/final DOM, changed lookup value/type, consumer stack, timing and semantic effect.
Record browser and sanitizer versions; named-property details are browser/context-sensitive.
Execution can be transient; capture it before the DOM is rebuilt.
Park when names do not collide, the consumer uses an independent safe binding, or no security-relevant sink is reachable.
Reopen for a new consumer, permitted HTML shape, rendering order or sanitizer configuration.
Do not label all HTML injection or all writable ids as DOM-clobbering XSS.

## Primary references

Sources reviewed 2026-11-13; named-property/gadget behavior needs target-browser reproduction.

- [PortSwigger DOM clobbering](https://portswigger.net/web-security/dom-based/dom-clobbering) — lookup shapes and real script consumers.
- [OWASP DOM Clobbering Prevention](https://cheatsheetseries.owasp.org/cheatsheets/DOM_Clobbering_Prevention_Cheat_Sheet.html) — risky named access and implementation defenses.
- [DOMPurify upstream](https://github.com/cure53/DOMPurify) — `SANITIZE_NAMED_PROPS`, configuration and hooks.
