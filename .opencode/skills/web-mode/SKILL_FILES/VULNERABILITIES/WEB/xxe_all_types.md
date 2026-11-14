# XML external entities — separate parsing, resolution and disclosure

## Contents

- Boundary and discovery
- Controls and bounded proof material
- Payloads and paired experiments
- Office/archive correctness
- Evidence and interpretation
- References and freshness


## Boundary and discovery

Use for actual XML consumers: SOAP, SVG processing, XML imports, metadata, RSS and XML parts inside Office/EPUB archives.
The client accepting an XML-looking file is not evidence that its contents reach a permissive XML parser.
Trace upload/HTTP input → container unpacking → XML parser settings → entity resolver/XInclude → output or worker effect.
Parser language, library, version and explicit options matter more than a file extension.
An XML error is a lead, not proof of external entity access.

Write down:

- normal accepted document and the exact XML node consumed;
- whether DTD declarations are allowed, loaded and expanded;
- external general versus parameter entities and their distinct references;
- whether XInclude processing runs at all;
- parser-visible base URI, resolver/catalog and network restrictions;
- which actor can retrieve or render the result.

## Controls and bounded proof material

Keep a valid unmodified document as the first control.
Use a tiny researcher-controlled resource returning `AUDIT_XML_MARKER`; use unique path tokens for external requests.
Use a program-provided synthetic local file only when file access testing is authorized.
Do not read password databases or environment files merely to prove entity expansion.
Do not use entity expansion bombs, compressed bombs or expensive recursive resolution.
Place a DTD after an XML declaration and before the root; maintain XML well-formedness.

## Payloads and paired experiments

Substitute actual expected root/node names. The following tiny XML is for a feature that normally accepts `<audit>`.

```xml
<?xml version="1.0"?>
<!DOCTYPE audit [<!ENTITY marker "AUDIT_XML_MARKER">]>
<audit>&marker;</audit>
```

This tests internal entity expansion only. It does not prove external access.
For permitted controlled HTTP resolution:

```xml
<?xml version="1.0"?>
<!DOCTYPE audit [<!ENTITY marker SYSTEM "https://canary.example.invalid/xml/a1">]>
<audit>&marker;</audit>
```

Use a real controlled endpoint in place of `.invalid`; no request can reach the placeholder.
A remote DTD-only discriminator uses a parameter entity:

```xml
<!DOCTYPE audit [
  <!ENTITY % remote SYSTEM "https://canary.example.invalid/dtd/a1.dtd">
  %remote;
]>
<audit>AUDIT_LITERAL</audit>
```

The controlled DTD can be empty or contain `<!ENTITY marker "AUDIT_XML_MARKER">`.
Use `&marker;` in the XML only if that general entity is actually declared and intended for the test.
Do not confuse a `%name;` parameter entity fetched inside the DTD with an `&name;` general entity in document content.

| Question | Challenge | Control | Interpretation |
|---|---|---|---|
| Is this XML part consumed? | Change a normal harmless node to `AUDIT_LITERAL_B` | Valid original document | Output follows the changed node; otherwise the parser hypothesis is unproven. |
| Are internal entities expanded? | Internal entity example above | Literal `AUDIT_XML_MARKER` in the same node | Expansion establishes DTD/entity processing, not external retrieval. |
| Is an external DTD loaded? | Unique controlled parameter-entity URL | Same well-formed document without `%remote;` | Correlated request proves DTD load; a later parse error does not erase that narrower event. |
| Is external general entity content exposed? | External entity body `AUDIT_XML_MARKER` | Literal body and independent direct fetch of the canary | Returned marker proves expansion/visibility; DNS alone does not. |
| Is XInclude processed? | `<audit xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include href="https://canary.example.invalid/text/a1" parse="text"/></audit>` | Same namespace plus ordinary literal child | Requires an XInclude-processing step; blocking DOCTYPE does not imply XInclude runs. |
| Do async consumers differ? | Same tiny document through permitted preview and export workers | Normal document in each | Identify the actual permissive worker and result visibility, not only the upload response. |

## Office/archive correctness

Maintain original ZIP member paths such as `[Content_Types].xml` and `word/document.xml` at the archive root.
Do not repackage a `doc/` directory itself as the root; a corrupt OOXML file tests container validation instead.
Modify only the XML part the normal consumer reads; preserve relationships and required namespaces.
A local packaging example for an owned fixture is:

```python
from pathlib import Path
from zipfile import ZipFile
root = Path("owned_document_parts")
with ZipFile("owned_audit.docx", "w") as archive:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(root).as_posix())
```

Verify member names and that the normal application can still open the modified fixture.
An SVG displayed by the browser and an SVG rasterized server-side are separate XML consumers.
The input `Content-Type` and parser options can differ between import, thumbnail and export paths.

## Evidence and interpretation

Save valid-control acceptance, exact document bytes/container member, parser result and controlled logs.
Distinguish DTD recognition, HTTP/DNS resolution, entity expansion, local-file read and data exposure.
Attribute callbacks against link scanners, antivirus and format-validation services.
A 202 response may only enqueue processing; capture the worker's result or allowed observation.
Keep failed document parsing after a successful external request as a partial capability, not a complete negative.
No generic chain from XXE to assertion forgery or host code execution is implied.

Close only the tested parser/options/consumer if the relevant boundary is enforced with a valid document.
Reopen for a different XML part, explicit parser option, XInclude consumer or asynchronous transformation.

## References and freshness

Reviewed 2026-11-13; examples are bounded source-backed probes, not claims about every XML library.

- [PortSwigger XXE](https://portswigger.net/web-security/xxe) — entity mechanisms, blind channels and alternative XML consumers.
- [OWASP XXE prevention](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html) — per-parser options and external resolution controls.
- [Python XML modules](https://docs.python.org/3/library/xml.html) — parser-specific interfaces and XML security guidance; Python is not a universal XML behavior model.
