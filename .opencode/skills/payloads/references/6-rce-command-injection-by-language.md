# Context payload lookup: rce all vectors

Canonical guide: [rce_all_vectors.md](../../web-mode/SKILL_FILES/VULNERABILITIES/WEB/rce_all_vectors.md).

This entry point contains selection rules, not a second payload library. Load the
canonical guide's experiment and payload sections; its controls, preconditions,
source/version limits and interpretation travel with every example.

## Select the experiment

- Contexts: Shell string / argv / language evaluation / process invocation.
- Choose a non-persistent output marker in an isolated lab or the minimum permitted target proof. Shell operators are not interpreted by every process API. No reverse shell is needed to establish execution.
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
