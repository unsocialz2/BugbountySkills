---
name: recon-mode
description: Use when a user activates "RECON" or "RECON MODE", asks for "reconnaissance", "subdomain" enumeration, "OSINT", "attack surface", "asset discovery", "enumerate", "enumeration", "fingerprint", "passive recon", "wayback", "dork", or "how do I start on <target>" — this skill runs the full bug-bounty reconnaissance workflow from passive OSINT through subdomain enumeration, DNS analysis, JS/archive mining, content discovery, port scanning, fingerprinting, dorks, and cloud asset discovery, and produces prioritized attack-surface intelligence. ALSO activates whenever the operator pastes/links their own recon results for a target — audit them against the coverage matrix first (§0), fill only missing stages, never repeat completed work.
---

# recon-mode

> Target context comes from `HUNT_RULES.md §0`. The active workspace is the current
> `<repo>/targets/<target>/` directory. Scope comes from its `scope.txt`/scope CSV
> plus `rules.txt`; program restrictions always override generic recon defaults.
> Kali + VPS, free-tier first (`subfinder/httpx/nuclei/katana/dnsx/naabu`). Paid
> APIs (`$ST_KEY`, `$VT_KEY`, Chaos) optional. Log everything to `./recon_data/`.

> **VIABILITY GATE (HUNT_RULES.md §1 — mandatory before any deep-dive):** write the 4-line pre-flight — ATTACKER / REACH (+proving command) / IMPACT / DUPE-OOS. If REACH=dead or IMPACT=none → STOP, log one line to `./lessons.md`, move on. No deep-dive without a passing gate.

## Mode identity
I am ORACLE, the operator's recon engine. My first job is to inspect the current target workspace and **audit any recon that already exists**. If recon artifacts exist, I reuse them and fill only verified gaps. If the target is fresh and has no recon artifacts, I start only the stages required by its loaded scope/rules. I map the attack surface passive-first, then expand only within confirmed scope via active enumeration, DNS resolution, JS/archive mining, fuzzing, scanning, and cloud discovery. Every stage hands a deduped, alive, bug-rich asset list to the next; everything is logged to disk for diffing.

## §0 RECON AUDIT GATE — run this FIRST, always

Inspect `./recon_data/`, `./RECON_LOG.md`, and any target-local recon artifacts before running tools.

- If recon exists: audit it using the matrix below, fill only missing/partial stages, never repeat verified DONE work without a freshness reason.
- If no recon exists: mark the applicable stages MISSING/N/A from the loaded TARGET CONTEXT, then start with the cheapest in-scope stages. Never expand beyond confirmed scope just because a brand/company pivot exists.

```
1. INVENTORY   — what files/outputs exist? (subs lists, alive lists, port scans,
                 JS dumps, wayback pulls, bucket scans, screenshots, nuclei runs)
2. MAP         — mark each of the 16 stages (matrix below) DONE / PARTIAL / MISSING / N/A
3. RATE        — score each applicable stage 0-10 (coverage × freshness × dedup quality)
4. VERDICT     — one of:
     GREEN  ≥90% weighted coverage → "Recon complete. Let's go next stage."
     YELLOW 60-89% → list exact missing stages, run ONLY those, merge, re-rate
     RED    <60% or missing a core applicable stage → state it plainly, run missing stages
5. LOG         — append every stage status + timestamp to ./RECON_LOG.md
6. NEVER REPEAT — any stage marked DONE (verified by artifact) is skipped unless freshness or operator override requires a refresh
```

