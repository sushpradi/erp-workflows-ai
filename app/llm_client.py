from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from app.models import IntentResult
from app.prompts import INTENT_PROMPT_TEMPLATE, SYSTEM_PROMPT, build_answer_prompt


DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def llm_is_configured() -> bool:
    return bool(os.getenv("LLM_API_KEY"))


def _get_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL),
    )


def _chat_json(prompt: str) -> dict[str, Any]:
    response = _get_client().chat.completions.create(
        model=os.getenv("LLM_MODEL", DEFAULT_MODEL),
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def classify_intent_with_llm(question: str) -> IntentResult:
    result = _chat_json(INTENT_PROMPT_TEMPLATE.format(question=question))
    return IntentResult(
        intent=result["intent"],
        confidence=float(result.get("confidence", 0.5)),
        secondary_intents=list(result.get("secondary_intents", [])),
        period=result.get("period", "unknown"),
        needs_cross_functional_data=bool(result.get("needs_cross_functional_data", False)),
        reason=result.get("reason", ""),
        source="llm",
    )


def render_answer_with_llm(question: str, tool_result: dict[str, Any]) -> str:
    response = _get_client().chat.completions.create(
        model=os.getenv("LLM_MODEL", DEFAULT_MODEL),
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_answer_prompt(question, tool_result)},
        ],
    )
    return (response.choices[0].message.content or "").strip()
