# Async jobs and webhooks — authority across delayed work

## Contents

- Map job and event authority
- Discovery and valid controls
- Differential experiments and PAYLOADS
- Local signature fixture
- Evidence, closure and sources

## Map job and event authority

Test whether queued work and delivered events preserve the correct actor, tenant, resource,
state, uniqueness and authenticity across scheduling, execution and result consumption.
A `202 Accepted` only establishes request acceptance; it does not prove a worker executed,
a webhook signature passed, a payment occurred or a result became readable.

Trace the observed workflow:

```text
actor -> create/schedule -> queued -> worker start -> external effect/result
                                      -> status/read -> download/cancel/delete
publisher -> authenticate event -> identify object/tenant -> deduplicate -> state transition
```

Record when authorization is intended to be decided: issue time, execution time, download time,
or a documented snapshot policy. Legitimate delegation can intentionally survive membership changes.
For jobs, identify creator, input resource, tenant, result object and each consuming operation.
For webhooks, distinguish inbound event validation from outbound URL fetching/SSRF.

Use sandbox/test-mode events or a program-approved synthetic provider and two owned tenants.
Do not manufacture payment events against production merely because the endpoint is public.
A provider-controlled delivery tool is a useful legitimate control, not authority to alter real billing.

## Discovery and valid controls

Perform one normal harmless export/import/report job and retrieve a marker-filled result.
Observe status polling, result links, cancel, retries and UI updates; do not guess destructive routes.
For webhook-backed workflows, create one normal sandbox event and independently observe its effect.
Keep the exact raw payload, content encoding, signature/header scheme, event identifier,
timestamp and relevant endpoint secret/tenant selection logic, with secrets redacted.

Identify which stage a response acknowledges. An endpoint may return 200 before validation or
intentionally suppress errors to avoid retries. Compare the authoritative object/ledger afterward.
If processing observability is unavailable, mark signature-bypass claims inconclusive.

## Differential experiments and PAYLOADS

| Boundary | Smallest challenge and matched control | Protected outcome |
|---|---|---|
| Job input binding | Keep A's creator session and substitute owned tenant B's resource ID in a valid schedule request. | Worker cannot read/process B's fixture without the relevant authority. |
| Poll/result authorization | A requests status/result for B's populated job; compare B's legitimate retrieval. | Protect sensitive status and result separately; a job ID alone is not a capability unless product defines it so. |
| Lifecycle authorization | Schedule while B is authorized, remove B, then start/retrieve through the observed path. | Apply documented issue/use-time policy; record meaningful disclosure during any stale window. |
| Cancellation ownership | Cancel only a disposable controlled B job as A, using a valid normal cancel control. | No cross-tenant cancellation; 200 without changed job state is not proof. |
| Inbound authenticity | Send an owned sandbox fixture with valid, missing and one-byte-invalid signature in separate fresh events. | Only authenticated events cause the protected transition; compare semantic effects, not response codes. |
| Signed-byte coverage | Change one byte/whitespace of the raw payload while retaining its prior signature, then compare properly signed changed body in the local/provider sandbox. | Authenticate the provider's specified signed message, not a lossy reserialization. |
| Event/tenant binding | In authorized synthetic setup, send tenant A's valid signed event referring to owned B's object. | Do not treat authentic publisher data as authorization for another tenant's object. |
| Replay/idempotency | Redeliver the exact valid test event once; separately use a new event ID representing the same logical operation if the provider can legitimately generate it. | One business effect where once-only semantics apply; duplicate acknowledgement is legitimate. |
| Event ordering | Deliver two valid synthetic lifecycle events in supported reverse order. | Avoid restoring invalid old authority/value; provider ordering may intentionally be unspecified. |

```http
POST /observed/jobs HTTP/1.1
Host: app.example.invalid
Content-Type: application/json

{"resource_id":"OWNED_RESOURCE_B","format":"audit-text"}
```

```json
{"id":"AUDIT_EVENT_1","type":"audit.fixture.ready",
 "data":{"object_id":"OWNED_FIXTURE_A","tenant_id":"OWNED_TENANT_A"}}
```

These field names are schematic. Match the actual provider schema; an invalid event that never
reaches the worker cannot test state transition or tenant authorization.
For webhook signature tests, apply the provider's exact timestamp/envelope and key-selection rules.
GitHub-style raw-body HMAC and Stripe-style timestamped signatures are not interchangeable.

## Local signature fixture — no network or real credentials

This validates byte coverage in an isolated generic HMAC-SHA256 fixture.
It is not a complete implementation of any provider's scheme.

```python
import hashlib, hmac

key = b"AUDIT_SYNTHETIC_WEBHOOK_KEY_ONLY"
body = b'{"id":"AUDIT_EVENT_1","value":"AUDIT_A"}'
signature = hmac.new(key, body, hashlib.sha256).hexdigest()

def valid(raw, supplied):
    expected = hmac.new(key, raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, supplied)

assert valid(body, signature)
assert not valid(body.replace(b"AUDIT_A", b"AUDIT_B"), signature)
assert not valid(body + b" ", signature)
```

A valid signature authenticates the signed message under that key; it does not alone establish
freshness, replay resistance, tenant authority or a valid business transition.
Some integrations fetch authoritative provider state instead of trusting the event body; inspect
that path before interpreting a body mutation or event field as an exploitable control.

## Evidence, closure and source boundaries

Preserve the successful normal workflow, actors/tenants, job/event IDs, exact stage boundaries,
control/challenge raw requests, provider validation state if observable, and independent output/effect.
Capture actual marker-bearing content rather than collecting customer data or full reports.
For once-only effects count committed changes in the authoritative ledger, not matching success messages.

Close only the tested stage; secure creation does not prove secure polling/download/cancellation.
A rejected bogus signature cannot prove all valid-event tenant and replay bindings are correct.
Reopen for another observed endpoint secret, result representation or lifecycle event.

Sources reviewed 2026-11-13. The HMAC fixture was executed locally; no provider or live webhook
was tested. Vendor retry/order/tolerance details must be rechecked for the actual integration.

## Primary references

- [PortSwigger: Access control](https://portswigger.net/web-security/access-control) — per-operation ownership and workflow authority.
- [PortSwigger: Smashing the state machine](https://portswigger.net/research/smashing-the-state-machine) — delayed/interleaved transitions and intermediate state.
- [OWASP: Webhook Security](https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html) — authenticity, replay and inbound/outbound trust separation.
- [Stripe: Webhooks](https://docs.stripe.com/webhooks) — raw-byte verification, duplicate delivery and unspecified event order for Stripe integrations.
- [GitHub: Validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries) — GitHub's HMAC delivery scheme and comparison requirements.
