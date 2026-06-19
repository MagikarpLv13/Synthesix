import { LitElement, html, css, unsafeCSS } from "lit";
import { customElement, property } from "lit/decorators.js";
import { tokensCss } from "../tokens";

type CaptureScope = "viewport" | "region";

@customElement("sx-overlay-capture-menu")
export class SxOverlayCaptureMenu extends LitElement {
  @property({ type: Boolean, reflect: true })
  open = false;

  static styles = css`
    ${unsafeCSS(tokensCss)}

    :host {
      box-sizing: border-box;
      display: none;
      position: absolute;
      right: 0;
      bottom: 50px;
      width: 180px;
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

    input {
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
    this.open = false;
  }

  firstUpdated(): void {
    this.renderRoot.querySelectorAll<HTMLButtonElement>("[data-scope]")
      .forEach((button) => {
        button.addEventListener("click", () => {
          this.choose(button.dataset.scope as CaptureScope);
        });
      });
  }

  render() {
    return html`
      <input
        type="text"
        maxlength="120"
        placeholder="Capture name (optional)"
        aria-label="Capture name"
      >
      <button type="button" data-scope="viewport">Visible area</button>
      <button type="button" data-scope="region">Select area</button>
    `;
  }

  private input(): HTMLInputElement | null {
    return this.renderRoot.querySelector("input");
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
