import { LitElement, html, css } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * <sx-entity-panel data-graph-entity-id="..." data-inspector-entity="..." hidden>
 *
 * Shell for the graph-entity management card shown in the investigation
 * rail, ported from the hand-rolled `.graph-entity-card`/`.entity-section`
 * markup in `investigations/view.py` (`_graph_entities_markup`). Four named
 * slots (`identity`, `properties`, `relations`, `sources`) hold the existing
 * light-DOM fields/lists/forms unchanged — same classes and `data-*`
 * attributes, so the injected JS (queueAction bindings, tag editor, relation
 * add/remove, `hideInspectorPanels`/`revealInspector`) keeps working without
 * modification. This component only supplies the section spacing/separator
 * chrome that used to come from the now-removed `.entity-section` wrapper.
 *
 * Defensive against the `[hidden]` display trap hit three times already in
 * this project (Lots 9/12, plain divs re-appearing under `hidden`): the host
 * is `display: none` by default, only `:not([hidden])` opts into layout.
 */
@customElement("sx-entity-panel")
export class SxEntityPanel extends LitElement {
  static styles = css`
    :host {
      display: none;
    }
    :host(:not([hidden])) {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .section {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .section:not(.identity) {
      padding-top: 14px;
      border-top: 1px solid var(--line, #cbd5e1);
    }
  `;

  render() {
    return html`
      <div class="section identity" part="identity">
        <slot name="identity"></slot>
      </div>
      <div class="section" part="properties">
        <slot name="properties"></slot>
      </div>
      <div class="section" part="relations">
        <slot name="relations"></slot>
      </div>
      <div class="section" part="sources">
        <slot name="sources"></slot>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-entity-panel": SxEntityPanel;
  }
}
