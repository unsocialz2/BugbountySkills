# NoSQL injection — distinguish operator authority from value handling

## Boundary and discovery

Use for JSON/document queries, search filters, nested form parameters and code-built database expressions.
NoSQL is a family of systems, not a single injection grammar.
Identify the actual database/client/query builder before adapting operators or string syntax.
Separate query operator injection, string/code expression injection, type confusion and authorization omissions.
A request containing `$ne` does not prove that the server forwards it as an operator.
A rich filter API may intentionally support operators while correctly limiting fields and tenant scope.

Map actor input → HTTP parser/type → validation → query construction → database operation → response.
Record string versus object versus array handling, reserved-key policy and expected result visibility.
Do not assume JSON and URL-encoded nested input reach the same shape.
Use synthetic records and ordinary searches before any authentication-related test.

## Normal control and fixture

Create two owned records with titles `AUDIT_ALPHA` and `AUDIT_BETA` through a normal permitted flow.
Capture exact-match searches returning each and a guaranteed nonmatching marker.
If the feature should accept only a scalar string, prove that documented contract with a successful request.
If it exposes a filter object, identify authorized fields/operators and actor scoping separately.
Keep tenant, collation, pagination and search index state stable across paired probes.
A generic 500 on an object where a string is expected remains a parsing/validation lead.

## Context-specific payloads

These use MongoDB-style query operators only when the application actually forwards that model.
The outer request shape is illustrative; copy the real normal request instead of inventing a route.

```json
{"title":{"$eq":"AUDIT_ALPHA"}}
```

```json
{"title":{"$in":["AUDIT_ALPHA","AUDIT_BETA"]}}
```

| Question | Challenge | Paired control | Meaningful result |
|---|---|---|---|
| Are scalars replaced by executable operators? | `{"title":{"$eq":"AUDIT_ALPHA"}}` | Scalar title and `$eq` nonmatching marker | Operator semantics matter only if forbidden by the field contract or crossed data policy. |
| Does negation broaden a protected query? | `{"title":{"$ne":"AUDIT_ALPHA"}}` | `$eq` and ordinary B title query | Controlled results show query change; tenant/private records must remain inaccessible. |
| Is multi-value input expanded? | Small `$in` array of two owned marker values | One-element array and scalar value | Distinguish intended multi-search from unauthorized type/operator handling. |
| Is regex interpreted? | `{"title":{"$regex":"^AUDIT_ALPHA$"}}` | Exact literal and `^AUDIT_Z$` | Bounded predictable pattern; no catastrophic regex or unknown-secret extraction. |
| Do nested form parsers alter type? | `title[$eq]=AUDIT_ALPHA` only for an observed bracket parser | Ordinary scalar form body | Compare parsed shape; literal treatment is not a bypass. |
| Does actor scope remain independent? | Same valid query as controlled A versus B | Each actor's own successful result | Unauthorized dataset exposure proves the policy boundary, not just operator support. |
| Do missing/null/array values alter authority? | One schema-relevant type change on a read-only owned query | Valid scalar, explicit missing-result control | Distinguish coercion/default behavior from a query that drops a required security condition. |

## String/code contexts

Some applications historically assembled JavaScript expressions, but operators do not imply a JavaScript evaluator.
Do not introduce `$where` or sleep syntax by default; support and server policy vary by version.
If source proves an expression consumer, construct a harmless matched true/false condition valid in that exact language.
Prove server-side evaluation independently from browser expressions and from intended search syntax.
Use a boolean observation on known synthetic fields; do not enumerate password/token values.
An unused field or unknown operator error does not establish underlying code execution.

## Authorization and query composition

Ask whether tenant/owner constraints are fixed server predicates or client-overridable keys.
Compare AND composition with replacement/merge semantics only where source or valid traffic supports the question.
Do not overwrite the normal actor context in a local fixture and claim the external application permits it.
An object-type mismatch can cause fail-open defaults; verify returned record identities and their policy.
Index lag, case folding, stemming and null/missing semantics are plausible benign explanations.
Use count/list/get consistency to isolate a query-policy fault from pagination artifacts.

## Evidence and scoped conclusions

Save allowed scalar/filter controls, exact altered type/operator, existing fixture identities and result contents.
Show which operator/condition was interpreted and what unauthorized data/action it enabled.
If only a parser error or operator support is proved, keep it a lead or intended behavior.
A database driver's use does not mean every route shares the same query construction.
Read-only inference and mutation capabilities must be demonstrated separately.
Capture temporary disclosure even when later state repairs; do not require a lasting write for a read flaw.

Close only a tested field/representation when scalar/schema enforcement or safe query composition holds.
Mark unknown DB/parser, invalid controls and unstable search results inconclusive.
Reopen for another representation, exposed filter grammar, raw-expression consumer or alternate query builder.

## References and freshness

Reviewed 2026-11-13. MongoDB syntax examples are conditional, not claims about all document databases.

- [PortSwigger NoSQL injection](https://portswigger.net/web-security/nosql-injection) — operator versus syntax injection and controlled observations.
- [MongoDB query operators](https://www.mongodb.com/docs/manual/reference/operator/query/) — actual operator/type semantics; select the deployed server version.
- [OWASP NoSQL security](https://cheatsheetseries.owasp.org/cheatsheets/NoSQL_Security_Cheat_Sheet.html) — field/operator validation, query construction and server-side scripting restrictions.

Use `orm_filter_inference.md` when an intentionally supported filter leaks forbidden field predicates without syntax injection.
