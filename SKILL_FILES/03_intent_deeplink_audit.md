# Android Intent & Deep-Link Audit

Recovered compatibility deep-dive for `.opencode/skills/mobile-mode/SKILL.md`.

## Fast manifest view

```bash
adb shell dumpsys package <pkg> > pkg.txt
```

When reading `dumpsys`, Android may render a host as `Authority: "host": port`; do not rely on a `Host:` grep alone.

Decoded alternative:

```bash
apktool d -f -o apk_out/ app.apk
grep -nE 'intent-filter|android:scheme|android:host|android:path|android:pathPrefix|android:pathPattern|android:exported' apk_out/AndroidManifest.xml
```

## URI composition

A filter containing scheme + authority + literal path requires all three pieces. Example:

```text
scheme = gxsdev
authority = ovo.id
path = /oauth-callback
```

Correct shape:

```text
gxsdev://ovo.id/oauth-callback?code=TEST
```

Do not confuse the authority in `scheme://name` with a path.

## Resolve before launching

```bash
adb shell cmd package query-activities \
  -a android.intent.action.VIEW \
  -d 'gxsdev://ovo.id/oauth-callback'
```

Use resolution first for sensitive routes. Only invoke a route after confirming the test is authorized and non-destructive.

## Route triage

Prioritize names suggesting authentication, payments, identity, navigation, or embedded web content: `login`, `oauth`, `callback`, `verify`, `transfer`, `withdrawal`, `checkout`, `kyc`, `webview`, `jsbridge`, `upgrade`.

For every candidate trace:

```text
external URI/Intent
  -> exported component
  -> parsing/validation
  -> navigation/auth state
  -> WebView/native bridge/API action
  -> concrete attacker capability
```

Related upstream deep dives:
- `SKILL_FILES/VULNERABILITIES/MOBILE/android_deeplink_attacks.md`
- `SKILL_FILES/VULNERABILITIES/MOBILE/android_intent_attacks.md`
- `SKILL_FILES/VULNERABILITIES/MOBILE/android_webview_attacks.md`
