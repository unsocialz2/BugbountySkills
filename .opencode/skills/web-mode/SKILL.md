---
name: web-mode
description: Web application research for browser/session/authentication/authorization flows, business logic, concurrency, background jobs, rendering and isolation, HTTP/proxy/cache/parser behavior, backend injections, file processing, server actions, and web ownership edges. Use for evidence-driven discovery and validation with contextual payload/control pairs. Route protocol-wide REST/GraphQL/gRPC to api-mode; keep connected feature flows intact.
---

# Web research — select a boundary, preserve the whole feature

Use HUNT_RULES for scope/evidence/autonomy. This router locates one contextual
methodology; it is not a universal scan plan or a guarantee that a target has bugs.

## Research loop

1. Recover one real normal workflow, actor/resource and observable consequence.
2. Model how authority/data/state passes through its actual consumers. Keep
   competing hypotheses, including a benign explanation; unknown impact is allowed.
3. Select the cheapest informative discovery probe. Do not demand a confirmed
   primitive before trying a justified inert marker or policy differential.
4. Load the matching guide below; its payloads carry controls and preconditions.
5. Verify semantic effect and realistic attacker delivery. Follow an observed
   lifecycle/representation even after a direct read/auth control works correctly.
6. Preserve evidence, uncertainty, and the next discriminator. Close the tested
   boundary only; report not-tested/blocked/inconclusive separately.
7. Investigate a chain only when each link can be tested. Scoring belongs to
   reporting-mode; no fixed CVSS or promised bounty belongs in discovery.

For selecting among hypotheses, statistical controls, source use and progression,
load [research method](references/web-research-method.md) only when needed. Do not
preload the full catalogue or convert the index into a sequential checklist.

## Browser and access environment

Read target policy first. Consult `ENV.md` at repository root only when resolving
this workstation's browser/tool preferences. It preserves the operator's browser
preference: headed Playwright first, ego-browser as the second option where
available; verify the runtime before use. Other hosts may use an available permitted isolated browser.
A missing preferred browser is a specific tooling blocker, not application security
evidence. Never silently change personal profiles, clear user data, import sessions,
or claim a browser/runtime that did not execute.

For browser-sensitive claims record actual origin/site/partition, cookie and CSP
state, build/version and natural delivery. Proxy/curl observations cannot by
themselves prove browser response readability, embedding or script execution.

## Methodology catalogue

Every substantive guide carries contextual experiments/payloads and primary
sources. Synthetic paths, tokens and marker names must be replaced with observed
valid shapes and controlled fixtures. Source review does not attest target
versions or execution. Index/source metadata is in `references/web-catalog.json`.

### Identity, authorization and lifecycle

| Boundary/question | Guide |
|---|---|
| Authentication proof/state transitions | [auth_bypass_all_types.md](SKILL_FILES/VULNERABILITIES/WEB/auth_bypass_all_types.md) |
| MFA and step-up bindings | [2fa_mfa_bypass.md](SKILL_FILES/VULNERABILITIES/WEB/2fa_mfa_bypass.md) |
| Ownership, role, tenant and relationship policy | [idor_bola_bfla.md](SKILL_FILES/VULNERABILITIES/WEB/idor_bola_bfla.md) |
| OAuth/OIDC client, flow and identity binding | [oauth_misconfig.md](SKILL_FILES/VULNERABILITIES/WEB/oauth_misconfig.md) |
| Token verifier, keys, purpose and audience | [jwt_attacks.md](SKILL_FILES/VULNERABILITIES/WEB/jwt_attacks.md) |
| SAML signer/consumer and assertion bindings | [saml_attacks.md](SKILL_FILES/VULNERABILITIES/WEB/saml_attacks.md) |
| Session issue/refresh/revoke and stale authority | [session_lifecycle.md](SKILL_FILES/VULNERABILITIES/WEB/session_lifecycle.md) |
| WebAuthn ceremony, RP/origin and recovery | [webauthn_passkeys.md](SKILL_FILES/VULNERABILITIES/WEB/webauthn_passkeys.md) |
| Email validation, delivery and identity normalization | [email_identity_parsing.md](SKILL_FILES/VULNERABILITIES/WEB/email_identity_parsing.md) |
| Share/signed/invite capability scope and lifecycle | [capability_links.md](SKILL_FILES/VULNERABILITIES/WEB/capability_links.md) |
| Confirmed capability to actual account control | [account_takeover_chains.md](SKILL_FILES/VULNERABILITIES/WEB/account_takeover_chains.md) |

