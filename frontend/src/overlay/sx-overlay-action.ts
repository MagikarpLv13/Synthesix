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
      --sx-action-bg: var(--accent, #2563eb);
      --sx-action-border: var(--accent-strong, #1d4ed8);
      --sx-action-hover: var(--accent-strong, #1d4ed8);
      --sx-action-hover-border: #1e40af;
    }

    :host([variant="archive"]) {
      --sx-action-bg: #0891b2;
      --sx-action-border: #0e7490;
      --sx-action-hover: #0e7490;
      --sx-action-hover-border: #155e75;
    }

    :host([variant="capture"]) {
      --sx-action-bg: var(--text, #0f172a);
      --sx-action-border: #334155;
      --sx-action-hover: #334155;
      --sx-action-hover-border: #475569;
    }

    :host([state="saving"]),
    :host([state="archiving"]),
    :host([state="capturing"]) {
      --sx-action-bg: #475569;
      --sx-action-border: #334155;
      --sx-action-hover: #475569;
      --sx-action-hover-border: #334155;
    }

    :host([state="saved"]),
    :host([state="archived"]),
    :host([state="captured"]) {
      --sx-action-bg: var(--success, #16a34a);
      --sx-action-border: #047857;
      --sx-action-hover: #047857;
      --sx-action-hover-border: #065f46;
    }

    :host([state="error"]) {
      --sx-action-bg: var(--danger, #dc2626);
      --sx-action-border: #b91c1c;
      --sx-action-hover: #b91c1c;
      --sx-action-hover-border: #991b1b;
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
      color: #ffffff;
      box-shadow: var(--shadow-soft, 0 8px 22px rgba(15, 23, 42, 0.18));
      cursor: pointer;
      font: 700 14px/1 system-ui, Arial, sans-serif;
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
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.34);
      transform: translateY(-1px);
    }

    button:focus-visible {
      outline: 3px solid rgba(6, 182, 212, 0.55);
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
        <svg viewBox="0 0 128 128" aria-hidden="true">
          ${Array.from({ length: 10 }, (_unused, index) => html`
            <path
              d="M58 12 69 6l9 38-12 9-9-7z"
              transform="rotate(${index * 36} 64 64)"
              fill=${index % 2 === 0 ? "#FFFFFF" : "#67E8F9"}
            ></path>
          `)}
          <circle cx="64" cy="64" r="14" fill="#FFFFFF"></circle>
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
