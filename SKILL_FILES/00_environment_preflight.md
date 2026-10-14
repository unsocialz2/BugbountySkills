# Mobile Environment Preflight

Recovered compatibility deep-dive for `.opencode/skills/mobile-mode/SKILL.md`.

## Device capability checks

Run these before deciding an Android app cannot execute on the test device:

```bash
adb shell getprop ro.product.cpu.abi
adb shell getprop ro.dalvik.vm.native.bridge
adb shell getprop ro.product.cpu.abilist
adb shell getprop persist.sys.locale
adb shell pm list packages | grep -E 'vending|gms'
```

An x86_64 host may still execute arm64 apps when Android exposes ARM translation (for example `libndk_translation.so`) and `arm64-v8a` appears in the ABI list.

## APK / split-package preflight

Modern Play-distributed apps commonly use split APKs. A base APK alone may fail with `INSTALL_FAILED_MISSING_SPLIT`.

```bash
unzip -o app.xapk -d app/
adb install-multiple -r -g app/base.apk app/config.arm64_v8a.apk app/config.xxhdpi.apk
adb shell cmd package resolve-activity --brief -c android.intent.category.LAUNCHER <pkg>
adb shell am start -n <pkg>/<resolved.activity>
```

## Tool-path checks

```bash
command -v adb jadx apktool frida frida-ps objection
printf '%s\n' "$PATH"
```

User-installed Python/pipx CLIs often live under `~/.local/bin`; ensure the active shell includes it.

## Frida compatibility preflight

Keep the CLI/client and device `frida-server` versions aligned. The parent mobile skill was validated around the Frida 16.x invocation model, where spawn resumes by default and `--no-pause` is not a valid flag.

```bash
frida --version
python3 -c 'import frida; print(frida.__version__)'
adb shell su -c 'ps -A | grep frida-server'
```

If those versions disagree, fix the environment before treating dynamic-analysis failures as app defenses.
