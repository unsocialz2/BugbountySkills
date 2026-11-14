# HTTP Request Smuggling — framing, forwarding, and connection-state evidence

## Contents

- Boundary and safety model
- Understand the notation
- Cheap discovery before a confirmed primitive
- Discriminating experiments
- Exact payload construction — local fixture only
- Validation and falsification
- Evidence and bounded closure
- Sources and version limits


Use this guide when intermediaries may disagree about request boundaries or how an HTTP/2+ request becomes an upstream HTTP/1 message. A protocol error, timeout, `200`, or scanner label is not a confirmed desynchronization.

## Boundary and safety model

Write the invariant: bytes from request A must not become part of an independently authorized request B, nor create an unintended upstream request through a different enforcement path.

Map client protocol, edge, gateway, upstream protocol, origin, connection pool, keep-alive behavior, and response association. Distinguish request tunnelling within one exchange from a persistent desync affecting later exchanges. Identify which connection is attacker-controlled and whether other users can share it.

Begin on local labs or a program-approved isolated fixture. Framing experiments can affect shared connections even when every path is a harmless canary. If shared-user isolation cannot be established, preserve a narrow discrepancy lead and use the program's permitted verification route; do not wait for another user's response.

## Understand the notation

The first symbol describes the frontend's interpretation and the second the backend's interpretation. Actual forwarding transformations still need observation.

| Family | Disagreement | What must be established |
|---|---|---|
| CL.TE | Front uses Content-Length, back uses chunked Transfer-Encoding | Surplus bytes after the backend's chunk terminator are interpreted differently |
| TE.CL | Front uses chunked framing, back uses Content-Length | The backend's consumed length diverges from the forwarded stream |
| TE.TE | Header interpretation differs, typically enabling one of the above outcomes | Which parser recognizes the transfer coding and what bytes are forwarded |
| H2.CL | Front uses HTTP/2 frame length, downgraded backend trusts inconsistent Content-Length | Exact HTTP/2-to-HTTP/1 representation and backend remainder |
| H2.TE | Front uses HTTP/2 length but upstream interprets a transfer coding that should not be forwarded this way | HTTP/2 validation and downgrade behavior; text header display is not wire evidence |
| CL.0 | Front consumes a length-framed body, back effectively ignores that body | A body remainder is available to a later backend parse |
| H2.0 | HTTP/2-to-HTTP/1 equivalent of body ignoring | Backend's ignored body after downgrade; not a synonym for pseudo-header injection |
| 0.CL | Front treats the body as absent, back waits for/consumes Content-Length bytes | Frequently a deadlock first; a target-specific gadget/sequence is needed to demonstrate useful desync |
| Expect-based | Front/backend differ in early/final-response and body-forwarding decisions | Timing and connection-state transition around `Expect`, not mere presence of the header |
| CRLF-powered | An input injects upstream header/message boundaries | Prove request-header injection first; route to `crlf_header_injection.md` |

Pseudo-header/request-line injection is a distinct parsing primitive; describe the actual field and transformation rather than relabeling it H2.0. HTTP/2 support on the client-facing connection does not prove end-to-end HTTP/2 upstream.

## Cheap discovery before a confirmed primitive

1. Establish stable normal requests with a synthetic response marker; compare fresh connections and controlled connection reuse.
2. Inventory protocol negotiation, redirects, early responses, method/body handling, and safe endpoint behavior. Prefer exact source/config or local upstream logs if available.
3. Form one framing question from the architecture. A body-ignoring route, observable proxy rewrite, or protocol downgrade is useful evidence, not mandatory proof before discovery.
4. Use a maintained tool's narrow detection mode only with known connection/rate/isolation settings. Preserve raw sent bytes, not just its verdict.
5. Compare matched valid controls. A malformed-request rejection can establish parser behavior but cannot establish a second request was executed.

## Discriminating experiments

| Hypothesis | Controlled comparison | Decisive result / benign alternative |
|---|---|---|
| CL/TE precedence differs | In an isolated fixture, compare valid CL-only, TE-only, and ambiguous forms with the same semantic canary | Backend stream position changes; universal rejection or normalized forwarding is a valid negative |
| An endpoint ignores the body | Send a valid short body to a body-accepting control and the candidate early-response route, then an owned follow-up on the same controlled connection | Follow-up marker is parsed from leftover bytes; an early response alone is not sufficient |
| HTTP/2 downgrade introduces framing | Compare equal semantic H1 and H2 controls, then one inconsistent H2 field in a lab | Upstream trace shows a different boundary; the frontend rejecting before forwarding is a narrow negative |
| A delay is an actual parser wait | Repeat a matched complete/incomplete pair with bounded timeout and fresh connections | Delay tracks missing bytes and ends when the expected local bytes arrive, rather than load/WAF jitter |
| A discrepancy is connection-locked | Repeat with controlled same/different connections and no unrelated traffic | Effect follows the tested connection; this limits exploitability rather than proving cross-user reach |
| Expect changes body forwarding | Compare no Expect and normal `100-continue` sequences in a fixture with traceable early/final responses | Different forwarding/consumption is demonstrated; a standalone `417`/`100` is not desync proof |

