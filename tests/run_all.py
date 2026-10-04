"""End-to-end local check: every test suite, the demo build and the PDF build. Exit code 1 on any failure."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

STEPS = [
    ("Tool unit tests (Python)", [sys.executable, "tests/test_preflight_lint.py"]),
    ("Score Fuser tests (JS)", ["node", "workflow/score_fuser.test.js"]),
    ("Python <-> JS parity", ["node", "demo/parity.test.js"]),
    ("Build demo + site", [sys.executable, "demo/build_demo.py"]),
    ("Site script parses", ["node", "-e",
        "const h=require('fs').readFileSync('public/index.html','utf8');"
        "const s=h.split('<script>')[1].split('</script>')[0];new Function(s);"
        "if(!h.startsWith('<!doctype html>'))throw new Error('missing doctype');console.log('ok')"]),
    ("Build submission PDF", [sys.executable, "submission/build_pdf.py"]),
]

failed = 0
for name, cmd in STEPS:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    ok = r.returncode == 0
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        print((r.stdout + r.stderr)[-2000:])
print(f"\n{len(STEPS) - failed}/{len(STEPS)} steps passed")
sys.exit(1 if failed else 0)
