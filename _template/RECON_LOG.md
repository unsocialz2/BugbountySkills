# RECON_LOG — <target> (append-only run ledger)

Add rows for executed stages, not a mandatory full pipeline. Preserve the last good baseline on failed/partial refreshes. A new run must not overwrite the identity of an earlier run.

| Run ID / UTC time | Stage / scope version | Input artifact / count | Output artifact / count | Snapshot hash or immutable path | Completion / errors evidence | Status | Delta / decision |
|-------------------|-----------------------|------------------------|-------------------------|----------------------------------|------------------------------|--------|------------------|

Status: `DONE`, `PARTIAL`, `FAILED`, `UNVERIFIED`, `MISSING`, `N/A`. A refresh is a new run with one of these outcomes, not proof of completeness by itself.

Before DONE, validate format, representative content, counts, input coverage, and tool completion/errors. A zero-length results file with no completion record is UNVERIFIED, not “zero findings.” Record tool/version and the exact input/template selection in the run evidence when needed to reproduce the result. Keep secrets out of recorded command arguments.

Counts describe the named snapshot. When an artifact changes, append a new run and update STATE's current run pointer; do not silently reuse old counts. Distinguish collection completeness from downstream testing coverage. A scanner's no-hit result does not establish absence of a vulnerability class.
