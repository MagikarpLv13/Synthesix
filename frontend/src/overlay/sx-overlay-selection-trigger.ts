import { LitElement, html, css, unsafeCSS } from "lit";
import { customElement, property } from "lit/decorators.js";
import { tokensCss } from "../tokens";

@customElement("sx-overlay-selection-trigger")
export class SxOverlaySelectionTrigger extends LitElement {
  @property()
  label = "";

  static styles = css`
    ${unsafeCSS(tokensCss)}

    :host {
      box-sizing: border-box;
      display: none;
      position: fixed;
      left: 0;
      top: 0;
      z-index: 2147483647;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      max-width: min(260px, calc(100vw - 16px));
      padding: 7px 9px;
      border: 1px solid var(--accent-strong, #23408f);
      border-radius: 999px;
      background: var(--accent, #2a46a6);
      color: #ffffff;
      box-shadow: 0 10px 26px rgba(23, 24, 30, 0.26);
      cursor: pointer;
      font: 700 12px/1.1 var(--font-ui, system-ui, Arial, sans-serif);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    button:hover,
    button:focus-visible {
      background: var(--accent-strong, #23408f);
      outline: 3px solid rgba(138, 160, 238, 0.45);
      outline-offset: 2px;
    }
  `;

  render() {
    return html`<button type="button"></button>`;
  }

  updated(): void {
    const button = this.renderRoot.querySelector("button");
    if (!button) {
      return;
    }
    const label = this.getAttribute("label") || this.label;
    button.textContent = label;
    button.setAttribute("aria-label", label);
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-overlay-selection-trigger": SxOverlaySelectionTrigger;
  }
}
