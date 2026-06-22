import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import "./sx-overlay-selection-trigger";

interface GraphEntity {
  id: string;
  label: string;
  tags?: string[];
  propertyKeys?: string[];
}

const PROPERTY_TYPE_LABELS: Record<string, string> = {
  text: "Texte",
  number: "Nombre",
  date: "Date",
  datetime: "Date/heure",
  geo: "Géo",
  country: "Pays",
  link: "Lien",
};

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

  /** Map of tag -> suggested property key -> zeroneurone property type. */
  @property({ attribute: false })
  tagsetPropertyTypes: Record<string, Record<string, string>> = {};

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
  @state() private _selectedPropertyType = "";
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
      width: 318px;
      max-height: 430px;
      padding: 10px;
      border: 1px solid rgba(34, 211, 238, 0.38);
      border-left: 3px solid #22d3ee;
      border-radius: 10px;
      background: #0f172a;
      box-shadow: 0 18px 42px rgba(2, 6, 23, 0.38);
      color: #e5edf8;
      font: 600 13px system-ui, Arial, sans-serif;
      z-index: 2147483647;
    }
    .menu.is-visible {
      display: block;
    }
    .title {
      padding: 1px 2px 2px;
      color: #67e8f9;
      font: 800 12px system-ui, Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .preview {
      overflow: hidden;
      margin: 0 0 8px;
      padding: 0 2px;
      color: #f8fafc;
      font: 800 13px system-ui, Arial, sans-serif;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .create-title,
    .attach-title {
      padding: 0 2px 5px;
      color: #9fb0c6;
      font: 800 11px system-ui, Arial, sans-serif;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }
    .row {
      display: flex;
      gap: 6px;
      padding: 5px 0 8px;
    }
    input,
    select {
      all: initial;
      box-sizing: border-box;
      display: block;
      width: 100%;
      padding: 8px 9px;
      border: 1px solid #334155;
      border-radius: 7px;
      background: #111c2f;
      color: #f8fafc;
      font: 600 13px system-ui, Arial, sans-serif;
    }
    input::placeholder {
      color: #94a3b8;
    }
    input:focus,
    select:focus {
      border-color: #22d3ee;
      box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.18);
    }
    .type-input {
      flex: 1;
      min-width: 0;
    }
    .attach {
      margin-top: 3px;
      padding-top: 9px;
      border-top: 1px solid #243349;
    }
    .attach .prop-input,
    .entity-select,
    .property-type-select {
      margin-bottom: 6px;
    }
    button {
      all: initial;
      box-sizing: border-box;
      border-radius: 7px;
      cursor: pointer;
      font: 800 13px system-ui, Arial, sans-serif;
      color: #ffffff;
    }
    .create-btn {
      padding: 8px 10px;
      background: #2563eb;
    }
    .attach-btn {
      display: block;
      width: 100%;
      padding: 9px 10px;
      border: 1px solid rgba(34, 211, 238, 0.42);
      background: #2563eb;
      text-align: center;
    }
    .create-btn:hover,
    .attach-btn:hover {
      background: #1d4ed8;
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

  private _suggestedPropertyType(propertyKey: string): string {
    const key = String(propertyKey ?? "").trim().toLowerCase();
    if (!key) return "";
    const entity = this._entities.find(
      (e) => String(e.id ?? "").trim() === String(this._selectedEntityId).trim(),
    );
    for (const tag of entity?.tags ?? []) {
      const propertyTypes =
        this.tagsetPropertyTypes[String(tag ?? "").trim()] ?? {};
      for (const [propertyName, propertyType] of Object.entries(propertyTypes)) {
        if (propertyName.trim().toLowerCase() === key) {
          return Object.prototype.hasOwnProperty.call(
            PROPERTY_TYPE_LABELS,
            propertyType,
          )
            ? propertyType
            : "";
        }
      }
    }
    return "";
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
    this._selectedPropertyType = "";
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
    const prop = this.renderRoot.querySelector<HTMLInputElement>(".prop-input");
    this._selectedPropertyType = this._suggestedPropertyType(prop?.value ?? "");
  };

  private _onPropertyInput = (event: Event) => {
    this._selectedPropertyType = this._suggestedPropertyType(
      (event.target as HTMLInputElement).value,
    );
  };

  private _onPropertyTypeChange = (event: Event) => {
    this._selectedPropertyType = (event.target as HTMLSelectElement).value;
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
    const select = this.renderRoot.querySelector<HTMLSelectElement>(
      ".entity-select",
    );
    const prop = this.renderRoot.querySelector<HTMLInputElement>(".prop-input");
    const entityId = select?.value ?? "";
    const propertyKey = (prop?.value ?? "").trim();
    const propertyType = this._selectedPropertyType;
    const label = this._selectedText;
    this._close();
    if (!label || !entityId || !propertyKey) return;
    this.dispatchEvent(
      new CustomEvent("synthesix-entity-attach", {
        bubbles: true,
        composed: true,
        detail: { label, entityId, propertyKey, propertyType },
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
          <select
            class="entity-select"
            ?disabled=${!hasEntities}
            @change=${this._onEntityChange}
          >
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
            @input=${this._onPropertyInput}
            @keydown=${this._onPropKeydown}
          >
          <datalist id="__sx-entity-props">
            ${this._propertySuggestions.map(
              (p) => html`<option value=${p}></option>`,
            )}
          </datalist>
          <select
            class="property-type-select"
            aria-label="Property type"
            .value=${this._selectedPropertyType}
            ?disabled=${!hasEntities}
            @change=${this._onPropertyTypeChange}
          >
            <option value="">Type auto</option>
            ${Object.entries(PROPERTY_TYPE_LABELS).map(
              ([value, label]) => html`<option value=${value}>${label}</option>`,
            )}
          </select>
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
