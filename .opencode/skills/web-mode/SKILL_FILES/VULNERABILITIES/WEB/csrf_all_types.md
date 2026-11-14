# CSRF — browser-deliverable actions and request binding

## Navigation

Boundary → normal action → request probes → delivery experiment → lifecycle evidence.

## Boundary and discovery

Test whether an attacker-controlled context can cause a victim browser to perform a security-relevant action using authority the attacker does not possess.
Start by exercising ordinary owned-account actions and identifying ambient credentials and unpredictable request fields.
A successful replay in an HTTP client is a lead; it is not proof an attacker page can deliver that request.
Classic CSRF, login/account-switch CSRF, client-side CSRF and CSWSH have different authority and delivery models.
Use `client_side_csrf.md` when trusted JavaScript constructs the sensitive request from attacker-controlled input.

## Normal flow and attacker model

Record method, path, content type, required headers, cookies, Origin/Referer, token source and resulting state.
Use a reversible synthetic preference or test record for initial validation rather than a payment or account deletion.
Confirm the authoritative state before and after the legitimate action.
Identify the actual hosting requirement: arbitrary cross-site page, same-site untrusted sibling, sandboxed document or another demonstrated context.
Same-site attacker control is a precondition to prove, not a universal reason to dismiss a CSRF candidate.

## PAYLOADS — isolate one binding assumption

| Existing mechanism | Control | Candidate change | Interpretation |
|---|---|---|---|
| Token field required. | Valid current token. | Field omitted, then empty in a separate experiment. | Acceptance needs semantic readback and deliverable request shape. |
| Session-bound token. | A token in A session. | B token in A session using two owned accounts. | A token tied to A's session can be perfectly valid; binding to session is not itself a flaw. |
| Origin check. | Real trusted origin. | Real attacker-origin browser request. | Impossible hand-built Origin values do not establish delivery. |
| Referer fallback. | Full normal Referer. | Actual browser referrer policy/context omitting it. | Header removal in Repeater alone is insufficient. |
| JSON content type. | Normal application/json request. | Valid equivalent body with an actually accepted simple content type. | Invalid JSON rejection does not prove origin binding. |
| Equivalent routes. | Current normal action. | Discovered alternate method/route reaching the same action. | A public read or no-op endpoint is not equivalent. |

Do not run every variant unless the feature has the corresponding mechanism.

## Form-deliverable proof

Adapt only to an observed endpoint that accepts this form representation.
Serve from an owned attacker origin and use the owned victim session in a clean browser context.
The example uses a synthetic label; it neither exports data nor changes account recovery settings.

```html
<form id="audit" action="https://app.example.invalid/preferences/label"
      method="POST">
  <input type="hidden" name="label" value="AUDIT_MARKER_7e31">
</form>
<button id="run">Run owned-account test</button>
<script>
document.querySelector('#run').onclick = () => {
  document.querySelector('#audit').submit();
};
</script>
```

Record the interaction requirement. Automatic form submission is a separate delivery variant if that difference matters.
A form generally cannot set arbitrary Authorization/custom headers.
A JSON fetch with `Content-Type: application/json` is normally preflighted cross-origin; do not assume the POST will be sent.
CORS can prevent reading a simple-request response while the underlying state change still succeeds.

## Conditional JSON representation probe

Only use this when the target accepts JSON parsing despite `text/plain`.
The browser inserts an equals sign between a form field's name and value.
Choose a syntactically valid body with that equals sign inside a harmless string:

```html
<form action="https://app.example.invalid/preferences/label" method="POST"
      enctype="text/plain">
  <input name='{"label":"AUDIT_MARKER_7e31","padding":"' value='"}'>
</form>
```

The submitted body is shaped like `{"label":"AUDIT_MARKER_7e31","padding":"="}` plus a line ending.
Confirm the exact bytes, accepted parser and actual effect; this is not a universal JSON-CSRF bypass.

## Cookie and navigation experiments

Use the actual browser's cookie inclusion rules, not a curl Cookie header.
Compare top-level GET navigation, form POST, subresource, iframe and fetch only when the action supports those semantics.
Explicit SameSite=Lax differs from browser-specific default-Lax behavior; avoid universal short grace-window claims.
Sibling subdomains may be same-site but cross-origin; verify public-suffix boundaries and scheme.
An open redirect or on-site gadget is useful only if every navigation/request preserves the required method, body and credentials.
Never disable third-party-cookie blocking or security features without labeling the result as a modified lab condition.

## Identity-switch branch

For login/linking CSRF, prove the resulting account/session identity before any impact claim.
Use distinct controlled accounts and a clean logged-out or authenticated initial state matching the attack model.
Being logged into the attacker's account can cause context confusion without giving control of the victim's original account.
If later user input could reach the wrong account, demonstrate that with synthetic content and the actual workflow.
Do not turn an identity switch into ATO by assuming untested follow-up steps.

## Evidence, stop and reopen

Preserve valid normal control, accepted altered request, actual browser delivery and independent state/identity readback.
An action can have a transient but completed effect; capture that effect before any rollback instead of demanding persistence alone.
A missing token, permissive header or 200 response without state change remains a lead.
Narrow negative conclusions to the tested account, action and delivery context.
Stop where step-up or unpredictable proof prevents the action; reopen for a new supported representation or genuine attacker context.
Restore the synthetic preference/record after evidence is saved.

## Primary references

Sources reviewed 2026-11-13; cookie behavior must be reproduced in the relevant browser.

- [PortSwigger CSRF](https://portswigger.net/web-security/csrf) — meaningful action, credential and request-binding conditions.
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) — token/origin defenses and client-side CSRF distinction.
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS) — preflight and simple-request behavior.
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) — cookie inclusion and SameSite constraints.
