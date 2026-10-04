RESULT: ✅ BLOCKED path · Trigger → Static Lint → Secrets found? (true) → Reject: Secrets · no agent/LLM step ran

**Input:** StandupBot, with a Slack token hard-coded in its instructions.

**Run log (CortexOne):** Manual Trigger ✔ Succeeded → Static Lint ✔ Succeeded → Secrets found? ✔ Succeeded → Reject: Secrets ✔ Succeeded → *run succeeded*. The Red-Team / Score / Repair branch never executed.

**Final output (verbatim):**
```json
{
  "status": "BLOCKED",
  "message": "Submission rejected: hard-coded credentials found. Rotate them, move them to CortexOne Secrets and resubmit. The prompt was NOT sent to any model.",
  "secrets": [
    { "line": 3, "type": "Slack token", "field": "instructions", "redacted": "xoxb******** (38 chars)" }
  ],
  "agent_name": "StandupBot",
  "static_score": 6
}
```

**Why this is the key design result:** the leak is caught by deterministic code, and "Output only these fields" means the raw prompt is not passed downstream, so the secret never reaches a model and only the redacted form appears in the output. This is the guarantee the chat agent couldn't give in TC3.
