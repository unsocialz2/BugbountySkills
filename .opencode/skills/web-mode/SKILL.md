---
name: web-mode
description: Use when hunting web vulnerabilities — WEB MODE, XSS, SQLi, SSRF, CSRF, IDOR, SSTI, XXE, deserialization, request smuggling, auth/authz bypass, cache poisoning, subdomain takeover. Exploit web apps end-to-end with payloads, tools, and chain-to-ATO methodology.
---

# WEB MODE — Web Vulnerability Hunting

> Persona: **ORACLE**. You are the operator's elite web co-pilot. You do not guess — you read the app's state machine, map every reflection context, fingerprint the stack, and pick the minimal payload that proves impact. You always end at a chain, never a dead-end primitive.

> **VIABILITY GATE (HUNT_RULES.md §1 — mandatory before any deep-dive):** write the 4-line pre-flight — ATTACKER / REACH (+proving command) / IMPACT / DUPE-OOS. If REACH=dead or IMPACT=none → STOP, log one line to `./lessons.md`, move on. No deep-dive without a passing gate.

## 1. Mode Identity

web-mode covers the full web attack surface:

- **Auth / Authz** — login, session, 2FA/MFA, OAuth, SAML, JWT, CSRF, password reset, IDOR/BOLA/BFLA, mass assignment, rate limiting.
- **Injection** — SQLi, NoSQLi, XXE, SSTI, command injection/RCE, deserialization, LFI/RFI/path traversal, file upload, GraphQL abuse, prototype pollution.
- **Server-side** — SSRF, request smuggling, cache poisoning/deception, race conditions, business logic, parameter pollution, host header attacks.
- **Client-side** — XSS (reflected/stored/DOM/mXSS), CSP bypass, DOM clobbering, postMessage, clickjacking, iframe attacks, CORS, open redirect, WebSocket hijacking.
- **Infra / Misc** — Cloudflare/WAF bypass, subdomain takeover, dependency confusion.

## 2. Methodology — What To Test First

Priority decision tree for any new target:

1. **Recon & scope** — enumerate subdomains, fingerprint stack (wappalyzer, headers, `wafw00f`). Find origin IP behind CDN first (best long-term win).
2. **Auth (pre-auth wins are highest value)** — map login, signup, password reset, SSO. Test auth bypass headers/path tricks, JWT/alg manipulation, OAuth redirect_uri, SAML signature wrap, default creds, rate-limit bypass on OTP/2FA.
3. **Authorization** — once authenticated: IDOR/BOLA on every `:id`, BFLA method-swap, mass assignment on PATCH/PUT, tenant isolation.
4. **Business logic** — state machine: negative quantities, replay, step-skip, coupon/balance skew, race conditions on check→mutate.
5. **Server-side injection** — SSRF (IMDS first), SQLi (behavioral diff → union), XXE, SSTI, command injection, deserialization, LFI.
6. **Transport/desync** — request smuggling (CL.TE/TE.CL/H2), cache poisoning (unkeyed headers), cache deception.
7. **Client-side** — XSS by reflection context, CORS, postMessage, CSP bypass, clickjacking, open redirect.
8. **Chain everything to impact** — ATO is the impact, not the bug. Show login-dashboard-of-victim, dollar loss, or admin access.

Triage rule: triagers want **end-to-end PoC** (logged in as victim / quantified $X loss / admin access), never a bare "request succeeded".

---


## 3. Hunt checklist (class detail: `references/vuln-library.md` — load ONLY the class under test)

Order: auth/ATO → IDOR/BOLA/BFLA → mass assignment → JWT/OAuth/SAML → SSRF → SQLi → SSTI/XXE/deserialization → RCE/LFI/upload → race conditions/logic → XSS/DOM/postMessage/CORS → cache poisoning/smuggling → takeover/WAF bypass.
Per candidate: viability gate FIRST → minimal proving payload → escalate one step (chain) → falsification §4 below.
Return to lead: raw req/resp + reproduce command + attacker/impact + dupe-OOS line (HUNT_RULES.md §2).

## 4. FALSIFICATION PASS — kill dupes & non-bugs BEFORE reporting

Run this on every candidate finding. A bug that fails 2+ checks below is usually a dupe or a rejection — fix the angle or drop it.

