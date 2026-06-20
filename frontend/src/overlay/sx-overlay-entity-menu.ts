import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import "./sx-overlay-selection-trigger";

interface GraphEntity {
  id: string;
  label: string;
  tags?: string[];
  propertyKeys?: string[];
}

/**
 * "Add to investigation" entity tool for the injected overlay.
 *
 * Faithful extraction of the inline entity trigger + menu from main.py. On a
 * text selection it floats a trigger pill near the selection; clicking it opens
 * a panel to either create a graph entity (free type, with tag suggestions) or
 * attach the selection as a property of an existing entity (with per-entity
 * property suggestions). It owns selection detection, positioning and outside-
 * click/Esc dismissal, and only emits intent events — the host (main.py) builds
 * the CDP payloads with the page payload + investigation id:
 *  - `synthesix-entity-create` `{ label, category }`
 *  - `synthesix-entity-attach` `{ label, entityId, propertyKey }`
 */
@customElement("sx-overlay-entity-menu")
export class SxOverlayEntityMenu extends LitElement {
  /** Built-in entity type suggestions (ZERONEURONE tagsets). */
  @property({ attribute: false })
  baseTagsets: string[] = [];

  /** Tags already present in the active investigation. */
  @property({ attribute: false })
  existingTags: string[] = [];

  /** Map of tag -> suggested property keys. */
  @property({ attribute: false })
  tagsetProperties: Record<string, string[]> = {};

  /** Existing graph entities the selection can be attached to. */
  @property({ attribute: false })
  graphEntities: GraphEntity[] = [];

  // i18n labels — defaults match the current overlay copy.
  @property() heading = "Ajouter à l'enquête";
  @property() createHeading = "Créer une entité";
  @property({ attribute: "type-placeholder" }) typePlaceholder = "Type d'entité...";
  @property({ attribute: "create-label" }) createLabel = "Créer";
  @property({ attribute: "attach-heading" }) attachHeading = "Ajouter comme propriété";
  @property({ attribute: "choose-entity-label" }) chooseEntityLabel = "Choisir une entité...";
  @property({ attribute: "property-placeholder" }) propertyPlaceholder = "Type de l'information";
  @property({ attribute: "attach-label" }) attachLabel = "Rattacher";

  @state() private _selectedText = "";
  @state() private _selectedEntityId = "";
  @state() private _triggerVisible = false;
  @state() private _menuVisible = false;
  @state() private _triggerLeft = 0;
  @state() private _triggerTop = 0;
  @state() private _menuLeft = 0;
  @state() private _menuTop = 0;

