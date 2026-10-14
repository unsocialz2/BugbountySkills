# ~/bugbounty — SHARED HUNTING ENVIRONMENT

Applies to ALL targets. Per-target facts live in each target's `STATE.md`.
Do not copy STATE across targets — this file is the exception, it is infra.

## LAST VERIFIED: 2026-10-03

## PINNED VERSIONS — do not drift, host and device MUST match

| Component | Version | Location |
|---|---|---|
| frida (host client) | **16.5.7** | pipx venv `~/.local/share/pipx/venvs/frida-tools` |
| frida (host lib) | **16.5.7** | `~/.local/lib/python3.14/site-packages/frida` |
| frida-tools | **13.7.1** | both of the above, aligned |
| frida-server (device) | **16.5.7** | `/data/local/tmp/frida-server` |
| frida-server binary | linux-x86_64-android | md5 `d5c3a70163eba510432339dd04f30588` |

Why 16.5.7 and not 17.x: Frida 17 broke the Android Java bridge for this
workflow. 16.5.7 is the last version where `Java.perform` +
`Java.use('android.app.ActivityThread')` work out of the box for hooking
Android apps. VALIDATED on this device — spawn, Java.perform, ActivityThread
resolve, and application context retrieval all pass.

### VERSION DRIFT WARNING
There were two host installs and they disagreed. If `frida --version` and
`python3 -c "import frida; print(frida.__version__)"` ever disagree again,
you have reintroduced the split brain. Fix by pinning both:

    pipx install frida-tools==13.7.1 --suffix= 2>/dev/null   # or
    pip install --user "frida==16.5.7" "frida-tools==13.7.1"

Reinstalling frida-server must always match whatever `frida --version` reports.

## HOST TOOLING

| Tool | Status |
|---|---|
| adb | `/usr/bin/adb` — OK |
| jadx | `/usr/local/bin/jadx` — OK |
| apktool | `/var/lib/snapd/snap/bin/apktool` — OK |
| nuclei / subfinder / httpx | `~/go/bin` — OK |
| java | Temurin 21.0.5 — OK |
| frida CLI | `~/.local/bin` — **was broken, now fixed** |
| objection | MISSING — install only if pinning blocks you |
| mobsf | MISSING — optional |
| drozer | MISSING |

### THE ZSH PATH BUG (do not reintroduce)
`~/.bashrc` exports `~/.local/bin` to PATH. `~/.zshrc` did not, and the shell
here is zsh — so `frida`, `frida-ps`, `mitmproxy` were all silently unreachable
while appearing to be installed. Fixed in `~/.zshrc` with a guarded prepend.
If a pip-installed tool reports "command not found" despite being installed,
check PATH before assuming a broken install.

## DEVICE — 192.168.240.112:5555

| Property | Value |
|---|---|
| Type | **WayDroid** container, not a physical handset |
| Model string | `WayDroid_x86_64_Device` |
| Arch | x86_64 |
| Android | 13 (SDK 33) |
| Root | Magisk Delta (`0fe46c5a-delta:MAGISK:R`), `su` at `/system/bin/su` |
| Google | Play Store + GMS present and running (10 matching packages) |
| frida-server | 16.5.7, running as root, autostart enabled |

### PERSISTENCE
`/data/adb/service.d/frida-server.sh` starts frida-server on boot and waits
for the binary to exist. This exists because **`/data/local/tmp` got wiped
once** and silently killed the server — it is why the ServiceNow notes claimed
frida was running when it was not.

If `frida-ps -U` ever hangs or returns nothing:

    adb shell su -c "ps -A | grep frida-server"          # is it alive?
    adb shell su -c "/data/local/tmp/frida-server"        # restart manually
    adb shell su -c "cat /data/local/tmp/frida.log"       # why did it die

Note: reading files back out of `/data/adb` via `adb shell su -c cat` returns
"Permission denied" on this Magisk Delta build even though writes and chmods
succeed. Verify service.d registration with `ls -la`, not by cat'ing the file.

## HARDWARE CONSTRAINT — CORRECTED 2026-10-03 (I was wrong)

