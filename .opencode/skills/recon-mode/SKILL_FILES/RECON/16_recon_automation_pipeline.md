# Recon automation — stage contract

Automate the stage needed for the current question, not a universal enum-to-scanner sequence. Read the active scope, restrictions, and existing artifacts before planning a run. Scheduling or external notifications require the operator's request; a discovery event is not permission to scan a new asset.

## Run design

- Inputs: explicit approved assets, exclusions, current scope source/date, existing usable baseline.
- Limits: target-specific rates, request budget, concurrency, permitted techniques, and bounded retry policy.
- Run directory: a new directory inside TARGET_ROOT/recon_data; never a global hunting directory or sibling target.
- Stages: only applicable stages, each with declared input/output format and validation criteria.
- Results: success, partial, or failed with counts, errors, artifact paths, and provenance. Empty or truncated output cannot silently become a successful baseline.

Validate upstream output before downstream work. Keep raw observations and filtered in-scope candidates distinct. Check redirect destinations before following them. Preserve the last good baseline on partial failure; a missing item is not a removal until collection completeness is established.

For JavaScript/source-map collection, use `05_javascript_analysis.md` and the recon-mode `scripts/collect_assets.py` helper. Do not embed duplicate downloader implementations in pipelines.

## Delta and restart

Diff normalized comparable artifacts against the last successful compatible run, not the lexically last directory. First run has no previous baseline. Include content/schema changes on existing assets when relevant, not only new hostnames. Revalidate scope before a queued action executes. Serialize overlapping runs for the same target and resume only completed validated stages.

Scanner results are leads requiring semantic validation. Secret-verification calls are separate target actions; regex matches do not automatically authorize verification. Notifications, when requested, should report sanitized meaningful deltas and failures without raw credentials or customer data.

## Before unattended use

Exercise first-run, no-change, partial failure, invalid output, scope removal, duplicate event, and interrupted-run behavior using local fixtures. Confirm no failed run overwrites the good baseline and no event silently expands scope or request limits. Use automation-mode for implementation details.
