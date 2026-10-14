# Android Static Workflow

Recovered compatibility deep-dive for `.opencode/skills/mobile-mode/SKILL.md`.

## 1. Inventory the package

```bash
APKiD app.apk
apktool d -f app.apk -o apk_out/
jadx --no-res -d java_out/ app.apk
```

Use `jadx --no-res` for a fast code-first pass on large multidex apps.

## 2. Build the backend map

```bash
grep -rniE 'api[_-]?key|secret|password|token|client_secret|firebase|AKIA|googleapis' java_out/
grep -rhoE 'https?://[a-z0-9.-]+\.[a-z]{2,}[a-zA-Z0-9/._-]*' java_out/ \
  | sed -E 's#(https?://[^/]+).*#\1#' | sort | uniq -c | sort -rn | head -30
```

Rank discovered hosts by reference count, then separate production, staging/dev, analytics, CDN, and third-party services.

## 3. Manifest/security configuration

```bash
grep -nE 'android:exported|allowBackup|debuggable|usesCleartextTraffic|networkSecurityConfig|intent-filter' apk_out/AndroidManifest.xml
```

Treat configuration flags as leads. Prove reachability and impact before reporting.

## 4. Native-layer triage

```bash
python3 - <<'PY'
import zipfile
z=zipfile.ZipFile('app.apk')
print(sorted({n.split('/')[1] for n in z.namelist() if n.startswith('lib/') and len(n.split('/')) > 2}))
PY
```

Native libraries tell you which ABIs and security-sensitive components exist, but do not let native complexity block Java/Kotlin and API analysis.

## 5. Trace findings to a boundary

For every secret, endpoint, exported component, or unsafe setting, record source -> validation -> sink -> attacker capability. Static evidence without a reachable attack path remains a lead.

Related upstream deep dive: `SKILL_FILES/VULNERABILITIES/MOBILE/android_static_analysis.md`.
