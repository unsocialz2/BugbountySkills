# XS-Leaks — infer a protected fact through a browser oracle

## Navigation

Secret/invariant → observable oracle → labeled controls → blinded inference → delivery and limits.

## Boundary and discovery

Investigate when a cross-origin attacker can learn a protected fact without directly reading the response body.
Examples include whether an owned test record matches a search, whether a session is logged in, or which of two synthetic states is active.
Start with the smallest fact the product intends to keep private; do not begin by extracting real user secrets.
A response-size, timing or event difference is a lead only until an attacker-controlled page can observe it under browser restrictions.
CORS denial does not rule out XS-Leaks, and missing isolation headers do not prove one.

## Model the oracle

Record secret/state, victim authority, request context, observer API, expected signal, nuisance variables and attacker cost.
Choose the oracle suggested by real behavior: load/error events, permitted window properties, frame count, cache state, navigation behavior or timing.
Distinguish HTTP response differences visible to a proxy from observations available to foreign-origin JavaScript.
Record browser/version and protections including cookie policy, cache partitioning, COOP, CORP, framing and Fetch Metadata handling.
Do not assume Resource Timing exposes cross-origin response sizes or detailed timing without the required permissions.

## Labeled synthetic controls

1. Create two controlled states that differ in only the intended protected fact.
2. Verify the true state with legitimate direct access, outside the attacker observer.
3. Run the same attacker-origin probe against each state using identical browser/session/partition conditions.
4. Randomize/interleave order to separate the secret effect from warm-up, caching, network drift or account differences.
5. Keep unrelated positive and negative targets where feasible to detect an oracle that always returns one class.
6. Predict held-out synthetic states without using the privileged ground truth during observation.

A single slow request or two different status codes in Burp is not a demonstrated inference channel.

## PAYLOADS — low-volume observation harness

This event probe is relevant only if the observed resource type genuinely yields different browser-visible events across the two states.
It measures no private response body and uses a bounded timeout.

```javascript
async function auditImageProbe(url, timeoutMs = 5000) {
  return new Promise(resolve => {
    const image = new Image();
    const start = performance.now();
    let timer;
    const finish = event => {
      clearTimeout(timer);
      image.onload = image.onerror = null;
      image.remove();
      resolve({event, elapsedMs: performance.now() - start});
    };
    image.onload = () => finish('load');
    image.onerror = () => finish('error');
    timer = setTimeout(() => finish('timeout'), timeoutMs);
    image.src = url;
  });
}
```

Use one observed candidate URL at a time and preserve raw outcomes.
Do not assume `<img>` can distinguish arbitrary 200/404 HTML responses: both may produce an error event.
Do not append cache-busting parameters when cache behavior is the very oracle being tested unless that change is a deliberate separate control.
A local fixture showing load/error discrimination is not evidence that the target exposes those states.

## Discriminating experiment matrix

| Observed architecture | Controlled experiment | Falsification |
|---|---|---|
| Search result changes resource behavior. | Present vs absent synthetic marker in otherwise identical owned records. | Differences depend on public data, cache or account identity rather than protected content. |
| Window/frame observable changes. | Same allowed popup/embed flow with two synthetic states. | COOP severs the reference, framing blocks it, or observed property is invariant. |
| Cache oracle. | Deliberately warmed vs cold owned resource under the same partition. | Partitioning prevents attacker observation or network jitter explains the difference. |
| Timing oracle. | Interleaved labeled states and held-out predictions within policy budget. | Confidence disappears with order randomization, realistic network or a fresh session. |
| Redirect behavior differs. | Two controlled allowed redirect destinations/states. | Foreign-origin observer cannot distinguish them or a browser patch removes the signal. |
| Resource type/error oracle. | Known valid resource vs controlled invalid variant. | Both generate the same event once actual credentials and policy are applied. |

For timing, preserve samples and distributions rather than selecting the most favorable pair.
Predeclare a simple decision rule using training samples, then assess false positives/negatives on separate samples.
No fixed number of samples guarantees validity; remain within program rates and stop when the oracle is not informative.
Prefer a clear event/property oracle over noisy timing when both answer the same question at lower cost.

## Browser delivery and attacker knowledge

Prove that the attack page can cause the probe request with the required victim authority.
Cross-origin, cross-site and cross-partition are different conditions; preserve the actual topology.
A result requiring disabled cookie protections, unpartitioned lab caches or privileged DevTools observation is a modified-condition result.
If the attacker needs a secret resource identifier before probing, document how it is obtained; do not grant it silently.
A detectable login state and recovery of arbitrary private text are different claims with different costs.
Do not amplify a small oracle into bulk extraction without evidence for each step and policy permission.

## Evidence and stopping

Preserve legitimate ground truth, attacker-observable outputs, raw trial order, browser policy, decision rule and held-out accuracy.
Transient observation is sufficient if the protected fact is learned during the window; final state persistence is not necessary.
Report the exact inferable fact, prerequisites, uncertainty and request cost.
Park if the foreign observer cannot distinguish states or the distinction is intentionally public.
Reopen only for a new real observable, supported browser behavior or target state transition.

## Primary references

Sources reviewed 2026-11-13; browser side channels can change with updates.

- [PortSwigger timing research](https://portswigger.net/research/listen-to-the-whispers-web-timing-attacks-that-actually-work) — measurement discipline and side-channel reasoning; a proxy timing method is not automatically a browser XS-Leak.
- [PortSwigger research review](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) — redirect/ETag XS-Leak examples as research leads, not universal payloads.
- [XS-Leaks Wiki](https://xsleaks.dev/) — observer families, partitioning and isolation mechanisms.
- [OWASP XS-Leaks](https://cheatsheetseries.owasp.org/cheatsheets/XS_Leaks_Cheat_Sheet.html) — threat models and defensive boundaries.
