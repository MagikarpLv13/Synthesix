import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * <sx-score level="good">7.80</sx-score>
 *
 * Compact relevance-score pill, ported from `score_badge()` (ui.py). The value
 * comes from the default slot (tabular figures); pass `expandable` plus a
 * `breakdown` slot (`<li>` items) and optional `note` slot to make it an
 * inline <details> that reveals the reasoning — mirroring the Python two-path
 * behaviour. Theming via inherited tokens, value text stays in light DOM.
 */
@customElement("sx-score")
export class SxScore extends LitElement {
  @property({ reflect: true })
  level: "none" | "strong" | "good" | "moderate" | "weak" = "none";

  @property({ type: Boolean, reflect: true })
  expandable = false;

  static styles = css`
    :host {
      display: inline-block;
    }

    .value {
      display: inline-block;
      font-variant-numeric: tabular-nums;
      font-weight: 600;
      font-size: 13px;
      padding: 3px 9px;
      border-radius: var(--radius-sm, 6px);
      background: var(--surface-2, #f1f5f9);
      color: var(--text, #0f172a);
      border: 1px solid var(--line, #cbd5e1);
    }

    :host([level="strong"]) .value {
      background: var(--success-soft, #dcfce7);
      color: var(--success-ink, #166534);
      border-color: transparent;
    }

    :host([level="good"]) .value {
      background: var(--accent-soft, #dbeafe);
      color: var(--accent-ink, #1d4ed8);
      border-color: transparent;
    }

    :host([level="moderate"]) .value {
      background: var(--warning-soft, #fef3c7);
      color: var(--warning-ink, #92400e);
      border-color: transparent;
    }

    details.score {
      display: inline-block;
    }

    summary {
      list-style: none;
      cursor: pointer;
    }

    summary::-webkit-details-marker {
      display: none;
    }

    summary:focus-visible .value {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .list {
      margin: 8px 0 4px;
      padding-left: 18px;
      font-size: 12px;
      color: var(--muted, #64748b);
    }

    .note {
      display: block;
      font-size: 11px;
      color: var(--muted, #64748b);
    }

    ::slotted([slot="note"]) {
      color: var(--muted, #64748b);
    }
  `;

  render() {
    const value = html`<span class="value" part="value"><slot></slot></span>`;
    if (!this.expandable) {
      return html`<span class="score" part="score">${value}</span>`;
    }
    return html`
      <details class="score" part="score">
        <summary part="summary">${value}</summary>
        <ul class="list" part="breakdown">
          <slot name="breakdown"></slot>
        </ul>
        <small class="note" part="note">
          <slot name="note"></slot>
        </small>
      </details>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-score": SxScore;
  }
}
