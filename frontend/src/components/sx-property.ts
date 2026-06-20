import { LitElement, html, css } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * <sx-property>
 *   <span slot="label">email</span>
 *   alice@example.com
 *   <button slot="actions">…</button>
 * </sx-property>
 *
 * Key/value property row, ported from `.graph-property-list li`: a label
 * column, a flexible value column and an optional trailing actions column. All
 * text stays in light-DOM slots for i18n; theming via inherited tokens.
 */
@customElement("sx-property")
export class SxProperty extends LitElement {
  static styles = css`
    :host {
      display: block;
    }
    .property {
      display: grid;
      grid-template-columns: minmax(100px, auto) minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
      font-size: 13px;
    }
    .label {
      color: var(--secondary, #06b6d4);
      text-transform: capitalize;
      overflow-wrap: anywhere;
    }
    .value {
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    .actions {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    @media (max-width: 540px) {
      .property {
        grid-template-columns: 1fr auto;
      }
      .label {
        grid-column: 1 / -1;
      }
    }
  `;

  render() {
    return html`<div class="property" part="property">
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="value" part="value"><slot></slot></span>
      <span class="actions" part="actions"><slot name="actions"></slot></span>
    </div>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-property": SxProperty;
  }
}
