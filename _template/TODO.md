# TODO — <target>

- [ ] Read `rules.txt` and scope source(s); extract active restrictions/limits.
- [ ] Inspect existing `STATE.md`, `RECON_LOG.md`, findings, and `recon_data/` before new work.
- [ ] Audit applicable recon stages; mark DONE / PARTIAL / MISSING / N/A.
- [ ] Choose the highest-signal missing step instead of blindly running the full pipeline.
- [ ] Establish a normal successful product flow and required account/tenant access.
- [ ] Prioritize reachable, business-relevant boundaries from evidence; retain competing hypotheses.
- [ ] Record meaningful experiments and gaps in HYPOTHESES.md / COVERAGE.md when useful.
- [ ] For each candidate: viability gate -> minimal proof -> falsification -> demonstrated impact.
- [ ] Use `exploit-mode` only after a concrete primitive exists and a compact PoC/chain is useful.
- [ ] Use `reporting-mode` for final severity/CVSS and platform-ready writeup.
- [ ] Update concise state and lessons before ending the session.

Optional starter copy:

```bash
mkdir -p targets/<new-name>
cp -r _template/. targets/<new-name>/
# replace scope/rules with the real program data, then:
cd targets/<new-name>
opencode
```