### Product state and background execution

| Boundary/question | Guide |
|---|---|
| Target-specific state machine and invariants | [business_logic_bugs.md](SKILL_FILES/VULNERABILITIES/WEB/business_logic_bugs.md) |
| Concurrent operations, sub-states and transient impact | [race_conditions.md](SKILL_FILES/VULNERABILITIES/WEB/race_conditions.md) |
| Queue/result/download/cancel and signed callback lifecycle | [async_jobs_webhooks.md](SKILL_FILES/VULNERABILITIES/WEB/async_jobs_webhooks.md) |

### Browser and rendering trust

| Boundary/question | Guide |
|---|---|
| Source/transform/sink and victim execution | [xss_reflected_stored_dom.md](SKILL_FILES/VULNERABILITIES/WEB/xss_reflected_stored_dom.md) |
| Named DOM properties and actual consumer gadgets | [dom_clobbering.md](SKILL_FILES/VULNERABILITIES/WEB/dom_clobbering.md) |
| Sender/source binding, replies and downstream action | [postmessage_attacks.md](SKILL_FILES/VULNERABILITIES/WEB/postmessage_attacks.md) |
| Cross-origin response read authority | [cors_misconfig.md](SKILL_FILES/VULNERABILITIES/WEB/cors_misconfig.md) |
| Ambient authority and browser request delivery | [csrf_all_types.md](SKILL_FILES/VULNERABILITIES/WEB/csrf_all_types.md) |
| Trusted client constructing attacker-influenced requests | [client_side_csrf.md](SKILL_FILES/VULNERABILITIES/WEB/client_side_csrf.md) |
| Actual CSP directives, nonces, hashes and allowed gadgets | [csp_bypass.md](SKILL_FILES/VULNERABILITIES/WEB/csp_bypass.md) |
| Origins/sites, cookies, Trusted Types, workers and embedding | [browser_isolation.md](SKILL_FILES/VULNERABILITIES/WEB/browser_isolation.md) |
| Sandbox and parent/child origin boundaries | [iframe_attacks.md](SKILL_FILES/VULNERABILITIES/WEB/iframe_attacks.md) |
| Actual hit targets, victim cookies and sensitive actions | [clickjacking.md](SKILL_FILES/VULNERABILITIES/WEB/clickjacking.md) |
| Validator and actual navigation destination | [open_redirect.md](SKILL_FILES/VULNERABILITIES/WEB/open_redirect.md) |
| Handshake, message authorization and subscription lifetime | [websocket_attacks.md](SKILL_FILES/VULNERABILITIES/WEB/websocket_attacks.md) |
| Browser-visible cross-origin oracle and secret inference | [xs_leaks.md](SKILL_FILES/VULNERABILITIES/WEB/xs_leaks.md) |
| CSS grammar, rendering and conditional network inference | [css_injection.md](SKILL_FILES/VULNERABILITIES/WEB/css_injection.md) |

### HTTP, caching and routing

| Boundary/question | Guide |
|---|---|
| Framing, downgrade, CL.0/H2.0/0.CL and modern desync | [http_request_smuggling.md](SKILL_FILES/VULNERABILITIES/WEB/http_request_smuggling.md) |
| Header grammar and context-specific splitting/tunnelling | [crlf_header_injection.md](SKILL_FILES/VULNERABILITIES/WEB/crlf_header_injection.md) |
| Keying/cacheability and clean-client influenced response | [cache_poisoning.md](SKILL_FILES/VULNERABILITIES/WEB/cache_poisoning.md) |
| Private content and path/cache interpretation | [web_cache_deception.md](SKILL_FILES/VULNERABILITIES/WEB/web_cache_deception.md) |
| Decode/normalize/validate/route destination disagreement | [url_parser_differentials.md](SKILL_FILES/VULNERABILITIES/WEB/url_parser_differentials.md) |
| Duplicate input/accessor semantics across layers | [http_parameter_pollution.md](SKILL_FILES/VULNERABILITIES/WEB/http_parameter_pollution.md) |
| Input embedded in internal query/path/structured request | [server_side_parameter_pollution.md](SKILL_FILES/VULNERABILITIES/WEB/server_side_parameter_pollution.md) |
| Host trust in URL generation and backend selection | [host_header_attacks.md](SKILL_FILES/VULNERABILITIES/WEB/host_header_attacks.md) |
| Observed parser/configuration differential | [waf_bypass_all_techniques.md](SKILL_FILES/VULNERABILITIES/WEB/waf_bypass_all_techniques.md) |
| Origin reach and independent enforcement | [cloudflare_bypass.md](SKILL_FILES/VULNERABILITIES/WEB/cloudflare_bypass.md) |

