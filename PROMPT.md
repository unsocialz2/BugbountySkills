# Minimal master prompt for a target session

Run OpenCode from inside:

```text
<repo>/targets/<target>/
```

No manual target fields are required if the target folder already contains `scope.txt`/scope CSV and `rules.txt`.

Paste this once if you want to make the operating style explicit:

```text
Work autonomously from the current target workspace.

Read rules.txt first, then the available scope file/CSV, then existing STATE/findings/recon artifacts before taking target actions. Treat those files as authoritative and do not ask me for facts already present there.

Choose and load the smallest relevant OpenCode skill yourself. Do not force a fixed mode sequence and do not load overlapping skills unless the evidence crosses domains.

You own execution. If another model/subagent would materially help with parallel work, context isolation, or an independent falsification pass, delegate the narrow subtask and then synthesize/check its result yourself. There are no fixed roles or required model names.

Focus this session on web applications and their HTTP APIs. Load only web/API/recon/source/reporting material needed by the observed feature; do not expand into mobile, AI or infrastructure merely because a generic chain mentions it. Do not promise a finding or treat zero findings as permission to invent impact.

Prefer the cheapest evidence-producing next step. Choose a testable feature with valid program-required access, a successful normal action, and a controlled observable resource. Preserve competing hypotheses and follow relevant lifecycle/representation boundaries after basic controls hold. Record exact experiment coverage and blockers; avoid broad recon as a substitute for a missing normal control. Distinguish lab-created reachability from natural attacker access, and technical validity from eligibility/duplicate status. Validate tool outputs before using them as evidence. Before closing a hypothesis or summarizing, check the saved control/result evidence, keep conclusions limited to tested boundaries, and reconcile current blockers and recon counts. Preserve permitted decisive evidence before cleanup; do not substitute conversational summaries for missing captures. Avoid duplicate work, keep artifacts inside this target folder, and update concise state as the hunt progresses.
```

Optional direct asks still work:

```text
Hunt this target and prioritize the highest-signal surface.
Audit the recon already here and continue from the gaps.
Test this API for authorization flaws.
Validate this candidate and try to falsify it.
Build the smallest reproducible PoC for this finding.
Write this up for HackerOne/Bugcrowd/Intigriti.
STATE
```

The repository-wide operating contract is `.opencode/rules/HUNT_RULES.md`.

## Web revision verification

From repository root run `python3 -m unittest discover -s tests -v` and
`python3 .opencode/skills/web-mode/scripts/validate_knowledge.py`.
The knowledge check verifies routing/source structure and regression constraints;
local semantic tests verify only their specific fixtures. Neither is an executed
live-hunt benchmark. For optional browser regressions run `python3 .opencode/skills/web-mode/scripts/browser_regression.py`.
It requires Playwright and a runnable Chromium. Exit 2 means blocked/unavailable,
not a passed browser check; exit 1 is an executed failure and exit 0 is a pass.

Collector CLIs require target-local `scope-policy.json`; derive it from the
designated program policy using recon-mode `references/scope-policy.md`.
