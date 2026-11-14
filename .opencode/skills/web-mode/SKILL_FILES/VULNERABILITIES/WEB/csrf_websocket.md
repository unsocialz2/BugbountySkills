# Cross-Site WebSocket Hijacking — compatibility route

Canonical methodology and PAYLOADS: [websocket_attacks.md](websocket_attacks.md).
Load that guide once; do not maintain a second CSWSH recipe here.

The decisive boundary is a real foreign-origin browser gaining protected WebSocket read/action capability using authority it should not exercise.
Origin-header oddities, a successful handshake, or a CLI-supplied victim token alone do not prove that boundary.
Preserve the normal handshake, actual attacker-browser credential behavior and protected synthetic message/action.
Use [csrf_all_types.md](csrf_all_types.md) only for a distinct HTTP state-changing request in the same flow.
