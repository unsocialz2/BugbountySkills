# Evaluate skill decisions

Use after meaningful hunting-workflow changes or recurring missed/false findings. These evaluations are local reasoning exercises, not authorization to test external targets.

Use `evaluation/cases.json` as raw case prompts. Give the evaluated model HUNT_RULES.md, the relevant router/reference, and one case's `prompt` only. Keep `evaluation/rubric.json` hidden until grading. Request its observation, hypothesis, verdict, evidence limits, next discriminating test, proposed coverage row, and one-sentence handoff summary. The summary must not strengthen the detailed verdict. Do not coach it with the expected answer. Run each case in fresh context and keep model/settings constant when comparing revisions.

After answering, grade against the matching rubric: pass only when all required distinctions hold and no listed failure occurs. Report per-case outcome, unsupported claims, missed boundaries, unnecessary repeated tests, and unresolved prerequisites. Measure time/request cost only when actually recorded. The case set includes missing evidence, misleading negative controls, webhook acceptance, stale inventory/blockers, and prerequisite prioritization. Validate case/rubric IDs and JSON separately; structural checks are not model behavior results.

Repeat with new held-out product scenarios before drawing broad conclusions; a perfect fixture score is not proof of real-world discovery performance.

Save evaluation outputs in an isolated temporary workspace or the active target's authorized local evaluation folder. Do not place secrets in fixtures. Repository script tests cover collection correctness separately and do not measure hunting ability.
