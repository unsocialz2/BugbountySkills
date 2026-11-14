# Design informative web experiments

## Contents

- Model a feature as connected authority
- Explore without demanding a finished exploit
- Design controls and interactions
- Follow lifecycle, representation and time
- Preserve evidence and uncertainty
- Choose progress and source freshness

## Model a feature as connected authority

Recover a normal request from client traffic, supported schema or exact source.
Use the smallest meaningful feature with an actor and observable owned fixture.
Anonymous processing is also a feature; do not demand two accounts for every class.
For ownership claims, two sessions of one account are not separate principals.

Write a compact model, not a transcript:

```text
Actor/authority: A, ordinary member of tenant TA
Asset: owned draft DA with unique synthetic marker
Normal path: submit -> queued conversion -> preview -> share -> revoke
Invariant: only current authorized actors, or intended bearer capabilities,
           may consume the corresponding private content
Representations: draft ID, revision ID, conversion job ID, signed preview URL
Competing explanations: public share by design / worker snapshot / stale ACL
Next discriminator: legitimate preview control then post-revocation owned viewer
```

Treat ID, role, tenant, workflow state, origin and capability as distinct sources
of authority. Ask where one component trusts a fact established by another. A
feature graph crosses API/worker/cache/browser boundaries; skill routing must not
fragment its security question.

## Explore without demanding a finished exploit

A hypothesis can be uncertain and still deserve a cheap test. Use input tracing,
small schema/source-assisted discovery, an inert marker or a legitimate actor
comparison to learn which consumer exists. Never require execution or proven
impact before attempting a justified discovery probe.

Maintain a short competing queue selected by observed architecture, not only the
first familiar vulnerability label. Read the relevant methodology for inspiration;
novel hypotheses outside it remain valid questions. The next action should
separate plausible explanations at low cost, not maximize requests or notes.

Three gates prevent both overclaiming and premature rejection:

| Gate | Sufficient question/evidence | What is not required yet |
|---|---|---|
| Discovery | Permitted reachable input/feature and a discriminating probe | A known exploit, score or final impact |
| Validation | Reproduced boundary failure with meaningful controls and natural attacker reach | A maximal chain, bulk data or ATO |
| Reporting | Exact reproducible claim, scope basis, effects and limits supported | Hypothetical scale or prohibited secret replay |

## Design controls and interactions

A normal control must succeed at the same action and relevant state. A list with
no items, nonexistent ID, stale token, invalid body, unsupported method or response
that only looks successful cannot certify the protected boundary.

Start by changing one meaningful relationship. When the hypothesis is an
interaction, use valid controls for each factor and their combination; do not let
a rigid single-field rule prevent testing parser/body, role/state or parent/child
couplings. For example, a Content-Type and its body encoding must change together
to remain a valid semantic request.

Use distinctive synthetic markers so a response identifies the actual object,
revision and principal. Independent readback can disprove echoed/no-op writes.
For blind paths use unique correlators and rule out link scanners, DNS prefetch,
async previews and retries. Callback provenance and demonstrated capability are
different claims; no domain name alone proves the component performing a fetch.

For timing/inference use interleaved or randomized matched controls, baseline
variance, enough permitted observations and held-out synthetic inputs. Reusing the
same noisy trace to invent and validate a classifier overstates evidence. Status,
length and latency differences become security evidence only when tied to the
specific protected fact or semantic effect.

## Follow lifecycle, representation and time

A correct direct denial does not certify export, preview, nested lookup, share or
background output. Follow observed representations and transitions rather than
spraying imaginary aliases. Likewise a valid user-owned update says nothing about
another actor/tenant or a later security-setting transition.

For capability links establish intended bearer vs identity-bound semantics. An
unguessable deliberately shared link can be the authorization mechanism. Ask
about actual scope, recipient, expiry, revocation and derived capabilities instead
of assuming “no login” means missing authentication.

For queued work, distinguish enqueue authorization, execution authorization,
artifact ownership and later consumption. For concurrency, compare sequential
controls and actual effects. A later rollback can repair a balance but cannot
un-disclose a document or undo a completed external effect. Capture only the
minimum policy-permitted decisive observation before cleanup.

## Preserve evidence and uncertainty

Use HYPOTHESES/COVERAGE/EXPERIMENT target-local artifacts as needed. A useful row
states actor/tenant, action, resource/revision, state, control, probe, observation,
source/result location, interpretation and next discriminator. Keep these outcomes:

- `not-tested`: no relevant experiment occurred;
- `blocked`: a named access/tool/policy prerequisite prevents this experiment;
- `inconclusive`: observations do not distinguish the explanations;
- `enforced-in-tested-case`: valid control and relevant denial at this boundary;
- `boundary-failure`: protected data/action/capability crossed as demonstrated.

Labels are scoped facts, not certificates for the whole endpoint or class. Track
technical validity, program eligibility and submission/duplicate status separately.
Reopen on a repaired control, changed state/version, new consumer or new evidence;
do not replay completed work solely because a guide was reloaded.

## Choose progress and source freshness

Prioritize evidence gain, feasible access and a concrete authority boundary over
root-cause familiarity or promised severity. Park a path when the next allowed test
cannot add useful information; retain why and the reopen condition. No fixed
payload quota, arbitrary timeout or report deadline substitutes for judgment.

Guides synthesize primary research and official protocol/vendor docs. PortSwigger
is a key research source, not a guarantee a historical gadget works now. Preserve
source URL, relevant version/configuration and observed transformations. “Sources
consulted” is not “payload executed”, and an updated page date is not a deployed
patch/behavior attestation. If sources disagree, resolve the parser/build/flow
question with a controlled experiment rather than choosing the confident text.

- [PortSwigger research practice](https://portswigger.net/research/so-you-want-to-be-a-web-security-researcher) — form useful new security questions.
- [PortSwigger race methodology](https://portswigger.net/research/smashing-the-state-machine) — hidden states and meaningful concurrent effects.
- [OWASP WSTG](https://wstg.owasp.org/) — assessment structure and explicit tested coverage.
