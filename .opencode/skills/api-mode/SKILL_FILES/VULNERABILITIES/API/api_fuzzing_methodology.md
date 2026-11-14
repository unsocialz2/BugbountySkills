# API Fuzzing — hypothesis-driven differential testing guide

Use this file when the API surface is understood well enough that targeted input variation can answer a concrete parser, validation, authorization, or state question.

## Goal

Use **small, discriminating variations** to discover where equivalent inputs are parsed, validated, authorized, or normalized differently.

Do not inject every vulnerability-class payload into every parameter.

## Start from a question

Before fuzzing, state what you are trying to distinguish, for example:

- does this field accept a different type than the schema/UI suggests,
- do JSON/form/XML paths reach different validators,
- do two HTTP methods hit the same business action with different middleware,
- does an undocumented parameter change ownership/role/state,
- does parser normalization create a security-relevant discrepancy?

## Minimal loop

1. Establish a stable control request.
2. Start with the smallest valid semantic change: value, type, field presence, nesting, content type, method, header, or path representation. Coupled representation changes may require both header and body changes to remain valid. For a suspected interaction, compare valid controls for each factor and their combination where feasible; do not mistake an invalid request for enforcement.
3. Compare semantic result and authoritative state.
4. Repeat enough to rule out cache/jitter/random backend errors.
5. Escalate to a vulnerability-specific skill only when the differential supports that hypothesis.
6. Stop broadening when additional variations no longer change the security question.

## Useful variation dimensions

Select only those justified by observed API design:

- type: string/integer/boolean/null/array/object,
- presence: omitted/empty/default/duplicate field,
- nesting/parent-child representation,
- JSON vs form/XML/multipart when the API actually accepts them,
- method variants that plausibly map to the same action,
- version/route aliases,
- documented vs undocumented fields,
- boundary/length/enum values,
- header-driven behavior where the gateway/framework exposes such controls.

## Auth and state before payloads

Prioritize identity, authorization, writable-state, version drift, and parser differences before generic injection payloads. Once a concrete sink/engine is suspected, hand off to the owning vulnerability skill or `payloads` for exact probes.

## Evidence contract

Record:

1. control request,
2. semantic change, coupled fields and controls for any tested interaction,
3. semantic/state difference,
4. why that difference matters to a security boundary,
5. repeatability,
6. strongest benign explanation tested.

## Stop conditions

Stop or narrow when:

- changes only affect validation/error formatting,
- no authoritative state/capability difference exists,
- behavior is documented schema coercion,
- broad variation is producing noise without a concrete hypothesis.

## Tools

Choose schema-aware/manual tooling that preserves clean controls and low-noise differentials. Tool choice is secondary to the experiment design.

## Discovery and experiment payloads — Small interaction experiments with valid controls

Examples below are synthetic request shapes, not discovered target endpoints.
Read policy first, substitute existing owned resources, and start with a normal
successful operation. A cheap discriminating discovery probe does not require a
previously confirmed vulnerability. No example has been replayed against an
external target by this revision.

| Question | Minimal control / probe | Protected or benign outcome to discriminate |
|---|---|---|
| Presence/type | Valid scalar with marker vs absent/null/array only where schema permits meaningful comparison | Validation errors identify parser behavior; they do not prove exploitation or enforce ownership. |
| Duplicate semantics | name=A, name=B, name=A&name=B, name=B&name=A on a harmless own fixture | Map first/last/array/multi-value access at each layer; framework name alone does not decide behavior. |
| Coupled parser change | Valid JSON body+header vs valid form body+header | Preserve semantics. Mismatched header/body rejection is not an authorization result. |
| Two-factor interaction | Control X, control Y, X+Y and neither on a local fixture | A failing factor alone does not rule out a composition flaw; justify combinations from the architecture. |
| Second-order consumer | Stored marker control vs downstream preview/export consuming the same field | Track transformations and actors across storage/render/query steps; storage acceptance alone is not downstream execution. |

### Payload context

```text
CONTROL A: label=AUDIT_A
CONTROL B: label=AUDIT_B
PROBE AB:  label=AUDIT_A&label=AUDIT_B
PROBE BA:  label=AUDIT_B&label=AUDIT_A
```
These are form/query bytes, not four JSON values. A duplicate JSON key test uses
a different parser and must preserve exact bytes; a dictionary serializer may
remove the duplicate before transmission. Retain a distinctive output marker,
normal successful controls and downstream state evidence. The smallest useful
interaction can vary two coupled inputs; a rigid one-field rule must not prevent
it when the combination is the hypothesis.

### Evidence and reopening

Keep actor/role/tenant, exact request bytes, successful normal control, probe
response, authoritative readback or transient protected result, strongest benign
explanation, and remaining gap. Close only the tested relationship/representation;
reopen for an observed alternate consumer, changed lifecycle, repaired control, or
new source evidence. Absence of output is not evidence that processing never ran.

### Primary sources and applicability

Sources checked 2026-11-13 for mechanism/design support; they are not target
version or exploitability attestations. The experiment matrix is a synthesis.

- [PortSwigger API testing](https://portswigger.net/web-security/api-testing) — parameter discovery and supported formats.
- [PortSwigger server-side parameter pollution](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution) — internal request construction boundaries.
- [OWASP HPP](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/07-Injection/04-HTTP_Parameter_Pollution/) — interacting component parser behavior.
