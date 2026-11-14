# Evidence-based severity and CVSS

Score only a demonstrated finding, or give an explicitly qualified assessment
when the program requests one. Select the CVSS version required by the current
program; do not infer platform defaults from an old repository note.

## Build the metric argument

1. Describe attacker starting privileges, entry context and user interaction.
2. Separate exploit preconditions from the privilege the exploit gains.
3. Identify exact confidentiality, integrity and availability effects evidenced.
4. Identify the vulnerable component and any subsequent security authority.
5. Choose metrics using that version's definitions; retain uncertain assumptions.
6. Compute with the matching official calculator and publish full version/vector.
7. Keep program taxonomy/priority, eligibility, duplicate status and CVSS separate.

## Version-specific considerations

- v3.1 uses AV/AC/PR/UI/S/C/I/A for Base. Scope is a security-authority concept,
  not automatically changed because a different URL/tenant/server appears.
- v4.0 adds Attack Requirements and distinguishes vulnerable-system from
  subsequent-system impacts, with version-specific user interaction definitions.
  Do not mechanically translate a v3.1 vector into v4.0 numbers.
- Threat and Environmental metrics require their own evidence/assumptions. Do not
  silently mix an environmental score with a base score in a report title.

## Reject score-by-name shortcuts

RCE, XSS, IDOR, SSRF, redirect and takeover names do not determine a score.
Authentication alone does not determine all metrics. Data sensitivity alone does
not establish the extent of confidentiality loss. Do not assign availability
impact from an untested ability to read/write, nor full cloud control from a
metadata callback. A sandboxed execution context has its own authority limits.

A CSP bypass is not “XSS score + 1–2”. Additional confirmed links change the
metric facts and require recomputation, not arithmetic bonuses. No score or
program-priority prediction is warranted for a lead or a hypothetical chain.

## Report the uncertainty clearly

State the affected records/actions/roles and exact scope actually established.
Where one unresolved prerequisite changes a metric, explain the conservative
interpretation and the missing evidence; do not invent a precise final score.
A program may accept technical validity while rejecting eligibility or marking a
duplicate. Preserve those independent outcomes.

## Primary sources

- [FIRST v3.1 specification](https://www.first.org/cvss/v3.1/specification-document) — authoritative metric definitions and vector requirements.
- [FIRST v3.1 calculator](https://www.first.org/cvss/calculator/3.1) — matching calculation.
- [FIRST v4.0 specification](https://www.first.org/cvss/v4.0/specification-document) — v4 definitions and system impacts.
- [FIRST v4 calculator](https://www.first.org/cvss/calculator/4.0) — matching calculation.
