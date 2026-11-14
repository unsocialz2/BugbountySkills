# Context payload lookup: prototype pollution

Canonical guide: [prototype_pollution.md](../../web-mode/SKILL_FILES/VULNERABILITIES/WEB/prototype_pollution.md).

This entry point contains selection rules, not a second payload library. Load the
canonical guide's experiment and payload sections; its controls, preconditions,
source/version limits and interpretation travel with every example.

## Select the experiment

- Contexts: Unsafe assignment / prototype scope / inherited-property gadget.
- Use a unique inert property and a fresh process for lab cleanup. JSON.parse alone does not modify Object.prototype. Do not overwrite core methods or use crashes as the default detection signal.
- Name the input source, decoder/parser and expected security boundary first.
- Discovery may use a cheap justified probe before any primitive is confirmed.
- Choose a valid baseline, a minimally changed probe, and a matched negative control.
- Substitute only owned actor/resource IDs and a unique `AUDIT_MARKER`.
- Preserve the real parser bytes and any required URL/base64/JSON encoding.
- Record a denied request as the tested observation; do not certify the whole class.
- An observed source example is not a vendor-wide working payload or target proof.

## Return to the owning methodology

If no example fits the observed sink, reason from that sink or current primary
research rather than loading unrelated variants. If the application rejects the
probe, discriminate parsing, reachability, authorization and delivery failure
before either expanding or closing the hypothesis.
