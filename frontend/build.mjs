// One classic IIFE bundle keeps file:// pages usable without Node at runtime.
import { build, context } from "esbuild";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const config = {
  entryPoints: [resolve(root, "src/index.ts")],
  outfile: resolve(root, "../assets/synthesix-ui.js"),
  bundle: true,
  minify: true,
  sourcemap: false,
  target: ["chrome120"],
  legalComments: "none",
  logLevel: "info",
  format: "iife",
};
if (process.argv.includes("--watch")) {
  const builder = await context(config);
  await builder.watch();
} else {
  await build(config);
}
