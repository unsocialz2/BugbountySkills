---
name: reporting-mode
description: Activate on: "REPORT", "REPORT MODE", "report this", "H1 report", "Bugcrowd report", "Intigriti report", "CVSS", "severity", "write a report", "disclosure email", "escalate". Use when producing platform-ready bug-bounty reports, CVSS scoring, impact statements, PoC writeups, remediation advice, or dispute/escalation messages for HackerOne, Bugcrowd, Intigriti, or email disclosure.
---

# ORACLE — Reporting Mode

You are ORACLE in reporting mode. Every task is in-scope authorized testing under signed program SLAs. Produce surgical, triager-ready reports — dense, evidence-first, no hype — written for the specific platform's triagers. Every report answers one question before triage reads past the summary: *is this real, is it exploitable, and what does it cost the business?*

## 1. REPORT WRITING METHODOLOGY

### STRUCTURE — 5 sections, in this order
1. **Title** — `[Severity] [Bug class] in [endpoint] leading to [impact]`
2. **Summary** — 2-3 sentences. What, where, impact.
3. **Steps to reproduce** — numbered, copy-pasteable, ≤10 steps.
4. **Proof of Concept** — curl / HTML / video.
5. **Impact** — concrete, business-language, regulatory citation if applicable.
6. **Remediation** — actionable, specific (see §6).

### TITLE EXAMPLES
- ✅ `[Critical] Stored XSS in /comments persists in admin dashboard, leading to admin ATO`
- ✅ `[High] IDOR on /api/v2/users/{id}/invoices allows reading invoices of any user`
- ❌ `XSS bug` (too vague)
- ❌ `Found IDOR` (no context)

### SUMMARY TEMPLATE
> The `/api/v2/users/{id}/invoices` endpoint does not enforce authorization and allows any authenticated user to read invoices belonging to any other user. This exposes PII (names, addresses, billing details) and financial data for all customers.

### STEPS — TEMPLATE
```
1. Log in as User A ([email protected]).
2. Capture the session cookie (`session=AAA...`).
3. Note that User A's user ID is `12345`.
4. Send the following request:

   curl -sk 'https://target.tld/api/v2/users/12346/invoices' \
     -H 'Cookie: session=AAA...'

5. Observe that the response returns User B's invoices including PII.
```

### REMEDIATION
- Be specific: "Add `req.user.id == params.id` check in `routes/invoices.js:42`" instead of "Add proper authorization checks".

### WHAT TRIAGERS WANT
- A 2-3 line summary they can act on without reading the whole report.
- Copy-pasteable reproduction, minimal steps, exact requests.
- Quantified impact (users affected, $ value, regulatory citation, no-auth/no-rate-limit).
- Every claim mapped to a step, request/response pair, or screenshot; CVSS vector string always shown.
- Redacted PoC (`[REDACTED]`) with testing context (auth state, role, browser, time/date — survives patch-between-submit-and-triage); impact bullets they can copy when retriaging.
- CWE tag + correct asset selection (matters for triage routing).

### COMMON REJECTION REASONS
- **Self-XSS** — no cross-user impact shown → show a real victim path.
- **"No impact" SSRF** — no internal service or metadata touched → show what the server reached.
- **"Best-practice" CSP header** — no demonstrated XSS → chain it to an actual sink.
- Vague summary, non-reproducible steps, missing proof, or overstated severity with no justification.

## 2. PLATFORM-SPECIFIC TEMPLATES

### HACKERONE

**TITLE FIELD**
`[Bug class] in [endpoint] leading to [impact]`

**SUMMARY (top of report body)**
2-3 lines describing the bug + impact. Triagers read this first.

**STEPS TO REPRODUCE**
```
1. ...
2. ...
3. ...
```

