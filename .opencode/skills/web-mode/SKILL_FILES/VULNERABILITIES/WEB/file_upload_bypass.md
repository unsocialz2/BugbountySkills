# File upload and processing — test the complete artifact lifecycle

## Boundary and discovery

Use for uploads, attachments, imports, avatars, report conversions, archive extraction and generated previews.
A filename or MIME bypass is a step, not the final security claim.
Map create permission → acceptance → stored identity/path → processing → serving origin/headers → reader authority → revoke/delete.
Separate bytes accepted, bytes stored, processor consumption, browser execution and server execution.
File extension, request Content-Type and magic bytes can be checked by different components.
A successful upload to static storage does not execute server-side code.

Record the attacker/reader roles, intended file types, storage origin, object ACL and exposed representations.
Observe thumbnail/original/export/download routes independently.
Capture content-type, content-disposition, nosniff, CSP and redirects on the *served* response.
Do not infer browser behavior from the multipart request's content type.

## Normal fixture and readback

Create a tiny legitimate file containing `AUDIT_UPLOAD_A` through the ordinary workflow.
Prove a legitimate reader can retrieve it and an unrelated controlled actor is subject to the expected policy.
Preserve original bytes and the transformed output if re-encoding occurs.
Use a unique resource/path and prevent replacement of shared or existing application files.
Use a second tiny marker fixture with one changed property for every format differential.

## Context-specific payloads and experiments

| Boundary | Harmless challenge | Control | What counts / what does not |
|---|---|---|---|
| Filename versus MIME validation | Owned `audit.txt` with tiny text body and different declared MIME | Same bytes/name with correct MIME | Acceptance difference identifies a validation path, not execution. |
| Filename canonicalization | `audit.txt.` or case variation only when observed storage/platform makes it meaningful | Canonical `audit.txt` | Compare stored name and serving behavior; trailing-dot acceptance alone has no security impact. |
| Content sniffing / active document | Tiny SVG below, only in a permitted isolated test | SVG with no event handler | Browser marker execution in actual served context plus relevant origin/reader authority. |
| Cross-tenant file reference | Actor A retrieves actor B's controlled private attachment id | Each actor's own successful download | Unauthorized bytes, not predictable object name or an error with 200. |
| Processor fetch boundary | Owned document referring to a permitted controlled canary | Same document with local static content | Distinguish server-renderer fetch from browser load and scanner activity. |
| Archive extraction | ZIP with one synthetic member path designed for an authorized lab directory | Same member at archive root | Independent extraction effect; no webshell or existing-file overwrite. |
| Approval/preview state | Read own unapproved artifact through preview versus published route | Same flow after approved normal state | Actual intended reader policy, not simply a hidden link. |
| Revocation/deletion | Re-read the same controlled file after authorized revoke/delete | Fresh authorized access and an unrelated nonexistent id | Test original, preview and cache separately; a temporary leak can matter. |

A tiny SVG execution marker for a documented active-document surface:

```xml
<svg xmlns="http://www.w3.org/2000/svg" onload="document.documentElement.setAttribute('data-audit','AUDIT_MARKER')">
  <text x="1" y="20">AUDIT_UPLOAD</text>
</svg>
```

This is a conditional browser probe, not an assertion it runs in `<img>`, every viewer or every bucket.
Avoid third-party callbacks when a local DOM marker proves the same effect.
For a serving test, preserve the real navigation/embedding mode and reader credentials.

## Interpret browser origin correctly

SVG loaded as an image generally has different scripting behavior from a navigated active SVG document.
HTML/SVG hosted on a separate file origin does not automatically gain the application origin's authority.
A sandboxed viewer may have an opaque origin; inspect actual frame policy and script capabilities.
A forced attachment download and inline document are different delivery models.
PDF JavaScript is not interchangeable with page JavaScript and does not prove browser-origin XSS.
If the file origin is intentionally isolated, look for a separate proven trust bridge rather than inventing one.
Same-site cookies, CORS trust or parent-domain capabilities need their own valid browser proof.

## Processing and archives

Keep file containers valid while mutating the part actually consumed.
For OOXML, files such as `[Content_Types].xml` and `word/document.xml` must remain at the ZIP root with the original relationship structure.
Do not wrap the complete parts directory as a new archive member folder.
Use tiny files and a new synthetic extraction directory; exclude bombs and expansive recursive archives.
Path traversal entries, symlinks and filename collisions are different hypotheses with different extractor prerequisites.
A re-encoded image may remove active content; verify final bytes instead of assuming the original survives.
Use `xxe_all_types.md`, `ssrf_all_types.md` or `lfi_rfi_path_traversal.md` for the specific downstream mechanism.

## Server execution and restrictions

A PHP-like extension on static storage is not an interpreter boundary.
Uploading configuration files, webshells or persistent loaders is not a default proving step.
If permitted execution validation is necessary, use an inert non-persistent marker and a reachable known handler.
Record whether server behavior depends on a modified local handler/configuration; that does not prove a production exploit.
Do not equate extension allowlist bypass with RCE, stored XSS or full tenant takeover.

## Falsification and evidence

Save accepted bytes, normal control, storage identifier, served headers and actual browser/processor result.
Record reader role, origin, embedding mode, any user interaction and whether the content survives transformation.
Compare unrelated actor access with an existing owned fixture, not a guessed or empty file.
Test no-op upload, raw text rendering, sanitized/re-encoded content, isolated origin and approval policy as benign explanations.
Capture any unauthorized read/action during a processing window even if the final artifact is rejected.

Close only the tested representation/processor/reader state when the intended boundary holds.
Mark invalid document/unknown consumer or unavailable reader inconclusive.
Reopen for another view, processing worker, content type, owner/tenant transition or serving policy.

## References and freshness

Reviewed 2026-11-13. Examples require the observed file consumer; no universal MIME or extension bypass is promised.

- [PortSwigger file upload](https://portswigger.net/web-security/file-upload) — acceptance versus execution and differing server-side handling.
- [OWASP file upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) — storage, validation, filename and processing boundaries.
- [MDN Content-Disposition](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition) — attachment/inline response semantics.
