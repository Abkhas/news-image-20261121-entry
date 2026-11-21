// SPDX-License-Identifier: MIT
// Entry program for news-image-20261121: copies the pre-drawn
// entry.png (1024x1024, Saturday 21 November 2026 world news) into the
// grader's output directory. Standard library only, no network, no
// randomness: both runs write the same bytes.
import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const target = join(outDir, "entry.png");

const size = statSync(source).size;
if (size < 1 || size > 1048576) {
  throw new Error(`entry.png is ${size} bytes, outside 1..1048576`);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);
console.log(`wrote ${target} (${size} bytes)`);