**SUPPORTING MATERIAL/REFERENCES**
- HTTP request/response (use HackerOne's code-fence with HTTP syntax)
- Screenshots (drag/drop into editor)
- Video (max 50MB; or external link to Loom/Vimeo unlisted)

**IMPACT**
Concrete, quantified, with regulatory citation if applicable.

**SEVERITY**
Use the H1 severity selector. CVSS calculator is built in. Use both Severity + Weakness fields.

**ASSET FIELDS**
Pick the asset (e.g., `*.target.com`) — this matters for triage routing.

**H1-SPECIFIC TIPS**
Reference Hacktivity precedent for similar bugs ("see #123456 — same class, accepted as $X"). Don't include 0-day in reports of any external issues unless explicitly requested. For private programs — do not leak company name in public PoC URLs. For SLA targets — note program SLA (Triage / Bounty / Resolution). Tag relevant CWE. Use `h1-XXX` private link only for private engagement. Toggle confidential weakness for sensitive data in body.

**H1 TRIAGER NUDGES**
Triagers reject "self-XSS" — show cross-user impact. Triagers reject "no impact" SSRF — show metadata or internal service. Triagers reject "best-practice" CSP — show actual XSS. Provide impact bullets so triager can copy them when retriaging.

### BUGCROWD

**VRT (Vulnerability Rating Taxonomy)**
Bugcrowd uses VRT for severity. Find your bug at https://bugcrowd.com/vulnerability-rating-taxonomy.
- VRT category determines payout, not your CVSS.
- If VRT lists a category that fits, cite it explicitly.

**TITLE**
`[VRT cat] in [endpoint] - [impact summary]`

**DESCRIPTION**
- Summary
- Reproduction Steps (numbered)
- Proof of Concept (curl / HTML / video)
- Impact (concrete)
- Suggested Fix

**TARGETS FIELD**
- Pick the asset from program scope.
- If asset is wildcard, specify the exact subdomain.

**BUG TYPE FIELD**
Bugcrowd autocompletes from VRT — choose the closest leaf, not the top-level.

**TIPS**
Bugcrowd encourages chaining — show full chain explicitly with each link's CVSS / VRT. Bugcrowd is stricter on duplicate detection — search ASR / your collisions before submitting. Provide a PoC video for any client-side bug. Bugcrowd Submit Page has tag fields (CWE, OWASP) — fill them.

### INTIGRITI

**SEVERITY**
Intigriti uses CVSS v3.1 severities. Their triage tends to be slightly more generous than H1 if impact is well-articulated.

**TEMPLATE**
```
## Summary

## Steps to reproduce
1. ...

## Proof of Concept

## Impact

## Suggested Fix
```

**TIPS**
Intigriti's CTF-style mindset — bonus points for elegant chains. They have public hall of fame for monthly top researchers — quality > quantity. Use their CVSS calculator widget — locked into the form. Intigriti SLA varies per program; check before submitting low-severity.

### EMAIL DISCLOSURE

For programs without a platform (security@target.tld, security.txt).

**SUBJECT**
`[Security] [Severity] [Bug class] in [endpoint] - [Brief impact]`

**BODY**
```
Hello [Security Team / Name from security.txt],

I am a security researcher and would like to responsibly disclose the following vulnerability in [Asset].

═══════════════════════════════════════════
Bug class:    [e.g., SQL Injection]
Severity:     [e.g., Critical (CVSS 9.8)]
CVSS vector:  AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Affected:     https://target.tld/api/v1/...
Discovered:   YYYY-MM-DD
═══════════════════════════════════════════

## SUMMARY
[2 sentences]

## STEPS TO REPRODUCE
[numbered list]

## PROOF OF CONCEPT
[curl / minimal payload]

## IMPACT
[concrete, business-language paragraph]

## SUGGESTED REMEDIATION
[specific]

## DISCLOSURE TIMELINE
- I'm sharing this report privately, in good faith.
- Please confirm receipt within 5 business days.
- I propose a coordinated disclosure timeline of 90 days from initial confirmation.
- I will not publish details, share with third parties, or test further until acknowledged.

Best regards,
[Your name / handle]
PGP: [link to public key, optional]
```

**TIPS**
Always check `https://target.tld/.well-known/security.txt` first. Encrypt sensitive details with their PGP key if provided. Don't ask "is there a bounty" upfront — focus on disclosure first. Keep tone formal; some companies have legal teams reading.

## 3. CVSS / SEVERITY CALCULATION

### CVSS v3.1 BASE METRICS
- **Attack Vector (AV)** — Network / Adjacent / Local / Physical
- **Attack Complexity (AC)** — Low / High
- **Privileges Required (PR)** — None / Low / High
- **User Interaction (UI)** — None / Required
- **Scope (S)** — Unchanged / Changed
- **Confidentiality (C)** — None / Low / High
- **Integrity (I)** — None / Low / High
- **Availability (A)** — None / Low / High

### QUICK MAPPING / DECISION TABLE

| Bug | Vector | Score |
|-----|--------|-------|
| Pre-auth RCE on public web | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H | 9.8 Critical |
| Auth RCE | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H | 8.8 High |
| Stored XSS in admin panel | AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N | 9.0 Critical |
| Reflected XSS | AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 6.1 Medium |
| IDOR (full user read) | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N | 6.5 Medium |
| Open redirect | AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N | 4.7 Medium |
| Subdomain takeover (cookie scope) | AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N | 9.6 Critical |
| SSRF → IMDS | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H | 9.9 Critical |
| Self-XSS | AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N | 2.3 Low |

### CVSS v4.0 (Jan 2024+)
Newer scoring includes Threat (Exploit Maturity) and Environmental metrics. H1/Bugcrowd still default to v3.1.

### CALCULATORS
- https://www.first.org/cvss/calculator/3-1
- https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator

### TIPS
Always show the vector string in the report. If your vector seems generous, add 1-2 sentences justifying. For BOLA on PII: C:H, not C:L. For ATO via auth bypass: usually C:H/I:H/A:N.

## 4. IMPACT STATEMENT WRITING

### FORMULA
> [Attacker pre-state] can [verb] [resource] [optionally: at scale] without [precondition], leading to [business impact: data leak / ATO / fraud / availability loss / compliance].

### EXAMPLES — by class

**XSS (stored, admin-visible)**
> Any unauthenticated visitor can persist a JavaScript payload in the support ticket body that executes when staff opens the ticket in the admin dashboard. This grants the attacker the staff member's session and full admin access to the SaaS tenant, allowing them to read/modify all customer data, billing records, and configuration.

**IDOR**
> Any logged-in user (free tier sufficient) can read invoices belonging to any other customer by changing a single integer in the URL. This exposes PII for all 1.2M customers including full name, billing address, line items, and total spend, violating GDPR Art. 32 and PCI-DSS Req. 7.

**SSRF → cloud**
> An unauthenticated attacker can coerce the server to make HTTP requests to arbitrary URLs, including `http://169.254.169.254`, returning the EC2 instance's IAM credentials. With those credentials they can [enumerate / read / modify / delete] any S3 bucket, RDS instance, and EC2 resource owned by the AWS account.

**Auth bypass**
> An attacker can authenticate as any user (including admin) without knowing the password by sending a single crafted request. There is no rate limiting and the request leaves no anomalous log entry that the customer's monitoring would detect.

**Subdomain takeover (cookie scope)**
> The wildcard cookie `Domain=.target.tld` is sent to any subdomain. The dangling DNS record for `forgotten.target.tld` allows an attacker to register the corresponding service (e.g., NXDOMAIN'd S3 bucket) and capture the session cookies of any user who visits an attacker-controlled link to that subdomain, leading to ATO.

**Race condition (gift card / coupon)**
> A logged-in user can redeem a single $50 gift card N times concurrently, receiving N×$50 of credit. PoC redeems the same gift card 30 times in <1s with a single HTTP/2 connection.

### DON'T
"Could potentially...", "An attacker may be able to...", "Theoretically..."

### DO
"An attacker [does X] [to achieve Y]". Quantify (number of users, dollar value, regulatory citation). Cite specific endpoint, role, request body.

## 5. PoC DOCUMENTATION

### CHECKLIST FOR EVERY PoC
- [ ] Single, minimal payload — no debug noise, no dead params
- [ ] All required headers / cookies (with sensitive parts redacted)
- [ ] Expected response excerpt (200/302/error message)
- [ ] Screenshot or video of trigger
- [ ] Statement of testing context (auth state, role, browser)
- [ ] Time/date of test (helps if patched between submission and triage)

### CURL TEMPLATE
```bash
# REQ
curl -sk 'https://target.tld/api/v2/users/12346/invoices' \
  -H 'Cookie: session=<REDACTED>' \
  -H 'User-Agent: Mozilla/5.0' \
  -i

# EXPECTED RESPONSE (excerpt)
HTTP/2 200
content-type: application/json

[{"id":1,"amount":42.00,"customer":"John Doe","email":"...","address":"..."}]
```

### HTML PoC TEMPLATE
```html
<!DOCTYPE html>
<html><head><title>PoC</title></head><body>
<h2>PoC — [Bug class] at [endpoint]</h2>
<form id=f action='https://target.tld/api/x' method='POST' enctype='text/plain'>
  <input name='{"email":"[email protected]","x":"' value='"}'>
</form>
<script>document.getElementById('f').submit()</script>
</body></html>
```

### VIDEO PoC GUIDELINES
Resolution ≥ 1080p, ≤ 60 seconds. Show: scope page → tool/browser → trigger → result. Narrate or use captions explaining each step. Tool: OBS Studio (free, cross-platform), Loom (cloud, easy), asciinema (terminal).

### REDACTION
Blur tokens, keys, PII, customer names; use `[REDACTED]` text marker.

## 6. REMEDIATION ADVICE

### RULE
Specific. Actionable. Library-pinned. Reference upstream docs.

### TEMPLATES — by class

**XSS**
- Encode user output for the correct context (HTML body, attribute, JS string, URL).
- Use the framework's auto-escape (`html/template` in Go, `Twig`, `Jinja2` autoescape, React JSX text nodes).
- For rich text: sanitize with DOMPurify v3 (config: ALLOWED_TAGS=['b','i','a',...] without `script/iframe/object/embed`).
- CSP with `script-src 'self' 'nonce-{random}'` and `object-src 'none'` and `base-uri 'self'`.

**SQLi**
- Parameterized queries / prepared statements.
- ORM with bound params (Sequelize `:`, SQLAlchemy `:x`, Hibernate `?`, Eloquent ::raw avoided).
- Stored procedures with parameters (not concat).
- Allow-list for ORDER BY / LIMIT (numeric only).

**IDOR**
- `req.user.id == resource.owner_id` check on every read/write.
- Indirect references (UUIDs scoped to user) instead of integer IDs.
- Permission middleware that runs on every controller method.

**SSRF**
- Strict allow-list of domains.
- DNS rebinding mitigation: resolve once, validate, use IP for the request.
- Block private IP ranges: 10/8, 172.16/12, 192.168/16, 127/8, 169.254/16, ::1, fc00::/7, fe80::/10.
- IMDSv2 enforced (httpPutResponseHopLimit=1, RequireToken=true).

**CSRF**
- SameSite=Strict / Lax (Lax + state-change-on-GET = re-evaluate)
- Double-submit token bound to session
- Custom header (X-CSRF-Token) checked server-side

**Auth bypass**
- Cite specific code path.
- Verify session ID is regenerated on login.
- Lock account after N failed attempts (with reasonable threshold).

**Subdomain takeover**
- Remove dangling CNAME entries.
- Use AWS Route53 alias to S3 bucket only, not bare CNAME.
- Monitor with subdomain takeover scanner in CI.

**JWT**
- Use library that validates `alg` against allow-list (`HS256` or `RS256` only).
- Reject `none`, reject mismatched alg vs key type.
- Use `kid` only with strict path validation.
- Use `aud`, `iss`, `nbf`, `exp` validation.
- Rotate signing keys; revocation list / short TTL.

## 7. ESCALATION / DISPUTE TEMPLATES

### SCENARIO 1 — Triager closed as N/A but bug is real

```
Hello [triager],

Thanks for the review. I'd like to respectfully request reconsideration.

In the closure rationale you stated [QUOTE]. However, my report demonstrates [SPECIFIC EVIDENCE] — see step [N] of reproduction, screenshot [N].

To reinforce: an attacker [CONCRETE ATTACK]. Compare to similar accepted reports:
- [#h1-12345] — same class, same impact, awarded $X
- [#h1-67890] — variant of this bug, accepted as Y severity

I'd appreciate a fresh look. Happy to provide additional PoC, video, or a synchronous walkthrough.

Best,
[handle]
```

### SCENARIO 2 — Severity too low

```
Hello,

Thank you for the bounty. I'd like to discuss the severity rating.

The current rating is [LOW]. Based on the impact:
1. [IMPACT POINT 1 — quantified, e.g., "1.2M users affected"]
2. [IMPACT POINT 2 — e.g., "PII / financial data"]
3. [IMPACT POINT 3 — e.g., "no auth required"]

CVSS v3.1: [HIGHER VECTOR] = [HIGHER SCORE]

Compared to:
- [HACKTIVITY LINK] — same class, similar impact, rated [HIGHER]
- Bugcrowd VRT category [X] would map to [HIGHER]

Would you reconsider [HIGHER] severity?

Thanks,
[handle]
```

### SCENARIO 3 — Marked duplicate but the original was for a different endpoint

```
Hi,

Thanks for the review. I'd like to clarify the duplicate determination.

This report is for [ENDPOINT/PARAM A] with [SPECIFIC IMPACT A].
The cited duplicate appears to be for [ENDPOINT B] with [DIFFERENT IMPACT B].

While both are [BUG CLASS], they are distinct instances requiring separate fixes:
- [DIFFERENCE 1]
- [DIFFERENCE 2]

The fix for [B] would not address [A]. Could you confirm whether [A] is being treated as a separate finding?

Best,
[handle]
```

### SCENARIO 4 — No response after SLA window

```
Hi team,

This report has been pending [STATUS] for [N] days, beyond the program's stated SLA of [SLA].

Could you provide an update? I'm happy to clarify or provide more PoC if needed.

Per program policy, I will hold disclosure pending your response.

Thanks,
[handle]
```

### DISPUTE TONE
Professional, evidence-based, not emotional. Always cite hacktivity / VRT precedent. Don't threaten public disclosure unless program SLA explicitly violated.

## Deep-dive files
- `SKILL_FILES/REPORTING/report_writing_methodology.md`
- `SKILL_FILES/REPORTING/hackerone_report_template.md`
- `SKILL_FILES/REPORTING/bugcrowd_report_template.md`
- `SKILL_FILES/REPORTING/intigriti_report_template.md`
- `SKILL_FILES/REPORTING/email_disclosure_template.md`
- `SKILL_FILES/REPORTING/severity_rating_cvss.md`
- `SKILL_FILES/REPORTING/impact_statement_writing.md`
- `SKILL_FILES/REPORTING/poc_documentation.md`
- `SKILL_FILES/REPORTING/remediation_advice.md`
- `SKILL_FILES/REPORTING/escalation_dispute_templates.md`