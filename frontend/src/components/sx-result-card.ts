import { LitElement, html, css, type PropertyValues } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * Search-engine-style result row (Google/DuckDuckGo-like).
 *
 * Layout: a top source line (letter avatar + site name, with the engine badge
 * and score on the right), a prominent blue link title, a small grey URL
 * breadcrumb under the title, then a muted snippet. Query matches in the title
 * and snippet are bolded by the caller via `<b>`. The primary link and any
 * actions stay in light-DOM slots so existing generated-page scripts keep
 * querying `[data-triage-link]` without piercing Shadow DOM.
 */
@customElement("sx-result-card")
export class SxResultCard extends LitElement {
  /** Kept for API compatibility; score is conveyed by the slotted score badge. */
  @property({ reflect: true })
  accent: "none" | "strong" | "good" | "moderate" | "weak" = "none";

  /**
   * Opt the host into keyboard triage: adds `data-triage-item` and makes the
   * host focusable so the generated-page navigation (`j`/`k`/`Enter`) and the
   * focus ring work, mirroring the Python `result_card(triage=True)` default.
   */
  @property({ type: Boolean, reflect: true })
  triage = false;

  static styles = css`
    :host {
      display: block;
      max-width: 680px;
      margin-bottom: 8px;
      outline: none;
    }

    .card {
      padding: 6px 8px;
      border-radius: var(--radius-sm, 6px);
      font-family: system-ui, Arial, sans-serif;
      transition: background-color 120ms ease;
    }

    :host(:hover) .card {
      background: var(--surface-2, #f1f5f9);
    }

    :host(:focus-visible) .card,
    :host(:focus) .card {
      background: var(--surface-2, #f1f5f9);
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .source {
      display: flex;
      align-items: center;
      gap: var(--space-2, 8px);
      min-width: 0;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
      margin-left: auto;
      flex: 0 0 auto;
    }

    .title {
      margin: 3px 0 0;
      line-height: 1.3;
    }

    .breadcrumb {
      margin: 1px 0 0;
    }

    .snippet {
      margin: 3px 0 0;
    }

    .extra {
      display: contents;
    }

    ::slotted([slot="favicon"]) {
      flex: 0 0 auto;
      display: inline-grid;
      place-items: center;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: var(--surface-2, #f1f5f9);
      border: 1px solid var(--line, #cbd5e1);
      color: var(--muted, #64748b);
      font: 700 11px system-ui, Arial, sans-serif;
    }

    ::slotted([slot="source"]) {
      min-width: 0;
      overflow: hidden;
      color: var(--text, #0f172a);
      font-size: 13px;
      line-height: 1.3;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    ::slotted([slot="title"]) {
      color: var(--accent, #2563eb);
      font-size: 18px;
      font-weight: 400;
      overflow-wrap: anywhere;
      text-decoration: none;
    }

    ::slotted([slot="title"]:hover) {
      text-decoration: underline;
    }

    ::slotted([slot="domain"]) {
      display: block;
      min-width: 0;
      overflow: hidden;
      color: var(--muted, #64748b);
      font-size: 12px;
      line-height: 1.3;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    ::slotted([slot="snippet"]) {
      margin: 0;
      color: var(--muted, #64748b);
      font-size: 14px;
      line-height: 1.45;
      overflow-wrap: anywhere;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
  `;

  protected willUpdate(changed: PropertyValues) {
    if (changed.has("triage")) {
      if (this.triage) {
        this.setAttribute("data-triage-item", "");
        if (!this.hasAttribute("tabindex")) this.setAttribute("tabindex", "0");
      } else {
        this.removeAttribute("data-triage-item");
      }
    }
  }

  render() {
    return html`
      <article class="card" part="card">
        <div class="source" part="source">
          <slot name="favicon"></slot>
          <slot name="source"></slot>
          <span class="meta" part="meta"><slot name="meta"></slot></span>
        </div>
        <div class="title" part="title"><slot name="title"></slot></div>
        <div class="breadcrumb" part="breadcrumb"><slot name="domain"></slot></div>
        <div class="snippet" part="snippet"><slot name="snippet"></slot></div>
        <div class="extra" part="extra"><slot name="extra"></slot></div>
        <slot name="actions"></slot>
      </article>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-result-card": SxResultCard;
  }
}
