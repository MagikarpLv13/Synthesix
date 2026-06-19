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

export const OVERLAY_TOKENS = tokensCss;
