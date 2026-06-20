import { LitElement, html, css, unsafeCSS } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { tokensCss } from "../tokens";

type OverlayActionElement = HTMLElement & {
  ariaText?: string;
  disabled?: boolean;
  label?: string;
  state?: string;
  titleText?: string;
};

const POSITION_STORAGE_KEY = "synthesix:external-overlay-position";
const VIEWPORT_MARGIN = 16;
const FLOATING_MENU_WIDTH = 200;
const FLOATING_MENU_HEIGHT = 170;

interface DragState {
  height: number;
  pointerId: number;
  startLeft: number;
  startTop: number;
  startX: number;
  startY: number;
  width: number;
}

@customElement("sx-overlay-root")
export class SxOverlayRoot extends LitElement {
  @property({ type: Boolean, reflect: true })
  collapsed = false;

  @state()
  private horizontalEdge: "left" | "right" = "right";

  @state()
  private verticalEdge: "top" | "bottom" = "bottom";

  private dragState: DragState | null = null;

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

    :host([edge="left"]) .toolbar .grip {
      order: 10;
    }

    .grip {
      all: initial;
      box-sizing: border-box;
      display: inline-grid;
      width: 16px;
      height: 32px;
      place-items: center;
      border-radius: 999px;
      color: rgba(226, 232, 240, 0.95);
      cursor: grab;
      pointer-events: auto;
      touch-action: none;
      user-select: none;
    }

    .grip::before {
      content: "";
      display: block;
      width: 8px;
      height: 18px;
      background:
        radial-gradient(currentColor 1.4px, transparent 1.7px) 0 0 / 4px 6px;
      opacity: 0.9;
    }

    .grip:hover,
    .grip:focus-visible {
      background: rgba(15, 23, 42, 0.28);
      outline: none;
    }

    :host([dragging]) .grip {
      cursor: grabbing;
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
      align-items: center;
      flex-direction: column;
      gap: 6px;
      justify-content: flex-end;
      animation: sx-overlay-pop 140ms ease-out both;
    }

    :host([collapsed][vertical-edge="top"]) .collapsed {
      flex-direction: column-reverse;
    }

    :host([collapsed][edge="left"]) .collapsed {
      align-items: flex-start;
    }

    :host([collapsed][edge="right"]) .collapsed {
      align-items: flex-end;
    }