Do not vary multiple framing mechanisms at once. Understand why a probe changes the stream before trying an obfuscation. Keep valid controls for both encoding and application semantics.

## Exact payload construction — local fixture only

Generate bytes instead of copying visually aligned Markdown. This example constructs one deliberately ambiguous CL.TE laboratory stream; it does not transmit anything and does not assert any server accepts it.

```python
canary = (
    b'GET /audit-canary/AUDIT_MARKER HTTP/1.1\r\n'
    b'Host: lab.example.invalid\r\n\r\n'
)
body = b'0\r\n\r\n' + canary
request = (
    b'POST /audit-input HTTP/1.1\r\n'
    b'Host: lab.example.invalid\r\n'
    + f'Content-Length: {len(body)}\r\n'.encode('ascii')
    + b'Transfer-Encoding: chunked\r\n\r\n'
    + body
)
assert len(body) == int(request.split(b'Content-Length: ')[1].split(b'\r\n')[0])
assert body[:5] == b'0\r\n\r\n'
```

The CL reader consumes `len(body)` bytes; a hypothetical chunked reader ends at the five-byte zero chunk and sees the canary afterward. RFC-compliant handling should reject or normalize conflicting framing, not silently preserve ambiguity.

Build valid controls separately: CL-only with a harmless body and correct octet count; TE-only with correctly encoded chunk sizes/trailers. Do not use an ambiguous message as the only control. TE.CL requires its own measured forwarded stream; changing just the label on this example is invalid.

For CL.0/H2.0 lab controls, compare the same valid body on a known consuming route and a candidate early-response route. To test H2, use genuine HTTP/2 frames/tooling; a pasted `HTTP/2` request line does not create HTTP/2. Preserve the tool's automatic Content-Length fixes and normalization settings.

For browser-powered hypotheses, reproduce through an unmodified supported browser and account for permitted methods/headers, CORS/preflight, redirects, connection reuse, and negotiated protocol. A raw-client result is not browser delivery proof.

## Validation and falsification

Separate four levels:
- a parser/error/timing discrepancy;
- an unintended upstream request demonstrated by a unique local marker;
- persistent stream/response misassociation on a controlled connection;
- a reachable authorization/data/consumer effect with a realistic attacker model.

Try incomplete normal bodies, server overload, rate limiting, connection closure, multiple backend replicas, tooling auto-fixes, harmless request pipelining, and cached responses as competing explanations. An intentionally permitted two-request pipeline is not smuggling.

Do not request real users' responses, poison queues for random consumers, or escalate a primitive into an assumed account takeover. Narrow the report when only isolated tunnelling or a bounded routing bypass is proven. Transient unauthorized execution still matters even if a later request resets the connection.

## Evidence and bounded closure

Save exact bytes/frames, line endings and byte counts, negotiated protocols, connection reuse/closure, tool version/settings, timestamps, positive and negative controls, upstream trace/marker result where permitted, and the semantic effect. State inferred topology separately from observed topology.

A WAF rejection or failed timing probe leaves other framing families unknown. Scope a negative to that route, transport, parser variation, and connection state. Reopen for a body-ignoring gadget, a different upstream path, changed proxy configuration, or a newly observed parsing primitive.

## Sources and version limits

Source review: 2026-11-13. The byte constructor is an isolated reasoning fixture, not an end-to-end exploit or live-vendor validation.

- [PortSwigger — Advanced request smuggling](https://portswigger.net/web-security/request-smuggling/advanced): HTTP/2 downgrade primitives and distinctions.
- [PortSwigger — CL.0 request smuggling](https://portswigger.net/web-security/request-smuggling/browser/cl-0): body ignoring and H2.0 correspondence.
- [PortSwigger — Browser-powered desync](https://portswigger.net/research/browser-powered-desync-attacks): browser reachability and client-side connection conditions.
- [PortSwigger — HTTP/1.1 must die](https://portswigger.net/research/http1-must-die): 0.CL, double-desync, parser discrepancies, and Expect-based research; use published cases as conditional mechanisms.
- [PortSwigger — CRLF-powered desync](https://portswigger.net/research/crlf-powered-desync-attacks): upstream header injection and connection/IP-locked cases; not a universal escalation recipe.
- [HTTPWG — RFC 9112](https://httpwg.org/specs/rfc9112.html): message framing, chunked grammar, conflicting lengths, and connection handling.
