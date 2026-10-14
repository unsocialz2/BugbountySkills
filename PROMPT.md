# Copy-paste prompt for every new target (run inside ~/bugbounty/<target>/)

## Setup (terminal, once per target)

```bash
cp -r ~/bugbounty/_template ~/bugbounty/<name>
cd ~/bugbounty/<name>
# edit scope.txt with +in-scope / -out-of-scope from program policy
opencode
```

## Master prompt (paste into opencode, fill the 5 fields)

```
ORACLE — new target init. Scope in ./scope.txt is authoritative, do not go outside it.

TARGET: [example.com]
PROGRAM: [HackerOne VDP/private — link policy]
AUTH STATE: [unauth / user role=user]
TECH STACK: [unknown — fingerprint first / Cloudflare → Laravel + MySQL]
GOAL: [recon → alive → top-50 eyeball → hunt + chain]

1. Read ./scope.txt + ./STATE.md, update STATE to match above.
2. RECON MODE plan only: passive-first commands writing to ./recon_data/, free-tier tools first (subfinder/httpx/nuclei/katana/dnsx/naabu).
3. Stop before active scan and list what you will run for my approval.
```

## Follow-ups (same session, same folder)

```
RECON MODE — run passive for TARGET above, save to ./recon_data/
WEB MODE — TARGET + [stack from httpx -tech-detect], prioritize auth → IDOR → logic → SSRF/SQLi → XSS, chain to ATO
API MODE — [api host], BOLA/BFLA first, build auth matrix unauth/user/admin
PAYLOAD [class] [context] — e.g. PAYLOAD XSS attribute-double-quoted Cloudflare
EXPLOIT MODE — [finding + endpoint], minimal PoC + chain + bypass variants
SCR MODE — [language], audit this paste/diff, file:line + source-to-sink
REPORT MODE — [vuln + endpoint + impact], H1/Bugcrowd/Intigriti format + CVSS vector
STATE — echo current, RESET — clear on target switch
```

Rules enforced by AGENTS.md: per-target STATE isolation, scope.txt authoritative,
no CPE/pool ranges, Kali + Burp Pro + VPS assumed.
