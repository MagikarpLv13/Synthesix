import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * Full-viewport drag-to-select overlay for region evidence capture.
 *
 * Extracted verbatim from the inline `__synthesixStartRegionSelection` overlay
 * in main.py. Behaviour is preserved exactly: dim backdrop + crosshair, a hint
 * pill, a cyan selection rectangle, Esc to cancel, an 8px minimum, and page
 * coordinates (viewport + scroll offset). It only dispatches events — the host
 * (main.py) owns toolbar visibility and the capture queue:
 *  - `synthesix-region-selected` `{ x, y, width, height }` on a valid drag;
 *  - `synthesix-region-cancel` on Esc or a too-small selection.
 */
@customElement("sx-overlay-selection-box")
export class SxOverlaySelectionBox extends LitElement {
  /** Instruction pill text; defaults to English, host page may translate it. */
  @property()
  hint = "Drag to select evidence · Esc to cancel";

  private _selecting = false;
  private _startX = 0;
  private _startY = 0;

  static styles = css`
    :host {
      all: initial;
      display: block;
      position: fixed;
      inset: 0;
      z-index: 2147483647;
      cursor: crosshair;
      background: rgba(15, 23, 42, 0.16);
      user-select: none;
      touch-action: none;
    }
    .hint {
      position: fixed;
      top: 16px;
      left: 50%;
      transform: translateX(-50%);
      padding: 9px 12px;
      border-radius: 6px;
      background: #0f172a;
      color: #ffffff;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.3);
      font: 600 13px Arial, sans-serif;
      pointer-events: none;
    }
    .box {
      display: none;
      position: fixed;
      border: 2px solid #06b6d4;
      background: rgba(6, 182, 212, 0.12);
      box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.38);
      pointer-events: none;
    }
    .box.is-active {
      display: block;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    document.addEventListener("keydown", this._onKeyDown, true);
    this.addEventListener("pointerdown", this._onPointerDown);
    this.addEventListener("pointermove", this._onPointerMove);
    this.addEventListener("pointerup", this._onPointerUp);
  }

  disconnectedCallback() {
    document.removeEventListener("keydown", this._onKeyDown, true);
    super.disconnectedCallback();
  }

  private get _boxEl(): HTMLElement | null {
    return this.renderRoot.querySelector(".box");
  }

  private _onKeyDown = (event: KeyboardEvent) => {
    if (event.key !== "Escape") return;
    event.preventDefault();
    this._emitCancel();
  };

  private _onPointerDown = (event: PointerEvent) => {
    event.preventDefault();
    this._selecting = true;
    this._startX = event.clientX;
    this._startY = event.clientY;
    const box = this._boxEl;
    if (box) box.classList.add("is-active");
    try {
      this.setPointerCapture(event.pointerId);
    } catch {
      // Synthetic events and older browsers may not expose capture.
    }
  };

  private _onPointerMove = (event: PointerEvent) => {
    if (!this._selecting) return;
    const box = this._boxEl;
    if (!box) return;
    const left = Math.min(this._startX, event.clientX);
    const top = Math.min(this._startY, event.clientY);
    box.style.left = `${left}px`;
    box.style.top = `${top}px`;
    box.style.width = `${Math.abs(event.clientX - this._startX)}px`;
    box.style.height = `${Math.abs(event.clientY - this._startY)}px`;
  };

  private _onPointerUp = (event: PointerEvent) => {
    if (!this._selecting) return;
    this._selecting = false;
    const left = Math.min(this._startX, event.clientX);
    const top = Math.min(this._startY, event.clientY);
    const width = Math.abs(event.clientX - this._startX);
    const height = Math.abs(event.clientY - this._startY);
    if (width < 8 || height < 8) {
      this._emitCancel();
      return;
    }
    this.dispatchEvent(
      new CustomEvent("synthesix-region-selected", {
        bubbles: true,
        composed: true,
        detail: {
          x: left + window.scrollX,
          y: top + window.scrollY,
          width,
          height,
        },
      }),
    );
  };

  private _emitCancel() {
    this.dispatchEvent(
      new CustomEvent("synthesix-region-cancel", {
        bubbles: true,
        composed: true,
      }),
    );
  }

  render() {
    return html`
      <div class="hint">${this.hint}</div>
      <div class="box"></div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "sx-overlay-selection-box": SxOverlaySelectionBox;
  }
}
