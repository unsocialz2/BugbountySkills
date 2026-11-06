# ffuf automation — preserve the discovery contract

The maintained path-discovery example is `../../../recon-mode/SKILL_FILES/RECON/15_content_discovery_fuzzing.md` relative to this file's directory. Use it when building a wrapper instead of keeping another default recipe here.

A wrapper must inherit the current target's exact scope, identification header, input list, policy rate and new target-local output directory. Keep raw responses/results and completion/errors distinguishable. Do not silently discard 403/404, enable auto-calibration/recursion, overwrite old results, or substitute mixed payload/password/DNS lists for a path list.

For a fixed approved URL set, use recon-mode's `scripts/probe_urls.py` via the API-discovery stage. Parameter, method, host and header experiments require their own valid controls and a concrete hypothesis; they are not an automatic follow-on to every path run. Confirm installed ffuf options before generating wrappers.
