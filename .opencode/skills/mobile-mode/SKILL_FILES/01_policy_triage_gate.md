# Mobile policy triage — explicit conditions

Read the current target scope and mobile exclusions before target actions or lab setup. This reference determines which questions and proofs are eligible; it does not predict payout, require a purchase, or create permission for additional actions.

## Scope and eligibility decisions

| Condition supported by program policy | Decision |
|---|---|
| App is explicitly listed, or a clearly applicable broader asset rule includes it | Record package/bundle/build and scope basis; apply the actual exclusions. |
| App scope is absent or ambiguous | Resolve scope before active testing; do not infer inclusion from branding. |
| Policy excludes findings that require an attacker to root/jailbreak the victim device | Do not claim a rooted-only attacker path as eligible. Observation-only instrumentation used during research is a separate question; apply any explicit research-method restrictions too. |
| Policy excludes attacker physical/ADB access | Findings requiring that attacker access are excluded. A lab adb command may help trace an entry point, but does not prove remote browser/app delivery. |
| Policy explicitly excludes WebView exploitation | Apply that exclusion to its stated boundary. If it does not exclude WebViews, do not manufacture an exclusion. |
| Policy excludes missing pinning, root detection, or obfuscation as standalone findings | Do not report those properties alone. This does not automatically exclude a distinct reachable app/backend vulnerability. |
| Policy requires a stock-device reproduction | Prove the claimed attacker path on that supported configuration, or retain a lead with the exact missing proof. Lab observations remain useful but must be labelled. |
| Policy accepts qualified hypotheses or credential disclosure without replay | Follow that reporting path with explicit uncertainty; do not invent impact or perform prohibited validation. |

The absence of an exclusion is not proof of acceptance. Record the relevant policy wording and source/date rather than reusing a payout table or another program's assumptions.

## Discovery method versus attacker prerequisite

Distinguish:

- observation-only hooks, traffic capture, and owned-state inspection;
- changes to flags, guards, routing, allowlists, browser providers, or authentication;
- the capabilities a real attacker needs on a naturally reachable supported build.

Frida/root use during research does not by itself prove either eligibility or ineligibility. A finding that only works because the hook bypassed the target control needs that limitation stated. A dummy token written after forcing a feature flag is not a successful real login. Prove external entry, lifecycle, and semantic outcome separately; see `../../core-identity/references/feature-discovery.md` relative to this file's directory.

## Before validation or reporting

Use controlled identities/resources that satisfy the program's account requirements. Do not create real orders, bookings or other material side effects as a generic account-realism step. Use the program's permitted test mechanisms and existing authorization. Backend endpoints discovered in an APK need their own scope basis and runtime evidence; a mobile listing does not establish a payout or automatic backend permission.

Separate source-mapped handler, observed external delivery, reproduced behavior, and demonstrated security effect. Reachability alone is a lead, not an automatic Low finding. A logged-out ignored intent leaves logged-in behavior unresolved; do not manufacture a session or report an assumed effect.

For a report, state build/device, attacker entry and preconditions, minimal reproduction, relevant control, actual outcome and falsification. Apply only the current program's stock-device, interaction, data-retention, timing and submission requirements. A one-fix rule concerns root causes; it is not a universal instruction to bundle independent findings. Scoring and final wording belong to reporting-mode.
