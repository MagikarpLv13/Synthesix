/**
 * Overlay bundle (IIFE) → assets/synthesix-overlay.js
 *
 * MIGRATION TARGET (see frontend/TASKS.md, task #1): move the inline overlay
 * currently built in `main.py` (_install_and_consume_save_overlay) here, as
 * Shadow-DOM Web Components. Hard requirements:
 *  - preserve EVERY CDP action and dataset contract main.py relies on;
 *  - inject `tokensCss` (theme.css is not present on third-party pages);
 *  - keep the footprint minimal and never obscure page content.
 *
 * This placeholder only makes the bundle build until the migration starts.
 */
import { tokensCss } from "../tokens";
import "./sx-overlay-capture-menu";
import "./sx-overlay-selection-trigger";
import "./sx-overlay-selection-box";
import "./sx-overlay-entity-menu";
import "./sx-overlay-action";
import "./sx-overlay-root";

declare global {
  interface Window {
    SynthesixOverlay?: {
      tokensCss: string;
      version: string;
    };
  }
}

window.SynthesixOverlay = {
  tokensCss,
  version: "0.1.0",
};

export const OVERLAY_TOKENS = tokensCss;

/**
 * Host pages with global keyboard shortcuts (TikTok, YouTube, ...) usually
 * decide whether to intercept a keypress by checking `document.activeElement`.
 * That check stops at our Shadow DOM boundary (it only ever sees the custom
 * element host, never the focused `<input>` inside its shadow root), so the
 * host page wrongly assumes no field is focused and calls `preventDefault()`
 * on keys meant to be typed into the overlay's own inputs. Intercepting the
 * event on `window` in the capture phase — the earliest point in the
 * propagation path — stops it from ever reaching the host page's listeners
 * (typically bound on `document`) when it originates in one of our fields.
 */
const isOverlayFieldEvent = (event: Event): boolean => {
  const target = event.composedPath()[0] as HTMLElement | undefined;
  const tag = target?.tagName;
  if (tag !== "INPUT" && tag !== "TEXTAREA" && tag !== "SELECT") {
    return false;
  }
  return event.composedPath().some((node) => {
    const tagName = (node as HTMLElement)?.tagName;
    return typeof tagName === "string" && tagName.startsWith("SX-OVERLAY-");
  });
};

for (const type of ["keydown", "keypress", "keyup"]) {
  window.addEventListener(
    type,
    (event) => {
      if (isOverlayFieldEvent(event)) {
        // stopImmediatePropagation, not just stopPropagation: also blocks
        // any other listener the host page bound on this same `window` node.
        event.stopImmediatePropagation();
        event.stopPropagation();
      }
    },
    true,
  );
}
