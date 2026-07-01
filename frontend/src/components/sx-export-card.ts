import { LitElement, html, css } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * <sx-export-card data-export-id="…">
 *   <strong slot="title">ZeroNeurone export</strong>
 *   <span slot="timestamp">1 Jul 2026, 13:24</span>
 *   <span slot="stat">14 nodes</span>
 *   <span slot="stat">9 links</span>
 *   <span slot="stat">0 assets</span>
 *   <span slot="description">curated entities or validated candidates</span>
 *   <a slot="link" href="…" download="…">…</a>
 *   <button slot="delete" class="delete-export">Delete export</button>
 * </sx-export-card>
 *
 * Shell + light-DOM slots, same pattern as <sx-saved-page-card>: every
 * translatable string and every JS-bound control (the delete button, the
 * download links) stays in light DOM so i18n and the inline CDP dispatch in
 * investigations/view.py keep working untouched. The Lit element only owns
 * the chrome — icon avatar, pill styling for the stats, and the link/delete
 * row layout.
 */
@customElement("sx-export-card")
export class SxExportCard extends LitElement {
  static styles = css`
    :host {
      display: block;
      border: 1px solid var(--line, #1e293b);
      border-radius: 10px;
      background: var(--surface, #0b1220);
      transition: border-color 120ms ease;
    }
    :host(:hover) {
      border-color: var(--accent, #6366f1);
    }
    .card {
      display: grid;
      gap: 10px;
      padding: 14px;
    }
    .head {
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }
    .icon-avatar {
      flex: 0 0 auto;
      display: grid;
      place-items: center;
      width: 30px;
      height: 30px;
      border-radius: 8px;
      background: color-mix(in srgb, var(--accent, #6366f1) 18%, transparent);
      color: var(--accent, #6366f1);
    }
    .icon-avatar svg {
      width: 17px;
      height: 17px;
    }
    .title-block {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 4px 10px;
      min-width: 0;
    }
    ::slotted([slot="title"]) {
      color: var(--text, #e2e8f0);
      font-size: 14px;
    }
    ::slotted([slot="timestamp"]) {
      color: var(--muted, #94a3b8);
      font-size: 12px;
    }
    .stats {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    ::slotted([slot="stat"]) {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 0 8px;
      border: 1px solid var(--line, #334155);
      border-radius: 6px;
      background: var(--surface-2, #172033);
      color: var(--muted, #94a3b8);
      font-size: 11px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    ::slotted([slot="description"]) {
      color: var(--muted, #94a3b8);
      font-size: 12px;
      font-style: italic;
    }
    .links {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
    }
    ::slotted([slot="link"]) {
      display: inline-flex !important;
      align-items: center;
      gap: 5px;
      height: 26px;
      padding: 0 10px;
      border: 1px solid var(--line, #334155);
      border-radius: 999px;
      background: var(--surface-2, #172033);
      color: var(--accent, #6366f1);
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      transition: border-color 120ms ease, background-color 120ms ease;
    }
    ::slotted([slot="link"]:hover) {
      border-color: var(--accent, #6366f1);
      background: color-mix(in srgb, var(--accent, #6366f1) 12%, transparent);
    }
    ::slotted([slot="link"]) svg {
      width: 13px;
      height: 13px;
    }
    ::slotted([slot="delete"]) {
      display: inline-flex !important;
      align-items: center;
      gap: 5px;
      height: 26px;
      padding: 0 10px;
      margin-left: auto;
      border: 1px solid color-mix(in srgb, var(--danger, #f87171) 45%, var(--line, #334155));
      border-radius: 999px;
      background: transparent;
      color: var(--danger, #f87171);
      font: inherit;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
    }
    ::slotted([slot="delete"]:hover) {
      background: color-mix(in srgb, var(--danger, #f87171) 10%, transparent);
    }
    ::slotted([slot="delete"]:disabled) {
      cursor: not-allowed;
      opacity: 0.5;
    }
    ::slotted([slot="delete"]) svg {
      width: 13px;
      height: 13px;
    }
  `;

  render() {
    return html`
      <article class="card" part="card">
        <div class="head">
          <span class="icon-avatar" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="4" rx="1"></rect>
              <path d="M5 8v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8"></path>
              <path d="M10 12h4"></path>
            </svg>
          </span>
          <div class="title-block">
            <slot name="title"></slot>
            <slot name="timestamp"></slot>
          </div>
        </div>
        <div class="stats">
          <slot name="stat"></slot>
        </div>
        <slot name="description"></slot>
        <div class="links">
          <slot name="link"></slot>
          <slot name="delete"></slot>
        </div>
      </article>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-export-card": SxExportCard;
  }
}
