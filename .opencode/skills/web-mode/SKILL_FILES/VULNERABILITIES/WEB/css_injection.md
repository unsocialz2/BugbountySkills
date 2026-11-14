# CSS injection — rendering authority and conditional network effects

## Contents

- Boundary and discovery
- Controlled experiment matrix
- Contextual payloads
- Interpretation, limits and evidence
- Primary sources

## Boundary and discovery

Trace attacker-controlled theme/style/template content into a real CSS consumer.
Distinguish a declaration value, style attribute, stylesheet rule, imported URL,
and HTML breakout. A style attribute cannot simply accept a stylesheet selector;
a `<style>` breakout tests the HTML parser instead. Harmless styling is a lead,
not JavaScript execution or arbitrary DOM reading.

Record the victim route/origin, who can supply the style, who renders it, the
sanitizer transformations, CSP style-src/style-src-attr/style-src-elem and image/
font/connect request policies, actual browser and available selectors/functions.
Do not infer that a CSP preventing script also prevents CSS-based disclosure.

Start with a distinctive outline on a researcher-owned fixture and compare an
inert value. Confirm computed style on the actual consumer. For blind rendering,
use at most a unique controlled callback with synthetic data and attribution to
the renderer; a security scanner fetching a URL is not conditional DOM inference.

## Controlled experiment matrix

| Question | Normal/control and minimal probe | Discriminator |
|---|---|---|
| CSS or literal text? | A valid color/outline vs the same value escaped/inert | Computed style changed in the real victim view, not just the returned string. |
| Selector or declaration context? | A property value vs a new declaration vs a full rule in a local fixture | Determine grammar accepted before adapting payloads; do not spray rules into every input. |
| HTML escape hatch? | Style-only canary vs closing the style element with an inert span marker | If a new HTML node appears, route HTML/XSS reasoning separately; no script execution is implied. |
| Conditional DOM attribute read? | Two otherwise identical synthetic pages with AUDIT_A/AUDIT_B attributes | Only the corresponding predicate should trigger the canary effect; unconditional URL loading is not a leak. |
| Attribute vs live property? | Change setAttribute('value',...) vs input.value in a fixture | Attribute selectors match attributes; ordinary typing may change a property without changing the attribute. |
| Reach and egress? | An allowed same-origin canary then one policy-approved controlled external image URL | CSP, network policy or hidden/non-rendered elements may prevent requests despite selector matching. |
| Persistence/other user? | Own editor vs separate owned viewer/session opening the saved artifact | Self-styling does not establish a cross-user boundary; identify actual victim reach. |
| New CSS feature? | CSS.supports and a positive local example for the exact function syntax | Lack of feature support is a blocked technique in this browser, not proof no CSS injection exists. |

## Contextual payloads

### Declaration-level rendering marker

```css
outline: 3px solid rgb(17, 123, 201);
```

This is a declaration for a compatible style sink, not a universal value payload.
Use a normal style value as the baseline and inspect the computed property.

### Rule-level synthetic attribute predicate

Prepare **only in the owned local fixture**:

```html
<div class="audit-box" data-audit="AUDIT_A">Synthetic canary</div>
```

```css
.audit-box[data-audit="AUDIT_A"] {
  background-image: url("/audit-pixel?case=A");
}
.audit-box[data-audit="AUDIT_B"] {
  background-image: url("/audit-pixel?case=B");
}
```

Serve both canary image routes from the local fixture. Switch the synthetic
attribute and show that the observed request switches accordingly. A URL request
alone, without this paired predicate control, only establishes fetching. Keep
requests unique to avoid cache suppression. Do not enumerate real token values.

### Modern inline-style research

Recent conditional CSS/typed attr research can work in contexts where whole
stylesheet injection is unavailable. First test feature support and permissible
value types in the observed browser. Do not copy an `if()`/`image-set()` chain
from a different build and label all inline styles exploitable. A source example
is mechanism evidence, not a cross-browser validation result for this target.

## Interpretation, limits and evidence

CSS selectors do not grant general reads of text nodes or JavaScript variables.
A browser may restrict URL use through attr() or policy. A selector on an element
that does not render a background may require a visible fixture relationship;
that is a prerequisite, not an automatic bypass. Do not use old IE CSS execution
constructs as modern browser payloads.

Preserve source→transform→CSS parser, actual generated DOM/attributes, computed
style or conditional request pairs, attacker/victim roles, origin, browser build,
CSP and egress, and the synthetic secret/negative control. Distinguish UI effect,
conditional attribute inference, and a separately proven reusable capability.

Close only the tested consumer/grammar/browser; reopen for another real rendering
surface, changed stylesheet policy, or supported browser primitive. No customer
secret extraction or persistent content poisoning is necessary for the canary.
The examples here were authored for controlled fixtures; execution support is
reported by the accompanying tests, not inferred from being printed in a guide.

## Primary sources

Sources consulted 2026-11-13; historical research is scoped to its browsers and
preconditions, not asserted as a current universal bypass.

- [PortSwigger blind CSS research](https://portswigger.net/research/blind-css-exfiltration) — conditional selectors and HTML-only disclosure boundary.
- [PortSwigger inline-style research](https://portswigger.net/research/inline-style-exfiltration) — newer conditional/function attack surface, with browser-specific constraints.
- [MDN attribute selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Attribute_selectors) — matching actual attributes and selector operators.
- [OWASP CSS injection testing](https://wstg.owasp.org/v4.1/4-Web_Application_Security_Testing/11-Client_Side_Testing/05-Testing_for_CSS_Injection/) — identifying CSS input-to-consumer paths; its legacy-browser examples must not be generalized.
