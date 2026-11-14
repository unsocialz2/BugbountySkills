# Web methodology revision and validation

This revision replaces contradictory web payload libraries with one canonical
methodology per boundary. It is a research aid, not a promise that a target has a
vulnerability or that a program will accept a report.

## Scope

- 41 existing WEB entry paths reviewed/reworked; four are compatibility pointers.
- 15 focused WEB guides added, giving 52 canonical methodologies and four pointers.
- Eight HTTP API guides enhanced with contextual experiment matrices and sources.
- Payload lookups and legacy entry paths resolve to those same methodologies.
- Adjacent PoC/impact/mitigation/scoring guidance corrected to avoid reintroducing
  the audited assumptions during validation/reporting.
- Mobile/AI/cloud methodology libraries were not rebuilt or certified here.

New guides cover session lifecycle, capability links, asynchronous jobs/webhooks,
WebAuthn, email identity parsing, client-side request forgery, browser isolation,
XS-Leaks, CSS injection, URL parser differentials, CRLF, server-side parameter
pollution, ORM inference, NoSQL injection and framework server actions.

## Audit resolution map

The identifiers refer to the preceding web content review, not live vulnerabilities.

| Review issue | Resolution |
|---|---|
| F01 source contradictions | web router/catalogue; old vuln-library and payload dumps now pointers |
| F02 CSP semantics | actual policy inventory, nonce/hash and inline/eval controls in csp_bypass |
| F03 Vary/cache inference | cacheability/keying/clean-client retrieval and harmful-effect proof |
| F04 H2.0/framing | corrected notation; byte-counted CRLF constructor and modern desync branches |
| F05 iframe origins | parent/child origin/sandbox matrix and actual delivery requirements |
| F06 invalid JS | vendor payload dump removed; executable/negative syntax regressions |
| F07 URL destinations | explicit WHATWG expected-host fixtures and actual consumer distinction |
| F08 CORS regex | old contradictory library removed; exact-origin and browser-read controls |
| F09 JWT generator | synthetic standard-library HMAC fixture independently checked with PyJWT |
| F10 SSTI | engine-valid arithmetic/filter/path examples; evaluation separated from RCE |
| F11 Ruby/load hooks | dump/load distinction, no invented target gadgets; inert pickle fixture |
| F12 destructive SSRF recipe | removed; controlled fetch/redirect/parser proofs with no Redis deletion |
| F13 rate-limit counts | canonical accounting/invariant API guide; no fixed burst/brute proof |
| F14 WebSockets | browser auth, handshake/message authority and real leak-channel distinctions |
| F15 GraphQL | canonical API guide; introspection/scalars/query reads do not imply exploit effects |
| F16 WAF/version | actual decoder/consumer and configured inspection/oversize behavior |
| F17 prototype pollution | source/scope/gadget/effect separated; non-destructive probes |
| F18 file serving | processing and origin/MIME/disposition/embedding context required |
| F19 XXE/OOXML | entity phases and archive-root-preserving repack, tested locally |
| F20 CVSS anchoring | no web discovery score tables; reporting uses versioned metrics/vector |
| F21 origin/provider/resolver | independent protection, provider claimability and real resolver provenance |
| F22 source freshness | topic-level primary source URLs/applicability; indexed references and retrieval record |
| F23 SAML depth | signer/consumer, profile bindings, replay/correlation/time and real attacker path |
| F24 premature gates | discovery/validation/reporting separated; competing hypotheses and scoped reopening |
| F25 integration/evaluation | portable environment hints, collector policy gates, content regressions and bounded forward test |

## Reproduce the checks

From repository root:

```bash
python3 -m unittest discover -s tests -v
python3 .opencode/skills/web-mode/scripts/validate_knowledge.py
python3 .opencode/skills/web-mode/scripts/browser_regression.py
```

The first two are automated local checks. The optional browser command distinguishes
executed pass (0), executed failure (1), and unavailable runtime (2); a blocked
browser is not a passing test. The final local environment could not launch
Chromium because its required process socket was disallowed. Downloading the
matching optional headless shell also failed; no browser-policy execution is
claimed for this environment.

`results.json` records the final unit/integrity results. `source-checks.json` is
availability metadata only: 140 of 141 declared source URLs retrieved, one WHATWG
URL Standard request timed out. This is not verification of every statement or a
target version. Each guide specifies the mechanism its sources support.

`forward-test.json` records a newly authored local lifecycle scenario and its
repaired twin. A fresh research agent received usage help and controlled accounts,
without source/answer/polarity. It discovered withdrawn-invitation acceptance,
proved private content/membership, and reported denial only for the repaired
flow. Twenty-five recorded requests/results were independently matched against
27 actual HTTP trace events. This is one bounded behavior spot check, with no
baseline comparison, real-browser claim, or estimate of general hunting success.
The now-known fixture must be treated as regression material in future evaluation.

## Collector policy migration

The two collector CLIs require `--scope-policy scope-policy.json`. Derive the
policy from designated program rules using recon-mode `references/scope-policy.md`
and `_template/SCOPE_POLICY.json`; do not treat the example host as authorization.
The guard validates the full URL batch, HTTP method, ports and budgets before
requests. Exact path checks preserve trailing slashes; common route/method override
headers are rejected. It gates those CLIs only, not arbitrary shell/browser/DNS
activity or application-specific query semantics. Library callers must pass a
policy or explicitly own the pre-approved-input responsibility.

## Remaining applicability limits

Synthetic snippets and semantic fixtures do not certify deployed Ruby/PHP/template
engines, SAML cryptography, WebAuthn ceremonies, browser gadgets, provider resource
claims, CDN state or real programs. These require the exact runtime/configuration,
current policy and minimal permitted target evidence. Raw callbacks, status codes,
versions, field names, metadata and final rollback each have narrower meanings.
