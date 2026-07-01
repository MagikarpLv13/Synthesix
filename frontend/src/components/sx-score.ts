import { LitElement, html, css, type PropertyValues } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * <sx-score level="good">7.80</sx-score>
 *
 * Compact relevance-score pill, ported from `score_badge()` (ui.py). The
 * value comes from the default slot (tabular figures). Pass `tip` plus a
 * `breakdown` slot (a light-DOM `<ul>`) and optional `note` slot to reveal
 * the scoring reasoning in a hover/focus tooltip — mirrors the Python
 * two-path behaviour after the Lot 7 UX change from a clickable `<details>`
 * to an always-in-DOM tooltip (screen-reader readable without interaction).
 * Theming via inherited tokens, slotted content stays in light DOM for i18n.
 */
@customElement("sx-score")
export class SxScore extends LitElement {
  @property({ reflect: true })
  level: "none" | "strong" | "good" | "moderate" | "weak" = "none";

  @property({ type: Boolean, reflect: true })
  tip = false;

  static styles = css`
    :host {
      display: inline-flex;
      align-items: center;
    }

    :host([tip]) {
      position: relative;
      cursor: help;
      outline: none;
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

    :host([tip]:focus-visible) .value {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .tooltip {
      position: absolute;
      z-index: 40;
      top: calc(100% + 6px);
      right: 0;
      width: max-content;
      max-width: 380px;
      padding: 8px 10px;
      text-align: left;
      background: var(--surface, #ffffff);
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-sm, 6px);
      box-shadow: var(--shadow-soft, 0 8px 24px rgba(15, 23, 42, 0.12));
      opacity: 0;
      visibility: hidden;
      transform: translateY(-3px);
      transition: opacity 120ms ease, transform 120ms ease,
        visibility 0s linear 120ms;
      pointer-events: none;
    }

    :host([tip]:hover) .tooltip,
    :host([tip]:focus) .tooltip,
    :host([tip]:focus-within) .tooltip {
      opacity: 1;
      visibility: visible;
      transform: translateY(0);
      transition: opacity 120ms ease, transform 120ms ease;
    }
  `;

  protected updated(changed: PropertyValues) {
    if (changed.has("tip")) this.tabIndex = this.tip ? 0 : -1;
  }

  render() {
    const value = html`<span class="value" part="value"><slot></slot></span>`;
    if (!this.tip) return value;
    return html`
      ${value}
      <span class="tooltip" part="tooltip" role="tooltip">
        <slot name="breakdown"></slot>
        <slot name="note"></slot>
      </span>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-score": SxScore;
  }
}
