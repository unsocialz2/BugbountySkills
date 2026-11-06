# Feature discovery and useful experiments

Use when selecting a target/feature, when recon keeps expanding without a candidate, when basic authorization holds, or when a lab PoC seems stronger than the real attacker path. Keep records in the active target. This is decision support, not a fixed phase sequence or a demand for a report.

## Start where a meaningful experiment is possible

Choose a feature you can actually exercise under the program's scope and access rules. Record briefly in the active hypothesis:

- legitimate actor and required researcher identity/role; access available, repairable or unavailable;
- one normal successful flow and a controlled resource with observable content/state;
- security invariant and the fact that should authorize the operation;
- attacker capability required, and what unauthorized advantage would be distinguishable;
- cheapest permitted experiment plus strongest benign alternative.

Anonymous features can be productive: public input processing may have a meaningful server/browser boundary. Do not demand two accounts or a paid plan for every bug class. For cross-account ownership, use genuinely distinct identities/resources; two sessions of one identity do not create that boundary. For role escalation, two owners/admins do not model a low-privilege attacker. Required researcher aliases and test-tenant rules must be satisfied before account-based work; do not substitute a disposable address silently.

Use the app normally first when available. Recover route, method, headers, body, and resource IDs from its traffic or precise source/schema. A singular/plural guess, unsupported GET, empty cart/order list or failed normal write is not a valid feature control. Missing prerequisites should produce a specific repair question, not a payload batch.

Once an access prerequisite repeatedly blocks the chosen feature, decide between a permissible one-time operator assist, a different reachable feature, and another target. Do not automatically enumerate hundreds more unrelated hosts or keep changing egress. Scope and anti-abuse restrictions still govern any next action. Respect an operator's explicit recon-only/unauthenticated-only task and report its discovery limits rather than silently expanding authority.

## Go deeper after baseline controls hold

A successful direct object denial is a useful result. For the same observed feature, ask where authority is represented or consumed differently: a share capability versus object ACL, queued export versus current membership, nested parent versus child, cached result versus authoritative state, update versus approval, account link versus revocation. Choose only a transition/representation the architecture actually exposes and state what result would contradict the invariant.

Retain the whole feature's flow across web, API, mobile and worker references; routing is a way to retrieve help, not a reason to stop tracing the boundary. If the normal operation depends on an attested client, permitted app-driven testing can still exercise semantics; inability to call it from a custom script is a tooling limitation, not proof that all feature testing is blocked.

For each experiment preserve the normal control, minimal challenge, and semantic observation/readback. Empty error bodies or HTTP success alone do not resolve it. For stateful work use researcher-owned fixtures and program-approved test mechanisms. A real purchase, external notification, policy/application, or other material production effect needs the relevant authorization; do not treat every harmless permitted fixture change as automatically prohibited, or infer authorization from owning an account alone.

Progress means a new normal flow recovered, a control repaired, a boundary distinguished, an actual primitive established, or a lead falsified. Host/payload/reviewer/draft counts are not substitutes. Use the operator's budget; otherwise pivot when the next experiment stops adding information rather than inventing elapsed time or enforcing a fixed quota.

## Test the observation before polishing the report

For apparent secrets, metadata or code exposure, identify the issuer, capability and intended audience. Compare exact non-sensitive context with first-party public/demo documentation where available; a role-gated link can lead to an intentionally public resource. Public placement alone does not make a real secret safe. Distinguish a client identifier/publishable key, a sample, a stale value, a current confidential credential, and an unknown value. If replay is prohibited, preserve the disclosure evidence and apply the program's specific reporting policy without claiming verified credential validity or access.

A public source map is a discovery aid: trace an actionable route, field or data flow. A version banner, matching static asset hash, field name, endpoint flag, root inside a sandbox, or expired token does not demonstrate the running vulnerable path or a crossed isolation boundary. Known-vulnerability research needs the relevant code/configuration/preconditions, not just a matching product label. Historical disclosure patterns inspire a test; they do not establish current provider claimability or authorization to claim a resource.

## Lab changes and attacker reachability

Classify each setup change in the experiment record:

- **observation-only:** tracing a function, recording traffic, viewing owned state;
- **behavior-changing:** forcing a feature flag, bypassing a guard, changing allowlists/configuration, replacing a component, accepting a dummy credential, or invoking an internal function directly;
- **normal configuration:** a setting a legitimate tenant administrator can select, with the resulting trust boundary and required privilege stated.

Instrumentation may reveal a useful lead. Show separately whether the unmodified supported client/server can reach that path from the claimed external entry, lifecycle and attacker privilege. A forced flag or browser shim cannot establish natural rollout; a direct adb/component/internal call does not by itself prove browser-link delivery. Dummy-token persistence and a login-failed dialog do not prove account replacement or data reaching an attacker. Record what the harness adds and a remaining discriminator, rather than discarding the lead or calling it end-to-end confirmed.

Do not grant the attacker the privilege the proposed exploit is meant to gain. An admin configuring their own tenant insecurely and an unprivileged actor crossing an enforced tenant boundary are different questions. Conversely, a documented supported configuration can expose a genuine provider boundary; investigate the actual intended authority rather than rejecting every configuration-related finding.

For browser findings, distinguish origin, schemeful site, registrable domain/public-suffix boundary, cookie partition and configured trusted origins. Test the required attacker-hosting model using browser-observed controls/partition keys and an authoritative current suffix source when relevant. Do not extrapolate a localhost port test to shared hosting suffixes or arbitrary cross-site attackers.

## Keep outcomes honest and actionable

Maintain independent outcome fields when useful:

- technical: lead / reproduced behavior / demonstrated boundary failure, with exact evidence limits;
- eligibility: supported by policy / excluded / unresolved, with policy source;
- submission: not submitted / submitted / accepted / duplicate / rejected / unknown, with platform evidence or operator attribution.

Do not count a duplicate as a technical false positive or count an unsubmitted draft as acceptance. A low-impact exposure and an unauthorized capability are distinct outcomes. An older review may be superseded by new evidence; compare provenance and preconditions instead of automatically preferring whichever verdict is more confident.

Before costly impact expansion, inspect the available program exclusions, local prior reports and public fix/root-cause information. Unknown private backlog stays unknown. After a duplicate, preserve the useful primitive and stop repeating its root cause; a different endpoint, payload or larger hypothetical score does not establish novelty. Choose new work based on a distinct unresolved boundary and feasible access, without manufacturing a variant or submitting automatically.
