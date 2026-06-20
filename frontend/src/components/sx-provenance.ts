import { LitElement, html, css } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * <sx-provenance>
 *   <svg slot="icon">…</svg>
 *   <span slot="label">Found via</span>
 *   exact query
 * </sx-provenance>
 *
 * Inline origin strip, ported from `provenance()` (ui.py): a leading icon, a
 * muted label and an emphasized detail. All text stays in light-DOM slots for
 * i18n; theming via inherited tokens.
 */
@customElement("sx-provenance")
export class SxProvenance extends LitElement {
  static styles = css`
    :host {
      display: inline-flex;
    }
    .provenance {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      color: var(--muted, #64748b);
      min-width: 0;
    }
    .detail {
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    ::slotted([slot="icon"]) {
      width: 0.95em;
      height: 0.95em;
      flex: 0 0 auto;
    }
  `;

  render() {
    return html`<span class="provenance" part="provenance">
      <slot name="icon"></slot>
      <span class="label" part="label"><slot name="label"></slot></span>
      <span class="detail" part="detail"><slot></slot></span>
    </span>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-provenance": SxProvenance;
  }
}
