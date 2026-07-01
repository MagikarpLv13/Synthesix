import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";

/**
 * <sx-grouping-rules>
 *   <script type="application/json" data-rules>
 *     [{"domain":"tiktok.com","path_segments":1,"enabled":true}, …]
 *   </script>
 * </sx-grouping-rules>
 *
 * Editor for the per-domain saved-page grouping rules (see
 * `get_url_based_result_groups()` in `investigations/repository.py`): pages
 * sharing a domain and the same leading URL path segments are shown as one
 * collapsed group in "Pages enregistrées". Rules are global (not per
 * investigation), fetched fresh into every generated page.
 *
 * Dispatches a single `sx-rule-change` CustomEvent (bubbles, composed) with
 * `detail: { domain, pathSegments, enabled }` on any edit, remove (=
 * enabled:false), or add-rule submit. The generated page's inline script
 * listens once and turns it into `queueAction("set_url_grouping_rule", …)` -
 * no other wiring needed here, consistent with how the rest of this app's
 * light-DOM controls are dispatched.
 */

export interface GroupingRule {
  domain: string;
  path_segments: number;
  enabled: boolean;
}

@customElement("sx-grouping-rules")
export class SxGroupingRules extends LitElement {
  /** Rules to display. Falls back to a child JSON `<script data-rules>`. */
  @property({ attribute: false })
  rules: GroupingRule[] | null = null;

  @state()
  private _newDomain = "";

  @state()
  private _newSegments = 1;

  static styles = css`
    :host {
      display: block;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 8px;
    }
    .rule {
      display: flex;
      flex-direction: column;
      gap: 6px;
      padding: 10px 12px;
      border: 1px solid var(--line, #334155);
      border-radius: 10px;
      background: var(--surface-2, #172033);
    }
    .rule__domain {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      font: 700 13px/1.2 var(--font-ui, system-ui, sans-serif);
      color: var(--text, #e2e8f0);
    }
    .rule__remove {
      display: grid;
      place-items: center;
      width: 22px;
      height: 22px;
      padding: 0;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: var(--muted, #94a3b8);
      font-size: 16px;
      line-height: 1;
      cursor: pointer;
    }
    .rule__remove:hover {
      background: color-mix(in srgb, var(--danger, #f87171) 18%, transparent);
      color: var(--danger, #f87171);
    }
    .rule__remove:focus-visible {
      outline: 2px solid var(--accent, #6366f1);
      outline-offset: 1px;
    }
    .rule__row {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--muted, #94a3b8);
    }
    input[type="number"],
    input[type="text"] {
      border: 1px solid var(--line, #334155);
      border-radius: 6px;
      background: var(--surface, #0b1220);
      color: var(--text, #e2e8f0);
      padding: 4px 6px;
      font: inherit;
    }
    input[type="number"] {
      width: 3.5em;
    }
    .add {
      display: flex;
      flex-direction: column;
      gap: 6px;
      padding: 10px 12px;
      border: 1px dashed var(--line, #334155);
      border-radius: 10px;
    }
    .add__fields {
      display: flex;
      gap: 6px;
    }
    .add__fields input[type="text"] {
      flex: 1 1 auto;
      min-width: 0;
    }
    .add__fields input[type="number"] {
      width: 4.5em;
    }
    button.primary {
      border: 0;
      border-radius: 6px;
      background: var(--accent, #6366f1);
      color: #fff;
      padding: 6px 10px;
      font: 600 12px/1 var(--font-ui, system-ui, sans-serif);
      cursor: pointer;
    }
    button.primary:hover {
      background: var(--accent-strong, #4f46e5);
    }
    button.primary:focus-visible {
      outline: 2px solid var(--accent, #6366f1);
      outline-offset: 1px;
    }
  `;

  connectedCallback(): void {
    super.connectedCallback();
    if (!this.rules) {
      this.rules = this._readInlineData();
    }
  }

  firstUpdated(): void {
    // synthesix-ui.js loads as a classic (non-deferred) <script> in <head>,
    // so custom elements are defined - and upgrade on their opening tag -
    // before the parser has reached this element's light-DOM <script
    // data-rules> child. connectedCallback can run too early to see it (see
    // the identical comment/fix in sx-entity-graph.ts's _build()). Retry
    // once the current frame has settled, by which point parsing is done.
    if (!this.rules) {
      requestAnimationFrame(() => {
        if (!this.rules) {
          this.rules = this._readInlineData();
        }
      });
    }
  }

  private _readInlineData(): GroupingRule[] | null {
    const script = this.querySelector<HTMLScriptElement>("script[data-rules]");
    if (!script?.textContent) return null;
    try {
      const parsed = JSON.parse(script.textContent) as GroupingRule[];
      if (Array.isArray(parsed)) return parsed;
    } catch {
      /* ignore malformed payload */
    }
    return null;
  }

  private _emit(domain: string, pathSegments: number, enabled: boolean): void {
    this.dispatchEvent(
      new CustomEvent("sx-rule-change", {
        bubbles: true,
        composed: true,
        detail: { domain, pathSegments, enabled },
      }),
    );
  }

  private _onSegmentsChange(rule: GroupingRule, event: Event): void {
    const value = parseInt((event.target as HTMLInputElement).value, 10) || 1;
    this._emit(rule.domain, value, rule.enabled);
  }

  private _onEnabledChange(rule: GroupingRule, event: Event): void {
    this._emit(
      rule.domain,
      rule.path_segments,
      (event.target as HTMLInputElement).checked,
    );
  }

  private _onRemove(rule: GroupingRule): void {
    this._emit(rule.domain, rule.path_segments, false);
  }

  private _onAddSubmit(event: Event): void {
    event.preventDefault();
    const domain = this._newDomain.trim();
    if (!domain) return;
    this._emit(domain, this._newSegments || 1, true);
    this._newDomain = "";
    this._newSegments = 1;
  }

  render() {
    const rules = this.rules ?? [];
    return html`
      <div class="grid">
        ${rules.map(
          (rule) => html`
            <div class="rule" data-domain=${rule.domain}>
              <div class="rule__domain">
                <span>${rule.domain}</span>
                <button
                  type="button"
                  class="rule__remove"
                  title="Désactiver cette règle"
                  aria-label="Désactiver cette règle"
                  @click=${() => this._onRemove(rule)}
                >
                  &times;
                </button>
              </div>
              <label class="rule__row">
                Segments
                <input
                  type="number"
                  min="1"
                  step="1"
                  .value=${String(rule.path_segments)}
                  @change=${(event: Event) => this._onSegmentsChange(rule, event)}
                />
              </label>
              <label class="rule__row">
                <input
                  type="checkbox"
                  .checked=${rule.enabled}
                  @change=${(event: Event) => this._onEnabledChange(rule, event)}
                />
                Activée
              </label>
            </div>
          `,
        )}
        <form class="add" @submit=${this._onAddSubmit}>
          <div class="add__fields">
            <input
              type="text"
              placeholder="ex. tiktok.com"
              aria-label="Domaine"
              .value=${this._newDomain}
              @input=${(event: Event) => {
                this._newDomain = (event.target as HTMLInputElement).value;
              }}
            />
            <input
              type="number"
              min="1"
              step="1"
              title="Segments de chemin"
              aria-label="Segments de chemin"
              .value=${String(this._newSegments)}
              @input=${(event: Event) => {
                this._newSegments =
                  parseInt((event.target as HTMLInputElement).value, 10) || 1;
              }}
            />
          </div>
          <button type="submit" class="primary">Ajouter la règle</button>
        </form>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-grouping-rules": SxGroupingRules;
  }
}
