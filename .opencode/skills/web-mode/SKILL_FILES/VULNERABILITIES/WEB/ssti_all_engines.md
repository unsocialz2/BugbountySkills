# Server-side template injection — identify evaluation, context and authority

## Boundary and discovery

Use for customizable emails, reports, CMS fragments, preview fields, error pages and values later rendered as templates.
Distinguish template *source* from template *data*: rendering a name containing braces as text is not injection.
Authorized template editing may be intended; investigate data access, sandbox guarantees and lower-privilege reach.
Template evaluation is not automatically command execution.
The engine, version, environment objects, helpers, loader and sandbox decide the available capability.

Map actor → stored/immediate input → template assembly → engine → output surface.
Separate server evaluation from client templating, browser DOM rendering and unrelated arithmetic formatting.
Use a unique marker with a harmless expression; do not begin with environment dumps or executable gadget chains.
One engine failing a probe is not evidence that another engine or another template context is safe.

## Normal control

1. Save or preview an ordinary marker such as `AUDIT_MARKER_4821` in the normal workflow.
2. Confirm who can author it and which role renders it.
3. Preserve a baseline with the same syntax treated as data where the product offers that option.
4. Capture immediate response and later reader/export/email preview separately.
5. Fix the exact version/config only when source or runtime evidence establishes it; do not fingerprint by one arithmetic result.

## Context-specific harmless payloads

These syntax probes are candidates for their named engines, not interchangeable detection strings.
A template rendered as a legitimate user feature may evaluate them by design.

| Engine/context | Probe | Matched control | Expected interpretation if evaluated |
|---|---|---|---|
| Jinja2/Twig expression source | `AUDIT_{{17*19}}` | `AUDIT_{{17*18}}` | Marker tracks 323 versus 306, not reflected source text. |
| FreeMarker interpolation | `AUDIT_${17*19}` | `AUDIT_${17*18}` | Same arithmetic distinction within valid FreeMarker expression context. |
| ERB/EJS output expression | `AUDIT_<%= 17*19 %>` | `AUDIT_<%= 17*18 %>` | Output contains calculated value; underlying Ruby/JS context still matters. |
| Pug full text-node template | `p AUDIT_#{17*19}` | `p AUDIT_#{17*18}` | Full local Pug template source; adapt to the actual text context. `{{...}}` is not a generic Pug arithmetic detector. |
| Razor expression | `AUDIT_@(17*19)` | `AUDIT_@(17*18)` | Requires source compilation in Razor context; not an arbitrary field parse rule. |
| Velocity statement/template | `#set($audit = 17 * 19)$audit` | Change 19 to 18 | VTL math requires its supported syntax and interpolation context. |
| Liquid filter expression | `{{ 17 | times: 19 }}` | `{{ 17 | times: 18 }}` | Liquid filter semantics; do not assume `{{17*19}}` is portable. |
| Handlebars helper/path model | `{{auditMarker}}` with a supplied harmless lab context | Missing key or a different supplied context | Context resolution, not arbitrary infix arithmetic. A custom math helper requires actual evidence. |

For unknown syntax, a short delimiter probe can produce a lead, followed by coherent engine-specific pairs.
Do not concatenate all syntaxes and interpret the whole result as an engine fingerprint.
Preserve escaping and nesting context: text source, expression source and quoted attribute are different questions.

## Experiments after an evaluation lead

| Hypothesis | Minimal challenge | Control / competing explanation |
|---|---|---|
| Server re-renders user data as template source | Change a value from marker to expression through the same normal flow | Compare original raw input, returned source and final rendered output; client arithmetic can imitate evaluation. |
| Stored author reaches another user's renderer | Own author/reader identities with a harmless calculated marker | Verify the second actor sees the same rendered object without copying it into their own template editor. |
| Unauthorized context data is available | Request one documented synthetic context variable outside the actor's allowed slice | Compare allowed variable, nonexistent variable and differently owned fixture; do not dump `config` or globals. |
| Sandbox restricts an operation | Use a documented harmless forbidden attribute/operation only in an authorized lab | A security exception establishes that operation was blocked, not universal sandbox safety. |
| Blind engine produces conditional errors | Choose a harmless valid expression and a conditionally invalid expression supported by the confirmed engine | Interleave valid/invalid conditions and a syntax-only failure; avoid generic 500 attribution. |
| A second rendering pass changes trust | Compare saved original content with preview/export/read path | Valid storage and escaping at the first pass do not prove safety of a later template compilation. |

## Blind/error-based reasoning

Define the observable error category from a stable normal control.
A parser error establishes syntax recognition at most; controlled conditional behavior is stronger.
If the app always returns the same wrapper, inspect permitted job status or synthetic output rather than inventing a missing callback.
Avoid intentional CPU/memory expansion, unbounded output and sleep loops as discovery defaults.
The original successful-errors research is useful for constructing engine-valid predicates; do not transplant its payloads without the matching interpreter context.

## Capability and impact

Keep evaluation, unauthorized context access, file inclusion and code execution as distinct claims.
Sandboxed custom templates are not inherently a bug when the documented authority is enforced.
A helper available only to a tenant administrator does not grant an unprivileged attacker the same reach.
If code execution genuinely remains necessary and authorized, prove only an inert marker in the actual natural entry path.
Do not add a hypothetical RCE chain because arithmetic returned a result.

## Evidence, stop and reopen

Save author/reader states, exact input bytes, calculated pair, transformation path and affected origin/output.
Test reflection, client evaluation, legitimate template editing and stale/cached preview as benign alternatives.
Close a candidate only for the inspected field and consumer when source stays inert or the intended sandbox/data boundary holds.
Mark engine ambiguity and missing downstream rendering blocked/inconclusive.
Reopen for an observed second pass, different template loader/helper, role-specific reader or deployment change.

## References and freshness

Reviewed 2026-11-13. Syntax is source-backed; target execution and all engine versions are not asserted.

- [PortSwigger SSTI](https://portswigger.net/web-security/server-side-template-injection) — context-led detection, engine identification and reach.
- [Jinja sandbox](https://jinja.palletsprojects.com/en/stable/sandbox/) — attribute/operator controls and limits of sandbox assumptions.
- [Handlebars expressions](https://handlebarsjs.com/guide/expressions.html) — path/helper evaluation and why generic arithmetic is unsuitable.
- [Successful Errors original research](https://github.com/vladko312/Research_Successful_Errors/blob/main/README.md) — error-based and conditional-error blind channels; match the actual language before adapting.

Engine syntax lookup when selecting a row (these do not prove the target uses that engine):

- [Pug interpolation](https://pugjs.org/language/interpolation.html) — buffered expression interpolation.
- [Liquid times](https://shopify.github.io/liquid/filters/times/) — multiplication through a named filter.
- [Velocity VTL user guide](https://velocity.apache.org/engine/2.4/user-guide.html) — set directives and arithmetic.
- [FreeMarker expressions](https://freemarker.apache.org/docs/dgui_template_exp.html) — arithmetic and conditional expression rules.
- [Twig templates](https://twig.symfony.com/doc/3.x/templates.html) — expression syntax and operators.
- [EJS](https://ejs.co/) — JavaScript output expressions and rendering model.
- [Razor syntax](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/razor?view=aspnetcore-10.0) — explicit C# expressions; match the deployed ASP.NET version.
