# Frida Dynamic Workflow

Recovered compatibility deep-dive for `.opencode/skills/mobile-mode/SKILL.md`.

## Environment sanity

Keep the local Python/CLI package and device `frida-server` aligned:

```bash
frida --version
python3 -c 'import frida; print(frida.__version__)'
adb shell su -c 'ps -A | grep frida-server'
```

The parent mobile skill was validated around Frida 16.x semantics. Spawn with:

```bash
frida -U -f com.target.app -l script.js
```

Do not copy obsolete `--no-pause` examples into this workflow.

## Java instrumentation skeleton

```javascript
Java.perform(function () {
  var ActivityThread = Java.use('android.app.ActivityThread');
  console.log(ActivityThread.currentApplication());
});
```

First prove the Java bridge works. Then instrument the specific class/method identified during static analysis rather than spraying generic hooks.

## Pinning workflow

1. Verify pinning exists in code/config or by observing a failed interception.
2. Identify the implementation: platform TrustManager, OkHttp CertificatePinner, Flutter/native library, or custom verifier.
3. Hook only the relevant implementation.
4. Use the resulting proxy visibility to test the actual server-side boundary.

Common authorized-lab helpers:

```bash
frida -U -f com.target.app --codeshare pcipolloni/universal-android-ssl-pinning-bypass-with-frida
objection -g com.target.app explore
```

A pinning bypass is normally an analysis enabler, not a standalone vulnerability.

## Persistence / reliability

`/data/local/tmp` may be ephemeral in some test environments. Before every dynamic session verify the server process rather than assuming persistence.

## What to instrument

Prioritize:
- deep-link / Intent parsing;
- WebView URL loading and JavaScript bridges;
- token creation/storage/use;
- request signing and auth headers;
- local cryptographic wrappers;
- feature/role checks that protect sensitive flows.

Related upstream deep dives:
- `SKILL_FILES/VULNERABILITIES/MOBILE/android_dynamic_analysis.md`
- `SKILL_FILES/VULNERABILITIES/MOBILE/certificate_pinning_bypass.md`
