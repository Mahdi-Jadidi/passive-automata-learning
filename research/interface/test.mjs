import { readFileSync } from "node:fs";
import { runTests } from "./audit.mjs";
const fixtures = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url), "utf8"));
const results = runTests(fixtures);
for (const result of results) console.log(result);
console.log(results.length + " passed");
