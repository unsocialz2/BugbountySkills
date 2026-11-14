# SQL injection — prove query interpretation before expanding access

## Boundary and discovery

Use for searches, reports, filters, sorting, exports, stored preferences and other features that construct SQL.
A matching database banner, apostrophe error or slow response is a lead, not SQL injection.
Start with a valid normal feature, even when no injection primitive is known yet.
Follow attacker input through HTTP decoding, validation, ORM/query builder, SQL execution and result rendering.
Identify whether the input occupies a string value, numeric value, identifier, list, sort direction or expression.
Parameterization protects values; dynamic identifiers need a separate policy and are not automatically vulnerable.
Do not change a read request into a mutation merely to obtain a stronger effect.

Record:

- actor and authorized dataset, including one researcher-owned result with a unique marker;
- exact endpoint/method/body, parser/content type, normal result and independent readback;
- query context and DB family as observed, or explicitly unknown;
- whether the observation is content, error, time, stored processing or an OOB event;
- cache, search ranking, pagination and WAF behavior that could imitate a result difference.

## Establish the control

1. Create two owned search records, `AUDIT_ALPHA` and `AUDIT_BETA`, through normal product flows if allowed.
2. Capture successful queries returning each and one returning neither.
3. Repeat a small interleaved sequence to measure ordinary result/timing variance.
4. Record an untouched request, a syntax-only perturbation and a matched logical pair separately.
5. Keep tenant/session/locale/pagination constant; remove stale browser session ambiguity.

The purpose is to distinguish database expression evaluation from the application's intended search language.
A product that deliberately supports SQL for authorized analytics has a different boundary: constrain its data, tenant and execution capabilities.

## Context-specific payloads and experiments

These are conditional probes, not a sequence to spray. Adapt quote/comment syntax only after the context supports it.
Use an owned read-only dataset. SQL text below is the parameter value, before normal HTTP encoding.

| Question | Positive/challenge | Matched control | What would distinguish the hypotheses? |
|---|---|---|---|
| Numeric expression evaluated? | `1 AND 1=1` | `1 AND 1=2` | Existing owned id 1 survives only the true branch; type errors alone are inconclusive. |
| Single-quoted string breakout? | `AUDIT_ALPHA' AND 'a'='a'-- ` | `AUDIT_ALPHA' AND 'a'='b'-- ` | Result toggles with predicate, not with the mere apostrophe. Requires a compatible string context/comment. |
| Inline expression in a lab query? | `SELECT CASE WHEN 2=2 THEN 'AUDIT_YES' ELSE 'AUDIT_NO' END` | Change `2=2` to `2=3` | Confirms the local oracle, not a remote injection point. |
| User-selected sort is an expression? | Two valid documented sort keys first; then a harmless DB-specific conditional expression if evidence supports raw SQL | Same expression with reversed condition | Owned records reorder as predicted, without changing dataset membership. |
| Error is condition-dependent? | A DB-specific expression that is valid in one branch and invalid in the other | Same structure, condition reversed | Error classification follows the condition over interleaved trials; generic 500/WAF signatures do not count. |
| Stored data reaches a later query? | Save `AUDIT_ALPHA'` in one owned preference consumed by an export | Save an ordinary marker through the same flow | Identify the later consumer and then use a matched predicate there; persistence alone proves no injection. |
| Representation chooses a different query path? | Equivalent documented JSON/form values | Original content type and equivalent body | Same authorized operation behaves differently because of query construction, not malformed serialization. |

Do not use `OR pg_sleep(...)` as a generic PostgreSQL boolean: `pg_sleep` returns void.
Do not assume a DB evaluates conditional branches exactly as a programming language does; optimizer behavior matters.
If timing is necessary, select a source-backed short delay valid in that precise expression context and obey request budgets.
Prefer content/boolean proof when it answers the same question with less load.

## Blind and statistical reasoning

Define the signal before collecting a timing sample: response category, owned row presence, error class or elapsed time.
Interleave challenge/control order and retain raw samples, not only averages.
Compare distributions and stability; a single large latency is not an oracle.
Check rate limiting, backend retries and cache misses with ordinary marker controls.
Avoid unbounded regex, heavy joins or benchmark loops as detection techniques.
For OOB, use a unique token and distinguish SQL execution from link scanners or log processors.
An outbound DNS event does not establish file read, credential access or command execution.

## Expand from the demonstrated capability

Once interpretation is proved, ask the nearest security question: unauthorized row visibility, tenant filter removal or protected write authority.
Use known synthetic records rather than enumerating schema or extracting real user data.
A query-construction error that cannot cross the intended data boundary may need a narrower report.
A database role may be read-only, sandboxed or restricted to one tenant; do not inherit a universal database-compromise claim.
Second-order input can execute only later; preserve the original write and exact consuming action.
An eventual rollback does not erase a read or completed action during the vulnerable window.

## Falsification and evidence

Save the successful normal action, matched pair, full raw responses and relevant independent state.
Record DB/context confidence, exact encoding, repeat count and noise controls.
Attempt the strongest benign account: documented query language, validation branch, search semantics, cache variation or WAF delay.
Separate injection demonstrated, protected data/action demonstrated, policy eligibility and submission status.
Do not assign a score from the class name.

Close only the exact tested context if the paired input is treated as literal data or rejected before query construction.
Keep an invalid-control or unexplained-timing result inconclusive.
Reopen for an observed second consumer, raw query fragment, alternate representation or changed deployment.
Do not label the whole endpoint or database safe after one protected parameter.

## References and freshness

Reviewed 2026-11-13. These support mechanisms; no claim that every DB/context or remote target was executed here.

- [PortSwigger SQL injection](https://portswigger.net/web-security/sql-injection) — contextual detection, blind channels and second-order processing.
- [OWASP SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) — value parameterization versus identifier allowlists and query construction.
- [PostgreSQL conditional expressions](https://www.postgresql.org/docs/current/functions-conditional.html) — context-dependent CASE behavior and evaluation caveats; consult the deployed major version.

Use `orm_filter_inference.md` for unauthorized filtering through otherwise parameterized ORM queries.
Use `nosql_injection.md` for non-SQL operator/type semantics.
