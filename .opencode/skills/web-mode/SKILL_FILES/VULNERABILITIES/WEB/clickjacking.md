# Clickjacking — actionable UI delivery, not missing headers

## Navigation

Action selection → framing controls → visible alignment → hit testing → real effect.

## Boundary and discovery

Investigate whether an attacker can misdirect a user's interaction onto a protected application control through an embedded page.
Start with an owned account and a reversible synthetic action, such as changing a test label.
Missing X-Frame-Options or frame-ancestors is a discovery signal, not an exploit result.
A publicly frameable information page with no meaningful action does not establish a security impact.
Define the intended user action, authority supplied by the browser, number of interactions, and deception/delivery conditions.

## Establish controls

1. Perform the action normally and independently verify its state change.
2. Capture the actual GET document headers, not only HEAD.
3. Embed the exact action page from an owned foreign origin.
4. Check whether it actually renders and has the victim authentication needed.
5. Inspect effective frame-ancestors across nested ancestors and XFO behavior in the relevant browser.

A login screen inside the frame is not a successful authenticated delivery control.
SameSite and third-party-cookie restrictions can alter the embedded session.
A single-use confirmation or step-up may prevent the sensitive operation even when the page renders.

## PAYLOADS — correct stacking for a controlled PoC

The iframe must receive the interaction; the decoy should not intercept it.
Use debug opacity first, align the real synthetic action, then test the demonstrated opacity.
Coordinates and dimensions below are illustrative and must be calibrated to the actual page/browser.

```html
<style>
#decoy {
  position: absolute; top: 350px; left: 600px;
  z-index: 1; pointer-events: none;
}
#target {
  position: absolute; top: 0; left: 0;
  width: 1280px; height: 800px;
  z-index: 2; opacity: 0.5;
}
</style>
<div id="decoy">Apply AUDIT_MARKER_7e31</div>
<iframe id="target"
        src="https://app.example.invalid/preferences/label"></iframe>
```

An overlay with higher z-index and active pointer events can make a convincing screenshot while preventing the target from receiving a click.
Use the top-document hit test to confirm the frame is the selected element:

```javascript
const hit = document.elementFromPoint(620, 365);
console.log({tag: hit?.tagName, id: hit?.id});
```

This confirms only the top-level frame hit; verify the actual target control and resulting action separately.
Do not use pointer-events:none on the target iframe to make it look aligned.
Do not claim a real deceptive flow merely because programmatic click() succeeded.

## Discriminating experiments

| Hypothesis | Control / change | Required observation |
|---|---|---|
| Page can be embedded. | Direct navigation vs foreign iframe. | Real document renders, not an error/login substitute. |
| Victim authority survives embedding. | Same owned session direct vs embedded. | Credentials actually sent and sensitive control available. |
| Correct interaction target. | Visible debug iframe vs intended opacity. | User click reaches the intended embedded control at both settings. |
| State change lacks independent confirmation. | Ordinary action vs misdirected equivalent click. | The same server-side effect occurs without additional unavailable proof. |
| Multi-step flow is realistically deliverable. | Each normal step vs embedded step. | All required gestures, page transitions and focus states fit the claimed flow. |
| Frame restriction bypass. | Known blocked context vs specific new nesting/embedding context. | Real browser permits the protected action, not just HTTP retrieval. |

Changing iframe to object is not a universal XFO bypass.
Changing sandbox flags can prevent the action, popup, navigation or script on which the PoC relies; capture the actual configuration.
CSS alignment can fail across viewport, zoom, locale and responsive layout; preserve the tested values and do not generalize to every user.
Transparency interventions and browser UI protections are version-sensitive.

## Effect and falsification

Use authoritative state readback after the click, not button animation or response text alone.
A frameable page plus a successful CSRF request is not automatically a clickjacking chain; determine which user gesture changes authorization.
If a re-authentication page appears, do not assume the user will enter their password through an unseen frame.
Keep account changes, permission changes, financial actions and cosmetic changes distinct.
Do not force ATO from a reversible label update.
If a state change is rolled back, check whether a meaningful completed action occurred before rollback.

## Evidence and stopping

Save direct-action control, full document policy, embedding origin, browser/version, session state, viewport, actual hit target and final readback.
Use video or screenshots only where permitted and redact unrelated information.
Stop when frame policy blocks the actual context, credentials are absent, or an independent confirmation prevents the action.
Reopen for a genuinely different sensitive flow or allowed ancestor topology, not another copy of the same missing header.
Restore the test state after preserving evidence.

## Primary references

Sources reviewed 2026-11-13; reproduce delivery in the actual browser and session configuration.

- [PortSwigger Clickjacking](https://portswigger.net/web-security/clickjacking) — overlay construction, stacking and action proof.
- [OWASP Clickjacking Defense](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html) — frame-ancestors/XFO and defense limitations.
- [MDN iframe](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe) — embedding and sandbox behavior.
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) — embedded credential constraints.
