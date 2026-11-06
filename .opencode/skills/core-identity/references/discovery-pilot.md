# Small controlled discovery pilot

Use when deciding whether a strategic skill revision improves actual discovery. This protocol is not an executed result or authorization to test external systems.

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
