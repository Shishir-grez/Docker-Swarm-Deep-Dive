import { build } from "esbuild";
await build({
  entryPoints: ["entry.js"], bundle: true, outfile: "dist/bundle.js", format: "iife",
  loader: { ".css": "empty", ".woff2": "empty" }, define: { "process.env.NODE_ENV": '"production"', "process.env.IS_PREACT": '"false"' },
  logLevel: "error", minify: false,
});
console.log("bundled");