### Backend inputs and data consumers

| Boundary/question | Guide |
|---|---|
| Query construction and matched semantic differentials | [sqli_all_types.md](SKILL_FILES/VULNERABILITIES/WEB/sqli_all_types.md) |
| Operator, expression and type-aware query boundaries | [nosql_injection.md](SKILL_FILES/VULNERABILITIES/WEB/nosql_injection.md) |
| ORM selectors, relationships and predicate inference | [orm_filter_inference.md](SKILL_FILES/VULNERABILITIES/WEB/orm_filter_inference.md) |
| Effective server request identity/destination/visibility | [ssrf_all_types.md](SKILL_FILES/VULNERABILITIES/WEB/ssrf_all_types.md) |
| Actual template language, context and sandbox | [ssti_all_engines.md](SKILL_FILES/VULNERABILITIES/WEB/ssti_all_engines.md) |
| XML fetch/expansion/XInclude and processing pipelines | [xxe_all_types.md](SKILL_FILES/VULNERABILITIES/WEB/xxe_all_types.md) |
| Integrity, loaded types and actual load-time hooks | [deserialization_all_langs.md](SKILL_FILES/VULNERABILITIES/WEB/deserialization_all_langs.md) |
| Command argv/shell and evaluation consumers | [rce_all_vectors.md](SKILL_FILES/VULNERABILITIES/WEB/rce_all_vectors.md) |
| Path containment, file read and include semantics | [lfi_rfi_path_traversal.md](SKILL_FILES/VULNERABILITIES/WEB/lfi_rfi_path_traversal.md) |
| Upload/store/process/serve/render lifecycle | [file_upload_bypass.md](SKILL_FILES/VULNERABILITIES/WEB/file_upload_bypass.md) |
| Assignment source, prototype scope and reachable gadget | [prototype_pollution.md](SKILL_FILES/VULNERABILITIES/WEB/prototype_pollution.md) |
| SSR/RSC/Server Actions and framework cache boundaries | [framework_server_actions.md](SKILL_FILES/VULNERABILITIES/WEB/framework_server_actions.md) |

### Ownership and build edges

| Boundary/question | Guide |
|---|---|
| Current provider claimability and subsequent trust | [subdomain_takeover.md](SKILL_FILES/VULNERABILITIES/WEB/subdomain_takeover.md) |
| Actual resolver precedence and package attribution | [dependency_confusion.md](SKILL_FILES/VULNERABILITIES/WEB/dependency_confusion.md) |

## Canonical API ownership and compatibility

Use api-mode for protocol-wide REST/GraphQL/gRPC/schema and HTTP API policy work.
A browser/session feature stays traceable across API, worker and renderer calls;
routing must not stop investigation at an artificial skill boundary.

| Old web entry | Canonical owner |
|---|---|
| `graphql_attacks.md` | api-mode `graphql_introspection_attacks.md` |
| `mass_assignment.md` | api-mode `api_mass_assignment.md` |
| `rate_limiting_bypass.md` | api-mode `api_rate_limiting_bypass.md` |
| `csrf_websocket.md` | this skill `websocket_attacks.md` |

Old paths remain compatibility pointers, not second methodologies.
`references/vuln-library.md` is an index only; it cannot supply legacy payloads.
The payloads skill locates the same canonical guide instead of maintaining another
executable copy. Use scr-mode for a source-root-cause investigation; downstream
cloud/mobile/AI boundaries require explicit relevance and policy, not automatic
expansion because a recipe mentions them.
