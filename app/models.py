from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float
    secondary_intents: list[str] = field(default_factory=list)
    period: str = "current_quarter"
    needs_cross_functional_data: bool = False
    reason: str = ""
    source: str = "rules"


@dataclass(frozen=True)
class ToolResult:
    intent: str
    facts: dict[str, Any]
    tools_used: list[str]


@dataclass(frozen=True)
class ChatResponse:
    question: str
    intent: IntentResult
    tool_result: ToolResult
    answer: str
    used_llm_for_intent: bool
    used_llm_for_answer: bool
