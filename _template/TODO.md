# TODO — <program>

- [ ] Confirm written policy + rate limits / no-DoS / data-access rules
- [ ] Provide own recon results → ORACLE runs §0 AUDIT (rate, fill gaps, never repeat)
- [ ] Gate: GREEN verdict in RECON_LOG.md before hunting
- [ ] DNS analysis (dangling CNAME → takeover check)
- [ ] JS + Wayback mining → endpoints + params
- [ ] Content discovery (ffuf/feroxbuster) on top alive
- [ ] API discovery (swagger/openapi/graphql/grpc/WS)
- [ ] Port scan (naabu on netblocks/IPs only if in scope)
- [ ] Fingerprint (httpx -tech-detect, wafw00f) → pick primitives
- [ ] Eyeball top-50 alive, pick highest-value endpoint
- [ ] Hunt per WEB/API/MOBILE skill → falsification pass (web-mode §4) before reporting
- [ ] Report per REPORT MODE template

New target: `cp -r ~/bugbounty/_template ~/bugbounty/<new-name>`
