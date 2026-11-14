# SSR, RSC and Server Functions — inspect server authority behind frontend features

## Boundary and discovery

Use for React/Next.js-style server-rendered pages, streamed component data, server-invoked functions, route handlers and framework caches.
Do not equate a framework fingerprint or action identifier with a vulnerability.
Server Functions execute on the server; UI visibility is not the authorization boundary for the callable operation.
React terminology distinguishes Server Functions generally from Server Actions used as actions; match the framework/version actually deployed.
RSC serialization is not ordinary page HTML and is not automatically safe merely because a property is not displayed.

Map one real feature:

1. browser navigation or interaction;
2. page HTML, component/data request and action request as actually captured;
3. server authorization/data-access layer;
4. object/tenant selection and server-owned fields;
5. serialization to client, redirects and error payloads;
6. request memoization, framework data cache and external CDN separately.

Record build/runtime evidence, router mode and hosting/cache configuration when observable.
An advisory version range is a lead; establish its preconditions and natural running path before claiming applicability.
Do not infer App Router behavior from a Pages Router case study or vice versa.

## Normal controls

Use two controlled actors/tenants with visible synthetic differences such as `AUDIT_A_PRIVATE` and `AUDIT_B_PRIVATE`.
Capture successful normal navigation and one harmless action on an owned object.
Save the full observed wire shape, including action transport fields and content type.
Replay an unchanged request under its rightful actor before modifying it.
Preserve a separate unprivileged/unauthenticated control; an arbitrary guessed action id cannot establish a protected function.

## Payloads: modify captured requests, not framework internals blindly

These are semantic substitutions inside a valid existing request, not universal standalone HTTP payloads.
Do not invent undocumented action encodings or copy a historical CVE request into every Next.js host.

| Boundary | Minimal challenge | Control | Decisive observation |
|---|---|---|---|
| Action authenticates independently of page | Replay a captured harmless owned action without its session | Same request under rightful actor | Protected mutation occurs without intended auth, not just a successful transport status. |
| Action enforces object/tenant policy | Replace one known owned object id with B's synthetic object id | A→A and B→B normal action/readback | A changes/reads B's protected state; hidden UI or opaque ids are not enforcement. |
| Client-bound values remain untrusted | Change one observed client argument or bound identifier in valid serialized input | Original argument and an invalid/nonexistent object | Server derives authority instead of trusting a client hint; preserve serializer validity. |
| Serialization exposes excess data | Place a unique synthetic private field in own account, inspect raw HTML/RSC/JSON using A then B | Public field and rightful private read | Unauthorized bytes reach another actor's response; absence from rendered UI is irrelevant. |
| Cache key includes user/tenant identity | Alternate A/B normal requests on an authorized isolated test resource | Fresh/uncached or distinct-key controls | B receives A's private marker through the actual shared cache, not a stale A session. |
| HTML/data representations collide | Compare only representations observed in normal client traffic | Clean requests using each normal representation | Wrong content/identity crosses representation or cache boundary; response header changes alone are leads. |
| Role changes revoke action authority | Capture an action, remove A's controlled role through normal admin flow, replay it | Before/after independent membership view | Server relies on stale role/state beyond intended policy. |
| Error/stream path leaks state | Trigger a harmless validation error on an owned object | Successful owned input and nonexistent object | Raw stream/error contains a synthetic protected value or completed unauthorized effect. |

## Action lifecycle and CSRF

Authentication and authorization must apply to the operation itself; a page redirect alone does not protect an action.
Opaque action identifiers are routing references, not a substitute for checking the actor's resource authority.
Captured actions may be build-bound or expire; an invalid reference is not an authorization denial.
Framework origin/host checks and POST-only mechanisms can affect cross-site delivery, but do not replace object authorization.
For CSRF, prove real browser credentials, request shape and actual state change with `csrf_all_types.md`.
Do not disable the framework's origin checks or encryption in a local mock and call it a target exploit.
A closure/bound value may be serialized/encrypted by the framework; record what is actually client-controlled.

## Cache and serialization subtleties

Request-local memoization and a cache shared across requests have different threat models.
A server-only data-access layer should return minimal DTOs; inspect actual serialized fields rather than function names alone.
A value intentionally exposed through a public component remains public even if it originated in a database.
Different header/status/content-type alone does not prove poisoning or private data leakage.
Use a unique owned test path/key for cache investigation; do not poison a public shared route to obtain broad impact.
A historical framework header accepted by the app may be inert or already fixed.
Keep framework-internal cache, CDN, browser cache and client router cache evidence separate.
If isolation cannot be established safely, retain source/config evidence and the unresolved test boundary.

## Known-vulnerability and patch-gap reasoning

Collect the exact advisory, affected code/config and fixed behavior from the framework owner when pursuing a specific CVE.
Test a benign discriminator of the vulnerable behavior rather than destructive impact payloads.
Version banners, asset hashes, dependency lockfiles and server behavior can disagree; preserve that uncertainty.
Reproduce privately in a matching local fixture if production testing would touch shared cache or execution surfaces.
A local reproduction establishes the code issue, while natural external reach and deployment applicability remain separate.
Do not reuse a published exploit as proof that this target has not patched or mitigated the path.

## Evidence and falsification

Save actor/tenant controls, captured normal action, exact altered serialized request and independent state/readback.
Record router/runtime/build, representation, cache layer and victim/reader state as observed or unknown.
Reject response echo, stale personal session, client-only state, wrong action id and intentionally public DTOs as false-positive explanations.
An exception after an unauthorized write/read can still be evidence; inspect effects before dismissing the response.
No score or universal framework-compromise claim follows from a class label.

Close only the tested action/data path/build/state when the corresponding normal control demonstrates enforcement.
Mark stale action references, unobservable workers and unknown cache isolation inconclusive.
Reopen for another deployed action, role/lifecycle transition, representation or cache boundary discovered in real traffic.

## References and freshness

Reviewed 2026-11-13. Framework behavior changes across versions; source links are not proof a target is affected.

- [Next.js data security](https://nextjs.org/docs/app/guides/data-security) — action-local authorization, data-access layers and safe client DTOs.
- [React Server Functions](https://react.dev/reference/rsc/server-functions) — invocation model, terminology and framework implementation/version boundaries.
- [PortSwigger research selection](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) — framework internal-cache attack research as a distinct direction.
- [Original Next.js cache-chain research](https://zhero-web-sec.github.io/research-and-things/nextjs-cache-and-chains-the-stale-elixir) — conditional historical cache mechanisms; not a universal payload for current deployments.