    :host([collapsed]) .grip {
      width: 42px;
      height: 36px;
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(148, 163, 184, 0.45);
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.2);
    }

    :host([collapsed]) ::slotted(sx-overlay-capture-menu) {
      display: none !important;
    }

    :host([menu-edge="left"]) ::slotted(sx-overlay-capture-menu) {
      right: auto !important;
      left: 0 !important;
    }

    :host([menu-edge="right"]) ::slotted(sx-overlay-capture-menu) {
      right: 0 !important;
      left: auto !important;
    }

    :host([menu-vertical-edge="top"]) ::slotted(sx-overlay-capture-menu) {
      top: 50px !important;
      bottom: auto !important;
    }

    :host([menu-vertical-edge="bottom"]) ::slotted(sx-overlay-capture-menu) {
      top: auto !important;
      bottom: 50px !important;
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

  connectedCallback(): void {
    super.connectedCallback();
    window.addEventListener("resize", this.handleResize);
  }

  disconnectedCallback(): void {
    window.removeEventListener("resize", this.handleResize);
    this.stopDrag();
    super.disconnectedCallback();
  }

  protected firstUpdated(): void {
    this.restorePosition();
  }

  private setCollapsed(nextCollapsed: boolean): void {
    if (this.collapsed === nextCollapsed) {
      return;
    }
    const previousRect = this.getBoundingClientRect();
    const anchorRight = previousRect.right;
    const anchorBottom = previousRect.bottom;
    const previousHorizontalEdge = this.horizontalEdge;
    const previousVerticalEdge = this.verticalEdge;
    this.collapsed = nextCollapsed;
    this.dispatchEvent(
      new CustomEvent("synthesix-overlay-toggle", {
        detail: { collapsed: this.collapsed },
        bubbles: true,
        composed: true,
      }),
    );
    void this.updateComplete.then(() => {
      const nextRect = this.getBoundingClientRect();
      const nextLeft =
        previousHorizontalEdge === "right"
          ? anchorRight - nextRect.width
          : previousRect.left;
      const nextTop =
        previousVerticalEdge === "bottom"
          ? anchorBottom - nextRect.height
          : previousRect.top;
      this.applyPosition(nextLeft, nextTop, true);
    });
  }

  private handleResize = (): void => {
    const rect = this.getBoundingClientRect();
    if (!this.hasInlinePosition()) {
      this.updateEdges(rect.left, rect.top, rect.width, rect.height);
      return;
    }
    this.applyPosition(rect.left, rect.top, false);
  };

  private hasInlinePosition(): boolean {
    return this.style.left !== "" && this.style.top !== "";
  }

  private restorePosition(): void {
    try {
      const rawPosition = window.localStorage.getItem(POSITION_STORAGE_KEY);
      if (!rawPosition) {
        const rect = this.getBoundingClientRect();
        this.updateEdges(rect.left, rect.top, rect.width, rect.height);
        return;
      }
      const position = JSON.parse(rawPosition) as {
        left?: unknown;
        top?: unknown;
      };
      if (
        typeof position.left !== "number" ||
        typeof position.top !== "number"
      ) {
        return;
      }
      this.applyPosition(position.left, position.top, false);
    } catch (_error) {
      const rect = this.getBoundingClientRect();
      this.updateEdges(rect.left, rect.top, rect.width, rect.height);
    }
  }

  private startDrag = (event: PointerEvent): void => {
    if (event.button !== 0) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    const rect = this.getBoundingClientRect();
    const target = event.currentTarget as HTMLElement | null;
    target?.setPointerCapture?.(event.pointerId);
    this.dragState = {
      height: rect.height,
      pointerId: event.pointerId,
      startLeft: rect.left,
      startTop: rect.top,
      startX: event.clientX,
      startY: event.clientY,
      width: rect.width,
    };
    this.style.left = `${rect.left}px`;
    this.style.top = `${rect.top}px`;
    this.style.right = "auto";
    this.style.bottom = "auto";
    this.toggleAttribute("dragging", true);
    window.addEventListener("pointermove", this.handleDragMove);
    window.addEventListener("pointerup", this.handleDragEnd);
    window.addEventListener("pointercancel", this.handleDragEnd);
  };

  private handleDragMove = (event: PointerEvent): void => {
    if (!this.dragState || event.pointerId !== this.dragState.pointerId) {
      return;
    }
    const nextLeft =
      this.dragState.startLeft + event.clientX - this.dragState.startX;
    const nextTop =
      this.dragState.startTop + event.clientY - this.dragState.startY;
    this.applyPosition(nextLeft, nextTop, false);
  };

  private handleDragEnd = (event: PointerEvent): void => {
    if (this.dragState && event.pointerId !== this.dragState.pointerId) {
      return;
    }
    this.persistPosition();
    this.stopDrag();
  };

  private stopDrag(): void {
    this.dragState = null;
    this.toggleAttribute("dragging", false);
    window.removeEventListener("pointermove", this.handleDragMove);
    window.removeEventListener("pointerup", this.handleDragEnd);
    window.removeEventListener("pointercancel", this.handleDragEnd);
  }

  private applyPosition(left: number, top: number, persist: boolean): void {
    const rect = this.getBoundingClientRect();
    const width = rect.width || this.dragState?.width || 42;
    const height = rect.height || this.dragState?.height || 36;
    const position = this.clampPosition(left, top, width, height);
    this.style.left = `${position.left}px`;
    this.style.top = `${position.top}px`;
    this.style.right = "auto";
    this.style.bottom = "auto";
    this.updateEdges(position.left, position.top, width, height);
    if (persist) {
      this.persistPosition();
    }
  }

  private clampPosition(
    left: number,
    top: number,
    width: number,
    height: number,
  ): { left: number; top: number } {
    const viewportWidth =
      window.innerWidth || document.documentElement.clientWidth || width;
    const viewportHeight =
      window.innerHeight || document.documentElement.clientHeight || height;
    const maxLeft = Math.max(VIEWPORT_MARGIN, viewportWidth - width - VIEWPORT_MARGIN);
    const maxTop = Math.max(VIEWPORT_MARGIN, viewportHeight - height - VIEWPORT_MARGIN);
    return {
      left: Math.min(Math.max(VIEWPORT_MARGIN, left), maxLeft),
      top: Math.min(Math.max(VIEWPORT_MARGIN, top), maxTop),
    };
  }

  private updateEdges(
    left: number,
    top: number,
    width: number,
    height: number,
  ): void {
    const viewportWidth =
      window.innerWidth || document.documentElement.clientWidth || width;
    const viewportHeight =
      window.innerHeight || document.documentElement.clientHeight || height;
    const roomRight = viewportWidth - left;
    const roomLeft = left + width;
    const roomBelow = viewportHeight - top;
    const roomAbove = top + height;
    const nextHorizontalEdge =
      left + width / 2 < viewportWidth / 2 ? "left" : "right";
    const nextVerticalEdge =
      top + height / 2 < viewportHeight / 2 ? "top" : "bottom";
    const nextMenuEdge =
      roomRight >= FLOATING_MENU_WIDTH + VIEWPORT_MARGIN
        ? "left"
        : roomLeft >= FLOATING_MENU_WIDTH + VIEWPORT_MARGIN
          ? "right"
          : roomRight >= roomLeft
            ? "left"
            : "right";
    const nextMenuVerticalEdge =
      roomBelow >= FLOATING_MENU_HEIGHT + VIEWPORT_MARGIN
        ? "top"
        : roomAbove >= FLOATING_MENU_HEIGHT + VIEWPORT_MARGIN
          ? "bottom"
          : roomBelow >= roomAbove
            ? "top"
            : "bottom";
    this.horizontalEdge = nextHorizontalEdge;
    this.verticalEdge = nextVerticalEdge;
    this.setAttribute("edge", nextHorizontalEdge);
    this.setAttribute("vertical-edge", nextVerticalEdge);
    this.setAttribute("menu-edge", nextMenuEdge);
    this.setAttribute("menu-vertical-edge", nextMenuVerticalEdge);
  }

  private persistPosition(): void {
    const rect = this.getBoundingClientRect();
    try {
      window.localStorage.setItem(
        POSITION_STORAGE_KEY,
        JSON.stringify({ left: Math.round(rect.left), top: Math.round(rect.top) }),
      );
    } catch (_error) {}
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
        <button
          class="grip"
          type="button"
          title="Drag Synthesix overlay"
          aria-label="Drag Synthesix overlay"
          data-synthesix-overlay-drag-handle
          @pointerdown=${this.startDrag}
        ></button>
        <slot name="toolbar"></slot>
        <button
          class="toggle"
          type="button"
          title="Collapse Synthesix overlay"
          aria-label="Collapse Synthesix overlay"
          data-synthesix-overlay-collapse
          @click=${() => this.setCollapsed(true)}
        >
          ${this.horizontalEdge === "left" ? html`&lsaquo;` : html`&rsaquo;`}
        </button>
      </div>
      <div class="collapsed" data-synthesix-overlay-collapsed>
        <button
          class="grip"
          type="button"
          title="Drag Synthesix overlay"
          aria-label="Drag Synthesix overlay"
          data-synthesix-overlay-drag-handle
          @pointerdown=${this.startDrag}
        ></button>
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
