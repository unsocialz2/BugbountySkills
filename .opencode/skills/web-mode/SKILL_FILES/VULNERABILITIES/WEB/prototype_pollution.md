# Prototype pollution — separate source, prototype scope, gadget and effect

## Boundary and discovery

Use for JavaScript deep merge/path assignment, nested query parsers, JSON settings, inherited option reads and browser messaging.
An input containing `__proto__` does not prove pollution.
`JSON.parse` treats that key as data; a subsequent vulnerable merge/assignment may cross the prototype boundary.
Distinguish mutation of one object's prototype from mutation of global `Object.prototype`.
A harmless marker property proves pollution only when its inherited read is observed in an appropriate fresh object.
It does not prove an executable gadget or a protected authority change.

Map input → key/path decoder → merge/set operation → prototype reached → inherited property read → final sink.
Record library/runtime versions and whether pollution survives across requests, users or processes.
Do not assume that every historical lodash/jQuery helper call remains vulnerable.
Choose a unique marker key that cannot affect ordinary application behavior.

## Valid control

In a permitted isolated client/lab, confirm that `({}).auditMarkerA1` is initially absent.
Submit an ordinary own property and prove it remains local to the intended object.
Submit one suspicious path through the normal entry point and inspect a fresh object's inherited value only when instrumentation permits it.
Use source/behavior evidence to distinguish an echo from inherited lookup.
Reset the isolated process/context between tests; on a live service, do not assume a global mutation is reversible by a request.

## Payloads and discriminating experiments

The following are conditional source probes, not proof that the parser accepts their notation.

```json
{"__proto__":{"auditMarkerA1":"AUDIT_MARKER"}}
```

```json
{"constructor":{"prototype":{"auditMarkerA1":"AUDIT_MARKER"}}}
```

For a query parser already observed to support bracket paths:

```text
?__proto__[auditMarkerA1]=AUDIT_MARKER
```

A local negative control for plain JSON parsing:

```javascript
const obj = JSON.parse('{"__proto__":{"auditMarkerA1":"AUDIT_MARKER"}}');
console.assert(Object.hasOwn(obj, '__proto__'));
console.assert(({}).auditMarkerA1 === undefined);
```

| Question | Challenge | Control | What is established? |
|---|---|---|---|
| Does input become a nested key path? | Unique harmless nested marker using observed notation | Ordinary nested key with same value | Parsed structure only, not prototype mutation. |
| Is the marker inherited by a fresh object? | Marker source probe | Same value as an own property on one object | Actual prototype scope, supported by read/source trace. |
| Do constructor/prototype paths behave differently? | Relevant alternative path only if parser supports it | Rejected or inert original path | A distinct traversal route; spelling the same blocked keys in brackets is not a magic bypass. |
| Is an option read inherited? | Unique lab marker on an option confirmed in source | Explicit own option set to a different harmless value | Own-value override should distinguish inheritance from response echo. |
| Can a non-destructive backend oracle be used? | Source-backed harmless formatting/status option on an isolated owned response | Original/default option and reset process | Requires the exact dependency/property read; never corrupt built-in methods or global error handling. |
| Does the claimed gadget naturally execute? | A harmless marker reaching the confirmed sink through supported client flow | Same source with gadget property absent | Proves source-to-gadget-to-sink, not only local console assignment. |

Do not pollute `toString`, constructors, encodings or other core behavior to obtain a crash.
Do not equate JSON parse success with pollution.
`NODE_OPTIONS=--inspect` is not code execution by itself; an inspector would need its own exposure and invocation path.
A shell/env option inherited by a process gadget still requires that actual process launch and applicable runtime behavior.

## Client-side versus server-side

In a client, show the attacker-controlled navigation/message/input can reach the source without privileged console access.
A manually assigned prototype in DevTools is an instrumentation aid, not the attack vector.
A usable XSS chain needs an inherited option read into an executable sink under the real CSP/Trusted Types policy.
A browser extension or local rewrite that removes a guard cannot establish target reach.

On a server, process lifetime and worker selection affect observations.
Do not use a global marker if even its selected key can affect shared application state.
Prefer source-backed isolated responses and documented non-disruptive black-box methods.
Record when a probe changes one request versus the whole process.
A rejected response may follow a mutation; do not continue sending repeated probes into unknown persistent state.

## Falsification and evidence

Preserve pristine state, normal parsed structure, source probe and inherited read/gadget evidence.
Separate own-property assignment, object-local prototype replacement, global pollution and downstream effect.
Attempt benign accounts: response reflection, expected nested object, stale polluted client, instrumentation change or unrelated worker.
Show the actor/tenant authority crossed before calling a cosmetic option change an authorization bypass.
Preserve transient execution/read effects even if later process state is reset.

Close only a tested source/key path if it remains ordinary data or a safe dictionary/own-property policy blocks inheritance.
Unknown persistence or missing readback is inconclusive, not a reason for crash probes.
Reopen for another parser, merge operation, dependency version or newly observed inherited option sink.

## References and freshness

Reviewed 2026-11-13. Gadget behavior is dependency/version-specific; no generic RCE chain is asserted.

- [PortSwigger prototype pollution](https://portswigger.net/web-security/prototype-pollution) — source/gadget/sink model and client paths.
- [PortSwigger non-destructive server-side research](https://portswigger.net/research/server-side-prototype-pollution) — safe detection reasoning and failure modes of destructive probes.
- [MDN prototype pollution](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution) — JSON data, assignment semantics and inherited properties.
