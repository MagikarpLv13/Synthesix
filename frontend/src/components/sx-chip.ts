import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * <sx-chip tone="info">Label</sx-chip>
 *
 * Reference pattern for every Synthesix Web Component (copy this structure):
 *  - Shadow DOM isolation (safe inside the overlay's host page).
 *  - Theming via inherited CSS custom properties (tokens) with fallbacks, so the
 *    same component works on app pages (theme.css provides tokens) and in the
 *    injected overlay (tokens.ts provides them).
 *  - Visible text comes from the light-DOM <slot> so i18n.js can translate it.
 */
@customElement("sx-chip")
export class SxChip extends LitElement {
  @property({ reflect: true })
  tone: "neutral" | "info" | "success" | "engine" | "muted" = "neutral";

  static styles = css`
    :host {
      display: inline-flex;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font: 12px/1 system-ui, Arial, sans-serif;
      padding: 4px 9px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--muted, #64748b);
      border: 1px solid transparent;
      white-space: nowrap;
    }
    :host([tone="info"]) .chip {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
    }
    :host([tone="success"]) .chip {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
    }
    :host([tone="engine"]) .chip {
      color: var(--text, #0f172a);
      border-color: var(--line, #cbd5e1);
    }
    :host([tone="muted"]) .chip {
      background: transparent;
    }
  `;

  render() {
    return html`<span class="chip"><slot></slot></span>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-chip": SxChip;
  }
}
