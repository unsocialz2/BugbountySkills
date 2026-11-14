# Cross-Site Scripting — source, parser, execution, reach

## Navigation

Boundary and discovery → controlled probes → context experiments → defenses → evidence and stopping.

## Boundary and starting model

Test whether input controlled by a weaker actor becomes executable browser content in an origin with authority that actor does not already possess.
Treat reflected, stored, DOM, mutation, and framework-template paths as mechanisms, not severity levels.
Begin discovery with ordinary feature use and a unique inert marker; an already-confirmed primitive is not required to investigate a plausible render path.
Use only the real feature's accepted inputs and observe where another controlled user can render them.
A public search box, invitation note, attachment preview, support view, or URL fragment can each expose a different reader and parser.
Record the actor, writer, reader, source, intermediate representations, sink, origin, authentication state, and required interaction.

## Establish the normal control

1. Create one synthetic record containing `AUDIT_MARKER_7e31` with actor A.
2. View it through the legitimate reader flow; use actor B when crossing users is the claimed boundary.
3. Save the request/response and the final rendered DOM, not just view-source.
4. Distinguish reflected bytes, DOM insertion, execution, and reader reach as separate observations.
5. If rendering is delayed, capture the worker/preview/notification path that actually consumes the value.

## PAYLOADS — select the matching parser only

The probes below are context-specific starting examples, not sanitizer bypass guarantees.
Use a different marker per trial, then compare with the inert marker control.
Keep execution proof inside the owned browser; do not collect cookies or real user data.

| Observed insertion context | Harmless execution probe | Required observation / benign alternative |
|---|---|---|
| Raw HTML body parsed as elements | `<svg onload="window.__AUDIT_MARKER__='7e31'"></svg>` | Marker set in the target frame; escaped text is a negative for this path. |
| Double-quoted HTML attribute | `" autofocus onfocus="window.__AUDIT_MARKER__='7e31'" x="` | Actual focus/event delivery; an inert unsupported attribute is not execution. |
| Single-quoted JavaScript string in script content | `';window.__AUDIT_MARKER__='7e31';//` | Surrounding JavaScript remains syntactically valid and executes. |
| JavaScript template literal | `${window.__AUDIT_MARKER__='7e31'}` | Evaluation in the application, not display in a text node. |
| User-controlled navigation to a permitted scheme | `javascript:window.__AUDIT_MARKER__='7e31';void 0` | Only relevant where the actual navigation API permits this scheme; HTTP Location alone is not equivalent. |
| HTML generated inside a script element | `</script><svg onload="window.__AUDIT_MARKER__='7e31'"></svg>` | HTML parser termination, then event execution; JS escape handling alone may not address the HTML boundary. |

Do not run all rows against one parameter.
If a probe fails, identify whether validation, transport, parsing, sanitization, CSP, Trusted Types, or reachability caused the failure.
Syntax validity in a local engine is necessary for a code-context example but does not prove browser execution or target applicability.

## Discriminating experiments

| Question | Minimal comparison | Why it discriminates |
|---|---|---|
| Reflection or executable insertion? | Inert marker vs context-matched marker-setting probe. | Separates content handling from code interpretation. |
| Server-rendered or client-generated? | Original response vs DOM after the normal rendering event. | Locates the responsible parser and decode stage. |
| URL source reaches sink? | Same route/state, only source marker changed. | Avoids attributing unrelated script behavior to the input. |
| Stored or self-only? | A writes, B loads using the normal product link. | Establishes a real writer-reader boundary. |
| Sanitizer or later mutation? | Sanitizer output, then final inserted DOM, same input. | A safe string may be changed by later processing; a rejected historical payload says little about other paths. |
| Browser defense or dead path? | Reachable benign DOM update vs execution variant; inspect violation/error. | CSP/Trusted Types blocking differs from a sink never being called. |

Use DOM breakpoints or DOM Invader to trace actual values and stack frames.
Instrumentation that replaces a sink, disables CSP, relaxes Trusted Types, or forces a feature flag changes exploitability; label it as a lead-only lab modification.
Trace second rendering passes such as markdown → HTML → sanitizer → framework insertion independently.
Mutation XSS requires the affected sanitizer/parser/version/configuration; do not label an old payload a bypass of every current release.

## Defense-specific branches

- With CSP, inspect every enforced policy and the specific directive controlling the sink; use `csp_bypass.md` for the remaining boundary.
- With Trusted Types, inspect whether enforcement is active and which policy transforms data; a policy name is not evidence of effective sanitization.
- With DOMPurify, identify version, parser environment, configuration and hooks; changing cleaned HTML afterward may invalidate its guarantees.
- With framework autoescaping, identify an actual escape hatch instead of assuming every template placeholder is executable.
- If WAF denial prevents the application receiving the input, record application exploitability as unresolved; do not call a frontend block proof of backend safety.

## Evidence and effect

Preserve exact input bytes, transformations, sink, runtime marker, affected origin, reader identity, browser version and delivery prerequisites.
Execution can be transient and still security-relevant; durability is not required for XSS.
For stored claims, preserve evidence that the normal reader actually consumed the stored value.
Any downstream account or tenant action requires its own authorization/control evidence; `HttpOnly` neither eliminates XSS nor proves account takeover.
Numeric scoring belongs to `reporting-mode` after the demonstrated capability is known.

## Stop, narrow, reopen

- Narrow a negative to the exact source, parser, browser, state and reader tested.
- Park a dead code path or self-only rendering with no cross-boundary consequence, retaining a concrete reopen condition.
- Reopen when a new reader, alternate renderer, sanitizer configuration, or lifecycle transition appears.
- Do not declare a feature XSS-free because one payload was encoded or one response lacked reflection.

## Primary references

Sources reviewed 2026-11-13; examples here remain conditional until reproduced in the target.

- [PortSwigger XSS](https://portswigger.net/web-security/cross-site-scripting) — mechanisms, contexts and proof of execution.
- [PortSwigger DOM XSS](https://portswigger.net/web-security/cross-site-scripting/dom-based) — source-to-sink tracing and runtime investigation.
- [MDN Trusted Types](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API) — enforcement versus policy transformations.
- [DOMPurify upstream](https://github.com/cure53/DOMPurify) — configuration, hooks and sanitizer environment limitations.
