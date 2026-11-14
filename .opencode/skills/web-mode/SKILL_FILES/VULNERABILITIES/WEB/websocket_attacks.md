# WebSocket security — handshake, messages and authority lifecycle

## Navigation

Protocol discovery → handshake controls → message controls → cross-site delivery → lifecycle evidence.

## Boundary and discovery

Investigate a real WebSocket feature from normal browser traffic: chat, collaboration, notifications, trading UI or a subscription stream.
Separate handshake authentication, per-message authorization, channel ownership and long-lived session revocation.
CORS response-read rules do not operate as they do for fetch, but that does not make all WebSocket endpoints exploitable cross-site.
Missing Origin validation is a lead; attacker delivery must also obtain the required authority and fulfill the application protocol.
Do not treat Sec-WebSocket-Key as an authentication secret; it is part of the protocol handshake.

## Capture the normal protocol

Record WebSocket URL, Origin, cookies, query tokens, subprotocols, initial authentication frames, ready messages and subscription format.
A native browser WebSocket constructor accepts a URL and optional protocols, not arbitrary Authorization headers like a CLI client.
Determine which credentials the attacker browser will supply or can legitimately learn.
Use two owned users/tenants and synthetic channels when testing ownership.
Preserve one normal successful connection and one normal protected read/action for the rightful actor.

## PAYLOADS — message authorization probes

Use actual schema learned from the product; these JSON names are illustrative.

```json
{"action":"subscribe","channel":"OWNED_CHANNEL_A"}
```

```json
{"action":"subscribe","channel":"OWNED_CHANNEL_B"}
```

Compare A→A and B→B normal controls, then A→B with only the channel changed.
An acknowledgment does not prove disclosure: require B's synthetic `AUDIT_MARKER_7e31` or an independent mutation readback.
If the product has an authentication frame, compare valid, missing and expired proof in separate connections.
Do not send oversized frames or flood to infer lack of authorization.

## Cross-site WebSocket hijacking proof

Serve this from an owned foreign origin using the owned victim browser session.
Adapt URL, subprotocol and the single harmless action to normal protocol observations.

```html
<pre id="result">waiting</pre>
<script>
const socket = new WebSocket('wss://app.example.invalid/ws');
const output = document.querySelector('#result');
socket.onopen = () => {
  socket.send(JSON.stringify({action:'readAuditMarker'}));
};
socket.onmessage = event => {
  output.textContent = JSON.stringify({
    hasMarker: String(event.data).includes('AUDIT_MARKER_7e31')
  });
  socket.close(1000, 'audit complete');
};
socket.onerror = () => { output.textContent = 'connection/error; inspect handshake'; };
</script>
```

This does not prove a real endpoint with `readAuditMarker` exists; recover the exact harmless operation before adapting.
If the app needs a ready message before an action, wait for that normal message rather than guessing timing.
Do not export messages; local boolean marker proof is enough.
Inspect actual cookies and Origin on the handshake. SameSite/partition/third-party-cookie behavior can prevent victim authority from arriving.
A separate bearer token unavailable to attacker script may block this route even if Origin is ignored.
Other ambient-auth models require their own credential/delivery analysis; avoid “cookies are the only route” or “token headers are universally safe” claims.

## Discriminating experiment matrix

| Boundary | Control / challenge | Required semantic outcome |
|---|---|---|
| Handshake identity. | Valid normal auth vs missing/invalid auth. | Protected protocol action becomes available without intended proof. |
| Foreign-origin handshake. | Trusted page vs foreign owned page. | Browser supplies victim authority and foreign script can read/act. |
| Channel ownership. | A→A, B→B, then A→B. | Private synthetic content/action across actors. |
| Message function/role. | Legitimate lower-role action vs discovered privileged message type. | Server executes a stronger function without the required role. |
| Membership revocation. | Authorized subscription, revoke membership, send/read next marker. | Capability persists beyond documented intended revocation behavior. |
| Token/session lifecycle. | Fresh valid socket vs logout/expiry/revoked token state. | Long-lived connection retains prohibited action/data authority. |
| Reconnect path. | Established normal state vs reconnect/resume token from wrong flow. | Wrong actor/session receives a previously protected stream. |

Stale buffered messages after revocation are different from fresh post-revocation disclosure; timestamp synthetic events.
A connection staying open is not itself a revocation flaw if protected operations stop.
If STOMP/SockJS or another layer carries authentication, analyze that application protocol too.
Message-level SQL/XSS/SSRF hypotheses belong to the corresponding sink guide after the data path is observed.

## URL tokens and leakage

A token in a WebSocket query may be retained by server/proxy/application logging, but it is not automatically a navigation-history or Referer leak.
Prove the actual unintended receiver and token usability without exporting real credentials.
Short-lived one-use handshake tokens have different semantics from durable session tokens.
A scanner/callback does not prove execution or message confidentiality impact.

## Evidence and stopping

Save normal handshake, attacker handshake, exact message sequence, actor/channel mapping and synthetic protected result.
Record browser/version, cookie state, subprotocol, connection lifetime and revocation timestamps.
Capture transient messages before closure if those messages crossed the boundary.
Stop where unpredictable proof, message auth or browser credential policy prevents the claimed route.
Reopen for a discovered alternate transport/auth path or changed membership/state; do not equate handshake success with full compromise.
Close all test sockets and restore test memberships after evidence preservation.

## Primary references

Sources reviewed 2026-11-13; reproduce browser credentials and protocol timing on the actual target.

- [PortSwigger CSWSH](https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking) — authenticated cross-site handshake conditions.
- [MDN WebSocket constructor](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket) — browser constructor/transport constraints.
- [OWASP WebSocket Security](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html) — authentication, message authorization and session lifecycle.
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie) — browser credential context.
