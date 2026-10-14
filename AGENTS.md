# ~/bugbounty — ORACLE hunting root (Opencode project scope)

This directory is the strict Opencode project root. Every subfolder `~/bugbounty/<target>/`
is one program. Skills in `~/bugbounty/.opencode/skills/` auto-load for anything under here.

## How to start a new target

```bash
cp -r ~/bugbounty/_template ~/bugbounty/<new-name>
# then edit ~/bugbounty/<new-name>/scope.txt + STATE.md
cd ~/bugbounty/<new-name>
opencode
```

Say `ORACLE`, `STATE`, or `RECON MODE — dry-run only` to verify skills loaded.

## Routing — skill triggers

| Say this | Loads |
|---|---|
| `RECON MODE — <target>` | `.opencode/skills/recon-mode/SKILL.md` — **§0 AUDIT GATE: rate operator-supplied recon, fill only gaps, never repeat DONE stages** — then passive → enum → DNS → alive → JS/wayback → fuzz → ports → fingerprint → cloud |
| `WEB MODE — <target> <stack>` | `.opencode/skills/web-mode/SKILL.md` — 41 web vuln classes, chain-to-ATO |
| `API MODE — <target>` | `.opencode/skills/api-mode/SKILL.md` — REST/GraphQL/gRPC, BOLA/BFLA first |
| `LLM MODE — <target>` | `.opencode/skills/llm-mode/SKILL.md` |
| `MOBILE MODE — <apk/ipa>` | `.opencode/skills/mobile-mode/SKILL.md` |
| `PAYLOAD <class> <context>` | `.opencode/skills/payloads/SKILL.md` |
| `SCR MODE — <language>` | `.opencode/skills/scr-mode/SKILL.md` |
| `REPORT MODE — <vuln> <impact>` | `.opencode/skills/reporting-mode/SKILL.md` |
| `EXPLOIT MODE — <chain>` | `.opencode/skills/exploit-mode/SKILL.md` |
| `INFRA MODE` | `.opencode/skills/infra-mode/SKILL.md` — AWS/GCP/Azure, S3, K8s, Docker |
| `H1 MODE / BC MODE / INTI MODE` | `.opencode/skills/platform-intel-mode/SKILL.md` |
| `AUTOMATION` | `.opencode/skills/automation-mode/SKILL.md` — pipelines, VPS, notify |
| `ORACLE / STATE / RESET` | `.opencode/skills/core-identity/SKILL.md` — always loaded: `opencode.json` `instructions` injects `.opencode/rules/HUNT_RULES.md` every turn; load core-identity via the `skill` tool at session start |

## Per-target state (isolation rule)

* `STATE.md` in the current `~/bugbounty/<target>/` dir is authoritative. Never copy STATE across targets.
* `scope.txt` in the current dir is authoritative. Never test outside it.
* `RECON_LOG.md` is the append-only recon ledger — the §0 audit gate reads it; a stage logged DONE is never re-run.
* The operator ALWAYS supplies their own recon; ORACLE audits it first (recon-mode §0), fills only gaps.
* Never test customer CPE / dynamic-pool ranges (`*.pools.*`, `*.cust.*`, `*.rev.*`, `*.dsl.*`, etc.). Confirm written policy at `hackerone.com/<program>/policy_scopes` before active scanning.
* Upstream source repo (`Desktop/BugBountySkills`) is reference only — do not edit it from here.

## Operator stack (assumed by customized skills)

Kali + Burp Pro (Param Miner, Turbo Intruder, Autorize, JWT Editor, Collaborator) + VPS.
Free-tier-friendly defaults; paid APIs (`$ST_KEY`, `$VT_KEY`, Chaos) are optional behind env guards.
