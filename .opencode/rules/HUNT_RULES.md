# HUNT_RULES — always-on operating contract

Loaded by `opencode.json`. Keep this contract small; detailed methodology belongs in skills/references.

## 0. TARGET CONTEXT

Work only inside the active `<repo>/targets/<target>/` workspace. Infer **TARGET_ROOT** as the nearest directory whose parent is `targets/`; never read/write a sibling target unless the operator switches targets.

Before target actions:

1. Read `rules.txt` when present.
2. Load scope from `scope.txt`, then `scope.csv` / `scope*.csv` / one obvious program-export CSV. Parse CSV by headers, not a hardcoded platform schema.
3. Inspect existing `STATE.md`, `HYPOTHESES.md`, `COVERAGE.md`, `findings.md`, `lessons.md`, `RECON_LOG.md`, and `recon_data/` only when present/relevant. Missing files are normal; create working artifacts only when useful.
4. Build a silent context: scope, restrictions/rates, auth prerequisites, known coverage/evidence, and active target facts.

`rules.txt` + explicit scope outrank generic skills. Never invent scope or treat brand/ownership resemblance as permission. Do not re-ask for facts already in the workspace. Keep all target artifacts inside TARGET_ROOT.

## 1. MODEL AUTONOMY

The current model owns strategy and execution. There are **no fixed roles, mandatory reviewers/workers, required model choices, or forced mode sequences**.

Work directly by default. Delegate only when it materially helps (parallel independent work, context isolation, falsification, second opinion). Give a delegate only the minimum target context and one narrow deliverable; the current model remains responsible for synthesis and next actions.

## 2. SKILL / REFERENCE LOADING

Top-level `SKILL.md` files are routers, not books. Load the smallest relevant domain skill and only the exact deep-dive/reference needed for the current question. Do not preload overlapping modes or giant libraries.

Default ownership:

| Need | Skill |
|---|---|
| recon / attack surface | `recon-mode` |
| browser/session/general web | `web-mode` |
| REST / GraphQL / gRPC | `api-mode` |
| cloud/container/network | `infra-mode` |
| Android/iOS | `mobile-mode` |
| source/repository review | `scr-mode` |
| LLM/RAG/agent security | `llm-mode` |
| exact payload lookup | `payloads` |
| confirmed primitive -> minimal PoC/chain | `exploit-mode` |
| tooling/automation | `automation-mode` |
| program/platform research | `platform-intel-mode` |
| final report / numeric severity | `reporting-mode` |

Browser/session flows stay in `web-mode` even if JSON is involved; schema/protocol-wide REST/GraphQL/gRPC work belongs to `api-mode`.

### Deep-dive rule

Deep dives are **decision support**, never replacement identities or mandatory playbooks.

- Reason from target evidence before skill examples.
- Ignore legacy persona/“always test” language.
- Do not enumerate listed payloads, headers, bypasses, tools, or chains unless the observed architecture creates that question.
- Use `payloads` for exact context-specific probes rather than loading duplicate payload dumps.
- A listed chain never substitutes for proving each transition.
- Legacy CVSS/platform baselines inside hunting files are non-binding; `reporting-mode` owns numeric scoring unless explicitly requested earlier.

For large/legacy files: formulate the security question first, search/inspect headings, then read only the relevant section when possible. Prefer current primary/vendor research for version-sensitive behavior.

## 3. DISCOVERY / VIABILITY

Before substantial deep work, keep the best-known candidate shape:

```text
ATTACKER:   <unauth / primary-auth-only / low-priv / adjacent tenant / ...>
REACH:      <live | dead | unknown> + cheapest proof
QUESTION:   <exact trust boundary / invariant>
IMPACT-HYP: <plausible capability if confirmed; unknown allowed>
SCOPE:      <clear | needs-check | OOS>
```

This is a discovery gate, **not** a report gate. Unknown impact is acceptable when the boundary is concrete and the next test can clarify it.

- `REACH=dead` or `SCOPE=OOS` -> stop active deep work.
- `REACH=unknown` -> normally test reachability cheaply first.
- Park candidates after repeated low-cost tests fail to establish a real boundary/reachable primitive/plausible attacker advantage.
- Source/static weakness without reachable attacker remains a lead/note, not a finding.

### Discovery and coverage memory

For multi-step hunts, keep a small target-local `HYPOTHESES.md` queue and `COVERAGE.md` experiment ledger (starter shapes in `_template/`). A single simple test can use equivalent fields in existing notes instead. Do not load or populate a giant universal checklist.

