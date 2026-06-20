import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * <sx-entity kind="email" confidence="92%" status="confirmed">
 *   alice@example.com
 *   <button slot="actions">…</button>
 *   <sx-tag slot="meta">leak</sx-tag>
 *   <sx-property slot="properties">…</sx-property>
 * </sx-entity>
 *
 * Graph-entity card, ported from `.graph-entity-card` / `.entity-value`: a kind
 * label + optional confidence in the head, the entity value (monospace), and
 * optional `meta` (tags) and `properties` slots. `status` drives the accent:
 * confirmed = solid secondary border, candidate = neutral, rejected = dimmed.
 * Value/labels stay in light DOM for i18n and existing graph scripts.
 */
@customElement("sx-entity")
export class SxEntity extends LitElement {
  /** Translated entity-type label, e.g. "Email", "Nom d'utilisateur". */
  @property()
  kind = "";

  /** Pre-formatted confidence, e.g. "92%" or "0.92". */
  @property()
  confidence = "";

  @property({ reflect: true })
  status: "candidate" | "confirmed" | "rejected" = "candidate";

  static styles = css`
    :host {
      display: block;
    }
    .entity {
      padding: 12px 14px;
      border: 1px solid var(--line, #cbd5e1);
      border-left: 4px solid var(--line, #cbd5e1);
      border-radius: var(--radius-md, 8px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
    }
    :host([status="confirmed"]) .entity {
      border-left-color: var(--secondary, #06b6d4);
    }
    :host([status="rejected"]) .entity {
      opacity: 0.65;
    }
    .head {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    .kind {
      color: var(--secondary, #06b6d4);
      font-size: 12px;
      font-weight: 700;
      text-transform: capitalize;
    }
    .confidence {
      color: var(--muted, #64748b);
      font-size: 11px;
    }
    .actions {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-left: auto;
    }
    .value {
      margin-top: 4px;
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 13px;
      color: var(--text, #0f172a);
      overflow-wrap: anywhere;
    }
    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .meta[hidden],
    .properties[hidden] {
      display: none;
    }
    .meta:not([hidden]),
    .properties:not([hidden]) {
      margin-top: 8px;
    }
    .properties {
      display: grid;
      gap: 4px;
    }
  `;

  private _onOptionalSlot(event: Event) {
    const slot = event.target as HTMLSlotElement;
    const wrapper = slot.parentElement;
    if (!wrapper) return;
    const filled = slot
      .assignedNodes({ flatten: true })
      .some(
        (node) =>
          node.nodeType === Node.ELEMENT_NODE ||
          (node.textContent ?? "").trim().length > 0,
      );
    wrapper.hidden = !filled;
  }

  render() {
    return html`
      <article class="entity" part="entity">
        <div class="head" part="head">
          <span class="kind" part="kind">${this.kind}</span>
          ${this.confidence
            ? html`<span class="confidence" part="confidence">${this.confidence}</span>`
            : null}
          <span class="actions" part="actions"><slot name="actions"></slot></span>
        </div>
        <div class="value" part="value"><slot></slot></div>
        <div class="meta" part="meta" hidden>
          <slot name="meta" @slotchange=${this._onOptionalSlot}></slot>
        </div>
        <div class="properties" part="properties" hidden>
          <slot name="properties" @slotchange=${this._onOptionalSlot}></slot>
        </div>
      </article>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-entity": SxEntity;
  }
}
