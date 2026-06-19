# Synthesix frontend (Palier 1)

TypeScript + Lit Web Components, bundled with esbuild. Read `../COLLAB.md` first
(work agreement + anti-collision protocol).

## Setup

```
cd frontend
npm install        # once; node_modules is git-ignored
npm run build      # writes ../assets/synthesix-ui.js + ../assets/synthesix-overlay.js
npm run watch      # rebuild on change
npm run typecheck  # tsc --noEmit
```

Commit the generated `assets/*.js` bundles together with their source so
`python main.py` keeps working without Node for end users.

## Where the bundles are consumed

- `assets/synthesix-ui.js` — ESM bundle of `<sx-*>` components. Load from a page
  with `<script type="module" src="{asset_prefix}assets/synthesix-ui.js">`, then
  use `<sx-chip>` etc. in markup (Python `ui.py` / `index.html`).
- `assets/synthesix-overlay.js` — IIFE bundle read and injected by `main.py` into
  third-party pages via CDP (replaces the inline overlay over time).

## Add a component

1. Claim the task in `TASKS.md`.
2. Copy `src/components/sx-chip.ts` as the pattern.
3. Register it in `src/index.ts` (app) or wire it in `src/overlay/index.ts`.
4. `npm run build`, add a `demo/<name>.html`, verify visually (below).

## Visual check (headless Chrome, no interactive browser needed)

```
"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new \
  --disable-gpu --hide-scrollbars --window-size=1440,1000 \
  "--screenshot=F:/Dev/Python/MSA/tmp_ui_render/sx-chip.png" \
  "file:///F:/Dev/Python/MSA/frontend/demo/sx-chip.html"
```

(`tmp_ui_render/` is git-ignored scratch space for screenshots.)
