# Insecure deserialization — bind attacker bytes to a real consumer

## Contents

- Boundary and discovery
- Valid normal control
- Payloads and discriminating experiments
- Language-specific reasoning
- Evidence and false-positive controls
- References and freshness


## Boundary and discovery

Use for encoded cookies, signed state, import/export blobs, queue messages and typed JSON/XML object reconstruction.
Serialization formats are leads: Base64, Java stream magic or a PHP object string alone prove no unsafe consumer.
Map input bytes → transport decode → integrity/authentication check → format parser → type selection → hooks/gadgets → application action.
Separate data tampering, object instantiation, unexpected method invocation and execution.
A JSON parser creating ordinary data is not equivalent to a native object deserializer invoking hooks.
A class definition invented by the researcher does not establish that a target loads that class.

Record:

- attacker control over the complete blob versus one field;
- envelope signatures, compression and canonicalization before parsing;
- exact consumer, supported types, dependencies and runtime version when known;
- whether deserialization occurs before authorization or only after a legitimate upload/queue event;
- what normal state is restored and how its effect can be observed safely.

## Valid normal control

Capture a legitimate serialized object from an owned flow; preserve the original unmodified bytes.
Replay it once in the same allowed state and prove the expected action or data restoration.
Modify a harmless display field using the same format/encoding, keeping lengths and envelope integrity valid where possible.
If a valid integrity-protected blob cannot be created under the attacker model, treat that as a concrete prerequisite.
Do not remove a signature in a lab and present the resulting reach as an external attack.
A format error in an otherwise invalid request is not a normal control.

## Payloads and discriminating experiments

The following formats are benign data illustrations. They are not universal exploit strings.

```text
PHP serialized scalar:   s:12:"AUDIT_MARKER";
JSON data:               {"label":"AUDIT_MARKER"}
```

A local pickle lifecycle demonstration can reconstruct an inert value without OS commands:

```python
import pickle
class AuditFixture:
    def __reduce__(self):
        return (str, ("AUDIT_MARKER",))
blob = pickle.dumps(AuditFixture())
assert pickle.loads(blob) == "AUDIT_MARKER"
```

This proves only the local reconstruction semantics; it does not prove the application accepts attacker-controlled pickle.
Do not unpickle unknown files to inspect them; use non-executing format inspection such as `pickletools.dis` in an isolated workflow.

| Question | Challenge | Valid comparison | Interpretation |
|---|---|---|---|
| Does the suspected field reach this decoder? | Encode `AUDIT_MARKER_B` with the observed format | Original `AUDIT_MARKER_A` blob | Restored field changes at the actual consumer, not merely response echo. |
| Does authenticity precede parsing? | Alter one byte in a signed owned blob | Valid signature and valid payload | Generic rejection is ambiguous; an instrumented authorized lab can show ordering. |
| Are restored fields trusted as authority? | Change one owned non-destructive field that should be server-derived | Normal schema-controlled update | Independent state shows whether authority is wrongly restored; may be integrity/authorization without RCE. |
| Can input choose an unexpected type? | A harmless alternate type known to exist in the authorized lab | Expected type with equivalent value | Type rejection versus construction; do not guess dangerous gadget classes on production. |
| Is there a method invoked during load? | Known lab hook records an in-memory marker | Same type without the hook-triggering field | Establish the precise hook and timing, including a later exception. |
| Does another worker consume the same artifact? | Same owned artifact through import/preview/queue consumers | Successful normal input in each | Attribute which consumer parses objects; one protected entry does not cover all. |

## Language-specific reasoning

### Python

`pickle` is an executable reconstruction format, not an untrusted-data format.
`__reduce__` describes how an object is reconstructed; the chosen callable can execute at load time.
`yaml.load` behavior depends on the selected loader and library version; a function-name match alone is insufficient.

### Ruby

`marshal_dump` runs while producing the serialized representation.
`marshal_load` runs while loading a representation produced by the matching protocol; `_dump`/`_load` are another pair.
Putting the only interesting side effect in `marshal_dump` proves a generator-side event, not victim-side deserialization.
Actual gadget chains require classes and hook behavior present in the target runtime.
Do not use a locally defined gadget or a non-marshallable `Method` object as a supposed universal payload.

### Java / .NET / PHP / Node

For Java, map `ObjectInputStream`/library-specific handling and configured filters to the exact loaded dependency graph.
A filter is not universally an allowlist and allowing one class does not establish a useful chain.
For .NET, distinguish serializers and type policies; `BinaryFormatter` risk does not make every JSON/XML serializer equivalent.
For PHP, constructor and magic-method execution are different; strings have byte lengths, and available classes matter.
For Node, ordinary `JSON.parse` does not execute function literals; legacy function-restoring libraries require their exact implementation.
No general jump from any deserialization acceptance to cluster takeover is justified.

## Evidence and false-positive controls

Preserve original and altered blobs, envelope transformations, natural entry point and normal replay result.
Prove restoration/dispatch at the named consumer with source/runtime evidence or a controlled semantic effect.
Record generator-side effects separately from victim-side load events.
A later parse/validation failure can follow an earlier hook effect; retain that narrower observation.
Distinguish reflection, client decoding, benign field restoration and a real protected boundary failure.
Do not extract system files or secrets to make a format issue appear more severe.

Close the tested type/consumer if input cannot reach it or expected checks block the meaningful capability.
Keep unknown library versions, unavailable dependencies and invalid blobs inconclusive.
Reopen for a discovered consumer, trusted-envelope bypass, new dependency or different hook path.

## References and freshness

Reviewed 2026-11-13. Local examples demonstrate format semantics only; no target gadget is asserted.

- [PortSwigger deserialization](https://portswigger.net/web-security/deserialization) — attacker-controlled state, types and gadget-chain reasoning.
- [Python pickle](https://docs.python.org/3/library/pickle.html) — trust warning and reduction/reconstruction protocols.
- [Ruby Marshal](https://docs.ruby-lang.org/en/3.4/Marshal.html) — dump/load hook distinction; select the deployed Ruby version.
