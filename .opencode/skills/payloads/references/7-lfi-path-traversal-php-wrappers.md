# Context payload lookup: lfi rfi path traversal

Canonical guide: [lfi_rfi_path_traversal.md](../../web-mode/SKILL_FILES/VULNERABILITIES/WEB/lfi_rfi_path_traversal.md).

This entry point contains selection rules, not a second payload library. Load the
canonical guide's experiment and payload sections; its controls, preconditions,
source/version limits and interpretation travel with every example.

## Select the experiment

- Contexts: Download path / archive path / include / stream wrapper.
- Use two researcher-created distinguishable files. File reading, template inclusion and code execution are separate capabilities. Null bytes and historical wrappers require matching versions and configuration.
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
