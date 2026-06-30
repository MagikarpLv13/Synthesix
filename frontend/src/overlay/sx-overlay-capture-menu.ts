import { LitElement, html, css, unsafeCSS } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { tokensCss } from "../tokens";

type CaptureScope = "viewport" | "region";

interface GraphEntity {
  id: string;
  label: string;
}

interface CaptureAttach {
  entityId: string;
  propertyKey: string;
  propertyType: string;
}

@customElement("sx-overlay-capture-menu")
export class SxOverlayCaptureMenu extends LitElement {
  @property({ type: Boolean, reflect: true })
  open = false;

  /** Existing graph entities the capture can be attached to right away. */
  @property({ attribute: false })
  graphEntities: GraphEntity[] = [];

  /**
   * User-facing strings. They default to English but the host page (main.py via
   * i18n.js) can pass translated values — no copy is hard-coded in the markup,
   * per the overlay i18n convention shared with sx-overlay-action.
   */
  @property()
  placeholder = "Capture name (optional)";

  @property({ attribute: "name-label" })
  nameLabel = "Capture name";

  @property({ attribute: "viewport-label" })
  viewportLabel = "Visible area";

  @property({ attribute: "region-label" })
  regionLabel = "Select area";

  @property({ attribute: "attach-heading" })
  attachHeading = "Attach to entity (optional)";

  @property({ attribute: "choose-entity-label" })
  chooseEntityLabel = "Don't attach";

  @property({ attribute: "property-placeholder" })
  propertyPlaceholder = "Property name";

  @property({ attribute: "default-property-key" })
  defaultPropertyKey = "Capture écran";

  @state()
  private _selectedEntityId = "";

  static styles = css`
    ${unsafeCSS(tokensCss)}

    :host {
      box-sizing: border-box;
      display: none;
      position: absolute;
      right: 0;
      bottom: 50px;
      width: 220px;
      padding: 6px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: var(--radius-sm, 6px);
      background: var(--surface, #ffffff);
      box-shadow: 0 14px 32px rgba(15, 23, 42, 0.24);
      color: var(--text, #0f172a);
      font: 600 13px/1.25 system-ui, Arial, sans-serif;
    }

    :host([open]) {
      display: block;
    }

    input,
    select {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      margin-bottom: 5px;
      padding: 8px 9px;
      border: 1px solid var(--line, #cbd5e1);
      border-radius: 4px;
      background: var(--surface, #ffffff);
      color: var(--text, #0f172a);
      font: 500 13px/1.2 system-ui, Arial, sans-serif;
    }

    .attach {
      margin: 2px 0 6px;
      padding-top: 6px;
      border-top: 1px solid var(--line, #cbd5e1);
    }

    .attach-heading {
      margin-bottom: 4px;
      color: var(--text-muted, #64748b);
      font: 700 11px/1.2 system-ui, Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      padding: 9px 10px;
      border-radius: 4px;
      color: var(--text, #0f172a);
      cursor: pointer;
      font: 600 13px/1.2 system-ui, Arial, sans-serif;
    }

    button:hover,
    button:focus-visible {
      background: var(--accent-soft, #eff6ff);
      color: var(--accent-ink, #1d4ed8);
      outline: none;
    }
  `;

  get captureName(): string {
    return this.input()?.value.trim() || "";
  }

  set captureName(value: string) {
    const input = this.input();
    if (input) {
      input.value = value;
    }
  }

  ensureCaptureName(value: string): void {
    const input = this.input();
    if (input && !input.value.trim()) {
      input.value = value;
    }
  }

  reset(): void {
    this.captureName = "";
    this._selectedEntityId = "";
    const prop = this.propertyInput();
    if (prop) {
      prop.value = "";
    }
    this.open = false;
  }

  private get _entities(): GraphEntity[] {
    return this.graphEntities.filter((entity) => String(entity.id ?? "").trim());
  }

  private get _attach(): CaptureAttach | null {
    if (!this._selectedEntityId) {
      return null;
    }
    const propertyKey =
      this.propertyInput()?.value.trim() || this.defaultPropertyKey;
    return {
      entityId: this._selectedEntityId,
      propertyKey,
      propertyType: "",
    };
  }

  private _onEntityChange = (event: Event): void => {
    this._selectedEntityId = (event.target as HTMLSelectElement).value;
  };

  firstUpdated(): void {
    this.renderRoot.querySelectorAll<HTMLButtonElement>("[data-scope]")
      .forEach((button) => {
        button.addEventListener("click", () => {
          this.choose(button.dataset.scope as CaptureScope);
        });
      });
  }

  render() {
    const hasEntities = this._entities.length > 0;
    return html`
      <input
        class="name-input"
        type="text"
        maxlength="120"
        placeholder=${this.placeholder}
        aria-label=${this.nameLabel}
      >
      ${hasEntities
        ? html`
            <div class="attach">
              <div class="attach-heading">${this.attachHeading}</div>
              <select
                class="entity-select"
                aria-label=${this.attachHeading}
                @change=${this._onEntityChange}
              >
                <option value="">${this.chooseEntityLabel}</option>
                ${this._entities.map(
                  (entity) => html`
                    <option value=${entity.id}>
                      ${entity.label || entity.id}
                    </option>
                  `,
                )}
              </select>
              <input
                class="prop-input"
                type="text"
                maxlength="100"
                placeholder=${this.propertyPlaceholder}
              >
            </div>
          `
        : ""}
      <button type="button" data-scope="viewport">${this.viewportLabel}</button>
      <button type="button" data-scope="region">${this.regionLabel}</button>
    `;
  }

  private input(): HTMLInputElement | null {
    return this.renderRoot.querySelector(".name-input");
  }

  private propertyInput(): HTMLInputElement | null {
    return this.renderRoot.querySelector(".prop-input");
  }

  private choose(scope: CaptureScope): void {
    this.open = false;
    this.dispatchEvent(
      new CustomEvent("synthesix-capture-choice", {
        bubbles: true,
        composed: true,
        detail: {
          scope,
          captureName: this.captureName,
          attach: this._attach,
        },
      }),
    );
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-overlay-capture-menu": SxOverlayCaptureMenu;
  }
}
