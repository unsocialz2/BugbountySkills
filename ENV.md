# Shared Hunting Environment

Local environment notes shared across targets. **This file describes observed machine/device state, not program policy and not universal tool guidance.**

Last verified: **2026-10-27**

When an exact version, device capability, path, or service state matters, verify it at runtime before relying on this file. Target-specific restrictions belong in `targets/<target>/rules.txt`.

## Host topology

- Windows host + WSL2 running **Kali GNU/Linux Rolling 2026.3** (`x86_64`, kernel `6.18.54.1-microsoft-standard-WSL2`).
- Windows user: `ahmed`; WSL user: `winchester`, home `/home/winchester`.
- WSL interop is enabled: Windows executables such as `node.exe`, `java.exe`, and `wsl.exe` run directly from WSL. Verified 2026-10-27.
- Windows Burp is reachable from WSL at `127.0.0.1:8080` (proxy) and `127.0.0.1:9876` (Burp MCP SSE). Both were reachable at last check.
- Browsers: Windows **Google Chrome 156.0.8078.48**; WSL **Chromium 150.0.7871.181** (`/usr/bin/chromium`).
- H1Username: nahidwin0x
## WSL tooling

Verified 2026-10-27:

| Tool | Path | Version / notes |
|---|---|---|
| `adb` | `/usr/bin/adb` | 1.0.41 |
| `jadx` | `/usr/bin/jadx` | 1.5.6 |
| `apktool` | `/usr/bin/apktool` | 2.7.0-dirty (Kali package, not the snap build) |
| `nuclei` | `/usr/bin/nuclei` | 3.11.1; templates in `/home/winchester/.local/nuclei-templates` |
| `subfinder` | `/home/winchester/go/bin/subfinder` | 2.9.0 |
| `httpx` | `/usr/bin/httpx-toolkit` | ProjectDiscovery build; interactive zsh aliases `httpx` to `httpx-toolkit` |
| `nmap` | `/usr/bin/nmap` | 7.99 |
| `node` | `/usr/bin/node` | v24.19.0; `npm` 11.19.1 |
| `python3` | `/usr/bin/python3` | 3.14.7; `python3.13` is also installed (3.13.15) |
| `pipx` | `/usr/bin/pipx` | CLI installs land in `~/.local/bin` |
| `java` | `/usr/bin/java` | OpenJDK 25.0.4 (Debian) |
| `chromium` | `/usr/bin/chromium` | 150.0.7871.181 |
| `ego-browser` | `/mnt/c/Users/ahmed/.local/share/ego/active_version_dir/ego-browser.exe` | Windows ego lite via interop (second-option browser); run `ego-browser skill` before ego tasks |
| `frida` | `/home/winchester/.local/bin/frida` | 17.24.3; `frida-tools` 14.11.0; Python `frida` 17.24.3 |

### Shell PATH gotcha

The interactive shell is zsh. If a pip/pipx-installed CLI exists but reports `command not found`, check that `~/.local/bin` is present in the active zsh PATH. ProjectDiscovery binaries installed with `go install` commonly live in `~/go/bin`, which must also be on PATH. In scripts or non-interactive contexts, call `httpx-toolkit` directly instead of relying on the interactive `httpx` alias.

## Windows tooling and paths

