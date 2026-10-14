# BugbountySkills — OpenCode project contract

This repository provides shared OpenCode rules and skills. Real target data lives under ignored local workspaces:

```text
<repo>/targets/<target>/
```

Example:

```text
<repo>/targets/vinted/
  scope.txt          # or scope/program CSV
  rules.txt
  STATE.md           # created/updated as work progresses
  recon_data/
  findings.md
  lessons.md
  RECON_LOG.md
```

Open OpenCode from inside the target folder. `.opencode/` at repository root supplies the shared skills/rules.

## Target bootstrap

At session start, follow `.opencode/rules/HUNT_RULES.md §0`:

1. infer the active target from `targets/<target>/`;
2. read `rules.txt` first;
3. load `scope.txt` or the available scope CSV;
4. inspect existing state/recon/findings before doing new work;
5. keep all new artifacts inside the active target folder.

`targets/` is gitignored. Never commit target recon, credentials, loot, or program data to this repository.

## Skill selection

The operator does **not** need to say `WEB MODE`, `API MODE`, etc. Those phrases remain valid shortcuts, but the model should normally choose the smallest relevant skill itself.

| Need | Primary skill |
|---|---|
| recon / asset discovery / JS-wayback / DNS | `recon-mode` |
| normal web application/session/form testing | `web-mode` |
| REST, GraphQL, gRPC, API authorization | `api-mode` |
| AWS/GCP/Azure, S3, Kubernetes, Docker, network infra | `infra-mode` |
| Android/iOS | `mobile-mode` |
| source code / repository review | `scr-mode` |
| LLM/RAG/agent/tool security | `llm-mode` |
| payload lookup | `payloads` |
| minimal PoC / chaining after a concrete candidate exists | `exploit-mode` |
| reporting / CVSS / platform-ready writeup | `reporting-mode` |
| platform/program intelligence | `platform-intel-mode` |
| scripts, pipelines, monitoring, automation | `automation-mode` |
| general hunting strategy/state | `core-identity` |

Load the top-level `SKILL.md` first, then only the exact deep-dive file needed. Avoid loading giant references or overlapping modes unless evidence genuinely crosses domains.

## Model autonomy

There is no fixed lead/worker/reviewer architecture.

The current model decides how to solve the task. It may work directly or delegate a narrow subtask to another model/subagent when that materially improves speed, context isolation, parallelism, or independent falsification. No specific model, role name, or hierarchy is required.

If delegation is used:
- pass only the relevant target context and scope/rules;
- define one narrow deliverable;
- tell the subagent what work is already done so it does not repeat it;
- merge and sanity-check the result before acting on it.

## State isolation

- Never copy `STATE.md`, findings, recon artifacts, or credentials across target folders.
- Program `rules.txt` + explicit scope files override generic skill guidance.
- Never infer that sibling/acquired/brand-related assets are testable until scope confirms them.
- Reuse existing artifacts and diff/merge rather than rerunning work blindly.

## Shared environment

`ENV.md` contains host/device notes and pinned local tooling facts. It is **environment evidence, not eternal truth**. Check its verification date and confirm actual installed/runtime versions when the exact version matters.

Default operator stack: Kali + Burp Pro + optional VPS. Paid APIs are optional; prefer a free path when practical.