My first read of this was wrong and it nearly cost us the targets. Corrected:

**The device DOES run arm64 apps.** It advertises:

    ro.dalvik.vm.native.bridge = libndk_translation.so
    ro.product.cpu.abilist     = x86_64,x86,arm64-v8a,armeabi-v7a,armeabi
    ro.product.cpu.abilist64   = x86_64,arm64-v8a

NDK translation (the same ARM translation layer used by Android-x86) executes
arm64-v8a native libraries on this x86_64 host. Every modern app is arm64-only
now, and they all run fine.

### VERIFIED 2026-10-03 — OVO (ovo.id) end to end
- OVO ships **arm64-v8a only** native code (`libfinauthlivenessv5Ex.so`,
  `libsafexEx.so`, `libconcealjni.so`, `libosec.so`, `libbarhopper_v3.so`).
- Installed with `adb install-multiple` of base + `config.arm64_v8a.apk` +
  density split. `primaryCpuAbi=arm64-v8a`.
- Launched, consent accepted, onboarding carousel, **reached live login screen**
  ("Masuk atau Daftar", +62 prefix, keyboard up, field accepting input).
- **`requestIntegrityToken()` FAILED** in logcat
  (`E Finsky: [83] requestIntegrityToken() failed for ovo.id`), and the app
  **did not block**. Play Integrity is NOT a gate for these apps.

### WHAT IS ACTUALLY BLOCKING
Only one thing: **registration needs an Indonesian +62 phone number.** Everything
up to and including the login screen works without it. You cannot create an
account without an Indonesian SIM/number.

Also note: installing from APKPure rather than Play Store produces
`GoogleCertificatesRslt: not allowed: pkg=ovo.id, sha256=[37d3...]` in logcat
because the signature differs from Play's. Harmless for research, but do not
treat that log as a finding.

### ARM APPS: how to install them
The APKPure `/b/APK/<pkg>` endpoint gives you the BASE APK only and it will
fail with `INSTALL_FAILED_MISSING_SPLIT`. Use the XAPK endpoint instead and
install with `install-multiple`:

    curl -sL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36" \
      -o app.xapk "https://d.apkpure.com/b/XAPK/<pkg>?version=latest"
    # unzip, then:
    adb install-multiple -r -g base.apk config.arm64_v8a.apk config.xxhdpi.apk

The browser User-Agent is required — APKPure returns 403 to curl's default UA.

### DEVICE LOCALE IS en-US
Grab is SEA-only, OVO Indonesia-only, iFood Brazil-only, Just Eat non-US.
None of these resolve from this Play Store account. Fetch APKs directly and
`adb install-multiple` them, or the region check blocks you at the store.

## TOOLING GOTCHAS FOUND 2026-10-03
- **apktool is a snap** — it cannot read `/tmp/opencode` (snap confinement).
  "Input file was not found" on a file that exists is the symptom. Use jadx, or
  run apktool from a path the snap can see.
- **gplaycli is dead** — its token dispenser service is gone, and it crashes on
  Python 3.14 (`exceptions must derive from BaseException`). Do not use it.
- `adb shell dumpsys package <pkg>` is the fastest way to get intent filters,
  schemes, authorities and exported components without decoding the manifest.
- dumpsys prints intent-filter **authority** as `Authority: "host": port`, NOT
  `Host:`. A grep for `Host:` silently returns nothing and makes it look like
  filters have no host restriction. They usually do.

Program policies differ, so the same rooted box is fine for some and not others:

| Target | Rooted/jailbroken device excluded? |
|---|---|
| Grab | NO — only rule is "test only accounts you own" |
| iFood | No exclusion found |
| Just Eat Takeaway | **YES** — plus ADB access, physical access, malware app install, and WebView exploitation |

Do NOT unroot this device. It is only Just Eat that cares, and Just Eat is the
weakest of the three.

## OPERATIONAL RULES LEARNED THE HARD WAY
- Verify `ps -A | grep frida-server` before trusting any note that says frida is running.
- Never report a finding that only reproduces on a rooted device.
- Report PII must be redacted on Grab and iFood; neither tolerates bulk data extraction.