- Node: `C:\Program Files\nodejs\node.exe` — v24.22.1.
- Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe` — 156.0.8078.48.
- Burp Suite: `C:\Users\ahmed\AppData\Local\Programs\BurpSuite`; bundled JRE is OpenJDK 26.0.2 at `...\BurpSuite\jre\bin\java.exe`.
- Burp MCP extension listens on `127.0.0.1:9876`; the stdio bridge is `C:\Users\ahmed\OneDrive\Desktop\mcp-proxy.jar`.
- Pinned MCP npm servers: `C:\Users\ahmed\mcp-servers` (`package.json` pins Chrome DevTools MCP, TempMail, HackTricks, Nuclei wrapper (headless Playwright MCP removed 2026-11-14)).
- DeepSeek Harness MCP bundle: `C:\Users\ahmed\mcp-bundles\bounty-mcps\cordis.patch.yml`.
- Mobile lab: `C:\Users\ahmed\OneDrive\Desktop\Mobile-Lab-Control\Mobile-Lab-Control\Mobile-Lab-Control.cmd`.

## Android lab device

Current endpoint: **`192.168.1.6:5555`** (verified 2026-11-10; older notes said 192.168.1.17 — device DHCP changes). Plain `adb shell` is uid 2000; run `adb root` first (works on MuMu).

- Reported as product `a55x`, model `SM_A5560`; process list shows MuMu emulator components.
- Android **15 / SDK 35**.
- Host ABI: `x86_64`.
- ABI list: `x86_64,arm64-v8a,x86`.
- ARM translation: `ro.dalvik.vm.native.bridge=libnb.so` — ARM64 app native libraries can execute on this x86_64 instance.
- ADB shell runs as **uid 0 (root)** with SELinux context `u:r:su:s0`; there is no `su` binary, so use `adb shell` directly rather than `adb shell su -c ...`.
- Google Play/GMS packages are present (`com.android.vending`, `com.google.android.gms`).

Earlier notes referenced a WayDroid endpoint at `192.168.240.112:5555`. That is superseded by the current mobile lab device above; do not assume the old endpoint is active.

Verify the device at runtime:

```bash
adb connect 192.168.1.17:5555
adb devices -l
adb shell getprop ro.product.cpu.abi
adb shell getprop ro.product.cpu.abilist
adb shell getprop ro.dalvik.vm.native.bridge
```

Do not infer app compatibility from host ABI alone.

## Mobile Lab Control (Burp + Frida)

Open `Mobile-Lab-Control.cmd` from:

```text
C:\Users\ahmed\OneDrive\Desktop\Mobile-Lab-Control\Mobile-Lab-Control\Mobile-Lab-Control.cmd
```

The GUI runs PowerShell, which invokes `mobile-lab.py` inside the WSL distro named `kali-linux`.

| Button | Action |
|---|---|
| Burp ON | Enable the proxy and temporary trust in Burp's CA certificate. |
| Burp OFF | Remove temporary CA trust and restore the previous proxy setting. |
| Frida ON | Start the installed Frida server. |
| Frida OFF | Stop the Frida server without changing Burp settings. |

Additional buttons in the GUI: **Burp STATUS** and **Frida STATUS**.

Reopen the target app after switching Burp ON or OFF.

Operational notes:

- Closing the control window does **not** stop Burp or Frida. Use the OFF buttons first if you want to undo the setup.
- Burp ON pulls the current CA from `http://127.0.0.1:8080/cert`, installs a temporary CA overlay in the relevant Android mount namespaces, runs `adb reverse tcp:8080 tcp:8080`, and sets the global proxy to `127.0.0.1:8080`.
- Burp OFF restores the saved proxy (or deletes it), removes the CA overlay and reverse tunnel, and leaves helper files in `/data/local/tmp/burp-switch`. It does not clear Burp history.
- If Burp Intercept is on, requests can wait for Forward; turn Intercept off when you only want HTTP history.
- Frida ON starts `/data/local/tmp/frida-server`; Frida OFF stops that process. The server log is `/data/local/tmp/mobile-lab-frida.log`.
- The lab checks that the device server version matches the WSL client before starting Frida. It does not download Frida or bypass SSL pinning.
- Config file: `config.json` with `device`, `wsl_distribution`, and `frida_server`.

Equivalent WSL commands from the project folder:

```bash
python3 mobile-lab.py burp-on
python3 mobile-lab.py burp-off
python3 mobile-lab.py burp-status
python3 mobile-lab.py frida-on
python3 mobile-lab.py frida-off
python3 mobile-lab.py frida-status
```

Add `--device 192.168.1.17:5555` to target a different device address.

State observed at last check (snapshot, not permanent): device connected, Frida ON as root with matching 17.24.3 client/server versions, `frida-ps -U` could enumerate processes; Burp proxy setting was `:0` (off) while the temporary CA trust and the `tcp:8080` reverse tunnel were still present. Use the STATUS buttons before assuming a clean state.

## Frida — current pin

The working local combination is now:

- Frida host library/client: **17.24.3**
- `frida-tools`: **14.11.0**
- device `frida-server`: **17.24.3**

The previous 16.5.7 / 13.7.1 pin is obsolete for this lab. Host library/client and device server should stay matched; the mobile lab enforces this for start.

Useful checks:

```bash
frida --version
python3 -c 'import frida; print(frida.__version__)'
frida-ps -U | head
adb shell 'pidof frida-server'
adb shell '/data/local/tmp/frida-server --version'
```

The server path is:

```text
/data/local/tmp/frida-server
```

It currently runs as root and can be started/stopped through the mobile lab. `/data/local/tmp` persistence should not be assumed; verify the process instead of trusting old notes.

## APK / bundle handling notes

Modern Android apps frequently ship as split APK/App Bundle packages. A base APK alone may fail with `INSTALL_FAILED_MISSING_SPLIT`.

For an XAPK/bundle already obtained, inspect its contents and install the required base + ABI + density/language splits together:

```bash
unzip -o app.xapk -d app/
adb install-multiple -r -g app/base.apk app/config.arm64_v8a.apk app/config.xxhdpi.apk
```

Select the actual splits present in the bundle rather than copying this command blindly.

Useful runtime checks:

```bash
adb shell dumpsys package <pkg>
adb shell cmd package resolve-activity --brief -c android.intent.category.LAUNCHER <pkg>
adb shell dumpsys window | grep mCurrentFocus
```

`dumpsys package` is often the fastest way to inspect exported components and intent filters without fully decoding an APK.

### Intent-filter parsing gotcha

