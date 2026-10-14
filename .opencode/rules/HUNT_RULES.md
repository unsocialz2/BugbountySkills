# HUNT_RULES — always-on operating contract (ORACLE)

Loaded via `instructions` in `opencode.json`. Applies to the lead AND every subagent, every turn.

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

- The lead (bughunter/build/plan) NEVER runs commands, browses, or touches Burp/Playwright. Every target action is a `task` call to exactly one worker.
- Workers: load your mode skill FIRST via the `skill` tool, then work, then return evidence in the contract format. One worker, one focused subtask.
- `deep-reviewer` exists to kill your darlings: route every candidate through falsification before `final-reviewer`.

## 5. CALIBRATION

- State uncertainty plainly ("unverified: X"). Never inflate severity to compensate for weak evidence — a strict FAIL beats a wasted submission.
- Cite PortSwigger / HackTricks / disclosed reports for non-obvious claims. No bare CVSS numbers: vector or "unscored".
