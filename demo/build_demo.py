"""
Inlines the lint engine and sample fixtures into the demo page.

Outputs:
  demo/preflight_console.html  - artifact version (the publisher adds the document skeleton)
  public/index.html            - standalone version for Vercel (full document with meta tags)
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"

SAMPLES = [
    ("Weak refund bot", "tc1_weak_refund_bot.json"),
    ("Well-built HR agent", "tc2_strong_hr_agent.json"),
    ("Leaked DB password", "tc3_leaked_secret_sql.json"),
    ("Hidden auditor bait", "tc4_injection_in_audited_prompt.json"),
    ("Travel booker", "wf1_travel_agent_medium.json"),
]

DESCRIPTION = ("PreFlight audits AI agents before they ship: readiness score, leaked-secret scan, "
               "auditor-tampering detection and a red-team plan. Built on Rival CortexOne.")

HEAD = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{DESCRIPTION}">
<meta property="og:title" content="PreFlight: AI agent readiness auditor">
<meta property="og:description" content="{DESCRIPTION}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0a0f18">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230e1726'/%3E%3Cpath d='M6 19l20-8-6 12-3-4-11 0z' fill='%23f2b53a'/%3E%3C/svg%3E">
<style>body{{margin:0}} img{{max-width:100%}} [hidden]{{display:none!important}}</style>
"""


def build() -> str:
    samples = [{"label": label, "config": json.loads((ROOT / "tests" / "fixtures" / f).read_text(encoding="utf-8"))}
               for label, f in SAMPLES]
    page = (DEMO / "console.template.html").read_text(encoding="utf-8")
    page = page.replace("/*__ENGINE__*/", (DEMO / "preflight_lint.js").read_text(encoding="utf-8"))
    return page.replace("/*__SAMPLES__*/", json.dumps(samples, ensure_ascii=False).replace("</", "<\\/"))


if __name__ == "__main__":
    page = build()
    (DEMO / "preflight_console.html").write_text(page, encoding="utf-8")
    # Standalone: the template starts with <title>/<link>/<style> (head content), then the body markup.
    head_part, body_part = page.split("</style>", 1)
    (ROOT / "public").mkdir(exist_ok=True)
    (ROOT / "public" / "index.html").write_text(
        f"{HEAD}{head_part}</style>\n</head>\n<body>{body_part}\n</body>\n</html>\n", encoding="utf-8")
    print("wrote demo/preflight_console.html and public/index.html")