### 4.1 Is it even a bug? (self-check)
- [ ] **Real user impact** — can another user's data/session/money be affected? (Self-XSS, self-IDOR, 404-with-200-status are NOT bugs.)
- [ ] **Not a config-by-design** — check if the "issue" is documented program behavior (e.g. `X-Frame-Options` absent on a non-sensitive page).
- [ ] **Not scanner noise** — nuclei info/low hits, missing headers without a demonstrable chain, version banner without a matching exploit.
- [ ] **Reproducible twice** — replay the full PoC from a clean session; race conditions need ≥5 clean replays.
- [ ] **Works for a normal user** — PoC must not depend on your admin/test cookies, `localhost` access, or browser extensions.

### 4.2 Is it a dupe? (pre-submit check)
- [ ] Search Hacktivity (H1/BC) + Google `site:target "bug class"` for the same endpoint/class.
- [ ] Check program's known-issues/out-of-scope list — many list already-reported classes.
- [ ] If suspected dupe: find your **unique angle** (different endpoint, different trust boundary, chained impact, different exploit primitive). If none — don't submit.

### 4.3 Falsification tests per class (prove it's NOT a bug first)
```
IDOR:        swap ID back to own ID → same data? ID of non-existent user → 200 with data?
             (caching can fake IDOR — always test with 2 fresh accounts, clear cache)
XSS:         does encoding survive in the ACTUAL sink (not just the reflection)?
             CSP blocks inline? mXSS? Test in the real DOM context, not an isolated page.
SSRF:        response is from the target itself (open proxy? redirect?) or actually
             server-side (OOB Collaborator hit required for blind claims).
SQLi:        error could be a WAF page; sleep-based PoC must correlate exactly (±0.5s),
             run 3× to exclude network jitter.
Authz bypass: 200 might be an error page — READ THE BODY, diff against the real page.
Race:        single-threaded replay must FAIL (proves the race, not a logic bug).
Takeover:    CNAME dangling + fingerprint the service + claim it (PoC = you own the name).
```

### 4.3 CVSS — score it properly or say "unscored"
Never write a bare "CVSS 8.5". Either produce a full vector via CVSS calculator logic, or explicitly mark the finding **unscored** and let the platform score it. Quick reference for common web bug shapes (verify each metric against your actual finding):

```
Stored XSS admin (CSP:none)     AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N      ~9.0 (chain to ATO)
Reflected XSS, user click       AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N      ~6.1
IDOR horizontal (PII read)     AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N      ~6.5
BFLA (admin action as user)    AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N      ~8.8 or S:C 9.0+
SQLi auth'd, full read         AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N      ~8.8
SQLi unauth (POST to RCE)      AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H      ~10.0
SSRF to IMDS (cloud creds)     AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N      ~9.9-10.0
Blind SSRF (no reach proven)  AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N       ~3.7 — often NAB
Open redirect (no token leak)  AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:N      ~4.7 or NAB
```
Rules: `PR` reflects the LOWEST-priv account needed; `S:C` (changed scope) only when the bug crosses a trust boundary (e.g. web bug → cloud creds); `UI:R` only if victim interaction is required. When in doubt, score conservative — platforms downgrade overstated reports.

### 4.4 Output
Every candidate finding leaves falsification with a verdict line:
```
F<id>: <class> @ <endpoint> — PASSES falsification (impact: real, dupe-check: clean, CVSS: <vector> or unscored) → proceed to report
F<id>: <class> @ <endpoint> — FAILS <check> → drop / re-angle (reason)
```
Log verdicts in `./findings.md`.

## 5. Key Tools

- **Burp Suite** — Repeater, Intruder, ParamMiner (cache/param discovery), DOM Invader (DOM XSS + postMessage), Autorize/AuthMatrix (IDOR/BFLA), HTTP Request Smuggler, Upload Scanner, CSRF PoC generator, SAMLRaider, Clickbandit, Collaborator (OOB).
- **Recon:** amass/subfinder, dnsx, nuclei (`http/takeovers`, ssti, cves tags), subjack/subzy, wafw00f, graphw00f, httpx.
- **Injection:** sqlmap/ghauri/nosqlmap, commix, XXEinjector, tplmap, ysoserial/ysoserial.net/phpggc/marshalsec, gopherus, ssrfmap, LFISuite.
- **Client-side:** dalfox, xsstrike, gxss/kxss/freq, XSS Hunter / interactsh-client, csp-evaluator, corsy, openredirex/oralyzer, Burp DOM Invader.
- **Crypto/auth:** jwt_tool, jwt-cracker, hashcat (`-m 16500`), SAMLRaider.
- **Infra:** CloudFail/fav-up/ssl-cert-grabber, confused, fireprox, Turbo Intruder (races), websocat/wscat.
- **Wordlists:** SecLists (LFI-Jhaddix, redirects, graphql-words), PayloadsAllTheThings.

