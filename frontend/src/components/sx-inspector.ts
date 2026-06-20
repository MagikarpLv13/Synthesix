import { LitElement, html, css, type PropertyValues } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * <sx-inspector> — list ↔ detail workspace primitive (investigation inspector).
 *
 * Layout-and-state only, unopinionated about item markup:
 *  - Put selectable rows in `slot="list"`, each tagged `data-inspector-item="<id>"`.
 *  - Put detail panels in `slot="detail"`, each tagged `data-inspector-panel="<id>"`.
 * The component keeps `selected` in sync: it marks the active row
 * (`aria-current="true"` + roving tabindex), shows the matching panel (hiding
 * the rest), exposes keyboard navigation (arrows / Home / End, selection follows
 * focus) and emits `sx-inspector-select` `{ value, previous }`. On narrow
 * viewports it collapses to a single pane with a Back control (`pane` attribute).
 * Row/panel content stays in light DOM for i18n and existing scripts.
 */
@customElement("sx-inspector")
export class SxInspector extends LitElement {
  @property({ reflect: true })
  selected = "";

  @property({ reflect: true })
  pane: "list" | "detail" = "list";

  /** Accessible label for the narrow-mode Back button; pass a translated string. */
  @property({ attribute: "back-label" })
  backLabel = "Back to list";

  static styles = css`
    :host {
      display: block;
    }
    .frame {
      display: grid;
      grid-template-columns: minmax(220px, 320px) 1fr;
      gap: var(--space-4, 16px);
      align-items: start;
    }
    .list {
      display: flex;
      flex-direction: column;
      gap: var(--space-2, 8px);
      min-width: 0;
    }
    .list-body {
      display: flex;
      flex-direction: column;
      gap: 6px;
      min-width: 0;
      max-height: var(--sx-inspector-list-h, 70vh);
      overflow: auto;
    }
    .detail {
      min-width: 0;
    }
    .detail-header {
      display: flex;
      align-items: center;
      gap: var(--space-2, 8px);
      margin-bottom: var(--space-2, 8px);
    }
    .detail-header:empty {
      display: none;
    }
    .header {
      font-size: 13px;
      font-weight: 600;
      color: var(--muted, #64748b);
    }
    .back {
      display: none;
      align-items: center;
      gap: 4px;
      font: inherit;
      font-size: 13px;
      padding: 4px 8px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-sm, 6px);
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      cursor: pointer;
    }
    .back:hover {
      border-color: var(--accent, #2563eb);
    }
    .back:focus-visible {
      outline: none;
      box-shadow: var(--focus, 0 0 0 3px rgba(37, 99, 235, 0.24));
    }
    ::slotted([data-inspector-item]) {
      cursor: pointer;
    }
    @media (max-width: 720px) {
      .frame {
        grid-template-columns: 1fr;
      }
      :host([pane="list"]) .detail {
        display: none;
      }
      :host([pane="detail"]) .list {
        display: none;
      }
      .back {
        display: inline-flex;
      }
    }
  `;

  private get _items(): HTMLElement[] {
    return Array.from(
      this.querySelectorAll<HTMLElement>("[data-inspector-item]"),
    );
  }

  private get _panels(): HTMLElement[] {
    return Array.from(
      this.querySelectorAll<HTMLElement>("[data-inspector-panel]"),
    );
  }

  private _valueOf(item: HTMLElement): string {
    return item.getAttribute("data-inspector-item") ?? "";
  }

  protected firstUpdated() {
    if (!this.selected) {
      const first = this._items[0];
      if (first) this.selected = this._valueOf(first);
    }
    this._sync();
  }

  protected updated(changed: PropertyValues) {
    if (changed.has("selected")) this._sync();
  }

  /** Re-apply active row + visible panel state to the light-DOM children. */
  private _sync() {
    const value = this.selected;
    for (const item of this._items) {
      const active = this._valueOf(item) === value;
      if (active) item.setAttribute("aria-current", "true");
      else item.removeAttribute("aria-current");
    }
    for (const panel of this._panels) {
      panel.hidden =
        panel.getAttribute("data-inspector-panel") !== value;
    }
  }

  private _select(value: string, focusRow = false) {
    if (value === this.selected) {
      this.pane = "detail";
      return;
    }
    const previous = this.selected;
    this.selected = value;
    this.pane = "detail";
    this.dispatchEvent(
      new CustomEvent("sx-inspector-select", {
        detail: { value, previous },
        bubbles: true,
        composed: true,
      }),
    );
    if (focusRow) {
      this.updateComplete.then(() => {
        const row = this._items.find((i) => this._valueOf(i) === value);
        row?.focus();
      });
    }
  }

  private _onListClick(event: Event) {
    const target = event.target as HTMLElement | null;
    const item = target?.closest<HTMLElement>("[data-inspector-item]");
    if (item && this.contains(item)) this._select(this._valueOf(item));
  }

  private _onListKeydown(event: KeyboardEvent) {
    const keys = ["ArrowDown", "ArrowUp", "Home", "End"];
    if (!keys.includes(event.key)) return;
    const items = this._items;
    if (!items.length) return;
    const current = items.findIndex(
      (i) => this._valueOf(i) === this.selected,
    );
    let next = current;
    if (event.key === "ArrowDown") next = Math.min(items.length - 1, current + 1);
    else if (event.key === "ArrowUp") next = Math.max(0, current - 1);
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = items.length - 1;
    if (next !== current) {
      event.preventDefault();
      this._select(this._valueOf(items[next]), true);
    }
  }

  private _onBack() {
    this.pane = "list";
    this.updateComplete.then(() => {
      const row = this._items.find((i) => this._valueOf(i) === this.selected);
      row?.focus();
    });
  }

  private _onSlotChange() {
    if (!this.selected) {
      const first = this._items[0];
      if (first) {
        this.selected = first.getAttribute("data-inspector-item") ?? "";
        return; // updated() will sync
      }
    }
    this._sync();
  }

  render() {
    return html`
      <div class="frame" part="frame">
        <div class="list" part="list">
          <div class="header" part="list-header"><slot name="list-header"></slot></div>
          <div
            class="list-body"
            @click=${this._onListClick}
            @keydown=${this._onListKeydown}
          >
            <slot name="list" @slotchange=${this._onSlotChange}></slot>
          </div>
        </div>
        <div class="detail" part="detail">
          <div class="detail-header" part="detail-header">
            <button
              class="back"
              part="back"
              type="button"
              aria-label=${this.backLabel}
              @click=${this._onBack}
            >
              ‹ <slot name="back-label">Back</slot>
            </button>
            <div class="header"><slot name="detail-header"></slot></div>
          </div>
          <div class="detail-body" part="detail-body">
            <slot name="detail" @slotchange=${this._onSlotChange}></slot>
          </div>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-inspector": SxInspector;
  }
}