In `dumpsys` output, intent-filter host information may appear as an `Authority:` entry rather than a literal `Host:` label. Avoid parsers that assume only `Host:` or they can silently misclassify filters as unhosted.

## Tool confinement gotcha

The current `apktool` is the Kali package at `/usr/bin/apktool`, so the earlier snap-confinement issue does not apply. If you switch back to the snap build, re-check whether it can read files outside its allowed filesystem view before treating an APK as invalid.

## ZCode agent environment

Installed from this repository's `.opencode/skills` on 2026-10-27; updated 2026-11-14:

- WSL: `~/.zcode/skills/` — 14 repo skills, 268 files.
- Windows: `C:\Users\ahmed\.zcode\skills\` — 14 repo skills, 268 files.
- Checksums of both copies match the source tree. This is a snapshot; re-copy after editing the repository skills.
- WSL additionally has three HackerOne gate skills (`bug-bounty-research-preflight`, `bug-bounty-scope-activation`, `hackerone-submission-gate`) and the unrelated `neon-*` set installed outside this repository; they are not part of the repo sync.

Skills: `core-identity`, `web-mode`, `api-mode`, `mobile-mode`, `infra-mode`, `llm-mode`, `scr-mode`, `recon-mode`, `exploit-mode`, `automation-mode`, `platform-intel-mode`, `reporting-mode`, `payloads`, `ego-browser`.

The skills reference `.opencode/rules/HUNT_RULES.md` and `targets/<target>/` workspaces. That contract is not installed at ZCode user scope, so run bug-bounty work from a target workspace or add the contract as workspace instructions.

MCP configurations:

- WSL: `~/.zcode/cli/config.json`
- Windows: `C:\Users\ahmed\.zcode\cli\config.json`

Configured servers and verified tool counts:

| Server | Tools | WSL launch | Windows launch |
|---|---:|---|---|
| `burp` | 27 | Windows Burp JRE + `mcp-proxy.jar` via WSL interop | Windows Burp JRE + `mcp-proxy.jar` |
| `playwright` | 25 | Linux `node` + `/usr/bin/chromium`, headed | Windows `node` + installed Chrome, headed |
| `chrome-devtools` | 32 | Linux `node` + `/usr/bin/chromium`, headless | Windows `node` + installed Chrome, headless |
| `tempmail` | 7 | Linux `node` | Windows `node` |
| `hacktricks` | 3 | Linux `node` | Windows `node` |
| `nuclei` | 1 | Native WSL `node` + `/usr/bin/nuclei` | `wsl.exe -d kali-linux` wrapper |

The exact config files were launch-tested on both sides with `initialize` → `tools/list`, and representative tool calls succeeded (Burp encoding, browser navigation, TempMail inbox creation, HackTricks search, Nuclei tech-detect).

Caveats:

- TempMail's free tier can rate-limit `create_inbox`; that is an external quota, not an MCP configuration failure.
- Burp's own approval gates still apply: history/scanner reads and `send_http*_request` can prompt until hosts are added under Burp's **MCP tab → auto-approve targets**.
- `chrome-devtools` runs headless with a separate browser profile, so its traffic does not appear in Burp history unless you configure a proxy. The `playwright` MCP runs headed (operator removed `--headless` on 2026-11-14) and is the preferred interactive browser; ego-browser is the second option (see the browser preference section).
- These browser MCPs overlap with ZCode's built-in browser tooling; expect duplicate capabilities.
- ZCode's MCP schema is strict: use `env` (not `environment`), one of `command` or `url`, and only supported keys, or the server is silently dropped. Default timeout is 30000 ms; the config sets longer values for slow servers.
- Restart ZCode after config changes and confirm status under **Settings → MCP**. The current session does not hot-reload new MCP entries.

## Environment vs target policy

This file answers questions like:

- what tools/device were available,
- what versions last worked locally,
- what lab-specific compatibility quirks were observed.

It does **not** answer:

- whether rooted/emulated testing is accepted,
- whether ADB/WebView/pinning findings qualify,
- what assets are in scope,
- what request rates or techniques are allowed.

Those decisions come from the active target's `rules.txt` and scope files every time.

## Browser preference for the operator workstation

The operator's preferred browser is headed Playwright: the ZCode `playwright`
MCP running without `--headless` (verified working on 2026-11-14), or an
equivalent headed Playwright launch on the current host. `ego-browser` is the
second option, for tasks that need the operator's logged-in ego session or when
Playwright is unavailable. Known ego paths: Windows
`C:/Users/ahmed/.local/share/ego/active_version_dir/ego-browser.exe`; WSL interop
`/mnt/c/Users/ahmed/.local/share/ego/active_version_dir/ego-browser.exe`.
These are environment hints, not portable requirements. Verify existence/version
and follow the installed guide before use (`ego-browser skill` for ego, matching
runtime and agent Space). On another host use its permitted isolated browser.
Record a missing-tool or onboarding blocker specifically. Do not alter personal
profiles or pretend fallback execution used a browser that did not run.
