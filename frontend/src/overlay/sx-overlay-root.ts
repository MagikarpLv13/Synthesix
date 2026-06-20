import { LitElement, html, css, unsafeCSS } from "lit";
import { customElement, property } from "lit/decorators.js";
import { tokensCss } from "../tokens";

type OverlayActionElement = HTMLElement & {
  ariaText?: string;
  disabled?: boolean;
  label?: string;
  state?: string;
  titleText?: string;
};

@customElement("sx-overlay-root")
export class SxOverlayRoot extends LitElement {
  @property({ type: Boolean, reflect: true })
  collapsed = false;

  static styles = css`
    ${unsafeCSS(tokensCss)}

    :host {
      all: initial;
      box-sizing: border-box;
      position: fixed;
      right: 18px;
      bottom: 18px;
      z-index: 2147483647;
      display: block;
      color: var(--text, #0f172a);
      font: 13px/1.2 system-ui, Arial, sans-serif;
      pointer-events: auto;
    }

    .toolbar {
      all: initial;
      box-sizing: border-box;
      display: flex;
      align-items: center;
      gap: 8px;
      pointer-events: auto;
      transform-origin: right bottom;
      transition:
        opacity 130ms ease,
        transform 130ms ease,
        filter 130ms ease;
    }

    .toggle,
    .collapsed-toggle {
      all: initial;
      box-sizing: border-box;
      display: inline-grid;
      place-items: center;
      border: 1px solid rgba(148, 163, 184, 0.55);
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.92);
      color: #f8fafc;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.26);
      cursor: pointer;
      font: 800 12px/1 system-ui, Arial, sans-serif;
      user-select: none;
    }

    .toggle {
      width: 32px;
      height: 32px;
    }

    .collapsed-toggle {
      width: 42px;
      height: 36px;
      letter-spacing: 0;
    }

    .toggle:hover,
    .toggle:focus-visible,
    .collapsed-toggle:hover,
    .collapsed-toggle:focus-visible {
      border-color: var(--accent, #2563eb);
      background: var(--accent-strong, #1d4ed8);
      outline: none;
    }

    .collapsed {
      display: none;
      pointer-events: auto;
    }

    :host([collapsed]) .toolbar {
      position: absolute;
      right: 0;
      bottom: 0;
      opacity: 0;
      pointer-events: none;
      transform: translateX(10px) scale(0.92);
      filter: blur(1px);
    }

    :host([collapsed]) .collapsed {
      display: flex;
      justify-content: flex-end;
      animation: sx-overlay-pop 140ms ease-out both;
    }

    :host([collapsed]) ::slotted(sx-overlay-capture-menu) {
      display: none !important;
    }

    @keyframes sx-overlay-pop {
      from {
        opacity: 0;
        transform: translateX(8px) scale(0.82);
      }
      to {
        opacity: 1;
        transform: translateX(0) scale(1);
      }
    }
  `;

  private setCollapsed(nextCollapsed: boolean): void {
    if (this.collapsed === nextCollapsed) {
      return;
    }
    this.collapsed = nextCollapsed;
    this.dispatchEvent(
      new CustomEvent("synthesix-overlay-toggle", {
        detail: { collapsed: this.collapsed },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private action(selector: string): OverlayActionElement | null {
    return this.querySelector(selector) as OverlayActionElement | null;
  }

  private setActionState(
    actionButton: OverlayActionElement | null,
    state: string,
    label: string,
    busyState: string,
  ): void {
    if (!actionButton) {
      return;
    }
    actionButton.dataset.state = state;
    actionButton.state = state;
    actionButton.setAttribute("state", state);
    actionButton.label = label;
    actionButton.setAttribute("label", label);
    actionButton.title = label;
    actionButton.titleText = label;
    actionButton.setAttribute("title-text", label);
    actionButton.ariaText = label;
    actionButton.setAttribute("aria-text", label);
    actionButton.disabled = state === busyState;
    actionButton.toggleAttribute("disabled", state === busyState);
  }

  setSaveButtonState(state: string, text: string): void {
    const button = this.action("[data-synthesix-save-page]");
    if (!button) {
      return;
    }
    button.dataset.state = state;
    button.state = state;
    button.setAttribute("state", state);
    button.label = text;
    button.setAttribute("label", text);
    button.disabled = state === "saving";
    button.toggleAttribute("disabled", state === "saving");
    button.titleText = button.title || text;
    button.setAttribute("title-text", button.title || text);
    button.ariaText =
      button.title || "Save page to active Synthesix investigation";
    button.setAttribute("aria-text", button.ariaText);
  }

  setCaptureState(state: string, tooltip = "Capture screenshot"): void {
    this.setActionState(
      this.action("[data-synthesix-capture]"),
      state,
      tooltip,
      "capturing",
    );
  }

  setArchiveState(
    state: string,
    tooltip = "Save page with HTML archive",
  ): void {
    this.setActionState(
      this.action("[data-synthesix-archive]"),
      state,
      tooltip,
      "archiving",
    );
  }

  render() {
    return html`
      <div class="toolbar" data-synthesix-overlay-toolbar>
        <slot name="toolbar"></slot>
        <button
          class="toggle"
          type="button"
          title="Collapse Synthesix overlay"
          aria-label="Collapse Synthesix overlay"
          data-synthesix-overlay-collapse
          @click=${() => this.setCollapsed(true)}
        >
          &rsaquo;
        </button>
      </div>
      <div class="collapsed" data-synthesix-overlay-collapsed>
        <button
          class="collapsed-toggle"
          type="button"
          title="Expand Synthesix overlay"
          aria-label="Expand Synthesix overlay"
          data-synthesix-overlay-expand
          @click=${() => this.setCollapsed(false)}
        >
          SX
        </button>
      </div>
      <slot></slot>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-overlay-root": SxOverlayRoot;
  }
}
