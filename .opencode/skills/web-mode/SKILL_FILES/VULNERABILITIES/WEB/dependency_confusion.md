# Dependency confusion — prove resolution before installation or execution

## Boundary and place in a web hunt

Use when allowed web/source artifacts expose real dependency names or build configuration relevant to an in-scope application.
This is a software supply-chain boundary adjacent to web testing, not a generic endpoint vulnerability.
A package name absent from a public registry is a lead, not proof of a vulnerable resolver.
Map manifest → registry/config → version constraints/lockfile → candidate selection → download → build/install hooks → consumer.
Scope, namespace ownership and package-publication permission are separate questions.
Do not register the organization's names or publish packages merely because this guide lists a test.

Record:

- exact dependency spelling, normalized name and ecosystem;
- public versus private source mapping and effective client configuration;
- version constraints, lockfile, hashes and cache influence;
- build mode, platform tags and optional/development dependency status;
- whether install scripts/build hooks run and which environment consumes the result;
- evidence that the application actually resolves this dependency, versus stale/sample configuration.

## Normal and adversarial lab fixtures

Begin with source/configuration analysis or a controlled resolver mirror.
Use researcher-owned package namespaces and two local package indexes/registries.
Place tiny inert packages with distinct version/marker metadata in each.
Reproduce the real resolver configuration without adding fallback behavior that the target does not have.
Keep network access confined to those controlled sources.
A copied manifest without its actual config/lockfile does not establish production selection.

## Payloads and differential experiments

The payload here is the package identity/version/metadata, not an exfiltration script.
A benign package can export the string `AUDIT_MARKER_A` or `AUDIT_MARKER_B` and have no install hook.

```json
{
  "name": "@researcher-owned/audit-fixture",
  "version": "1.0.0",
  "main": "index.js"
}
```

```javascript
module.exports = 'AUDIT_MARKER_A';
```

A Python resolver-selection experiment may use `--dry-run --report` in a controlled environment.
Use prebuilt inert wheels where possible: metadata preparation for source distributions may execute a build backend even under dry-run.
Do not point copied private source configuration at untrusted public packages for a supposedly read-only check.

| Question | Controlled challenge | Control | What does it prove? |
|---|---|---|---|
| Does the resolver compare multiple sources? | Same owned name at two controlled indexes, differing compatible versions | One index with the same exact requirement | Selected artifact provenance; not target execution. |
| Do version constraints prevent substitution? | Higher owned lab version outside the requirement range | Compatible candidate inside the range | Constraint enforcement, not just numerical version preference. |
| Does scope mapping bind registry? | Owned scoped package with explicit local registry mapping | Same fixture under observed configuration | Registry selection for that scope; do not infer behavior for unscoped packages. |
| Do lockfiles/hashes pin the artifact? | Competing inert artifact under the same name/version in an isolated mirror | Untouched lock/hash and original artifact | Integrity rejection or selection; cache effects must be observed separately. |
| Is the relevant dependency actually installed? | Normal lab build using the manifest's dependency group | Build excluding that group | Dependency reach and lifecycle, not merely manifest presence. |
| Is the package loaded by the application? | Inert exported marker on researcher-owned fixture | Original benign package | Runtime/module use, separate from download or metadata access. |

## Ecosystem differences

For pip, `--extra-index-url` does not give the private source a universal priority over other locations.
Candidate compatibility, version constraints, pre-releases, platform and artifact type still affect selection.
Never reduce pip behavior to “higher version always wins” without checking those requirements.
For npm, scope ownership and scope-to-registry mapping matter; one scope maps to one configured registry.
Lockfile URLs, integrity checks and caching can change the effective route.
Other package managers have different repository-order and namespace semantics; do not copy pip rules to Maven, NuGet or Go.
A public package can legitimately share a similar name without being consumed by this application.

## Evidence and callback attribution

Distinguish public registry lookup, package metadata fetch, artifact download, hook execution and application import.
A callback alone can come from security scanners, registry indexing or the researcher's own build.
For an explicitly authorized execution test, use an inert marker with minimal provenance; avoid system identities and credentials.
Do not publish broad telemetry hooks that contact a third party every time an unrelated person installs a package.
A build marker does not prove cloud/CI secret access or privilege beyond the observed build context.
No package publication or target installation is required to document a source-backed risk lead.

## Falsification and stop/reopen

Test stale manifests, private registry-only resolution, constraints, lock/hash enforcement, unsupported platform and unused dependencies.
Save effective redacted config, resolver version, input manifest/lock hash, candidate metadata and selected artifact report.
Do not expose private registry credentials while collecting configuration evidence.
Close a tested consumer when effective resolution cannot choose an attacker artifact under the claimed model.
Keep unobserved build config or unknown namespace claimability unresolved.
Reopen for changed lockfile/config, new package group, different resolver or observed public fallback.
Technical validity, publication authorization and program eligibility must remain independent.

## References and freshness

Reviewed 2026-11-13. This topic uses resolver-owner documentation and original research rather than inventing a PortSwigger-specific methodology.

- [pip install](https://pip.pypa.io/en/stable/cli/pip_install/) — multiple source selection, index options and dependency-confusion warning.
- [npm scopes](https://docs.npmjs.com/cli/v11/using-npm/scope/) — namespace ownership and scope-to-registry mapping.
- [OWASP dependency chain abuse](https://owasp.github.io/www-project-top-10-ci-cd-security-risks/CICD-SEC-03-Dependency-Chain-Abuse) — supply-chain trust boundary and execution stages.
