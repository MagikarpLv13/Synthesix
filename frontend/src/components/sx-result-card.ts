import { LitElement, html, css, type PropertyValues } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * Dense search/result card shell.
 *
 * The primary link and actions stay in light DOM slots so existing generated
 * page scripts can keep querying `[data-triage-link]` and action buttons without
 * piercing Shadow DOM.
 */
@customElement("sx-result-card")
export class SxResultCard extends LitElement {
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
      outline: none;
    }

    .card {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: var(--space-4, 16px);
      padding: var(--space-3, 12px) var(--space-4, 16px);
      border: 1px solid var(--line, #cbd5e1);
      border-left: 3px solid var(--line, #cbd5e1);
      border-radius: var(--radius-md, 8px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      transition:
        border-color 120ms ease,
        box-shadow 120ms ease;
    }

    :host([accent="strong"]) .card {
      border-left-color: var(--success, #16a34a);
    }

    :host([accent="good"]) .card {
      border-left-color: var(--accent, #2563eb);
    }

    :host([accent="moderate"]) .card {
      border-left-color: var(--warning, #d97706);
    }

    :host([accent="weak"]) .card {
      border-left-color: var(--line, #cbd5e1);
    }

    :host(:hover) .card {
      border-color: var(--accent, #2563eb);
      box-shadow: var(--shadow-soft, 0 8px 22px rgba(15, 23, 42, 0.08));
    }

    :host(:focus-visible) .card,
    :host(:focus) .card {
      border-color: var(--accent, #2563eb);
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }

    .body {
      flex: 1 1 auto;
      min-width: 0;
    }

    .head {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 4px var(--space-3, 12px);
      min-width: 0;
    }

    .snippet {
      margin: 0;
    }

    .extra {
      display: contents;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: var(--space-2, 8px);
    }

    .actions {
      display: flex;
      flex: 0 0 auto;
      align-items: center;
      gap: 6px;
    }

    ::slotted([slot="title"]) {
      color: var(--text, #0f172a);
      font-size: 15px;
      font-weight: 500;
      overflow-wrap: anywhere;
      text-decoration: none;
    }

    ::slotted([slot="title"]:hover) {
      color: var(--accent, #2563eb);
      text-decoration: underline;
    }

    ::slotted([slot="domain"]) {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--muted, #64748b);
      font-size: 12px;
    }

    ::slotted([slot="snippet"]) {
      margin: 4px 0 8px;
      color: var(--muted, #64748b);
      font-size: 13px;
      line-height: 1.5;
      overflow-wrap: anywhere;
    }

    @media (max-width: 720px) {
      .card {
        flex-direction: column;
      }

      .actions {
        width: 100%;
      }
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
        <div class="body" part="body">
          <div class="head" part="head">
            <slot name="title"></slot>
            <slot name="domain"></slot>
          </div>
          <div class="snippet" part="snippet">
            <slot name="snippet"></slot>
          </div>
          <div class="extra" part="extra">
            <slot name="extra"></slot>
          </div>
          <div class="meta" part="meta">
            <slot name="meta"></slot>
          </div>
        </div>
        <div class="actions" part="actions">
          <slot name="actions"></slot>
        </div>
      </article>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-result-card": SxResultCard;
  }
}
