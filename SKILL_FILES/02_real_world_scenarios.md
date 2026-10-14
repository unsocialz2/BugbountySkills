# Mobile Real-World Scenarios

Recovered compatibility deep-dive for `.opencode/skills/mobile-mode/SKILL.md`.

Use these as end-to-end workflows, not as standalone findings.

## Scenario 1 — Production app with dev/staging deep-link schemes

1. Acquire the complete split package and install it on the authorized test device.
2. Inspect `dumpsys package` and the decoded manifest for VIEW intent filters.
3. Separate production, dev, staging, and UAT schemes/hosts.
4. Resolve candidate URIs non-destructively before launching them.
5. Trace the receiving Activity and determine whether attacker-controlled URI data reaches auth, navigation, WebView, or native bridge logic.
6. Report only if the route creates a meaningful boundary break; the presence of a dev scheme alone is not account takeover.

## Scenario 2 — Mobile app exposes a richer backend map than the website

1. Extract URLs/hosts from the APK and decompiled code.
2. Rank hosts by references and identify mobile-only API versions.
3. Compare authorization behavior with the normal web/API surface.
4. Treat server-side authz/authentication failures as API findings; the app is the discovery source, not the security boundary.

## Scenario 3 — Frida/pinning confusion

1. Confirm the app actually implements certificate pinning before attempting a bypass.
2. Verify local Frida client and device server versions match.
3. Confirm the target process and Java runtime can be instrumented.
4. Only then hook the relevant trust/pinning implementation.
5. A bypass of a defensive control is normally a testing enabler, not a standalone report, unless the program explicitly treats it otherwise.

## Scenario 4 — Exported component / intent route

1. Enumerate exported Activities, Services, Receivers and Providers.
2. Determine required permissions and caller restrictions.
3. Resolve or invoke the component with a benign proof value.
4. Trace whether attacker input can trigger privileged action, data exposure, token handling, file access, or an unsafe WebView/native bridge.
5. Keep the PoC non-destructive and prove the concrete capability gained.
