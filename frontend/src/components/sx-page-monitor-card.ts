import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * <sx-page-monitor-card class="page-monitor-card" data-page-monitor-id="...">
 *
 * Tag-only wrapper for a monitored-page card, ported from
 * `_page_monitor_cards()` (investigations/view.py). `.page-monitor-card`
 * already carries the full grid layout directly on the root element — no
 * wrapper chrome to factor into Shadow DOM. Classes, `data-*` attributes
 * and injected JS bindings are unchanged.
 */
@customElement("sx-page-monitor-card")
export class SxPageMonitorCard extends LitElement {
  render() {
    return html`<slot></slot>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-page-monitor-card": SxPageMonitorCard;
  }
}
