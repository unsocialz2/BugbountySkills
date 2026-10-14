# Mobile Policy Triage Gate

Recovered compatibility deep-dive for `.opencode/skills/mobile-mode/SKILL.md`.

Before spending time on a mobile lead, read the program's mobile exclusions and record:

```text
ATTACKER: <unauth / normal user / physical-device holder / rooted-device holder>
REACH:    <stock device / emulator / rooted only / ADB only / unknown>
IMPACT:   <concrete cross-user or server-side impact>
POLICY:   <explicitly in scope / excluded / unclear>
```

## Common exclusions that kill a finding

- Root/jailbreak-only behavior.
- Findings requiring ADB or physical-device access when the program excludes that attacker model.
- Lack of obfuscation, root detection, or certificate pinning by itself.
- WebView exploitation when the program explicitly excludes it.
- `allowBackup=true` when exploitation requires an excluded local/ADB capability.

## High-value cases that often remain valid

- Server-side authorization/authentication failures discovered through the mobile app.
- Exposed mobile-only APIs reachable by a remote attacker.
- Exported components or deep links that produce a real cross-boundary impact without excluded prerequisites.
- Hardcoded credentials/secrets that grant capability beyond a normal unauthenticated user.

## Stop rule

If the only reproducible path depends on a prerequisite explicitly excluded by the program and there is no independent server-side impact, stop and log the lead instead of escalating it into a finding.
