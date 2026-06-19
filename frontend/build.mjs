// Build the Synthesix UI bundles with esbuild.
// Outputs are committed to ../assets so `python main.py` runs without Node:
//   assets/synthesix-ui.js       app components (ESM, loaded via <script type=module>)
//   assets/synthesix-overlay.js  overlay (IIFE, injected into third-party pages by main.py)
import { build, context } from "esbuild";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const assets = resolve(root, "..", "assets");
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
    format: "esm",
  },
  {
    ...common,
    entryPoints: [resolve(root, "src/overlay/index.ts")],
    outfile: resolve(assets, "synthesix-overlay.js"),
    format: "iife",
  },
];

function normalizeOutput(path) {
  const content = readFileSync(path, "utf8")
    .split(/\r?\n/)
    .map((line) => line.trimEnd())
    .join("\n");
  writeFileSync(path, `${content.trimEnd()}\n`, "utf8");
}

if (watch) {
  for (const config of configs) {
    const ctx = await context(config);
    await ctx.watch();
  }
  console.log("esbuild: watching frontend/src ...");
} else {
  await Promise.all(configs.map(build));
  configs.forEach((config) => normalizeOutput(config.outfile));
  console.log("esbuild: built assets/synthesix-ui.js + assets/synthesix-overlay.js");
}
