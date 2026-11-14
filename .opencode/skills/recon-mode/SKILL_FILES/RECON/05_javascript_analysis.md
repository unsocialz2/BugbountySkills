# JavaScript analysis — preserve artifacts and follow product flows

Collect scripts from the relevant successful browser flow, including lazy-loaded chunks and service workers when they participate in the feature. Archives and unauthenticated crawlers may miss current authenticated routes. Record URL, source page/flow, auth context, collection time, and content hash. Filter exact URLs through current scope/exclusions before fetching.

## Reliable collection

Use the bundled `scripts/collect_assets.py` relative to the recon-mode skill folder. From TARGET_ROOT, pass a pre-approved URL file and a NEW run directory:

```bash
# Set RECON_SKILL to this skill's absolute directory and REQUEST_INTERVAL
# to the target-policy-compatible spacing in seconds before executing.
python3 "${RECON_SKILL:?}/scripts/collect_assets.py" \
  --scope-policy scope-policy.json \
  --urls recon_data/js_urls_in_scope.txt \
  --output recon_data/js-run-001 --kind javascript \
  --interval "${REQUEST_INTERVAL:?}"
```

The helper uses distinct URL-derived filenames, verifies TLS, declines redirects, caps response size, records provenance/hashes, and returns failure if any URL fails. It never replaces an existing run. It does not implement program scope parsing: the supplied exact URL list must already be approved. Review redirect destinations separately before a new request. Do not reuse the old xargs command-substitution download pattern: it computes one filename before xargs iterates.

Manifest URLs may contain sensitive query values. Keep raw artifacts local with restricted access and redact before sharing. Authenticated collection is better captured through the existing browser/proxy session; do not add secrets to command-line arguments. Failed/expired-session responses are coverage gaps. JavaScript filtering rejects common HTML/error pages but is not a JavaScript parser; inspect representative content and compare downloaded scripts to the expected flow.

## Completion and offline verification

The collector creates `run.json` with the deduplicated input digest, requested/saved/failed counts, timing, limits, and manifest digest. It starts as `running`; only the terminal update marks completion. An interruption leaves an incomplete run instead of silently implying success. An exhausted run with errors is `partial` or `failed`, even though processing finished.

Before selecting a baseline or handing off saved artifacts, verify the run locally:

```bash
python3 "${RECON_SKILL:?}/scripts/verify_asset_run.py" recon_data/js-run-001
```

The verifier performs no network requests or writes. It checks completion, counts, input/manifest digests, distinct records, expected artifact paths, file sizes and hashes; it rejects symlink artifacts. Exit 0 means a complete, internally consistent run; nonzero means partial, failed, missing, or inconsistent evidence. A complete run still needs scope/feature coverage and representative content review. Hashes detect drift relative to this snapshot; they do not authenticate the collector or prove a vulnerability. Older runs lacking `run.json` remain unverified, not automatically invalid or subject to a full re-fetch. Keep usable partial artifacts and repair only the gap justified by the current question. This verifier applies to this collector format, not arbitrary scanner output.

## Program identification headers

When program rules require identification headers, supply `--headers-file` pointing to a local JSON object, for example `{"X-HackerOne-Handle":"your-handle"}`. Check the actual header requirement before collection; the helper does not infer it from rules.txt. Values are sent to every approved URL in that invocation but are omitted from run metadata and normal error output. Use separate runs when different origins require different identification. Do not supply secrets; Cookie/Authorization and transport-control headers are rejected. Use the existing browser/proxy workflow for authenticated collection. TLS verification and redirect refusal remain enabled.

## Analysis

Select the saved JS files from the manifest, keeping the working directory stable. Search for the feature's routes, request builders, role checks, object relationships, state transitions, and error handling. Follow call sites and data flow rather than reporting strings or sink names alone. Use installed tool help to verify optional extractor flags.

Endpoint extraction should retain methods, required headers, request shape, version, and owning feature where available. Establish a successful legitimate request before security mutations. An apparent secret must be classified by intended exposure and permissions; a publishable client key is not automatically a credential finding. Any live credential verification requires a scoped, bounded target-specific decision.

## Source maps

Resolve an observed sourceMappingURL against the script URL. Inline data maps can be decoded offline. Explicit .map guesses are hypotheses and must be filtered through scope like other URLs. Do not append `.map` after a query string or treat any nonempty response as success.

Use the same collector with `--kind sourcemap`, an approved map URL list, and another new output directory. It checks JSON/version/basic map structure; indexed maps with inline submaps are supported, externally referenced sections are left for separate review. It does not prove mappings are semantically valid. Inspect sources/content and use an appropriate local parser before relying on extracted code. Do not automatically fetch sourceRoot/sources URLs.

## Handoff

Record requested/saved/failed counts, relevant feature coverage, and evidence paths. A missing authenticated chunk or failed fetch means PARTIAL, not DONE. Hand off concrete request shapes to web/API testing and reachable source-to-sink candidates to source review. Exposure of a bundle or source map alone does not prove a vulnerability.

The CLI now requires `--scope-policy`. Build it from the designated program policy
using `references/scope-policy.md` in recon-mode; copy the example schema, not its
example.invalid authorization. The CLI validates the complete input list and
rate/byte/count budget before network access. It does not follow redirects.