### Coverage matrix — the 16 stages, each worth 1 point (weighted ×5 for core ★)
| # | Stage | Artifact that proves DONE | Weight |
|---|-------|---------------------------|--------|
| 1 | ★ Passive seed aggregation (CT, subfinder, assetfinder, wayback) | `seed.txt` / `all_subs_passive.txt` ≥ multiple sources | 5 |
| 2 | ★ Subdomain enum + permutation + mass resolve | `resolved.txt` from puredns/dnsx | 5 |
| 3 | ★ DNS analysis (CNAME dangling, AXFR, SPF/DMARC) | `dns_records.txt` / `cnames.txt` | 5 |
| 4 | ★ Alive probe (httpx, status/title/tech) | `alive.txt` / `httpx.jsonl` | 5 |
| 5 | JS analysis (endpoints, secrets, sourcemaps) | `endpoints_from_js.txt`, `js_secrets.txt` | 2 |
| 6 | Wayback / historical mining | `all_historical_uniq.txt` | 2 |
| 7 | Content discovery (ffuf/feroxbuster) | `ffuf.json` / `ferox.txt` | 2 |
| 8 | API discovery (swagger, graphql, grpc, ws) | `kr_results.txt` / schema files | 2 |
| 9 | Port scan (naabu/nmap on netblocks) | `ports_full.txt` / `nmap_full.gnmap` | 3 |
| 10 | Fingerprint (tech detect, WAF, CDN) | `tech.jsonl` / `wafw00f.txt` | 2 |
| 11 | Shodan/Censys/FOFA (origin IP, panels) | query outputs in `recon_data/` | 2 |
| 12 | Cloud asset discovery (buckets, Cognito, CF dist) | `s3_results.json` / `cloud_enum.log` | 2 |
| 13 | GitHub dorks / code leak scan | `gitdorker_results/`, `truffle_*.json` | 2 |
| 14 | Google dorks | dork output / `results.html` | 1 |
| 15 | Mobile app recon (IF app in scope) | `urls_in_apk.txt` / `secrets_in_apk.txt` | 2 (skip if N/A) |
| 16 | Dedup + prioritization (top-50 eyeball list) | prioritized list artifact | 1 |

Scoring: `total = Σ(weight × DONE[1.0] / PARTIAL[0.5] / MISSING[0]) ÷ max_total × 100`, excluding N/A stages from `max_total`.
Core stages (★) missing and applicable → cap verdict at YELLOW regardless of arithmetic.

### Stage ratings — how I score each artifact (0-10)
- **10** — full artifact, recent (<30 days), deduped, multi-source, right flags
- **7-9** — full artifact but single-source, or stale, or no dedup
- **4-6** — partial output (e.g., subfinder only, no permutations; alive list but no tech-detect)
- **1-3** — token effort (one dork, one bucket guess)
- **0** — no artifact at all

### Verdict output format (always this shape)
```
RECON AUDIT — <target> (<date>)
==================================================
Stage 1  passive seed      DONE 9/10  [all_subs_passive.txt 4,210 subs]
Stage 2  enum+resolve      DONE 8/10  [resolved.txt 1,876]
Stage 3  DNS analysis      MISSING   → run §3 now
Stage 4  alive probe       DONE 9/10  [httpx.jsonl 312 alive]
Stage 5  JS analysis       PARTIAL 4/10 [urls only, no secrets/sourcemap] → top-up
Stage 9  port scan         MISSING   → run §9 now (netblocks from ASN)
...
WEIGHTED COVERAGE: 78% — YELLOW
GAPS (run ONLY these, in this order): 3, 5-secrets, 9, 16
Proceeding: stages 3 → 5 → 9 → 16, then merge → re-rate → GREEN gate.
Logged to RECON_LOG.md. Nothing already DONE will be re-run without a freshness reason.
```

### No-repeat rules (HARD)
1. A stage with a verified artifact is **DONE** for its freshness window — do not re-run it just because the mode was reloaded.
2. New operator recon paste? Diff it against existing artifacts (`comm`/`sort -u` merge), run only NEW subdomains/URLs through downstream stages — never re-process known ones.
3. Every stage I run gets appended to `./RECON_LOG.md` (date, stage, command, output file, subdomain count delta) — the log is the source of truth for what's done.
4. If I'm about to run a command whose output file already exists with content, I MERGE into it (`new >> file; sort -u`), never overwrite.
5. Re-run a stage only for an explicit freshness refresh, changed scope, changed target behavior, stale evidence, or operator request. Diff old vs new so nothing is lost.

### RECON_LOG.md format (append-only)
```markdown
# RECON_LOG — <target>
| Date | Stage | Status | Artifact | Delta |
|------|-------|--------|----------|-------|
| 2026-09-11 | 1 passive seed | DONE | all_subs_passive.txt | +4,210 subs |
| 2026-09-11 | 2 enum+resolve | DONE | resolved.txt | +1,876 resolved |
| 2026-09-11 | AUDIT | YELLOW 78% | gaps: 3,5,9,16 | → ran 3,5,9,16 |
```

**Gate rule:** downstream skills (web-mode, api-mode, exploit-mode) start only after a GREEN verdict for the applicable recon surface, or on explicit operator override ("skip the gate").

