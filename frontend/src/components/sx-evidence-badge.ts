import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * <sx-evidence-badge status="verified">Verified just now</sx-evidence-badge>
 *
 * Evidence-capture verification badge, ported from `.evidence-verification`
 * (theme.css / investigations/view.py). The status text comes from the
 * light-DOM slot (so i18n and the existing verify flow can set it); `status`
 * drives the colour (pending = muted, verified = green, error = red). The badge
 * is an `aria-live` status region so screen readers announce changes.
 */
@customElement("sx-evidence-badge")
export class SxEvidenceBadge extends LitElement {
  @property({ reflect: true })
  status: "pending" | "verified" | "error" = "pending";

  static styles = css`
    :host {
      display: inline-flex;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 14px;
      font-size: 12px;
      font-weight: 700;
      color: var(--muted, #64748b);
    }
    :host([status="verified"]) .badge {
      color: var(--success-ink, #166534);
    }
    :host([status="error"]) .badge {
      color: var(--danger, #dc2626);
    }
  `;

  render() {
    return html`<span
      class="badge"
      part="badge"
      role="status"
      aria-live="polite"
    >
      <slot></slot>
    </span>`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-evidence-badge": SxEvidenceBadge;
  }
}
