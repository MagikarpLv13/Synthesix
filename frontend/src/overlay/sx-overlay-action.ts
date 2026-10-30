import { LitElement, html, css, nothing, unsafeCSS } from "lit";
import { customElement, property } from "lit/decorators.js";
import { tokensCss } from "../tokens";

type OverlayActionState =
  | "idle"
  | "saving"
  | "saved"
  | "archiving"
  | "archived"
  | "capturing"
  | "captured"
  | "error";

/**
 * Isolated action button for the injected third-party-page overlay.
 *
 * The host page never provides theme.css, so the component injects the token
 * fallback block itself and exposes all user-facing text through properties.
 */
@customElement("sx-overlay-action")
export class SxOverlayAction extends LitElement {
  @property({ reflect: true })
  variant: "primary" | "archive" | "capture" = "primary";

  @property({ reflect: true })
  state: OverlayActionState = "idle";

  @property()
  label = "";

  @property({ attribute: "title-text" })
  titleText = "";

  @property({ attribute: "aria-text" })
  ariaText = "";

  @property({ reflect: true })
  icon: "mark" | "archive" | "camera" | "none" = "none";

  @property({ type: Boolean, attribute: "icon-only", reflect: true })
  iconOnly = false;

  @property({ type: Boolean, reflect: true })
  disabled = false;

  static styles = css`
    ${unsafeCSS(tokensCss)}

    :host {
      display: inline-flex;
      --sx-action-bg: var(--accent, #2a46a6);
      --sx-action-border: var(--accent-strong, #23408f);
      --sx-action-hover: var(--accent-strong, #23408f);
      --sx-action-hover-border: var(--accent-ink, #17225a);
      --sx-action-text: #ffffff;
    }

    :host([variant="archive"]) {
      --sx-action-bg: var(--ink-surface, #17181d);
      --sx-action-border: var(--ink-border, #2b2d34);
      --sx-action-hover: var(--ink-border, #2b2d34);
      --sx-action-hover-border: #41434d;
      --sx-action-text: var(--on-ink-strong, #f7f5ef);
    }

    :host([variant="capture"]) {
      --sx-action-bg: var(--surface, #fbf9f4);
      --sx-action-border: var(--line, #dad4c7);
      --sx-action-hover: var(--surface-sunken, #ece8de);
      --sx-action-hover-border: #c9c2b2;
      --sx-action-text: var(--text, #191a1e);
    }

    :host([state="saving"]),
    :host([state="archiving"]),
    :host([state="capturing"]) {
      --sx-action-bg: #56513f;
      --sx-action-border: #56513f;
      --sx-action-hover: #56513f;
      --sx-action-hover-border: #56513f;
    }

    :host([state="saved"]),
    :host([state="archived"]),
    :host([state="captured"]) {
      --sx-action-bg: var(--success, #28613c);
      --sx-action-border: #1e4b2e;
      --sx-action-hover: #1e4b2e;
      --sx-action-hover-border: #173c25;
    }

    :host([state="error"]) {
      --sx-action-bg: var(--danger, #b33a3a);
      --sx-action-border: #8f2e2e;
      --sx-action-hover: #8f2e2e;
      --sx-action-hover-border: #742525;
    }

    button {
      all: initial;
      box-sizing: border-box;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      height: 42px;
      min-width: 42px;
      padding: 0 14px 0 11px;
      border: 1px solid var(--sx-action-border);
      border-radius: var(--radius-sm, 6px);
      background: var(--sx-action-bg);
      color: var(--sx-action-text);
      box-shadow: var(--shadow-soft, 0 8px 22px rgba(15, 23, 42, 0.18));
      cursor: pointer;
      font: 700 14px/1 var(--font-ui, system-ui, Arial, sans-serif);
      white-space: nowrap;
      transition:
        background-color 140ms ease,
        border-color 140ms ease,
        box-shadow 140ms ease,
        transform 140ms ease;
    }

    :host([icon-only]) button {
      width: 42px;
      padding: 0;
    }

    :host([icon-only]) [data-label] {
      display: none;
    }

    button:hover:not(:disabled) {
      background: var(--sx-action-hover);
      border-color: var(--sx-action-hover-border);
      box-shadow: 0 12px 30px rgba(23, 24, 30, 0.34);
      transform: translateY(-1px);
    }

    button:focus-visible {
      outline: 3px solid rgba(138, 160, 238, 0.55);
      outline-offset: 2px;
    }

    button:disabled {
      cursor: wait;
    }

    svg {
      display: block;
      width: 20px;
      height: 20px;
      flex: 0 0 20px;
    }
  `;

  render() {
    return html`
      <button
        type="button"
      >
        ${this.renderIcon()}
        <span data-label></span>
      </button>
    `;
  }

  updated() {
    const button = this.renderRoot.querySelector("button");
    const label = this.getAttribute("label") || this.label;
    if (!button) {
      return;
    }
    const labelNode = button.querySelector("[data-label]");
    if (labelNode) {
      labelNode.textContent = label;
    }
    button.disabled = this.disabled || this.hasAttribute("disabled");
    button.title = (
      this.getAttribute("title-text")
      || this.titleText
      || label
    );
    button.setAttribute(
      "aria-label",
      this.getAttribute("aria-text") || this.ariaText || label,
    );
  }

  private renderIcon() {
    if (this.icon === "mark") {
      return html`
        <svg viewBox="0 0 48 48" aria-hidden="true">
          <line x1="6" y1="12" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <line x1="6" y1="24" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <line x1="6" y1="36" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <line x1="16" y1="6" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <line x1="16" y1="42" x2="33" y2="24" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"></line>
          <circle cx="6" cy="12" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="6" cy="24" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="6" cy="36" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="16" cy="6" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="16" cy="42" r="2.5" fill="#8AA0EE"></circle>
          <circle cx="34" cy="24" r="5.5" fill="#8AA0EE"></circle>
        </svg>
      `;
    }
    if (this.icon === "archive") {
      return html`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 3h11l3 3v15H5zM8 3v6h8V3M8 14h8M8 18h6"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
        </svg>
      `;
    }
    if (this.icon === "camera") {
      return html`
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M14.5 4 16 7h3a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h3l1.5-3z"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          ></path>
          <circle
            cx="12"
            cy="13"
            r="3"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          ></circle>
        </svg>
      `;
    }
    return nothing;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-overlay-action": SxOverlayAction;
  }
}