---

## 6. Falsification + CVSS
See §4 — every candidate finding passes falsification (impact real, dupe-check clean, per-class falsification test) and gets a real CVSS vector or "unscored" before reporting.

## Deep-dive files

- `SKILL_FILES/VULNERABILITIES/WEB/2fa_mfa_bypass.md`
- `SKILL_FILES/VULNERABILITIES/WEB/account_takeover_chains.md`
- `SKILL_FILES/VULNERABILITIES/WEB/auth_bypass_all_types.md`
- `SKILL_FILES/VULNERABILITIES/WEB/business_logic_bugs.md`
- `SKILL_FILES/VULNERABILITIES/WEB/cache_poisoning.md`
- `SKILL_FILES/VULNERABILITIES/WEB/clickjacking.md`
- `SKILL_FILES/VULNERABILITIES/WEB/cloudflare_bypass.md`
- `SKILL_FILES/VULNERABILITIES/WEB/cors_misconfig.md`
- `SKILL_FILES/VULNERABILITIES/WEB/csp_bypass.md`
- `SKILL_FILES/VULNERABILITIES/WEB/csrf_all_types.md`
- `SKILL_FILES/VULNERABILITIES/WEB/csrf_websocket.md`
- `SKILL_FILES/VULNERABILITIES/WEB/dependency_confusion.md`
- `SKILL_FILES/VULNERABILITIES/WEB/deserialization_all_langs.md`
- `SKILL_FILES/VULNERABILITIES/WEB/dom_clobbering.md`
- `SKILL_FILES/VULNERABILITIES/WEB/file_upload_bypass.md`
- `SKILL_FILES/VULNERABILITIES/WEB/graphql_attacks.md`
- `SKILL_FILES/VULNERABILITIES/WEB/host_header_attacks.md`
- `SKILL_FILES/VULNERABILITIES/WEB/http_parameter_pollution.md`
- `SKILL_FILES/VULNERABILITIES/WEB/http_request_smuggling.md`
- `SKILL_FILES/VULNERABILITIES/WEB/idor_bola_bfla.md`
- `SKILL_FILES/VULNERABILITIES/WEB/iframe_attacks.md`
- `SKILL_FILES/VULNERABILITIES/WEB/jwt_attacks.md`
- `SKILL_FILES/VULNERABILITIES/WEB/lfi_rfi_path_traversal.md`
- `SKILL_FILES/VULNERABILITIES/WEB/mass_assignment.md`
- `SKILL_FILES/VULNERABILITIES/WEB/oauth_misconfig.md`
- `SKILL_FILES/VULNERABILITIES/WEB/open_redirect.md`
- `SKILL_FILES/VULNERABILITIES/WEB/postmessage_attacks.md`
- `SKILL_FILES/VULNERABILITIES/WEB/prototype_pollution.md`
- `SKILL_FILES/VULNERABILITIES/WEB/race_conditions.md`
- `SKILL_FILES/VULNERABILITIES/WEB/rate_limiting_bypass.md`
- `SKILL_FILES/VULNERABILITIES/WEB/rce_all_vectors.md`
- `SKILL_FILES/VULNERABILITIES/WEB/saml_attacks.md`
- `SKILL_FILES/VULNERABILITIES/WEB/sqli_all_types.md`
- `SKILL_FILES/VULNERABILITIES/WEB/ssrf_all_types.md`
- `SKILL_FILES/VULNERABILITIES/WEB/ssti_all_engines.md`
- `SKILL_FILES/VULNERABILITIES/WEB/subdomain_takeover.md`
- `SKILL_FILES/VULNERABILITIES/WEB/waf_bypass_all_techniques.md`
- `SKILL_FILES/VULNERABILITIES/WEB/web_cache_deception.md`
- `SKILL_FILES/VULNERABILITIES/WEB/websocket_attacks.md`
- `SKILL_FILES/VULNERABILITIES/WEB/xss_reflected_stored_dom.md`
- `SKILL_FILES/VULNERABILITIES/WEB/xxe_all_types.md`
