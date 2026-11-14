# Client-side CSRF — trusted JavaScript as a confused deputy

## Navigation

Request construction → controllable source → synthetic request pair → authority/effect → evidence.

## Boundary and discovery

Investigate JavaScript that builds authenticated requests from URL query/fragment, window.name, referrer, storage or postMessage input.
The attacker need not execute JavaScript in the target origin if existing trusted code already turns attacker input into a sensitive request.
Start with a unique inert marker in a plausible navigation input and observe whether a request is constructed.
Distinguish this from classic CSRF delivered directly by a foreign page and from DOM XSS that introduces executable code.
A token-protected server can still receive an unintended request if its trusted frontend attaches the token to attacker-selected parameters.

## Model the deputy

Record source → parsing/decoding → method/path/query/body/header construction → credentials/token attachment → server action.
Identify what the attacker can influence: destination alone, method, body fields, resource/tenant reference, or a combination.
Use the normal application route and supported lifecycle event that consumes the source.
Do not grant the attacker DevTools access, a preexisting target-origin session or a secret CSRF token they cannot obtain.
The real victim's browser may supply these through the legitimate application code; prove that behavior.

## Controls

1. Trigger the feature normally and preserve one legitimate request/effect.
2. Navigate to the same feature with an inert input marker and inspect resulting requests.
3. Change the smallest source component that challenges the intended action boundary.
4. Confirm that the request carries the application's normal authority automatically.
5. Independently read back a harmless owned-record change.

## PAYLOADS — source-to-request examples

The inputs below are meaningful only if the observed parser expects these shapes.
Do not guess them as evidence; derive the actual grammar from code/runtime.
Use a reversible preference or synthetic draft rather than account deletion/payment.

```text
https://app.example.invalid/dashboard#post;/preferences/audit-label
https://app.example.invalid/dashboard#post;/drafts/OWNED_DRAFT/mark
```

If the feature uses a query field instead:

```text
https://app.example.invalid/dashboard?endpoint=%2Fpreferences%2Faudit-label
```

A harmless body marker, where the real frontend already builds this schema, is:

```json
{"label":"AUDIT_MARKER_7e31"}
```

The fragment-only example does not invent a body: prove the frontend supplies a valid one or choose an existing action whose request shape the source can produce.
An arbitrary request to a nonexistent route proves only request construction, not an authorization impact.
A request to an attacker origin may be blocked by CORS or lack credentials; that does not settle the same-origin action branch.

## Minimal local model for reasoning

This synthetic vulnerable-looking code illustrates the dataflow; it is not a finding in the target:

```javascript
const raw = location.hash.slice(1);
const parsed = /^(get|post);(\/[^\r\n]*)$/.exec(raw);
if (parsed) {
  fetch(parsed[2], {
    method: parsed[1].toUpperCase(),
    credentials: 'same-origin',
    headers: {'X-CSRF-Token': document.querySelector('meta[name=csrf-token]').content}
  });
}
```

Use the model to ask whether request intent is bound to a fixed supported operation.
Do not paste it into the target to create a vulnerability that was not there.
SameSite, Origin and Fetch Metadata may all look legitimate because the deputy sends a same-origin request; the decisive issue is attacker control over intent/parameters.

## Discriminating experiment matrix

| Hypothesis | Paired trial | Secure/benign alternative |
|---|---|---|
| URL controls method/action. | Normal supported route input vs one observed alternative method/path. | Fixed allowlist or action mapping rejects unintended combinations. |
| Source controls object reference. | Own record identifier vs another owned account's protected record. | Server independently enforces resource authorization. |
| Token is automatically added. | Normal request vs attacker-input-triggered request. | The unintended request lacks required proof or is never sent. |
| Decode/normalization changes path. | Literal safe path vs one architecture-supported encoded delimiter. | Canonicalized path remains within a constrained allowed prefix/action set. |
| Message-driven deputy. | Legitimate sender/source vs foreign owned window with same schema. | Origin/source/correlation binding rejects the foreign message. |
| Interaction/state requirement. | Normal browser entry vs claimed delivered link. | Required application state cannot be reached by the attacker-delivered input. |

Changing only `GET` to `POST` is not enough unless the frontend and server accept the resulting valid action.
A protected server may still block cross-account mutations even when the frontend is a deputy; keep the narrower request-intent claim separate.
Do not report accepted raw input that affects only harmless public fetching with no trust boundary.

## Effect and reach

Prove the victim can enter the consuming route from the claimed link/message/navigation without already executing attacker code.
Capture the actual initiator stack and source-derived request fields.
Verify authoritative state rather than treating network issuance or 200 as a completed action.
If the action uses a user gesture, record that requirement and distinguish it from automatic page-load behavior.
If the state later rolls back, preserve any completed side effect or temporary disclosure before deciding the issue is harmless.
Chaining to account control requires independently proven transitions; the deputy primitive alone does not imply ATO.

## Evidence and stopping

Save the normal control, exact attacker-controlled input, parser/constructor path, browser-generated authenticated request and result.
Record browser/version, page state, token source and delivery prerequisite without exposing live token values.
Stop when the frontend maps input to a safe fixed operation or server-side intent/authorization checks prevent the effect.
Reopen for a new real request constructor, accepted schema, alternate lifecycle event or message source.
Route direct foreign-form requests to `csrf_all_types.md` and executable sink behavior to the XSS guide.

## Primary references

Sources reviewed 2026-11-13; target-specific request grammar and authority must be observed.

- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) — client-side CSRF model and request-construction example.
- [PortSwigger DOM vulnerabilities](https://portswigger.net/web-security/dom-based) — attacker-controlled browser sources and downstream sinks.
- [PortSwigger Ajax header manipulation](https://portswigger.net/web-security/dom-based/ajax-request-header-manipulation) — source-controlled request metadata as a distinct browser dataflow.
- [MDN postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage) — attacker-message source constraints for a deputy channel.
