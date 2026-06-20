import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * <sx-tag tone="muted">keyword</sx-tag>
 *
 * Keyword tag refined from `sx-chip`: same token-driven pill, but a dedicated
 * primitive so tag-specific behaviour stays out of the generic chip. Today the
 * archive renders tags as muted chips (search_view.py); this adds an optional
 * `removable` affordance that emits a composed `sx-tag-remove` CustomEvent.
 * Label text stays in the light-DOM slot for i18n.
 */
@customElement("sx-tag")
export class SxTag extends LitElement {
  @property({ reflect: true })
  tone: "neutral" | "info" | "success" | "engine" | "muted" = "muted";

  @property({ type: Boolean, reflect: true })
  removable = false;

  /** Accessible label for the remove button; pass a translated string. */
  @property({ attribute: "remove-label" })
  removeLabel = "Remove";

  static styles = css`
    :host {
      display: inline-flex;
    }
    .tag {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font: 12px/1 system-ui, Arial, sans-serif;
      padding: 3px 8px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--muted, #64748b);
      border: 1px solid transparent;
      white-space: nowrap;
    }
    :host([tone="neutral"]) .tag {
      color: var(--text, #0f172a);
    }
    :host([tone="info"]) .tag {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
    }
    :host([tone="success"]) .tag {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
    }
    :host([tone="engine"]) .tag {
      background: var(--surface-2, #f1f5f9);
      color: var(--text, #0f172a);
      border-color: var(--line, #cbd5e1);
    }
    .remove {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 14px;
      height: 14px;
      margin-right: -2px;
      padding: 0;
      border: none;
      border-radius: 50%;
      background: transparent;
      color: inherit;
      font: inherit;
      line-height: 1;
      cursor: pointer;
      opacity: 0.7;
    }
    .remove:hover {
      opacity: 1;
      background: color-mix(in srgb, currentColor 18%, transparent);
    }
    .remove:focus-visible {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }
  `;

  private _remove() {
    this.dispatchEvent(
      new CustomEvent("sx-tag-remove", { bubbles: true, composed: true }),
    );
  }

  render() {
    return html`<span class="tag" part="tag">
      <slot></slot>
      ${this.removable
        ? html`<button
            class="remove"
            part="remove"
            type="button"
            aria-label=${this.removeLabel}
            @click=${this._remove}
          >
            &times;
          </button>`
        : null}
    </span>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-tag": SxTag;
  }
}
