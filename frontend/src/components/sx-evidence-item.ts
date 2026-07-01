import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * <sx-evidence-item class="evidence-item" data-evidence-id="...">
 *
 * Tag-only wrapper for one evidence capture row, ported from
 * `_evidence_markup()` (investigations/view.py). Already flat and
 * class-driven (`.evidence-body`, `.evidence-row`) — no wrapper chrome to
 * factor into Shadow DOM. Renders as a child of `<ul class="evidence-list">`
 * (`list-style: none` already applies to the parent, so the native `<li>`
 * box type isn't relied upon). Classes, `data-*` attributes and injected JS
 * bindings are unchanged.
 */
@customElement("sx-evidence-item")
export class SxEvidenceItem extends LitElement {
  render() {
    return html`<slot></slot>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-evidence-item": SxEvidenceItem;
  }
}
