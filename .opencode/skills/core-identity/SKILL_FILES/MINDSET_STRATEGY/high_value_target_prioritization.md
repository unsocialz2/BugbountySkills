# Prioritize questions by evidence and access

Rank reachable features, not vulnerability names or noisy response headers.

Consider together:
- attacker-accessible roles and test resources available now;
- value controlled by the feature: data, authority, money, trust, or entitlements;
- a concrete boundary crossing, recent change, inconsistent representation, or unexplained behavior;
- cost of establishing a legitimate baseline and observing the actual outcome;
- previous tests and what a new experiment can distinguish.

Choose the question with the best supported combination; avoid invented numerical probabilities. A high-impact feature with no usable access may be blocked while a modest, accessible feature offers a productive next test.

Before broad fuzzing, use the product normally and capture the relevant successful flow. Hidden parameters matter when schema, source, traffic, or observed behavior suggests the backend consumes them. A stack trace, 500, long cookie list, or exposed schema is a lead, not a reliable ranking of bug richness.

Keep a short ranked hypothesis queue when there are competing leads. Record the reason for prioritization and the cheapest discriminating test. Execute one experiment at a time unless independent work actually benefits from concurrency. Re-rank on new evidence, not after every failed request.

When progress stalls, inspect a different actor, lifecycle transition, or representation of the same feature before automatically switching targets or spraying payloads.