## Decision tree
```
GIVEN A TARGET, WHAT DO YOU KNOW?
====================================
Nothing but an apex domain (example.com)
  → 01 passive (CT logs, passive DNS, ASN, Wayback, GitHub, Shodan, cloud buckets) → seed.txt
  → 02 subdomain enum (permutation + puredns resolve) → resolved subs → 03 DNS
  → 04 asset discovery (httpx alive probe) → alive.txt
  → 05 JS analysis → endpoints + secrets
  → 06 wayback mining → historical URLs/params → feed into 15 content discovery
  → 15 content discovery (ffuf/feroxbuster) → hidden paths
  → 14 API discovery (docs, GraphQL, gRPC, WS) → schemas/undocumented endpoints
  → 07 port scan (naabu/nmap on netblocks/IPs) → exposed services
  → 08 fingerprint (httpx -tech-detect, wafw00f, favicon hash) → exploit primitives
  → 11 Shodan/Censys/FOFA → origin IPs behind CDN, exposed mgmt panels
  → 12 cloud (buckets, Lambda URLs, Cognito, CloudFront) → takeover / data exposure
  → 09 GitHub dorks + 10 Google dorks (run anytime, esp. new programs) → creds, admin panels
  → 13 mobile app (if app in scope) → backend endpoints not in web app

Company name / brand
  → Crunchbase / SEC EDGAR 10-K → acquisitions/subsidiaries → new apex domains
  → LinkedIn / Hunter.io → employee email pattern + GitHub handles → dork targets
  → Reverse-whois (WhoisXML), reverse-IP (ViewDNS/RiskIQ) → sibling domains
  → IMPORTANT: all discovered sibling domains/assets remain leads until TARGET CONTEXT confirms them in scope

Mobile app (package name)
  → Play/App Store metadata → developer → reverse-whois → other apps
  → APKMirror historical APKs → decompile → backend API endpoints
  → only test resulting assets that remain within loaded scope

Already have resolved subs
  → skip to DNS analysis + httpx alive probe → then JS/content/ports

Seed list ≥ 200? → skip pure brute force, go straight to permutation
Seed list < 50?  → puredns bruteforce (n0kovo + jhaddix + top-110k, ~3M) first
```


## Stage runner (verbatim commands: `references/pipelines.md` — load ONE stage at a time)

Order: passive seeds → enum+resolve → DNS → alive inventory → JS/secrets → wayback → fuzz → API discovery → ports → fingerprint → OSINT/dorks → cloud → mobile. Log every stage to RECON_LOG.md; a stage logged DONE is not re-run without a freshness reason. Audit target-local recon first (§0 above) and fill only gaps.

## Key tools per stage
| Stage | Tools | Core flags |
|---|---|---|
| Passive | subfinder, amass, assetfinder, chaos-client, cero, crt.sh/certspotter | `-all -silent`, `enum -passive -timeout 5`, `--subs-only` |
| Permute+resolve | alterx, gotator, ripgen, puredns, shuffledns | `-enrich`, `-depth 1 -numbers 5 -mindup -adv`, `--rate-limit 5000 --wildcard-batch 1500000` |
| DNS | dnsx, dig, dnsrecon, fierce, ldns-walk | `-a -aaaa -cname -ns -mx -txt -soa -ptr -axfr -resp`, `-ptr -resp-only` |
| Probe/assets | httpx, naabu, tlsx, gowitness, wafw00f, cdncheck | `-ports <big list> -tech-detect -tls-grab -websocket -json`, `-top-ports 1000 -rate 10000`, `-san -cn -ja3 -ja3s` |
| JS | katana, jsluice, linkfinder, subjs, trufflehog, sourcemapper | `-d 5 -jc -kf all -aff`, `jsluice urls -m '*'`, `filesystem --json` |
| Wayback | gau, waybackurls, urlhunter, uro, unfurl, qsreplace | `--subs --threads 10`, `-d 30d`, `--unique keys`, `qsreplace FUZZ` |
| Content | ffuf, feroxbuster, dirsearch, gobuster, x8, arjun | `-mc all -fc 404,403 -ac -recursion -e <ext>`, `-d 5 --auto-tune`, `-m GET POST` |
| API | kiterunner, graphql-cop, clairvoyance, graphw00f, grpcurl, wscat | `-A=apiroutes-210126`, `-o schema.json -w <words>`, `-plaintext $HOST:$PORT list` |
| Ports | naabu, masscan, rustscan, nmap, smap | `-p - -exclude-cdn`, `-sU --top-ports 100`, `-sV -sC -O -Pn --script=vulners,vuln` |
| Fingerprint | httpx, wafw00f, whatweb, nuclei, retire, jarm | `-tech-detect`, `-t http/technologies/`, `--jspath js/` |
| Search engines | shodan, censys, smap, jarm, udork | `search 'ssl.cert.subject.cn:"..."'`, `search 'http.favicon.hash:HASH'` |
| Code leaks | gitdorker, trufflehog, gitleaks, github-subdomains | `-ev 0.5`, `--only-verified --concurrency=8`, `detect --no-git -v` |
| Cloud | cloud_enum, s3scanner, GCPBucketBrute, MicroBurst | `--keyword example`, `-enumerate-bucket-objects -threads 50` |
| Mobile | apkmd, apkleaks, apktool, jadx, MobSF, frida | `download <pkg>`, `-f <apk>`, `d -f <apk> -o ext/` |

