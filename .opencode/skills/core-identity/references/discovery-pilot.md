# Small controlled discovery pilot

Use when deciding whether a strategic skill revision improves actual discovery. The runnable local harness below implements this protocol. A prepared pilot or its self-tests are not an executed model result or authorization to test external systems.

## Runnable local pilot

The skill includes `scripts/discovery_lab.py` and independently authored synthetic fixtures in `scripts/discovery_lab_app.py`, both relative to the core-identity skill root. Python's standard library and local Git are sufficient; no provider SDK, API key, external target, purchase or real account is needed. The fixture source and oracle must not be given to the candidate. Once an evaluator knows these fixtures, treat them as regression tests and use freshly authored cases for claims about general discovery.

From a coordinator shell, choose two distinct local skill commits, a NEW output directory (normally `.lab-runs/<new-id>` under the repo, never a live target workspace), and declare the intended model/runtime/settings. Unknown provenance must remain labelled unknown.

```bash
python3 "${CORE_SKILL:?}/scripts/discovery_lab.py" prepare \
  --repo "${REPO_ROOT:?}" --output "${NEW_PILOT_ROOT:?}" \
  --baseline "${BASELINE_REF:?}" --candidate "${CANDIDATE_REF:?}" \
  --max-actions 24 --max-seconds 600 \
  --model-label "${MODEL_LABEL:?}" --runtime-label "${RUNTIME_LABEL:?}" \
  --settings-label "${SETTINGS_LABEL:?}"
python3 "$CORE_SKILL/scripts/discovery_lab.py" serve --root "$NEW_PILOT_ROOT"
```

The server binds only to `127.0.0.1`, chooses a local port, and writes coordinator dispatch paths to `public/index.json`. Give each fresh evaluated session only ONE run's `brief.json` and its allowed workspace. Do not give the index, private plan, snapshot/source files, app tests, prior answers or grades. Candidate instructions and references are delivered through that run's `/context`, `/skills/<id>` and `/files/<snapshot-relative path>` endpoints. App actions use the normal API described by `/context`, with two supplied researcher-owned synthetic account tokens. No other target or run is permitted.

The evaluator submits one `POST /report` with `verdict` (`finding`, `no-finding` or `blocked`), `summary`, and actual `evidence_ids`. The report endpoint acknowledges receipt without revealing the oracle or score. `/context` starts the run clock; application calls count toward the action budget. Instruction reads are separately recorded. Reports remain possible after budget exhaustion. The private server trace records actual calls and synthetic responses, skill/reference delivery events, measured elapsed time and chained hashes. It also records the supplied **fake lab** authorization headers so the grader can replay the actions; never put real credentials or production traffic into this harness.

```bash
python3 "$CORE_SKILL/scripts/discovery_lab.py" grade \
  --root "$NEW_PILOT_ROOT" --output "$NEW_PILOT_ROOT/grade.json"
```

The grader independently replays recorded application actions on fresh matching fixtures and checks log/snapshot/harness integrity. A finding requires cited successful-control and actual violation events. A repaired negative requires cited control and relevant boundary evidence; an untouched case is not a supported negative. It reports misses, unsupported findings, blocked/incomplete runs, load deliveries and cost separately. A malformed/fabricated citation does not earn finding credit. This is oracle-assisted local grading, not a replacement for human policy/root-cause review.

The server refuses a restart that would silently reset an observed app; prepare a new pilot to reset. It stops on Ctrl-C, its bounded lifetime, or when the coordinator creates the local `private/STOP` file. Keep raw runs ignored/private; do not commit them or expose the loopback server through a tunnel. Blinding is a procedural evaluation rule, **not an OS-enforced sandbox**. Model/runtime labels are coordinator declarations, and a skill delivered over HTTP is not proof the model obeyed it. This harness does not instrument production OpenCode sessions.

## Freeze and hide the answer

Start with two independently authored local synthetic workflows. Give each a vulnerable and repaired twin: four application cases. Run both frozen skill versions on each case in fresh sessions: eight runs. This is a small go/no-go pilot, not a general performance estimate. If either arm already knows the fixtures, use new independently authored cases.

The evaluated agent receives ordinary product access, controlled accounts/data, tools and an explicit local-only task. Hide the defect location, case polarity, twin relationship and scoring key. The author prepares the oracle after versions are frozen; do not expose a vulnerable source tree or test file in the agent's context. Include unknown/benign behavior and at least one meaningful unannounced boundary in each positive case. Avoid names that reveal the answer.

Keep model/settings/runtime/tools, initial state and declared action/time budget comparable. Randomize case order and reset accounts/objects/state between runs. Capture actual loads and application actions via runtime exports; see execution-provenance.md. Budget values belong to this experiment, not every live hunt.

## Grade execution, not promised tests

A blinded grader compares saved tool actions and semantic results against the hidden oracle and independently reproduces claimed findings. A plan, status code or polished report alone earns no discovery credit.

Record for each arm/case:
- whether the hidden defect was found with a valid control and minimal reproducible semantic proof;
- a missed positive or false finding on a repaired twin;
- whether the relevant benign boundary was actually exercised or simply left untested;
- tool actions and measured time to supported result or budget exhaustion;
- reason for blockage: genuine access, invalid control, tool/harness failure, missing hypothesis, or premature closure.

Predeclare session stop rules: reproducible supported result, budget exhaustion or a condition requiring intervention. Do not give one arm hints/extensions. Harness failures invalidate the affected paired comparison; repair and rerun both arms instead of scoring it as a skill failure. Actions outside the local task invalidate that run.

Do not advance a revision merely for fewer reports or longer notes. Compare discovered positives, false findings, valid controls and cost; record paired regressions explicitly. A tie is no demonstrated gain. A favorable pilot supports only that narrow result; repeat with new cases before generalizing to live discovery or rewards.

Keep fixture sources, oracle, raw outputs and grading outside the production target workspaces and outside the candidate prompts. Label design/structural checks, reasoning-fixture runs, and executed discovery-pilot results separately. Never invent eight-run completion from a written protocol.