- Model the feature's legitimate workflow before choosing a vulnerability label. Track competing explanations when needed; select one discriminating experiment at a time.
- Record exact actor/tenant, resource, action, lifecycle/auth state, control, observed result, and evidence. A failed request with no successful control does not establish a security boundary.
- Distinguish `not-tested`, `blocked`, `inconclusive`, `enforced-in-tested-case`, and `boundary-failure`. Do not silently convert unavailable access into a negative result.
- Park leads with a reason and reopen condition. Session expiry, tool failure, and missing objects require repair or a blocker, not a claim that the feature is secure.
- Recon completion requires usable output, not a zero exit code. Verify expected format, errors, counts, provenance, and representative content before downstream use. Partial/error output never replaces the last good baseline.

## 4. VALIDATION CONTRACT

Nothing is a validated finding without:

1. raw request/response, exact runtime evidence, or file:line/data-flow evidence;
2. one exact reproducible request/command/PoC;
3. attacker model + reachability;
4. scope/policy basis;
5. active falsification of the strongest benign/false-positive explanation.

A lead is not scored. Before reporting, reproduce from a clean-enough state and map every impact claim to evidence. Falsification may be done directly or delegated; no named reviewer is mandatory.

### Decision checkpoint — before closure, promotion, or summary

This applies to negative conclusions as well as findings. Preserve a compact reviewable record of the decisive experiment: exact tested boundary, valid control, request/result or runtime/source evidence, interpretation, and remaining gap. Link a real artifact and location; “session logs” without an accessible path is not evidence. Use `_template/EXPERIMENT.md` when useful, or equivalent existing records. Retain only policy-permitted, sanitized evidence; do not collect extra customer data to satisfy documentation. Save the permitted record before cleaning up test objects.

- Keep configuration declarations, observed responses, demonstrated execution, and verified effects distinct. Endpoint flags and HTTP success do not establish execution or mutation counts.
- A random/nonexistent ID returning 404, a disabled UI control, a WAF block, and a failed scan cannot establish the underlying authorization or application behavior. Record the narrow observation and mark the unresolved question blocked/inconclusive/not-tested as appropriate.
- `enforced-in-tested-case` needs a meaningful control showing that the valid resource/action is reachable and that the relevant boundary caused denial. It does not certify the endpoint or vulnerability class generally.
- Before a summary or closure, open the cited evidence, check that it supports the exact claim, and preserve uncertainty. Missing evidence means an unverified historical observation, not a fabricated proof or an automatic retest. Detailed checks: `.opencode/skills/core-identity/references/decision-checkpoint.md` relative to repo root.

## 5. TIME, STATE, NO-REPEAT

Time boxes are heuristics, not hard stops: prolonged recon without signal -> pivot; a candidate producing no new evidence -> park; a high-signal path that keeps producing evidence may continue. **Never invent elapsed time**—use timestamps when available or reason qualitatively.

Reuse existing evidence before collecting more. Do not repeat verified work merely because a skill reloads. Re-run only for changed scope, stale/changed behavior, a real evidence gap, or operator request. Merge/diff stateful outputs rather than overwriting blindly.

A temporary invalid state can still have lasting impact. Check actions and disclosure during the window before dismissing a rollback.

Keep `STATE.md` concise: target facts, auth state, tech stack, coverage, interesting surfaces, findings/leads, lessons, and next action—not a transcript. Reconcile it against current experiment IDs and evidence before handoff: supersede stale blockers, retain the history, and never convert “not observed in these tests” to “no bugs of this class.”

Tie recon counts to a named run and input/output snapshot (counts, timestamp, hash or immutable artifact). An empty scanner result alone does not prove a successful no-hit run; retain completion/error evidence. If output changes, append a new run/update the current pointer rather than silently reusing old counts.

Before expanding to another surface or recommending paid access/device/identity, name the unresolved question, prerequisite, discriminating test, and why it outranks reachable alternatives. A blocker applies to that experiment, not the entire target. Do not make purchases or create accounts from a recommendation alone.

## 6. CALIBRATION

- Evidence outranks scanner labels, model priors, skill examples, and theory.
- State uncertainty and pair it with the cheapest discriminating test.
- Do not inflate impact or force ATO/chains.
- **Do not generalize a control beyond the exact actor, auth/state, route/surface, and transition actually tested.** If cross-account enforcement, alternate paths/versions, or a broader ownership/binding claim was not tested, say so explicitly and scope the conclusion to the observed case.
- Do not suppress a novel hypothesis because no skill example matches it; skills are memory aids, not the boundary of possible bugs.
- Use current primary/authoritative sources for non-obvious or changeable technical/policy claims; community material is secondary.
