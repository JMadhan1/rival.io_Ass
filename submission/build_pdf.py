"""
Builds submission/PreFlight_Submission.pdf from SUBMISSION.md.

Directives in SUBMISSION.md:
  {{file:path}}         -> file contents in a code block (agent/system_prompt.txt is extracted from AGENT_CONFIG.md)
  {{shot:name.png|cap}} -> screenshots/name.png as a figure, or a visible "pending" box if missing
  {{output:id}}         -> outputs/id.md rendered as markdown, or a "pending" box
  {{result:id}}         -> first line of outputs/id.md starting with "RESULT:", else "pending"

Usage:  python submission/build_pdf.py
"""

import base64
import html
import pathlib
import re
import shutil
import subprocess
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUB = ROOT / "submission"
PENDING = []


def system_prompt() -> str:
    cfg = (ROOT / "agent" / "AGENT_CONFIG.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Instructions\*\* \(system prompt\)\s*```\n(.*?)```", cfg, re.S)
    return m.group(1).strip()


def run_tests() -> str:
    py = subprocess.run([sys.executable, "tests/test_preflight_lint.py"], cwd=ROOT, capture_output=True, text=True)
    js = subprocess.run(["node", "workflow/score_fuser.test.js"], cwd=ROOT, capture_output=True, text=True)
    par = subprocess.run(["node", "demo/parity.test.js"], cwd=ROOT, capture_output=True, text=True)
    lines = [l for l in (py.stderr + py.stdout).splitlines() if l.strip()]
    text = "$ python tests/test_preflight_lint.py\n" + "\n".join(lines[-15:])
    text += "\n\n$ node workflow/score_fuser.test.js\n" + (js.stdout or js.stderr).strip()
    text += "\n\n$ node demo/parity.test.js\n" + (par.stdout or par.stderr).strip()
    (SUB / "test_results.txt").write_text(text, encoding="utf-8")
    if py.returncode or js.returncode or par.returncode:
        print("WARNING: tests failed. See test_results.txt")
    return text


def pending(label: str) -> str:
    PENDING.append(label)
    return f'<div class="pending">PENDING: {html.escape(label)}</div>'


def sub_file(m):
    rel = m.group(1).strip()
    text = system_prompt() if rel == "agent/system_prompt.txt" else (ROOT / rel).read_text(encoding="utf-8")
    return f"<pre><code>{html.escape(text)}</code></pre>"


def sub_shot(m):
    name, _, cap = m.group(1).partition("|")
    path = SUB / "screenshots" / name.strip()
    if not path.exists():
        return pending(f"screenshot {name.strip()} ({cap.strip()})")
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<figure><img src="data:{mime};base64,{data}"/><figcaption>{html.escape(cap.strip())}</figcaption></figure>'


def sub_output(m):
    path = SUB / "outputs" / f"{m.group(1).strip()}.md"
    if not path.exists():
        return pending(f"output {path.name}: paste the agent/workflow response here")
    body = "\n".join(l for l in path.read_text(encoding="utf-8").splitlines() if not l.startswith("RESULT:"))
    return f'<div class="output">{markdown.markdown(body, extensions=["tables", "fenced_code"])}</div>'


def sub_result(m):
    path = SUB / "outputs" / f"{m.group(1).strip()}.md"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("RESULT:"):
                return html.escape(line[7:].strip())
    return "pending"


CSS = """
@page { size: A4; margin: 16mm 15mm; }
:root { --ink:#16181d; --muted:#5b6170; --accent:#4338ca; --accent2:#0f766e; --line:#e3e5ea; --soft:#f5f6fa; }
body { font: 10.3pt/1.5 "Segoe UI", system-ui, sans-serif; color: var(--ink); }
h1 { font-size: 17pt; color: var(--accent); border-bottom: 2px solid var(--accent); padding-bottom: 4px; margin-top: 26px; page-break-after: avoid; }
h2 { font-size: 13pt; color: var(--ink); margin-top: 18px; page-break-after: avoid; }
h3 { font-size: 11pt; color: var(--accent2); margin-top: 16px; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.3pt; page-break-inside: avoid; }
th, td { border: 1px solid var(--line); padding: 5px 7px; text-align: left; vertical-align: top; }
th { background: var(--soft); }
pre { background: #0f172a; color: #e2e8f0; padding: 10px 12px; border-radius: 6px; font-size: 8.2pt; line-height: 1.4; white-space: pre-wrap; word-break: break-word; }
code { font-family: Consolas, "Cascadia Mono", monospace; }
p code, td code, li code { background: var(--soft); padding: 1px 4px; border-radius: 3px; font-size: 9pt; }
blockquote { border-left: 3px solid var(--accent); margin: 10px 0; padding: 4px 12px; color: var(--muted); background: var(--soft); }
.cover { text-align: center; padding: 70px 20px 30px; page-break-after: always; }
.cover h1 { font-size: 40pt; border: none; margin: 0; }
.cover h2 { font-size: 15pt; color: var(--muted); font-weight: 400; }
.cover blockquote { text-align: left; max-width: 520px; margin: 40px auto; font-size: 11pt; }
.cta { margin-top: 30px; font-size: 12pt; } .cta a { color: var(--accent); font-family: Consolas, monospace; }
.tldr { border: 1.5px solid var(--accent2); border-radius: 8px; padding: 8px 16px; background: #f0fdfa; }
.pending { border: 2px dashed #d97706; color: #b45309; background: #fffbeb; padding: 8px 12px; border-radius: 6px; margin: 8px 0; font-weight: 600; }
.output { border: 1px solid var(--line); border-left: 4px solid var(--accent2); padding: 4px 14px; border-radius: 4px; background: #fcfcfd; font-size: 9.4pt; }
figure { margin: 10px 0; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%; max-height: 120mm; border: 1px solid var(--line); border-radius: 4px; }
figcaption { font-size: 8.8pt; color: var(--muted); margin-top: 3px; }
"""


def find_browser():
    for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"]:
        if pathlib.Path(p).exists():
            return p
    return shutil.which("msedge") or shutil.which("chrome") or shutil.which("google-chrome")


def main():
    run_tests()
    src = (SUB / "SUBMISSION.md").read_text(encoding="utf-8")
    src = re.sub(r"\{\{file:(.*?)\}\}", sub_file, src)
    src = re.sub(r"\{\{shot:(.*?)\}\}", sub_shot, src)
    src = re.sub(r"\{\{output:(.*?)\}\}", sub_output, src)
    src = re.sub(r"\{\{result:(.*?)\}\}", sub_result, src)
    body = markdown.markdown(src, extensions=["tables", "fenced_code", "md_in_html"])
    page = f'<!doctype html><html><head><meta charset="utf-8"><title>PreFlight: Rival.io Submission</title><style>{CSS}</style></head><body>{body}</body></html>'
    out_html = SUB / "PreFlight_Submission.html"
    out_html.write_text(page, encoding="utf-8")

    browser = find_browser()
    out_pdf = SUB / "PreFlight_Submission.pdf"
    if browser:
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out_pdf}", out_html.as_uri()], check=False, capture_output=True, timeout=120)
    print(f"HTML: {out_html}\nPDF:  {out_pdf if out_pdf.exists() else '(not generated: open the HTML and print to PDF)'}")
    if PENDING:
        print(f"\n{len(PENDING)} item(s) still pending:")
        for p in PENDING:
            print("  -", p)


if __name__ == "__main__":
    main()
