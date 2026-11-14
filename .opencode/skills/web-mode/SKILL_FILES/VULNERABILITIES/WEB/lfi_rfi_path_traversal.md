# Path traversal and file inclusion — identify read, write and evaluation separately

## Boundary and discovery

Use for downloads, attachments, themes/templates, localization, static asset routes, archive extraction and import paths.
Map user reference → decode/normalization → base directory/lookup → resolved filesystem object → operation → response.
A filename field justifies a small path-handling probe; it does not establish filesystem access.
Read-file APIs and language `include`/template loaders have different authority and execution semantics.
An absolute path accepted as a string is not proof that the server opened it.

Record:

- logical resource mapping versus raw filesystem path;
- base directory and platform separators if known;
- path existence and owner/tenant identity for controlled fixtures;
- read, write, delete, extract, template-evaluate or redirect behavior;
- symlink/canonicalization point and checks before versus after resolution;
- actual output channel and content handling.

## Valid normal fixture

Prefer a program-provided synthetic file outside the allowed base, or an authorized local mirror.
For a lab, create `allowed/a.txt` containing `AUDIT_ALLOWED` and sibling `outside/marker.txt` containing `AUDIT_OUTSIDE`.
Prove legitimate read of `a.txt` through the normal route.
Do not use a nonexistent filename's 404 as evidence that ownership/path controls work.
Maintain equal file content/types where comparing route authorization rather than parser behavior.
For writes/extraction use a new temporary directory and synthetic files only.

## Payloads and differential experiments

These are values before normal transport encoding. Depth and path names must come from the actual fixture layout.

| Hypothesis | Challenge | Control | Decisive evidence |
|---|---|---|---|
| Parent traversal reaches outside base | `../outside/marker.txt` | `a.txt` and a nonexistent sibling name | Exact outside synthetic marker returned, not an error containing the supplied path. |
| Decode order differs | `..%2Foutside%2Fmarker.txt` | Raw traversal and a literal `%2F` filename in a lab | Identify how many actual decode steps occur; URL encoding is not itself filesystem syntax. |
| Platform separator mismatch | `..\outside\marker.txt` only for an observed Windows-compatible parser | Slash form and normal file | Same outside fixture reached after normalization; do not assume Windows behavior on Linux. |
| Filter removes a single token | `....//outside/marker.txt` | `../outside/marker.txt` and an inert filename | Only meaningful if evidence shows one-pass removal yielding traversal. |
| Absolute path overrides join base | Absolute path to the synthetic outside marker | Absolute allowed fixture plus relative allowed path | Resolved target and readback demonstrate the base was discarded. |
| Symlink check/use mismatch | Authorized lab symlink from allowed directory to synthetic outside marker | Ordinary allowed file and an explicitly rejected outside path | Canonical target policy differs from lexical check; avoid changing target symlinks without permission. |
| Archive member escape | Tiny archive with one synthetic traversal member | Archive with the same content in an ordinary member | Independent safe extraction log/result shows actual escape; accepting a ZIP is not enough. |
| Inclusion versus plain read | A harmless template expression in an owned include fixture, only when source supports inclusion | Same file read as plain text | Evaluation is a separate boundary, not an automatic result of traversal. |

Double decoding and historical null-byte/overlong-UTF-8 techniques require a matching decoder/version.
Do not list obsolete encodings as universal bypasses; malformed encoding rejection is a valid narrow result.
`~` expansion is shell behavior in some contexts, not a general filesystem lookup property.
A URL fragment is normally not sent in HTTP and is not automatically a filename suffix bypass.

## Read versus include versus write

A download endpoint returning bytes does not execute embedded PHP or templates.
PHP wrappers depend on the specific file API, wrapper registration, runtime version and configuration.
A wrapper-looking string may be interpreted as a literal path or rejected before the file API.
Use an owned harmless fixture to compare plain content and any documented transformation.
Do not jump from file read to log poisoning, credentials, SSH access or command execution.
A write primitive needs proof of the resolved path, overwrite behavior and affected authority.
An archive symlink and a traversal entry are different extraction mechanisms; test each only if the extractor supports it.

## Object authorization and lifecycle

Some apparent traversal bugs are resource-ID authorization failures; preserve the ownership control.
Compare read permissions on the actual resolved object, not only on the original route parent.
Attachment downloads and exports can bypass tenant policy even when filesystem confinement holds.
A file deleted or revoked in the authoritative store may remain accessible in a cache; characterize that lifecycle separately.
If race conditions are suspected, record the check and operation states and any effect during the window.
A final rollback does not erase a demonstrated unauthorized read.

## Falsification and evidence

Save normal allowed access, exact encoded input, raw response and independent synthetic file content.
Where permitted, capture the resolved-path trace in a lab without changing the production path policy.
Reject reflected filenames, generic errors, content from a fallback file and local browser file loads as read proof.
Do not generalize a blocked slash form to backslashes, another decoder or another file consumer without evidence.
A path normalization difference needs a protected file/action consequence before reporting it as a vulnerability.

Close only the exact route/platform/operation where realpath or logical lookup confinement holds.
Mark unknown file existence, invalid archives and unavailable output inconclusive.
Reopen for an observed second consumer, alternate representation, extraction mode or symlink behavior.

## References and freshness

Reviewed 2026-11-13. Paths are synthetic and context-dependent; legacy runtime behavior must be independently established.

- [PortSwigger path traversal](https://portswigger.net/web-security/file-path-traversal) — confinement, decoding and route-specific testing.
- [OWASP path traversal](https://owasp.org/www-community/attacks/Path_Traversal) — path manipulation and filesystem boundary model.
- [OWASP file upload prevention](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) — filename/storage and archive-processing considerations.

Use `file_upload_bypass.md` for serving/rendering/processor trust and `race_conditions.md` for concurrent check/use boundaries.
