# Synthesix Chrome Extension

This directory contains the unpacked MV3 extension used by Synthesix for
future http/https page integration.

Current scope:

- content scripts run only on `http://*/*` and `https://*/*`;
- no scripts run on Synthesix `file://` pages;
- permissions are limited to `storage`;
- captures remain handled by Python through CDP.

Build:

```powershell
cd frontend
npm run build
cd ..
```

The build writes the service worker as `dist/background-<revision>.js` and
points `manifest.json` at it. Brave/Chromium cache the MV3 worker script by
URL across browser restarts (a rebuild or even a manifest version bump does
not refresh it); the per-build filename defeats that cache, so a browser
restart always picks up the latest worker. `dist/revision.json` exposes the
expected revision and Synthesix logs a warning when the running worker does
not match (stale worker: restart the browser).

Manual loading until T-032 wires automatic startup:

1. Open `chrome://extensions`.
2. Enable developer mode.
3. Choose `Load unpacked`.
4. Select the repository `extension` directory.
5. Open an `https://` page and verify
   `document.documentElement.dataset.synthesixExt` matches the manifest
   version.
6. Open a Synthesix `file://` page and verify that marker is absent.

Runtime loading:

- `SYNTHESIX_EXTENSION_MODE=auto` (default) asks Synthesix to pass
  `--load-extension=<repo>/extension` when the built files exist.
- `SYNTHESIX_EXTENSION_MODE=off` disables extension loading and keeps the
  current CDP overlay path.
- `SYNTHESIX_EXTENSION_DIR=<path>` overrides the extension directory.

If Chrome ignores `--load-extension`, install the unpacked extension once in
the persistent `zendriver-profile/` profile:

1. Start Synthesix normally.
2. In the controlled browser, open `chrome://extensions`.
3. Enable developer mode.
4. Load the repository `extension` directory as an unpacked extension.
5. Restart Synthesix and check that the marker appears on an `https://` page.
