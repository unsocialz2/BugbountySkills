# API discovery — recover valid feature requests

Start with the normal client, first-party schemas, source call sites and saved traffic. Record exact host/path/method, required identity/header/body, version, resource provenance, and owning feature. Discovering a route is different from successfully exercising it or proving a boundary failure.

## Bounded documentation checks

Create a target-local list of exact schema/documentation URLs justified by the app or a small relevant shortlist. Confirm each URL against scope/exclusions and program request limits. Do not combine every version, host, admin method, and schema path into an automatic scan.

From TARGET_ROOT, collect GET observations with the recon-mode helper:

```bash
# RECON_SKILL is the absolute recon-mode skill directory.
# REQUEST_INTERVAL is program-compatible spacing in seconds.
python3 "${RECON_SKILL:?}/scripts/probe_urls.py" \
  --scope-policy scope-policy.json \
  --urls recon_data/schema_urls_in_scope.txt \
  --output recon_data/schema-run-001 \
  --interval "${REQUEST_INTERVAL:?}"
```

The output directory must be new. Optional `--headers-file` points to a local JSON object of required non-credential program identification headers. Values are not printed or stored in run metadata; use browser/proxy capture for authenticated requests. URLs and bodies may contain sensitive values: retain only what the program permits and redact before sharing.

The helper verifies TLS, does not follow redirects, limits response bytes, preserves 2xx/3xx/4xx/5xx observations and content hashes, and distinguishes transport/storage errors. `run.json` starts incomplete and records final counts and a manifest hash; `responses.jsonl` links each saved body with status/type/encoding/truncation. A complete run means URL processing completed, not that a schema is valid, scope is complete, or the application is secure. Truncated/encoded bodies require appropriate review; SPA HTML at a .json URL is not an OpenAPI document. This format is not the JS collector format and is not an input to verify_asset_run.py.

For path-wordlist discovery rather than a fixed URL list, use the maintained example in `15_content_discovery_fuzzing.md`. A fuzzing job needs explicit input and substitution; do not invoke ffuf repeatedly on fixed URLs while overwriting one output file.

## Protocol-specific continuation

- **REST/OpenAPI:** parse documents only after checking format. Recover a valid allowed request and its resource/role relationship; stale docs are leads.
- **GraphQL:** use an observed endpoint and a bounded legitimate query first. Introspection is discovery, not a finding by itself. If disabled, decide whether permitted schema recovery would answer the current feature question before brute-force tooling. Metadata lists do not establish operation execution.
- **gRPC:** reflection/proto definitions may reveal methods. Use TLS and authenticated metadata appropriate to the observed service; plaintext is not a generic default.
- **WebSocket:** recover the actual handshake, origin/auth model and message shape from a normal flow. A successful upgrade does not establish authorization for messages or rooms.
- **Versions/methods:** inspect aliases supported by client/schema/routing evidence. Preserve semantic results, not just status differences. Do not invoke destructive methods as generic discovery.

Do not auto-fetch arbitrary server URLs referenced by schemas; those are untrusted leads requiring scope review. Hand valid request shapes and concrete boundary questions to api-mode/web-mode. Keep unknown methods, unavailable identity, blocked edges and invalid controls visible instead of declaring no API or no vulnerability.

The CLI now requires `--scope-policy`. Build it from the designated program policy
using `references/scope-policy.md` in recon-mode; copy the example schema, not its
example.invalid authorization. The CLI validates the complete input list and
rate/byte/count budget before network access. It does not follow redirects.
