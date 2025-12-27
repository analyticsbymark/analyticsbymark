import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const configPath = path.resolve(
  __dirname,
  "../docs/js/experiments.config.js"
);

const src = fs.readFileSync(configPath, "utf8");

const objText = src
  .replace(/^\s*window\.EXPERIMENT_CONFIG\s*=\s*/, "")
  .replace(/;\s*$/, "");

const config = Function(`"use strict"; return (${objText});`)();

console.log(JSON.stringify(config, null, 2));
