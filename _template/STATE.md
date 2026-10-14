# STATE — <program> (per-target, do not copy across targets)

```
TARGET:        # e.g. example.com (H1 VDP/private)
SCOPE:         # see scope.txt — authoritative
AUTH STATE:    # e.g. unauth / user alice@test.local (role=user)
TECH STACK:    # e.g. Cloudflare → AWS ALB → Laravel + MySQL
RECON COVERAGE: # e.g. GREEN 96% (date) — see ./RECON_LOG.md; §0 gate passed
INTERESTING ENDPOINTS:
  - # POST /api/v2/users/:id (mass assignment candidate)
FINDINGS SO FAR:
  - # F1: ... needs chain
LESSONS:       # see ./lessons.md — what worked on THIS target
NEXT:
  - # run recon §0 audit on operator recon → fill gaps → GREEN → web/api hunting
```

Say `STATE` to echo, `RESET` to clear. Update after every request/response paste.
Source: `.opencode/skills/core-identity/SKILL.md`.
