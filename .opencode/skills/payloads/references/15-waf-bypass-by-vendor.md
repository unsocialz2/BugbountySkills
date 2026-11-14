# Context payload lookup: waf bypass all techniques

Canonical guide: [waf_bypass_all_techniques.md](../../web-mode/SKILL_FILES/VULNERABILITIES/WEB/waf_bypass_all_techniques.md).

This entry point contains selection rules, not a second payload library. Load the
canonical guide's experiment and payload sections; its controls, preconditions,
source/version limits and interpretation travel with every example.

## Select the experiment

- Contexts: Transport encoding / WAF parser / application parser / inspected component.
- Identify which layer decodes each byte. Vendor identity is insufficient to choose a bypass. Prove the underlying application effect, not just removal of a block response.
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