  static styles = css`
    :host {
      all: initial;
    }
    .trigger {
      position: fixed;
      z-index: 2147483647;
    }
    .menu {
      box-sizing: border-box;
      display: none;
      position: fixed;
      width: 300px;
      max-height: 390px;
      padding: 6px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      background: #ffffff;
      box-shadow: 0 14px 34px rgba(15, 23, 42, 0.28);
      color: #0f172a;
      font: 600 13px Arial, sans-serif;
      z-index: 2147483647;
    }
    .menu.is-visible {
      display: block;
    }
    .title {
      padding: 4px 6px 2px;
      color: #475569;
      font: 700 12px Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .preview {
      overflow: hidden;
      padding: 0 6px 5px;
      color: #0f172a;
      font: 700 13px Arial, sans-serif;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .create-title,
    .attach-title {
      padding: 2px 6px 4px;
      color: #475569;
      font: 700 12px Arial, sans-serif;
    }
    .row {
      display: flex;
      gap: 5px;
      padding: 5px 0 4px;
    }
    input {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      padding: 6px 7px;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      color: #0f172a;
      font: 500 13px Arial, sans-serif;
    }
    .type-input {
      flex: 1;
      min-width: 0;
    }
    select {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      margin-bottom: 5px;
      padding: 6px 7px;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      background: #ffffff;
      color: #0f172a;
      font: 500 13px Arial, sans-serif;
    }
    .attach {
      margin-top: 5px;
      padding-top: 6px;
      border-top: 1px solid #e2e8f0;
    }
    .attach .prop-input {
      margin-bottom: 5px;
    }
    button {
      all: initial;
      box-sizing: border-box;
      border-radius: 5px;
      cursor: pointer;
      font: 700 13px Arial, sans-serif;
      color: #ffffff;
    }
    .create-btn {
      padding: 6px 9px;
      background: #2563eb;
    }
    .attach-btn {
      display: block;
      width: 100%;
      padding: 7px 9px;
      background: #0f172a;
      text-align: center;
    }
    button[disabled] {
      opacity: 0.55;
      cursor: not-allowed;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    document.addEventListener("mouseup", this._onDocMouseUp);
    document.addEventListener("click", this._onDocClick);
    document.addEventListener("keydown", this._onDocKeyDown, true);
  }

  disconnectedCallback() {
    document.removeEventListener("mouseup", this._onDocMouseUp);
    document.removeEventListener("click", this._onDocClick);
    document.removeEventListener("keydown", this._onDocKeyDown, true);
    super.disconnectedCallback();
  }

  private _dedup(values: string[]): string[] {
    const seen = new Set<string>();
    const out: string[] = [];
    for (const raw of values) {
      const value = String(raw ?? "").trim();
      const key = value.toLowerCase();
      if (!value || seen.has(key)) continue;
      seen.add(key);
      out.push(value);
    }
    return out;
  }

  private get _typeSuggestions(): string[] {
    return this._dedup([...this.baseTagsets, ...this.existingTags]);
  }

  private get _entities(): GraphEntity[] {
    return this.graphEntities.filter((e) => String(e.id ?? "").trim());
  }

  private get _propertySuggestions(): string[] {
    const entity = this._entities.find(
      (e) => String(e.id ?? "").trim() === String(this._selectedEntityId).trim(),
    );
    if (!entity) return [];
    const out: string[] = [];
    for (const tag of entity.tags ?? []) {
      out.push(...(this.tagsetProperties[String(tag ?? "").trim()] ?? []));
    }
    out.push(...(entity.propertyKeys ?? []));
    return this._dedup(out);
  }

  private _selectionText(): string {
    return String(window.getSelection()?.toString() ?? "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 200);
  }

  private _close() {
    this._menuVisible = false;
    this._triggerVisible = false;
    this._selectedEntityId = "";
    const type = this.renderRoot.querySelector<HTMLInputElement>(".type-input");
    const prop = this.renderRoot.querySelector<HTMLInputElement>(".prop-input");
    const select = this.renderRoot.querySelector<HTMLSelectElement>("select");
    if (type) type.value = "";
    if (prop) prop.value = "";
    if (select) select.value = "";
  }

  private _onDocMouseUp = (event: MouseEvent) => {
    if (event.composedPath().includes(this)) return;
    window.setTimeout(() => this._showTrigger(), 0);
  };

  private _onDocClick = (event: MouseEvent) => {
    if (!event.composedPath().includes(this)) this._close();
  };

  private _onDocKeyDown = (event: KeyboardEvent) => {
    if (event.key === "Escape") this._close();
  };

  private _showTrigger() {
    const label = this._selectionText();
    const selection = window.getSelection();
    if (!label || !selection || selection.rangeCount === 0) {
      this._close();
      return;
    }
    const rect = selection.getRangeAt(0).getBoundingClientRect();
    if (!rect || (!rect.width && !rect.height)) {
      this._close();
      return;
    }
    this._selectedText = label;
    this._triggerLeft = Math.min(
      Math.max(rect.left, 8),
      Math.max(8, window.innerWidth - 150),
    );
    this._triggerTop = Math.max(8, rect.top - 38);
    this._menuVisible = false;
    this._triggerVisible = true;
  }

  private _onTriggerClick = () => {
    const trigger = this.renderRoot.querySelector(".trigger");
    const rect = trigger?.getBoundingClientRect();
    const left = rect ? rect.left : this._triggerLeft;
    const top = rect ? rect.bottom + 6 : this._triggerTop;
    const label = this._selectionText() || this._selectedText;
    if (!label) {
      this._close();
      return;
    }
    this._selectedText = label;
    this._selectedEntityId = "";
    this._menuLeft = Math.min(Math.max(left, 8), Math.max(8, window.innerWidth - 316));
    this._menuTop = Math.min(Math.max(top, 8), Math.max(8, window.innerHeight - 320));
    this._triggerVisible = false;
    this._menuVisible = true;
  };

  private _onEntityChange = (event: Event) => {
    this._selectedEntityId = (event.target as HTMLSelectElement).value;
  };

  private _onCreate = () => {
    const input = this.renderRoot.querySelector<HTMLInputElement>(".type-input");
    const category = (input?.value ?? "").trim();
    if (!category) return;
    const label = this._selectedText;
    this._close();
    if (!label) return;
    this.dispatchEvent(
      new CustomEvent("synthesix-entity-create", {
        bubbles: true,
        composed: true,
        detail: { label, category },
      }),
    );
  };

  private _onTypeKeydown = (event: KeyboardEvent) => {
    if (event.key === "Enter") {
      event.preventDefault();
      this._onCreate();
    }
  };

  private _onAttach = () => {
    const select = this.renderRoot.querySelector<HTMLSelectElement>("select");
    const prop = this.renderRoot.querySelector<HTMLInputElement>(".prop-input");
    const entityId = select?.value ?? "";
    const propertyKey = (prop?.value ?? "").trim();
    const label = this._selectedText;
    this._close();
    if (!label || !entityId || !propertyKey) return;
    this.dispatchEvent(
      new CustomEvent("synthesix-entity-attach", {
        bubbles: true,
        composed: true,
        detail: { label, entityId, propertyKey },
      }),
    );
  };

  private _onPropKeydown = (event: KeyboardEvent) => {
    if (event.key === "Enter") {
      event.preventDefault();
      this._onAttach();
    }
  };

  private _stop = (event: Event) => event.stopPropagation();

  render() {
    const hasEntities = this._entities.length > 0;
    const triggerStyle =
      `display:${this._triggerVisible ? "block" : "none"};` +
      `left:${this._triggerLeft}px;top:${this._triggerTop}px;`;
    const menuStyle = `left:${this._menuLeft}px;top:${this._menuTop}px;`;
    return html`
      <sx-overlay-selection-trigger
        class="trigger"
        style=${triggerStyle}
        label=${this.heading}
        @click=${this._onTriggerClick}
      ></sx-overlay-selection-trigger>
      <div
        class="menu ${this._menuVisible ? "is-visible" : ""}"
        style=${menuStyle}
        @mousedown=${this._stop}
        @mouseup=${this._stop}
        @click=${this._stop}
      >
        <div class="title">${this.heading}</div>
        <div class="preview">${this._selectedText}</div>
        <div class="create-title">${this.createHeading}</div>
        <div class="row">
          <input
            class="type-input"
            type="text"
            maxlength="50"
            placeholder=${this.typePlaceholder}
            list="__sx-entity-types"
            @keydown=${this._onTypeKeydown}
          >
          <button class="create-btn" type="button" @click=${this._onCreate}>
            ${this.createLabel}
          </button>
          <datalist id="__sx-entity-types">
            ${this._typeSuggestions.map((t) => html`<option value=${t}></option>`)}
          </datalist>
        </div>
        <div class="attach">
          <div class="attach-title">${this.attachHeading}</div>
          <select ?disabled=${!hasEntities} @change=${this._onEntityChange}>
            <option value="">${this.chooseEntityLabel}</option>
            ${this._entities.map(
              (e) => html`<option value=${e.id}>${e.label || e.id}</option>`,
            )}
          </select>
          <input
            class="prop-input"
            type="text"
            maxlength="100"
            placeholder=${this.propertyPlaceholder}
            list="__sx-entity-props"
            @keydown=${this._onPropKeydown}
          >
          <datalist id="__sx-entity-props">
            ${this._propertySuggestions.map(
              (p) => html`<option value=${p}></option>`,
            )}
          </datalist>
          <button
            class="attach-btn"
            type="button"
            ?disabled=${!hasEntities}
            @click=${this._onAttach}
          >
            ${this.attachLabel}
          </button>
        </div>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-overlay-entity-menu": SxOverlayEntityMenu;
  }
}
