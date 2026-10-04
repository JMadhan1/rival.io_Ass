# Runbook: getting PreFlight onto CortexOne (about 60–90 min)

Everything to paste is already in this repo. Work top to bottom and save screenshots into `submission/screenshots/` using the exact names shown.

## 1. Tool: `preflight_lint` (15 min)
1. cortexone.rival.io → **Tools → New Tool** → runtime **Python 3.13** → name `preflight_lint`.
2. **Code** tab: replace `cortexone_function.py` with `tools/preflight_lint/cortexone_function.py`.
3. **Preview** tab: add a test event for each file in `tools/preflight_lint/test_events/` → Run each.
   Expected: tc1 → REVIEW, tc2 → CLEAR (88), tc3 → BLOCKED, tc4 → REVIEW/HIGH, edge → 400.
4. **Listing**: tagline "Deterministic readiness lint and secret scan for AI-agent prompts", category Developer Tools, add a changelog "1.0 initial" → **Publish** (Unlisted is fine).
5. 📸 `05_tool_studio.png` (code and a passing test output).

## 2. Agent: PreFlight (20 min). Source: `agent/AGENT_CONFIG.md`
1. **Agents → New Agent** → Name, Description, Instructions, Theme → Save. 📸 `01_agent_identity.png`
2. **Persona & Guardrails** → Tone, Working style, 5 Values, 9 guardrails. 📸 `02_persona_guardrails.png`
3. **Tools & Memory** → attach `preflight_lint`; upload `agent/preflight_rubric.md`. 📸 `03_tools_memory.png`
4. **Sub-agents** → New → *Target Simulator* (no tools) and *Prompt Surgeon* (no tools). 📸 `04_subagents.png`
5. **Rituals** → New → *Weekly rubric refresh*. 📸 `06_ritual.png`

## 3. Test in Trial Chat (20 min). Source: `tests/AGENT_TEST_CASES.md`
For each of TC1–TC5:
- Send the message → 📸 `tcN.png`
- Copy the response into `submission/outputs/tcN.md`, with this as the **first line**:
  `RESULT: ✅ FAIL as expected (static 0, A4 broke)` (a one-line summary; it fills the results table)
- If a result differs from what's expected, don't hide it. Tighten the prompt, re-run, and mention the iteration in section 5. Graders reward that.

## 4. Workflow: PreFlight Gate (25 min). Source: `workflow/WORKFLOW.md`
1. Create a standalone agent **Prompt Surgeon** (same instructions as the sub-agent).
2. **Workflows → New** → build steps 1–8 (or paste the RivalBot shortcut, then fix the bindings). Keep the step names exact.
3. Code step → paste `workflow/score_fuser.js`. If the Code step's API differs, keep the `fuse()` function and adapt only the 6-line wrapper at the bottom.
4. 📸 `07_workflow_canvas.png`
5. Run with `tests/fixtures/wf1_travel_agent_medium.json` → 📸 `wf1.png` → final output → `submission/outputs/wf1.md` (with a RESULT: line).
6. Run with `tests/fixtures/wf2_leaked_slack_token.json` → 📸 `wf2.png` → `submission/outputs/wf2.md`.

## 5. Build and send
```bash
python submission/build_pdf.py
```
- It lists anything still pending. Fill in your name in `submission/SUBMISSION.md` (`[YOUR FULL NAME]`).
- Open `submission/PreFlight_Submission.pdf`, review it, and reply to the email with the PDF **before 6 Oct 2026, midnight**.
