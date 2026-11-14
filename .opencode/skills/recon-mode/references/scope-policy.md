# Explicit policy for bundled URL collectors

The scope checker interprets an operator/program-approved policy; it cannot infer
legal scope, ownership, a subdomain's tenant, permission for a technique, or the
meaning of a platform CSV. Read the designated rules and exclusions first.

## Policy format

Copy `_template/SCOPE_POLICY.json` from repository root into the active target as
`scope-policy.json`, replace its example domain and provenance, and encode the
actual restrictions. A policy grants only the listed schemes/ports/methods.
Defaults inside a rule are HTTPS, port 443 and GET. Use exact hosts; `*.example.com`
matches subdomains only, never its apex. IPs must be canonical literal addresses.

`path` matches exactly after conservative normalization, preserving a literal trailing slash (`/api/item` differs from `/api/item/`). `path_prefix` matches the
named segment and descendants: `/api` includes `/api` and `/api/items`, not `/apix`.
An omitted path means host-wide. Deny rules win over allow rules. Set deny methods
and schemes/ports to cover every relevant excluded action; a deny rule has the
same HTTPS/443/GET defaults as an allow rule. Do not assume one GET exclusion
implicitly denies POST to a separate tool.

URL userinfo, fragments, backslashes, malformed encodings and controls are refused.
Decoded path separators/dot segments are conservatively folded for exclusions.
Where a relevant allow/deny is path-restricted, ambiguous encodings, dot segments,
matrix parameters and repeated slashes are refused rather than guessing which
component's parser wins. Host-wide path-fuzzing may require a different purpose-
built tool and explicit reasoning when the collector's conservative policy rejects
it. Do not loosen exclusions to force a test through.

## Offline check and actual collection

```bash
python3 "${RECON_SKILL:?}/scripts/scope_policy.py" \
  --policy scope-policy.json --urls recon_data/js_urls_in_scope.txt \
  --interval "${REQUEST_INTERVAL:?}" --max-bytes 1000000
```

This command makes no requests. Both `collect_assets.py` and `probe_urls.py` require
`--scope-policy scope-policy.json` and rerun scope/budget checks on the complete
input list before network access or output creation. They record policy digest,
refuse over-budget counts/bytes and intervals faster than policy, and never follow
redirects. Start another run only within the program's overall rate/request budget;
per-run counters cannot enforce a global lifetime quota.

## Enforcement limits

This gates the two bundled collector CLIs. It does not intercept curl, Burp,
browsers, nuclei, sibling scripts, DNS rebinding or source-selected callback URLs.
The library functions retain an explicit pre-approved-input interface for isolated
tests/integrators; pass `policy=ScopePolicy(...)` to enforce it there. A null digest
and `preapproved-library-input` mode are not proof of policy enforcement.

No automatic redirect policy is implied: a Location is an observation, not
permission to fetch it. Revalidate a new destination independently and never
forward credentials merely because the first URL was approved. API specs/source
maps and target pages cannot authorize their own external server references.

Collector custom headers are for program identification, not route/method control.
Common method-override, original/rewrite URL and forwarding headers are rejected
along with credentials and transport headers. Specialized parser/header testing
belongs to an explicitly scoped purpose-built experiment, not this GET collector.

Method rules describe the wire HTTP method, not an inference that the business
operation is read-only. Query-driven actions and application-specific routing
semantics still require policy review and a normal workflow control.
