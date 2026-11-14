# Polyglots: select only after understanding the parsers

Canonical guide: [XSS](../../web-mode/SKILL_FILES/VULNERABILITIES/WEB/xss_reflected_stored_dom.md).

Prefer a small context-specific payload/control. A polyglot combines grammar
breakouts, which also makes its failure harder to interpret. Do not use one as a
universal detector or infer an absence of injection when it fails.

## Differential construction

1. Trace an inert `AUDIT_MARKER` through the actual transformations.
2. Record which HTML/JavaScript/URL/template parser consumes which substring.
3. Obtain a working harmless control for each context in an isolated fixture.
4. Combine only the breakouts needed by the observed path; test each intermediate
   output, not just the final response. Encoding belongs to a specific layer.
5. Compare against an inert string with the same delimiters/length where possible.
6. Verify actual execution origin, browser restrictions and victim delivery.

`AUDIT_MARKER<>&"'` is a parser/escaping observation marker, **not** an execution
payload. `<span data-audit="AUDIT_MARKER">AUDIT_MARKER</span>` can distinguish HTML
rendering from literal text in an owned fixture; rendering HTML alone is not XSS.
CSV formulas, remote redirects and template expressions belong to their own
consumer-specific methodologies; do not combine them into one expected result.

## Primary references

- [PortSwigger XSS contexts](https://portswigger.net/web-security/cross-site-scripting/contexts) — why parser context changes the payload.
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) — encoding is context-specific.
- [WHATWG HTML parsing](https://html.spec.whatwg.org/multipage/parsing.html) — HTML parser states and recovery.
