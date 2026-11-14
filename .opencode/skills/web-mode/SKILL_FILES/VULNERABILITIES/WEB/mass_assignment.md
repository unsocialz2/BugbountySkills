# Mass assignment — compatibility route to writable-field authorization

The canonical method is [API mass assignment](../../../../api-mode/SKILL_FILES/VULNERABILITIES/API/api_mass_assignment.md).
Use it for JSON, form or nested object binding; a browser-rendered form does not make its backend
a different vulnerability family. Keep one authoritative methodology rather than two conflicting lists.

## Browser-specific entry

Capture a valid owned profile/document create or update and its independent readback.
Compare actual schema/output fields with the form's submitted fields. Pick one security-relevant
field the server should derive or gate, not every guessed `admin`/`balance` name.
Retain normal CSRF/content-type/session requirements so the test reaches the legitimate binder.

## PAYLOADS — field-authority differential

```json
{"display_name":"AUDIT_MARKER"}
```

Compare with a separate request on a disposable owned fixture:

```json
{"display_name":"AUDIT_MARKER","owner_id":"OTHER_OWNED_ACTOR"}
```

The field and values must come from the observed model. Expected protection is rejection,
ignoring the unauthorized owner field, or an authorized transfer workflow—not merely hidden UI.
Verify ownership/authority independently after the response. Echoed JSON is not persistence.
Use the canonical guide for create/update/bulk/nested lifecycle differences and evidence criteria.

Read-only field exposure is a related property-authorization question, not writable-field proof.
OWASP API6:2019 mass assignment is historical; the 2023 taxonomy groups relevant property-level
read/write failures under API3:2023 BOPLA. Taxonomy labels do not determine program severity.

## Sources and limits

Sources reviewed 2026-11-13. The payloads are request-shape examples, not target-tested field names.
Do not assign a fixed score or assume modern frameworks all enable/disable binding the same way.

- [PortSwigger: API testing](https://portswigger.net/web-security/api-testing) — hidden writable parameters and real API request discovery.
- [OWASP: Mass Assignment](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html) — binding mechanisms and allowlisted input models.
- [OWASP: API3:2023 BOPLA](https://api-security.owasp.org/editions/2023/en/0xa3-broken-object-property-level-authorization/) — property-level authorization taxonomy and impact.
