# HTTP Parameter Pollution — accessor and cross-layer interpretation

## Contents

- Boundary and preconditions
- Cheap discovery and normal controls
- Discriminating experiments
- Context-specific payloads
- Local accessor control
- Proof and falsification
- Evidence, stop, and reopen
- Sources and version limits


Use this guide when a request can represent the same logical field more than once, or a frontend inserts user input into an internal query/path/body without sufficient encoding. Duplicate parameters alone are normal protocol/application behavior.

## Boundary and preconditions

Model the exact chain: client serialization -> proxy/security checks -> framework parser -> accessor -> internal request builder -> downstream parser -> authorization/business action.

Write the invariant in concrete terms: the object/account/value authorized by one component must be the object/account/value used by the next.

Record parameter location and content type, decoded values, nesting/array conventions, parser versions/configuration, accessors used (`get`, `getlist`, indexed lookup, automatic binding), and expected behavior for duplicates. Do not infer first/last/list semantics from a framework name alone. Different accessors in the same request handler can disagree.

Distinguish:
- client-side duplicates (`x=A&x=B`);
- server-side parameter injection into a constructed downstream URL;
- JSON duplicate members;
- path injection through an unencoded downstream segment;
- an intended array versus an unexpected type change.

## Cheap discovery and normal controls

Capture a real read or harmless update involving researcher-owned resources A and B. Establish A-only and B-only behavior; both values must be valid and observable. Use a harmless display/filter field before any ownership/role identifier.

Test two distinct marker values in both orders. Track normalized meaning, not response length alone. If `x` is ignored, choose a field from actual feature traffic. If duplicates are rejected, record that narrow behavior and inspect only another observed representation or downstream builder with a concrete reason.

## Discriminating experiments

| Hypothesis | Payload pair | Expected benign alternative |
|---|---|---|
| Different components select different duplicate values | `view=AUDIT_A&view=AUDIT_B` versus reversed order | Both layers select the same scalar/list or reject duplicates; selection variation alone is not a vulnerability |
| Encoded delimiter reaches a downstream query | A valid owned string containing `%26audit%3DAUDIT_MARKER` versus an equally long plain string | Proper encoding preserves the entire value as one downstream parameter |
| Fragment character truncates a server-built URL | `name=owned%23AUDIT_MARKER` versus literal safe suffix | The `#` stays escaped as data; an ordinary validation failure is not proof of truncation |
| Encoded key bypasses one name comparison | `view=AUDIT_A&%76iew=AUDIT_B` versus normal duplicate | Decode/validation occur consistently or both representations are rejected |
| Scalar/array binding differs between security and execution | `view=AUDIT_A` versus `view[]=AUDIT_A` on an explicitly supported parser | Unsupported array type rejected without changing protected capability |
| JSON member selection differs across languages/layers | Raw `{"view":"AUDIT_A","view":"AUDIT_B"}` versus reversed order | Consistent handling or rejection; reserializing through a dict would erase this experiment |
| Query/body precedence differs | Same field in query and valid body with distinct owned values | A documented precedence rule consistently governs both checks and action |

Choose one field and one representation per first experiment. Then compare factor controls and a justified combination if evidence points to an interaction.

## Context-specific payloads

```http
GET /audit/search?view=AUDIT_A&view=AUDIT_B HTTP/1.1
Host: app.example.invalid
```

```http
GET /audit/search?view=AUDIT_B&view=AUDIT_A HTTP/1.1
Host: app.example.invalid
```

For an observed server-side URL builder, encode once for the outer request so a single decode produces an inner delimiter:

```text
name=owned%26audit%3DAUDIT_MARKER
name=owned%2526audit%253DAUDIT_MARKER
```

These compare decode depth; the second is not inherently stronger. A field being echoed with `&` says nothing about a downstream call. Require source/dataflow, controlled internal fixture logs, or a semantic downstream differential.

For path building in a controlled fixture:

```text
item=owned%2Fchild
item=owned%252Fchild
```

Keep the selected route/object within the fixture. A changed 404 alone is an inconclusive route-interpretation clue, not authorization bypass.

## Local accessor control

The following explains why recording the accessor matters; it does not reproduce a target flaw:

```python
from urllib.parse import parse_qs
values = parse_qs('view=AUDIT_A&view=AUDIT_B')['view']
assert values == ['AUDIT_A', 'AUDIT_B']
assert values[0] != values[-1]
```

```javascript
const params = new URLSearchParams('view=AUDIT_A&view=AUDIT_B');
console.assert(params.get('view') === 'AUDIT_A');
console.assert(params.getAll('view').length === 2);
```

Application wrappers can add their own selection rule. Save raw bytes before any tool collapses duplicate headers/parameters/members.

## Proof and falsification

A finding needs the input interpreted as permitted by the checking layer and as a different unauthorized semantic value by the consuming layer. Demonstrate the controlled object/action difference, not simply that PHP returned one value and JavaScript another.

Try consistent parser/accessor behavior, intentional multiselect semantics, type rejection, cache variance, ignored fields, and unrelated errors as benign explanations. Verify authoritative state after a harmless write. If only the parser policy differs without an attacker advantage, retain a compatibility observation.

A transient cross-object read or operation before rollback can be meaningful; a later correct final value does not negate it. Do not require mass enumeration or sensitive field dumps to establish one boundary failure.

## Evidence, stop, and reopen

Keep raw request representations, valid A/B controls, parser/accessor evidence when known, the exact changed dimension, downstream semantic outcome, and the strongest rejected alternative. State unknown internal behavior explicitly.

Park if all relevant interpretations agree, input remains correctly escaped data, or no protected action is affected. Scope the negative to the tested field/representation/accessor. Reopen for a new internal API call, serializer, content type, bulk input, or legacy version observed in actual traffic.

Use `api-mode` for schema-wide property/type authorization and `url_parser_differentials.md` for authority/path normalization. Do not turn this into a general input-fuzzing exercise.

## Sources and version limits

Source review: 2026-11-13. Local accessor examples are reproducible standard-library demonstrations; target wrappers still need measurement.

- [PortSwigger — Server-side parameter pollution](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution): downstream query/path/body construction and delimiter injection.
- [OWASP WSTG v4.2 — HTTP parameter pollution](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/04-Testing_for_HTTP_Parameter_Pollution/): compare duplicate interpretation and security impact; use current section navigation if the guide reorganizes paths.
- [Python — urllib.parse](https://docs.python.org/3/library/urllib.parse.html): `parse_qs` list representation and decoding behavior.
- [Node.js — URL/URLSearchParams](https://nodejs.org/api/url.html): `get` versus `getAll`; this does not define every Express query-parser configuration.
