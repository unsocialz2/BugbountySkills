# STATE — <target> (per-target, concise)

```text
TARGET:
SCOPE SOURCE:   # scope.txt / scope.csv / program export
RULES SOURCE:   # rules.txt + policy source/date if known
AUTH STATE:
TECH STACK:
HYPOTHESES:    # active question + link to HYPOTHESES.md when useful
TEST COVERAGE: # exact tested boundaries + test IDs/evidence; include material gaps
UNVERIFIED:    # historical claims missing reviewable evidence
BLOCKERS:      # exact missing access/tooling and next independent work
RECON COVERAGE: # current run IDs/snapshots and counts, not a full-pipeline score
INTERESTING SURFACES:
  -
FINDINGS:
  -
LESSONS:
  -
NEXT:
  -
```

Before handoff, check each material claim against its cited evidence, supersede resolved blockers, and preserve unresolved scope/coverage limits. No class-wide “no IDOR/XSS” conclusions from narrow negative tests. Any proposed prerequisite must name the hypothesis and experiment it unlocks.

Keep this as a current decision snapshot, not a transcript. Detailed evidence belongs in
`findings.md`, `RECON_LOG.md`, and `recon_data/`.

`STATE` summarizes it. `RESET` clears transient/current target state only; it must not delete
scope/rules or historical evidence unless explicitly requested.
