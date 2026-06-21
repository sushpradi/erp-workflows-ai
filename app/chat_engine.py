from __future__ import annotations

from typing import Callable

from app import tools
from app.data_loader import load_all_data
from app.llm_client import classify_intent_with_llm, llm_is_configured, render_answer_with_llm
from app.models import ChatResponse, IntentResult, ToolResult


SUGGESTED_QUESTIONS = [
    "Why are purchases taking longer this quarter?",
    "Which workflows are stuck and who is blocking them?",
    "Which departments are likely to exceed their purchase budget this quarter?",
    "How much cash outflow should we expect from approved and pending purchases?",
    "Which vendors are causing the most delays or exceptions?",
    "Are there any purchases above approval limits without proper approval?",
    "Where are we spending more than usual compared to last quarter?",
    "What should I follow up on today?",
    "Why are we seeing losses this quarter?",
    "Where can we cut spending without affecting operations?",
]


def classify_intent_rule_based(question: str) -> IntentResult:
    text = question.lower()
    rules = [
        ("purchase_delay", ["taking longer", "delay", "slow", "bottleneck"]),
        ("stuck_workflows", ["stuck", "blocking", "blocked", "who is blocking"]),
        ("budget_overrun", ["budget", "over budget", "exceed"]),
        ("cash_outflow", ["cash outflow", "outflow", "payment", "approved and pending"]),
        ("vendor_risk", ["vendor", "vendors", "exceptions"]),
        ("policy_violation", ["approval limits", "proper approval", "policy", "violation"]),
        ("spend_trend", ["more than usual", "last quarter", "spending more"]),
        ("follow_up", ["follow up", "today", "attention"]),
        ("profitability", ["loss", "losses", "profit"]),
        ("savings", ["cut spending", "save money", "without affecting operations"]),
    ]
    scored = []
    for intent, keywords in rules:
        matches = sum(1 for keyword in keywords if keyword in text)
        if matches:
            scored.append((intent, matches / len(keywords), keywords))
    if not scored:
        return IntentResult(
            intent="follow_up",
            confidence=0.2,
            reason="No direct keyword match; defaulted to operational follow-up.",
            source="rules",
        )
    scored.sort(key=lambda item: item[1], reverse=True)
    primary = scored[0]
    secondaries = [intent for intent, _, _ in scored[1:3]]
    cross_functional = primary[0] in {"stuck_workflows", "follow_up", "profitability", "savings", "cash_outflow"}
    return IntentResult(
        intent=primary[0],
        confidence=round(min(0.95, 0.45 + primary[1]), 2),
        secondary_intents=secondaries,
        needs_cross_functional_data=cross_functional,
        reason=f"Matched keywords: {', '.join(keyword for keyword in primary[2] if keyword in text)}",
        source="rules",
    )


def should_use_llm_for_intent(result: IntentResult) -> bool:
    return llm_is_configured() and result.confidence < 0.6


def _execute_intent(intent: str, data: dict) -> ToolResult:
    mapping: dict[str, Callable[[dict], dict]] = {
        "purchase_delay": lambda payload: {
            "current_quarter_cycle_time": tools.get_average_purchase_cycle_time(payload, "Q2-2026"),
            "previous_quarter_cycle_time": tools.get_average_purchase_cycle_time(payload, "Q1-2026"),
            "stage_delay_breakdown": tools.get_stage_delay_breakdown(payload, "Q2-2026"),
            "top_bottlenecks": tools.get_top_bottleneck_stages(payload, "Q2-2026"),
        },
        "stuck_workflows": lambda payload: {
            "stuck_workflows": tools.get_stuck_workflows(payload, 3),
        },
        "budget_overrun": lambda payload: tools.project_budget_utilization(payload, "Q2-2026"),
        "cash_outflow": lambda payload: tools.forecast_purchase_cash_outflow(payload),
        "vendor_risk": lambda payload: {
            "vendor_performance": tools.get_vendor_performance(payload),
        },
        "policy_violation": lambda payload: {
            "policy_violations": tools.get_policy_violations(payload),
        },
        "spend_trend": lambda payload: {
            "category_spend_comparison": tools.compare_spend_by_category(payload, "Q2-2026"),
        },
        "follow_up": lambda payload: tools.get_items_requiring_attention(payload),
        "profitability": lambda payload: tools.analyze_profitability(payload, "Q2-2026"),
        "savings": lambda payload: tools.get_savings_opportunities(payload),
    }
    facts = mapping[intent](data)
    return ToolResult(intent=intent, facts=facts, tools_used=_tool_names_for_intent(intent))


