from __future__ import annotations

import json


SYSTEM_PROMPT = """You are Workflow Intelligence Copilot.

Rules:
- Never invent facts or numbers.
- Only use facts provided in the tool result JSON.
- If data is unavailable, say so plainly.
- Always answer in exactly four sections with these headings:
1. Direct Answer
2. Supporting Evidence
3. Root Cause
4. Recommendation
"""


INTENT_PROMPT_TEMPLATE = """Classify the ERP analytics question into one primary intent.

Available intents:
- purchase_delay
- stuck_workflows
- budget_overrun
- cash_outflow
- vendor_risk
- policy_violation
- spend_trend
- follow_up
- profitability
- savings

Return only JSON with this exact shape:
{{
  "intent": "one_of_the_intents",
  "confidence": 0.0,
  "secondary_intents": [],
  "period": "current_quarter|previous_quarter|today|unknown",
  "needs_cross_functional_data": true,
  "reason": "short explanation"
}}

Question:
{question}
"""


def build_answer_prompt(question: str, tool_result: dict) -> str:
    payload = json.dumps(tool_result, indent=2)
    return f"""Question: {question}

Structured facts:
{payload}

Write the final answer using the required four sections. Stay grounded in the facts.
"""
