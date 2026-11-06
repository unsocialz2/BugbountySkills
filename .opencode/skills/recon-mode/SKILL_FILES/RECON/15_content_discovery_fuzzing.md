# Content discovery — retain observations, select relevant inputs

Use when first-party traffic, source or a concrete hypothesis justifies finding an unlinked path or parameter. Read target policy first. Do not use a giant mixed dictionary or automatic method sweep as a substitute for a feature model.

## Exact URL list

For a small approved URL list, use `scripts/probe_urls.py` as documented in `14_api_discovery.md`. It retains denial/not-found observations and distinguishes transport failure. For a wordlist job, use the bounded example below.

## Path-wordlist example

Use a small pre-approved path-only wordlist. Set BASE_URL to the scoped HTTP(S) base, APPROVED_PATHS to that list, RUN to a new target-local run directory, REQUESTS_PER_SECOND from program policy, and IDENTIFICATION_HEADER to a non-secret researcher identification header (or an ordinary User-Agent if none is required). Install/verify ffuf locally before running.

```bash
mkdir -- "${RUN:?}" || exit 1
sha256sum -- "${APPROVED_PATHS:?}" > "$RUN/input.sha256" || exit 1
if ffuf -u "${BASE_URL:?}/FUZZ" -w "$APPROVED_PATHS" \
  -mc all -rate "${REQUESTS_PER_SECOND:?}" -t 1 -timeout 10 -noninteractive \
  -H "${IDENTIFICATION_HEADER:?}" -of json -o "$RUN/results.json" \
  2> "$RUN/errors.txt"; then
  printf '%s\n' 'exit=0' > "$RUN/completion.txt"
else
  result_code=$?
  printf 'exit=%s\n' "$result_code" > "$RUN/completion.txt"
  exit "$result_code"
fi
```

The example assumes no inherited ffuf preset adds filters, proxying, recursion or calibration; review/isolate the effective tool configuration first. No blanket 403/404 filter or automatic calibration is enabled by this command. A generic error signature can be suppressed in a derived review view after comparing stable controls. Preserve the original results and completion/errors. Inspect request errors and input coverage even when the process exits zero. Do not overwrite an earlier run, automatically recurse, follow redirects, disable TLS verification, rotate egress, or increase concurrency in response to a challenge. Reassess the question and program limits.

A distinctive application 403 can be a route lead for an authorized comparison; it is not proof of bypass. An identical SPA shell on unknown paths is not proof every path exists. Compare body/type/headers and normal controls, not status or byte size alone; calibration based on one response can hide dynamic differences.

## Keep dictionaries separate by input purpose

| Purpose | Suitable input | Do not combine by default |
|---|---|---|
| Paths | observed route segments, relevant framework paths, small path-only lists | SQLi/XSS values, passwords, DNS names, parameter names |
| Parameter names | client/schema fields, a relevant name list | path lists or arbitrary payload values |
| Parameter values | type/context-specific values for one hypothesis | every payload class on every input |
| Hostnames | exact scoped host candidates and relevant DNS labels | content paths and credential lists |

If combining compatible lists, preserve source identities, normalize/deduplicate, review the result and its count before use. No universal one4all dictionary is prescribed.

## Methods, headers and representations

Recover a successful normal request first. Compare only plausible methods/headers/versions for the same action and permitted fixtures. Do not enumerate DELETE/PUT/CONNECT/etc. against an admin route as generic content discovery. A 200 on an error body is not privileged success.

Use the smallest valid semantic change. Switching JSON to form input may require changing both Content-Type and body encoding. To investigate an interaction, establish valid controls for the relevant combinations rather than insisting every experiment changes only one literal field. Hand evidence-backed parser or authorization questions to the owning API/web skill.

## Handoff

Record input snapshot, exact command/tool version when relevant, completion/errors, original output and a concise selected set of leads. Distinguish observed routes, ambiguous wildcard responses, blocked application paths and untested actions. Raw discovery counts are not vulnerability counts.
