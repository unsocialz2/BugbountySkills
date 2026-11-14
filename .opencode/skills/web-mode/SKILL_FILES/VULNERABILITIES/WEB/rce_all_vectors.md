# Command and code execution — follow the actual interpreter boundary

## Boundary and discovery

Use for process launchers, converters, diagnostics, report expressions, template compilation and code-evaluating backends.
RCE is an outcome; begin with the specific parser or process boundary instead of injecting every input.
Map actor input → validation → string/argv/expression construction → interpreter → allowed output/effect.
Identify whether a shell exists. Shell punctuation passed as one argument is not shell execution.
Conversely, argument injection can be security-relevant without a shell if attacker-controlled options change tool behavior.
A library name, source function match or one delay does not prove natural external reach.

Record:

- protected function and legitimate actor capability;
- operating system, executable/interpreter and invocation mode if observed;
- input context: argv element, shell fragment, expression, source code, filename or config;
- allowed normal output and an inert marker observation channel;
- privilege and containment of the actual worker, separate from hypothetical host authority.

## Establish normal execution semantics

Capture a successful legitimate invocation with a researcher-owned input.
Use expected output to identify whether the app calls a process, a library or a remote service.
Preserve authoritative job status/result, not just an accepted-queue response.
If source is available, trace from a reachable route and include validation and argument construction.
A direct internal call in a lab establishes semantics only, until the supported external path is shown.

## Context-specific marker payloads

Use only a permitted controlled flow. A marker should not read unrelated files, open a shell session or persist changes.
The strings below need a known matching context; none is a universal RCE detector.

| Context | Harmless challenge | Control | Interpretation |
|---|---|---|---|
| POSIX shell fragment | `; printf AUDIT_MARKER` | Literal `AUDIT_MARKER` where normal input remains valid | Marker appears as process output only if the separator reaches a shell in executable position. |
| POSIX shell substitution | `$(printf AUDIT_MARKER)` | Literal `AUDIT_MARKER` | Compare shell expansion with raw argument delivery; quoting changes the question. |
| Python expression source in a lab | `'AUDIT_' + 'MARKER'` | `'AUDIT_LITERAL'` | Proves expression evaluation, not arbitrary OS execution. |
| JavaScript expression source in a lab | `['AUDIT','MARKER'].join('_')` | `'AUDIT_LITERAL'` | Trace whether the expression is evaluated server-side or in the browser. |
| Argument-taking tool | One documented harmless option, such as its documented version flag, only if safe for that tool | Normal positional argument and `--` termination where supported | Different tool behavior may prove option injection; does not require shell metacharacters. |
| Asynchronous converter | Distinct normal owned filenames/labels consumed by the worker | Same valid fixture and stable label | Establish invocation and result channel before testing an interpreter-specific boundary. |

Do not use shell syntax against `execFile`/`spawn` as if they always invoke a shell.
Do not assume `Runtime.exec` or `ProcessBuilder` interprets POSIX punctuation without an explicit shell.
For Windows, establish `cmd.exe`, PowerShell or direct process semantics separately; POSIX payloads are not portable.
`compile`, `__import__` or an interpreter API name is not sufficient evidence that attacker input executes.

## Discriminating experiment sequence

1. Establish the source field and normal consumer with an inert token.
2. Identify one parser assumption: literal argument versus option, expression versus text, shell versus direct executable.
3. Choose a paired marker/control that only the suspected interpretation should change.
4. Repeat with the same valid job/resources and capture authoritative output.
5. Test a competing account such as reflected input, client-side expression handling, cached output or a different worker.
6. Only after the first interpretation is established, ask whether it crosses an intended authority boundary.

For a blind channel, use an approved controlled marker endpoint only when the concrete interpreter path supports it.
An HTTP callback can also be a renderer fetch; prove attribution instead of labeling every OOB request code execution.
A timing-only hypothesis needs repeated interleaved controls and bounded delay, not a fixed sleep list.
Avoid costly loops or memory pressure to prove evaluation.

## Evidence and capability limits

Preserve original valid input, exact altered bytes, process/route dataflow and matching semantic output.
State the required role, victim interaction, executable rights and isolation actually observed.
An application worker executing as an unprivileged sandbox account does not prove host compromise.
A system command returning an inert marker may establish execution without reading system identities or secrets.
A non-zero exit code does not erase an earlier proven side effect, but an exception alone proves nothing.
Keep command injection, code injection, argument injection, SSTI and deserialization origins distinct in the report.
Use the corresponding guide for each origin instead of stacking hypothetical chains.

## Scope, stop and reopen

Run local fixture experiments before adapting context-sensitive quoting to an allowed target.
Do not install persistence, upload webshells, modify interpreters or collect customer data for demonstration.
If only one legitimate filename/label is echoed, retain a lead rather than declaring execution.
Close a tested source when the app preserves it as data and the suspected interpreter path is disproven.
Mark missing worker access/output or unknown invocation mode inconclusive.
Reopen for observed shell=true, dynamic expression compilation, unsafe option mapping or another consumer.

## References and freshness

Reviewed 2026-11-13. Probe validity depends on the interpreter and invocation mode; no universal bypass is claimed.

- [PortSwigger OS command injection](https://portswigger.net/web-security/os-command-injection) — command contexts, visible/blind channels and minimal detection.
- [OWASP command injection defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html) — argument injection and separation of data from commands.
- [Node child_process](https://nodejs.org/api/child_process.html) — shell versus direct-process APIs and their options; verify the installed runtime.

For templates, deserialization and unsafe file processing, load the exact owning guide rather than treating every mechanism as a shell.
