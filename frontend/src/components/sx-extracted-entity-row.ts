import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * <sx-extracted-entity-row class="entity-chip-row entity-item--{status}" ...>
 *
 * Tag-only wrapper for the extracted-entity triage row, ported from
 * `_extracted_entity_row()` (investigations/view.py). Unlike other `sx-*`
 * migrations, this block is already flat and fully class-driven (head/
 * fields/promote-form each carry their own layout classes) — there is no
 * wrapper chrome to factor into Shadow DOM. The component exists purely so
 * the block is a custom element rather than a plain `<div>`; all classes,
 * `data-*` attributes and injected JS bindings are unchanged.
 */
@customElement("sx-extracted-entity-row")
export class SxExtractedEntityRow extends LitElement {
  render() {
    return html`<slot></slot>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-extracted-entity-row": SxExtractedEntityRow;
  }
}
