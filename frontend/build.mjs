// Build the Synthesix UI bundles with esbuild.
// Outputs are committed to ../assets so `python main.py` runs without Node:
//   assets/synthesix-ui.js       app components (IIFE, loaded via classic <script>)
//   assets/synthesix-overlay.js  overlay (IIFE, injected into third-party pages by main.py)
// Both are IIFE so they load over file:// without --allow-file-access-from-files
// (ES modules are CORS-blocked on file:// pages).
import { build, context } from "esbuild";
import { createHash } from "node:crypto";
import { readFile, readdir, unlink, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const assets = resolve(root, "..", "assets");
const extensionDist = resolve(root, "..", "extension", "dist");
const watch = process.argv.includes("--watch");

const common = {
  bundle: true,
  minify: true,
  sourcemap: false,
  target: ["chrome120"],
  legalComments: "none",
  logLevel: "info",
};

const configs = [
  {
    ...common,
    entryPoints: [resolve(root, "src/index.ts")],
    outfile: resolve(assets, "synthesix-ui.js"),
    format: "iife",
  },
  {
    ...common,
    entryPoints: [resolve(root, "src/overlay/index.ts")],
    outfile: resolve(assets, "synthesix-overlay.js"),
    format: "iife",
  },
  {
    ...common,
    entryPoints: [resolve(root, "..", "extension/src/content/bootstrap.ts")],
    outfile: resolve(extensionDist, "content.js"),
    format: "iife",
  },
  {
    ...common,
    entryPoints: [resolve(root, "..", "extension/src/content/focus-guard.ts")],
    outfile: resolve(extensionDist, "focus-guard.js"),
    format: "iife",
  },
  {
    ...common,
    entryPoints: [resolve(root, "..", "extension/src/overlay-main.ts")],
    outfile: resolve(extensionDist, "overlay-main.js"),
    format: "iife",
  },
];

// Brave/Chromium cache the MV3 service worker script by URL and keep serving
// the cached copy across browser restarts — even after a rebuild or a
// manifest version bump (verified 2026-07-08 on Brave 150). The only reliable
// invalidation is a new script URL, so each build writes
// dist/background-<revision>.js, points the manifest at it, and stamps the
// revision into the bundle + dist/revision.json so the Python side can spot
// a still-stale worker and warn.
async function buildBackgroundWorker() {
  const result = await build({
    ...common,
    entryPoints: [resolve(root, "..", "extension/src/background.ts")],
    outfile: resolve(extensionDist, "background.js"),
    format: "esm",
    write: false,
  });
  const bundle = result.outputFiles[0].text;
  const revision = createHash("sha256").update(bundle).digest("hex").slice(0, 16);
  const workerFile = `background-${revision}.js`;

  for (const entry of await readdir(extensionDist)) {
    if (/^background.*\.js$/.test(entry) && entry !== workerFile) {
      await unlink(resolve(extensionDist, entry));
    }
  }
  await writeFile(
    resolve(extensionDist, workerFile),
    `${bundle}globalThis.synthesixBackgroundRevision=${JSON.stringify(revision)};\n`,
  );

  const manifestPath = resolve(root, "..", "extension/manifest.json");
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  manifest.background.service_worker = `dist/${workerFile}`;
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

  await writeFile(
    resolve(extensionDist, "revision.json"),
    `${JSON.stringify({ revision, serviceWorker: `dist/${workerFile}` })}\n`,
  );
  return revision;
}

if (watch) {
  for (const config of configs) {
    const ctx = await context(config);
    await ctx.watch();
  }
  // Watch mode skips the background worker (its filename is revision-stamped):
  // run a full `npm run build` before a real browser session.
  console.log("esbuild: watching frontend/src ...");
} else {
  await Promise.all(configs.map(build));
  const revision = await buildBackgroundWorker();
  console.log(
    "esbuild: built assets/synthesix-ui.js + assets/synthesix-overlay.js"
    + ` + extension/dist (background revision ${revision})`,
  );
}
