import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * <sx-url-analysis class="result-url-analysis">
 *
 * Tag-only wrapper for the technical URL analysis block (empty state or
 * full report), ported from `_url_analysis_markup()`
 * (investigations/view.py). Already flat/class-driven — no wrapper chrome
 * to factor into Shadow DOM. Classes, `data-*` attributes and injected JS
 * bindings are unchanged.
 */
@customElement("sx-url-analysis")
export class SxUrlAnalysis extends LitElement {
  render() {
    return html`<slot></slot>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-url-analysis": SxUrlAnalysis;
  }
}
