# HUNT_RULES — always-on operating contract (ORACLE)

Loaded via `instructions` in `opencode.json`. Applies to the lead AND every subagent, every turn.

## 0. TARGET WORKSPACE CONTRACT (mandatory BEFORE target work)

The operator opens OpenCode from a target directory under the repository:

```text
<repo>/targets/<target>/
# example
<repo>/targets/vinted/
```

Treat the nearest directory whose parent is `targets/` as **TARGET_ROOT**. Its basename is **TARGET_NAME**. If the current working directory is deeper inside that target, walk upward to that target root. Never read/write another sibling under `targets/` unless the operator explicitly switches target.

### Target bootstrap — run once at the start of every target session

Before any target network request, scanner, browser/Burp action, validation, or report:

1. **Locate TARGET_ROOT** from the working directory. Do not ask the operator for the target name when it is already encoded by `targets/<target>/`.
2. **Read `rules.txt` first** when present. Extract program-specific restrictions, prohibited techniques, rate/automation limits, auth/account requirements, excluded vulnerability classes, disclosure/reporting notes, and any scope statements embedded in the rules.
3. **Load scope from TARGET_ROOT**, in this priority order:
   - `scope.txt`
   - `scope.csv`
   - `scope*.csv`
   - a single obvious program-export `*.csv` in TARGET_ROOT
4. **Parse CSV by its headers, not by a hardcoded vendor schema.** Preserve the raw asset value and use fields such as asset/type, in-scope/out-of-scope, bounty eligibility, max severity, instruction/notes when they exist. Unknown columns stay unknown; never invent semantics.
5. Build a silent **TARGET CONTEXT** containing:
   - `TARGET_ROOT`, `TARGET_NAME`
   - scope source file(s)
   - explicit in-scope assets / asset types
   - explicit out-of-scope assets / exclusions
   - rules/restrictions and automation limits
   - auth/account prerequisites
   - platform/program hints if present
6. **Program files outrank generic skills.** `rules.txt` and explicit scope data override any default command, wordlist, scan depth, request rate, attack class, or assumption in a skill.
7. **Never invent scope.** If scope data is incomplete, active work is limited to assets explicitly marked in-scope by the available files or the operator's current prompt. Brand/company pivots are leads only until scope confirms them.
8. **Do not re-ask for known context.** If target, scope, or rules are already available in TARGET_ROOT, use them automatically.

### Target-local state

All hunting artifacts belong to TARGET_ROOT, never the repository root:

```text
./STATE.md
./findings.md
./lessons.md
./RECON_LOG.md
./recon_data/
```

Existing target files are authoritative history. Inspect them before creating or repeating work. Relative paths used by hunting modes resolve from TARGET_ROOT; paths inside a skill's own documentation still resolve from that skill directory.

## 1. VIABILITY GATE (mandatory BEFORE any deep-dive)

Before spending more than ~15 minutes on any candidate, write these 4 lines:

```
ATTACKER:  <who: unauth / low-priv user / adjacent tenant / ...>
REACH:     <live | dead | unknown> + one command proving it
IMPACT:    <concrete harm to target or other users, or 'none'>
DUPE-OOS:  <checked hacktivity/scope: clear | suspect | OOS>
```

- `REACH=dead` or `IMPACT=none` → **STOP immediately**, log one line to `./lessons.md`, move on. No deep-dive, no PoC, no report.
- `REACH=unknown` → your next and only action is the single cheapest reachability test. No theory before it passes.
- A source-code weakness with no reachable attacker is a **note**, never a finding.

## 2. EVIDENCE CONTRACT (mandatory BEFORE anything enters findings.md)

No entry may be marked candidate/validated without ALL of:

1. Raw request/response excerpt (or exact file:line source+sink for code bugs).
2. One exact reproduce command (copy-pasteable).
3. Attacker model + reachability proof (from the gate above).
4. "Why not a dupe / why in scope" — one line.
5. `final-reviewer` PASS for anything leaving the project as a report.

Hypotheses without 1–2 are leads, not findings. Never score CVSS on a lead.

## 3. TIME-BOX / KILL SWITCH

- Recon ≤4h per target, then manual hunting. No signal in 8h → pivot target, log why.
- One candidate gets max 2h of deep work without new evidence → park it, move on.
- Report budget 1h. No report without a `final-reviewer` PASS.

## 4. DELEGATION POLICY

- The lead (bughunter/build/plan) MAY read target-local metadata and existing artifacts needed for bootstrap/state (`rules.txt`, scope files, STATE/findings/lessons/RECON_LOG/recon_data inventory).
- The lead NEVER performs target network actions, scanners, browsing, Burp, or Playwright itself. Every target action is a `task` call to exactly one worker.
- Workers inherit the TARGET CONTEXT, then load the relevant mode skill FIRST via the `skill` tool before acting. One worker, one focused subtask.
- `deep-reviewer` exists to kill your darlings: route every candidate through falsification before `final-reviewer`.

## 5. CALIBRATION

- State uncertainty plainly ("unverified: X"). Never inflate severity to compensate for weak evidence — a strict FAIL beats a wasted submission.
- Cite PortSwigger / HackTricks / disclosed reports for non-obvious claims. No bare CVSS numbers: vector or "unscored".