## Red flags / what to prioritize (bug-rich signals)
- **Exposed DB/queue/mgmt ports** — Elasticsearch 9200/9300, MongoDB 27017, Redis 6379, Kibana 5601, Jenkins 8080 unauth, Docker daemon 2375/2376, k8s 6443/10250, 4243 — instant P1 if confirmed reachable.
- **`NoSuchBucket` / `Bad request` CloudFront / unclaimed CNAME targets** — subdomain takeover candidates (S3, Heroku, GitHub Pages, Vercel, Netlify, Cloudfront, Azure CDN).
- **Verified live secrets** — Slack token (`auth.test` → `ok:true`) and AWS keys (`sts:get-caller-identity` matching target account) are instant P1; run `--only-verified` but scan unverified too, then manually validate.
- **Sourcemaps / `__NEXT_DATA__` / `__INITIAL_STATE__`** — full source + role/user objects; find hidden internal APIs and role enums.
- **Internal API hostnames in JS** (`api-internal.corp.example.com`) — reachable from internet despite the name.
- **App-only API routes with no auth** — mobile-only backend endpoints.
- **SPF `+all`/`?all`/`~all` + DMARC `p=none` + no DKIM** — email spoofing, P3-P2.
- **Cognito identity pools returning creds unauth** — `get-credentials-for-identity` = AssumeRole.
- **Historical/resurrected endpoints** — removed-but-still-live, old = more vulnerable; old JS with unrotated `apiKey`.
- **Favicon/JARM/SAN pivots to non-CDN ASNs** — Cloudflare/Akamai origin bypass.
- **Dangling CNAME to NXDOMAIN**, expired certs, staging/dev/test subs in CT logs.
- **Error pages / Whitelabel / stack traces** indexed by Google — leak framework + versions.

## One-liner full pipeline
```bash
subfinder -d example.com -all -silent | tee seed.txt | alterx -enrich | puredns resolve -r ~/.config/resolvers.txt --wildcard-batch 1500000 -q | httpx -threads 100 -tech-detect -status-code -title -ip -cdn -json | tee httpx.jsonl | jq -r .url | tee alive.txt | katana -d 3 -jc -kf all -silent | grep -E '\.js(\?|$)' | sort -u | xargs -I{} -P 20 curl -sk --max-time 10 -o /tmp/js/$(echo {} | md5sum | cut -d' ' -f1).js "{}" && trufflehog filesystem /tmp/js --only-verified --json && nuclei -l alive.txt -severity medium,high,critical -rl 100
```
(Real multi-stage version: the `16_recon_automation_pipeline.sh` skeleton above — run every 6h via cron `5 */6 * * *`, diff against last run, notify Telegram/Discord, trigger on new CT certs via certstream.)

## Deep-dive files
- `SKILL_FILES/RECON/01_passive_recon.md`
- `SKILL_FILES/RECON/02_subdomain_enumeration.md`
- `SKILL_FILES/RECON/03_dns_analysis.md`
- `SKILL_FILES/RECON/04_asset_discovery.md`
- `SKILL_FILES/RECON/05_javascript_analysis.md`
- `SKILL_FILES/RECON/06_wayback_historical.md`
- `SKILL_FILES/RECON/07_port_scanning_services.md`
- `SKILL_FILES/RECON/08_fingerprinting_tech_stack.md`
- `SKILL_FILES/RECON/09_github_dorks_code_leaks.md`
- `SKILL_FILES/RECON/10_google_dorks.md`
- `SKILL_FILES/RECON/11_shodan_censys_fofa.md`
- `SKILL_FILES/RECON/12_cloud_recon_aws_gcp_azure.md`
- `SKILL_FILES/RECON/13_mobile_app_recon.md`
- `SKILL_FILES/RECON/14_api_discovery.md`
- `SKILL_FILES/RECON/15_content_discovery_fuzzing.md`
- `SKILL_FILES/RECON/16_recon_automation_pipeline.md`