// Checks the JS demo engine against the Python CortexOne tool on every fixture.
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { audit } = require("./preflight_lint.js");

const root = path.resolve(__dirname, "..");
const dir = path.join(root, "tests", "fixtures");
const fields = ["static_score", "grade", "gate", "checks", "secrets", "manipulation", "top_fixes"];

for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".json"))) {
  const py = JSON.parse(execFileSync("python", ["-c",
    "import json,sys; sys.path.insert(0,'tools/preflight_lint'); from cortexone_function import audit; " +
    `print(json.dumps(audit(json.load(open('tests/fixtures/${f}', encoding='utf-8')))))`], { cwd: root }).toString());
  const js = audit(JSON.parse(fs.readFileSync(path.join(dir, f), "utf8")));
  for (const k of fields) assert.deepStrictEqual(js[k], py[k], `${f}: field ${k} differs`);
  assert.deepStrictEqual(js.risk.level, py.risk.level, `${f}: risk differs`);
  assert.deepStrictEqual(js.risk.capabilities, py.risk.capabilities, `${f}: capabilities differ`);
  console.log(`parity ok  ${f.padEnd(40)} ${js.static_score} ${js.gate}`);
}
