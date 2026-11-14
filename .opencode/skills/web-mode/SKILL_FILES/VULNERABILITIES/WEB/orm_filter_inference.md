# ORM and filter inference — unauthorized predicates can disclose hidden data

## Boundary and discovery

Use for rich search, filter builders, OData, nested relationship queries, reporting and generic ORM-backed endpoints.
Parameterized SQL does not prevent an application from exposing unauthorized field predicates.
A field can remain absent from output yet leak through result membership, count, order or errors.
The boundary is *which fields and relationships the actor may query*, not just which fields the serializer returns.
Do not call every documented filter feature a vulnerability.

Map HTTP input → filter grammar/type coercion → ORM paths/joins → actor/tenant scoping → observable results.
Identify allowed fields, relations and operators from real client traffic, schema or source.
Pay attention to a model exposed only indirectly through an authorized parent object.
Keep ORM query-language injection distinct from raw SQL injection and from ordinary IDOR.

## Controlled dataset and normal observations

Use two controlled actors and synthetic records with different known private markers.
A useful fixture is a public article owned by B with private metadata `AUDIT_PRIVATE_B`, readable only by B.
Actor A can legitimately list the public article but must not learn its private metadata.
First prove A's normal public visibility and B's legitimate private read.
Then build a predicate against that synthetic private value without selecting the private field in output.
The test does not require reconstructing unknown secrets character by character.

## Payloads tied to actual filter syntax

These are candidate grammars for an application that demonstrably forwards them.
They are not valid URL parameters or JSON bodies for every Django/Prisma/OData application.
Use exact model names/relations from the controlled feature and encode transport characters normally.

| Observed grammar | Challenge | Paired control | What would be a leak? |
|---|---|---|---|
| Django lookup names exposed by app | `owner__private_note__startswith=AUDIT_PRIVATE_B` | Same path with `AUDIT_PRIVATE_Z` | Public result/count follows a field A cannot otherwise inspect. |
| Prisma-like structured filter accepted by app | `{"owner":{"privateNote":{"startsWith":"AUDIT_PRIVATE_B"}}}` | Same predicate with the mismatching synthetic prefix | Only meaningful if schema/relation cardinality makes this input valid. |
| OData filter exposed by app | `$filter=CreatedBy/PrivateNote eq 'AUDIT_PRIVATE_B'` | Replace B marker with Z marker | Forbidden predicate influences result while field itself is hidden. |
| Flat filter DSL | A documented field name replaced by one known synthetic private field, keeping operator/value type valid | Allowed field and nonexistent field controls | Different errors alone are a schema lead; membership/count oracle is stronger. |
| Relation traversal | Predicate on controlled parent's private related field | Same parent and an allowed public related field | Query access crosses the relationship policy, not simply the top-level serializer. |
| Sort/count representation | Same forbidden predicate with observed count endpoint or allowed sort grammar | Ordinary page/list response for matching owned fixtures | Hidden data affects an attacker-visible side channel beyond permitted semantics. |

## Hypothesis-driven expansion

1. Find one valid supported predicate on a public owned field; establish operator semantics.
2. Compare a known nonexistent field to understand error masking.
3. Select one synthetic private field revealed through your own legitimate account/schema, not guessed customer secrets.
4. Keep result visibility constant while changing only the private predicate.
5. Alternate true and false synthetic values, checking count, membership or ordering.
6. Repeat through an observed relation/alternate representation only if it changes the same policy decision.

Filtering a private value on a record already fully readable to A may gain no new capability.
If A is legitimately allowed to search that field but not display it, product policy must decide the intended inference guarantee.
Do not manufacture an invisible secret by making an arbitrary display field hidden in a local mock.
An intentionally public filter and an access-controlled field require different authority evidence.

## Parsers, operators and relational subtleties

Filter allowlists can apply to textual names before another parser expands aliases or relationships.
A parser differential is useful only if it reaches a forbidden field/operator after normalization.
Do not assume string comparisons are case-sensitive or lexicographic: collation and locale matter.
Null/missing values, arrays and existential relation filters can produce unexpected but legitimate matches.
Pagination and search relevance may obscure result membership; use controlled counts or direct fixture identity when available.
Parameterization can hold while the privacy boundary fails; report the actual field-policy problem.
A valid query with expensive joins is not justification to perform an unbounded resource-consumption test.

## Evidence and falsification

Save the actor/record visibility matrix, source of field knowledge and expected private-field policy.
Show public data available to A, private value visible only to B, and matched predicates changing A's observable result.
Demonstrate the oracle on a tiny known synthetic value; do not dump real private attributes.
Test public field equivalence, intended search authority, inconsistent pagination and stale indexes as benign accounts.
Keep raw query text, exact encoding, result identities/counts and independent B verification.
Field-name errors alone remain inventory unless sensitive schema exposure itself is independently eligible.

Close the tested predicate/path when a field/operator policy blocks it consistently with successful allowed controls.
Mark unknown field existence, wrong relation shape or search-index lag inconclusive.
Reopen for a discovered relation path, alternate serializer, count endpoint or different filter parser.

## References and freshness

Reviewed 2026-11-13. Examples must be adapted to the application's exposed grammar and deployed ORM.

- [PortSwigger 2025 research selection](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) — identifies ORM leaks as a research direction, not a universal payload catalog.
- [elttam original ORM leak research](https://www.elttam.com/blog/leaking-more-than-you-joined-for/) — relation and predicate-based disclosure across ORM/filter implementations.
- [Django QuerySet reference](https://docs.djangoproject.com/en/stable/ref/models/querysets/) — lookup paths/operator/collation semantics; verify the deployed version and HTTP mapping.

Use `sqli_all_types.md` if a filter escapes into raw SQL syntax; use `idor_bola_bfla.md` if the result exposes unauthorized objects directly.