def _tool_names_for_intent(intent: str) -> list[str]:
    names = {
        "purchase_delay": [
            "get_average_purchase_cycle_time",
            "get_stage_delay_breakdown",
            "get_top_bottleneck_stages",
        ],
        "stuck_workflows": ["get_stuck_workflows"],
        "budget_overrun": ["get_budget_vs_actual_by_department", "project_budget_utilization"],
        "cash_outflow": ["forecast_purchase_cash_outflow"],
        "vendor_risk": ["get_vendor_performance"],
        "policy_violation": ["get_policy_violations"],
        "spend_trend": ["compare_spend_by_category"],
        "follow_up": ["get_items_requiring_attention"],
        "profitability": ["analyze_profitability"],
        "savings": ["get_savings_opportunities"],
    }
    return names[intent]


def _format_currency(value: int | float) -> str:
    return f"₹{value:,.0f}"


def render_rule_based_answer(question: str, tool_result: ToolResult) -> str:
    facts = tool_result.facts
    intent = tool_result.intent
    if intent == "stuck_workflows":
        items = facts["stuck_workflows"]
        answer = f"{len(items)} workflows are stuck for more than 3 days."
        data_used = "\n".join(
            f"- {item['workflow_id']} with {item['current_owner']} at {item['current_stage']} for {item['days_stuck']} days"
            for item in items[:5]
        )
    elif intent == "budget_overrun":
        over = facts["over_budget_departments"]
        answer = f"{len(over)} departments are projected to exceed budget this quarter."
        data_used = "\n".join(
            f"- {item['department']}: budget {_format_currency(item['budget'])}, projected {_format_currency(item['projected_spend'])}, variance {_format_currency(item['variance'])}"
            for item in over
        )
    elif intent == "cash_outflow":
        answer = f"Expected purchase cash outflow in the next 45 days is {_format_currency(facts['expected_total_outflow'])}."
        data_used = "\n".join(
            [
                f"- Payment outflow total: {_format_currency(facts['payment_outflow_total'])}",
                f"- Pending commitments without payment records: {_format_currency(facts['pending_commitments'])}",
                f"- Next 7 days: {_format_currency(facts['windows']['7_days'])}",
                f"- Next 30 days: {_format_currency(facts['windows']['30_days'])}",
                f"- Next 45 days: {_format_currency(facts['windows']['45_days'])}",
            ]
        )
    elif intent == "vendor_risk":
        rows = facts["vendor_performance"]
        answer = f"{rows[0]['vendor']} is the highest-risk vendor right now."
        data_used = "\n".join(
            f"- {item['vendor']}: delay {item['avg_delivery_delay_days']} days, exception rate {item['invoice_exception_rate_percent']}%, risk score {item['risk_score']}"
            for item in rows[:4]
        )
    elif intent == "profitability":
        answer = f"Profit declined by {_format_currency(abs(facts['profit_delta']))} versus the previous quarter."
        data_used = "\n".join(
            [
                f"- Revenue change: {_format_currency(facts['revenue_change'])}",
                f"- Payroll change: {_format_currency(facts['payroll_change'])}",
                f"- Purchase spend change: {_format_currency(facts['purchase_spend_change'])}",
                f"- Receivables change: {_format_currency(facts['receivables_change'])}",
            ]
        )
    elif intent == "savings":
        answer = f"Identified {_format_currency(facts['estimated_savings'])} in potential savings without major operational impact."
        data_used = "\n".join(
            [f"- Discretionary pending purchases: {len(facts['discretionary_purchases'])} items"]
            + [
                f"- Unused {item['product']} licenses: {item['unused_licenses']} for {_format_currency(item['estimated_savings'])}"
                for item in facts["unused_subscriptions"]
            ]
        )
    else:
        answer = f"The question '{question}' was answered using deterministic workflow data."
        data_used = f"- Tools used: {', '.join(tool_result.tools_used)}"
    return "\n\n".join(
        [
            "Answer",
            answer,
            "Data Used",
            data_used or "- No supporting data available.",
        ]
    )


def answer_question(question: str) -> ChatResponse:
    data = load_all_data()
    rule_result = classify_intent_rule_based(question)
    if should_use_llm_for_intent(rule_result):
        try:
            intent = classify_intent_with_llm(question)
            used_llm_for_intent = True
        except Exception:
            intent = rule_result
            used_llm_for_intent = False
    else:
        intent = rule_result
        used_llm_for_intent = False
    tool_result = _execute_intent(intent.intent, data)
    tool_payload = {
        "intent": tool_result.intent,
        "tools_used": tool_result.tools_used,
        "facts": tool_result.facts,
    }
    if llm_is_configured():
        try:
            answer = render_answer_with_llm(question, tool_payload)
            used_llm_for_answer = True
        except Exception:
            answer = render_rule_based_answer(question, tool_result)
            used_llm_for_answer = False
    else:
        answer = render_rule_based_answer(question, tool_result)
        used_llm_for_answer = False
    return ChatResponse(
        question=question,
        intent=intent,
        tool_result=tool_result,
        answer=answer,
        used_llm_for_intent=used_llm_for_intent,
        used_llm_for_answer=used_llm_for_answer,
    )
