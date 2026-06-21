from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _current_quarter_label(today: date | None = None) -> str:
    today = today or date.today()
    quarter = ((today.month - 1) // 3) + 1
    return f"Q{quarter}-{today.year}"


def _previous_quarter_label(today: date | None = None) -> str:
    today = today or date.today()
    quarter = ((today.month - 1) // 3) + 1
    if quarter == 1:
        return f"Q4-{today.year - 1}"
    return f"Q{quarter - 1}-{today.year}"


def get_average_purchase_cycle_time(data: dict[str, Any], quarter: str) -> dict[str, Any]:
    values = [
        item["cycle_time_days"]
        for item in data["workflows"]
        if item["quarter"] == quarter and item["cycle_time_days"] is not None
    ]
    average = sum(values) / len(values) if values else 0.0
    return {"quarter": quarter, "average_cycle_time_days": round(average, 1), "count": len(values)}


def get_stage_delay_breakdown(data: dict[str, Any], quarter: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for item in data["workflows"]:
        if item["quarter"] == quarter:
            grouped[item["current_stage"]].append(item["days_stuck"])
    result = []
    for stage, days in grouped.items():
        result.append(
            {
                "stage": stage,
                "avg_days_stuck": round(sum(days) / len(days), 1),
                "workflow_count": len(days),
            }
        )
    return sorted(result, key=lambda item: item["avg_days_stuck"], reverse=True)


def get_top_bottleneck_stages(data: dict[str, Any], quarter: str) -> list[dict[str, Any]]:
    return get_stage_delay_breakdown(data, quarter)[:3]


def get_stuck_workflows(data: dict[str, Any], min_days: int = 3) -> list[dict[str, Any]]:
    approvals = {item["request_id"]: item for item in data["approvals"]}
    payments = {item["request_id"]: item for item in data["payments"]}
    results = []
    for item in data["workflows"]:
        if item["days_stuck"] > min_days:
            approval = approvals.get(item["request_id"], {})
            payment = payments.get(item["request_id"], {})
            reason = item.get("blocking_reason") or "Needs review"
            if approval.get("policy_violation"):
                reason = "Approval chain incomplete"
            elif payment.get("payment_status") == "OVERDUE":
                reason = "Payment overdue"
            results.append(
                {
                    "workflow_id": item["workflow_id"],
                    "request_id": item["request_id"],
                    "title": item["title"],
                    "current_stage": item["current_stage"],
                    "current_owner": item["current_owner"],
                    "status": item["status"],
                    "days_stuck": item["days_stuck"],
                    "reason": reason,
                }
            )
    return sorted(results, key=lambda item: item["days_stuck"], reverse=True)


def get_budget_vs_actual_by_department(data: dict[str, Any], quarter: str | None = None) -> list[dict[str, Any]]:
    quarter = quarter or _current_quarter_label()
    results = []
    for item in data["budgets"]:
        if item["quarter"] != quarter:
            continue
        projected = item["actual_spend"] + item["pending_commitments"]
        variance = projected - item["budget"]
        results.append(
            {
                "department": item["department"],
                "quarter": quarter,
                "budget": item["budget"],
                "actual_spend": item["actual_spend"],
                "pending_commitments": item["pending_commitments"],
                "projected_spend": projected,
                "variance": variance,
                "status": "OVER" if variance > 0 else "WITHIN",
                "drivers": item.get("drivers", []),
            }
        )
    return sorted(results, key=lambda item: item["variance"], reverse=True)


def project_budget_utilization(data: dict[str, Any], quarter: str | None = None) -> dict[str, Any]:
    rows = get_budget_vs_actual_by_department(data, quarter)
    over_budget = [item for item in rows if item["variance"] > 0]
    return {
        "quarter": quarter or _current_quarter_label(),
        "departments": rows,
        "over_budget_departments": over_budget,
    }


def forecast_purchase_cash_outflow(data: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    windows = {"7_days": 0, "30_days": 0, "45_days": 0}
    upcoming = []
    active_payment_request_ids = set()
    for item in data["payments"]:
        if item["payment_status"] in {"PAID", "CANCELLED"}:
            continue
        active_payment_request_ids.add(item["request_id"])
        due = _parse_date(item["due_date"])
        delta = (due - today).days
        amount = item["payment_amount"]
        if delta <= 7:
            windows["7_days"] += amount
        if delta <= 30:
            windows["30_days"] += amount
        if delta <= 45:
            windows["45_days"] += amount
        upcoming.append(item)
    pending_workflows_without_payment = [
        item
        for item in data["workflows"]
        if item["status"] in {"WAITING_FOR_APPROVAL", "BLOCKED", "PENDING_PO"}
        and item["request_id"] not in active_payment_request_ids
    ]
    pending_commitments = sum(item["amount"] for item in pending_workflows_without_payment)
    largest_payment = max(upcoming, key=lambda item: item["payment_amount"], default=None)
    return {
        "windows": windows,
        "payment_outflow_total": windows["45_days"],
        "pending_commitments": pending_commitments,
        "expected_total_outflow": windows["45_days"] + pending_commitments,
        "largest_upcoming_payment": largest_payment,
        "pending_workflows_without_payment": pending_workflows_without_payment,
        "excluded_request_ids_with_existing_payments": sorted(active_payment_request_ids),
    }


def get_vendor_performance(data: dict[str, Any]) -> list[dict[str, Any]]:
    workflow_counts: dict[str, list[int]] = defaultdict(list)
    for item in data["workflows"]:
        workflow_counts[item["vendor"]].append(item["days_stuck"])
    results = []
    for vendor in data["vendors"]:
        delays = workflow_counts.get(vendor["vendor"], [])
        workflow_delay = round(sum(delays) / len(delays), 1) if delays else 0.0
        risk_score = round(
            vendor["avg_delivery_delay_days"] * 1.5
            + vendor["invoice_exception_rate_percent"]
            + workflow_delay * 2,
            1,
        )
        results.append(
            {
                "vendor": vendor["vendor"],
                "avg_delivery_delay_days": vendor["avg_delivery_delay_days"],
                "invoice_exception_rate_percent": vendor["invoice_exception_rate_percent"],
                "workflow_delay_days": workflow_delay,
                "risk_score": risk_score,
            }
        )
    return sorted(results, key=lambda item: item["risk_score"], reverse=True)


def get_policy_violations(data: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for item in data["approvals"]:
        if item["policy_violation"]:
            missing = [
                approval
                for approval in item["required_approvals"]
                if approval not in item["actual_approvals"]
            ]
            results.append(
                {
                    "request_id": item["request_id"],
                    "amount": item["amount"],
                    "missing_approvals": missing,
                    "risk": item.get("risk", "Compliance breach"),
                }
            )
    return sorted(results, key=lambda item: item["amount"], reverse=True)


def compare_spend_by_category(data: dict[str, Any], current_quarter: str | None = None) -> list[dict[str, Any]]:
    current_quarter = current_quarter or _current_quarter_label()
    previous_quarter = _previous_quarter_label()
    by_quarter: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for item in data["workflows"]:
        if item["status"] == "COMPLETED":
            by_quarter[item["quarter"]][item["category"]] += item["amount"]
    results = []
    categories = set(by_quarter[current_quarter]) | set(by_quarter[previous_quarter])
    for category in categories:
        current_value = by_quarter[current_quarter].get(category, 0)
        previous_value = by_quarter[previous_quarter].get(category, 0)
        results.append(
            {
                "category": category,
                "current_quarter_spend": current_value,
                "previous_quarter_spend": previous_value,
                "increase": current_value - previous_value,
            }
        )
    return sorted(results, key=lambda item: item["increase"], reverse=True)


def get_items_requiring_attention(data: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    stuck = get_stuck_workflows(data, 3)[:5]
    due_soon = []
    for item in data["payments"]:
        if item["payment_status"] in {"PENDING", "OVERDUE"}:
            delta = (_parse_date(item["due_date"]) - today).days
            if delta <= 7:
                due_soon.append(item)
    budget_risk = [item for item in get_budget_vs_actual_by_department(data) if item["variance"] > 0][:3]
    actions = []
    for item in stuck:
        actions.append(f"Escalate {item['workflow_id']} with {item['current_owner']} ({item['reason']}).")
    for item in due_soon[:3]:
        actions.append(f"Review payment {item['payment_id']} due on {item['due_date']}.")
    for item in budget_risk:
        actions.append(f"Control {item['department']} spend; projected overrun is {item['variance']}.")
    return {
        "stuck_workflows": stuck,
        "payments_due_soon": due_soon,
        "budget_risks": budget_risk,
        "actions": actions,
    }


def analyze_profitability(data: dict[str, Any], current_quarter: str | None = None) -> dict[str, Any]:
    current_quarter = current_quarter or _current_quarter_label()
    previous_quarter = _previous_quarter_label()
    revenue_map = {item["quarter"]: item["revenue"] for item in data["revenue"]}
    payroll_map = {item["quarter"]: item["payroll"] for item in data["payroll"]}
    receivable_map = {item["quarter"]: item["outstanding_receivables"] for item in data["receivables"]}
    purchase_by_quarter: dict[str, int] = defaultdict(int)
    for item in data["workflows"]:
        purchase_by_quarter[item["quarter"]] += item["amount"]
    current_profit = revenue_map[current_quarter] - payroll_map[current_quarter] - purchase_by_quarter[current_quarter]
    previous_profit = revenue_map[previous_quarter] - payroll_map[previous_quarter] - purchase_by_quarter[previous_quarter]
    return {
        "current_quarter": current_quarter,
        "previous_quarter": previous_quarter,
        "current_revenue": revenue_map[current_quarter],
        "previous_revenue": revenue_map[previous_quarter],
        "current_payroll": payroll_map[current_quarter],
        "previous_payroll": payroll_map[previous_quarter],
        "current_purchase_spend": purchase_by_quarter[current_quarter],
        "previous_purchase_spend": purchase_by_quarter[previous_quarter],
        "revenue_change": revenue_map[current_quarter] - revenue_map[previous_quarter],
        "payroll_change": payroll_map[current_quarter] - payroll_map[previous_quarter],
        "purchase_spend_change": purchase_by_quarter[current_quarter] - purchase_by_quarter[previous_quarter],
        "receivables_change": receivable_map[current_quarter] - receivable_map[previous_quarter],
        "current_profit": current_profit,
        "previous_profit": previous_profit,
        "profit_delta": current_profit - previous_profit,
    }


def get_savings_opportunities(data: dict[str, Any]) -> dict[str, Any]:
    discretionary = [
        item
        for item in data["workflows"]
        if item["status"] in {"WAITING_FOR_APPROVAL", "BLOCKED"} and item.get("is_discretionary")
    ]
    subscriptions = []
    for item in data["subscriptions"]:
        unused = item["licenses"] - item["used"]
        if unused > 0:
            savings = round(item["annual_cost"] * (unused / item["licenses"]))
            subscriptions.append(
                {
                    "product": item["product"],
                    "unused_licenses": unused,
                    "estimated_savings": savings,
                }
            )
    vendor_risks = get_vendor_performance(data)[:2]
    over_budget = [item for item in get_budget_vs_actual_by_department(data) if item["variance"] > 0]
    estimated_savings = (
        sum(item["amount"] for item in discretionary)
        + sum(item["estimated_savings"] for item in subscriptions)
    )
    return {
        "discretionary_purchases": discretionary,
        "unused_subscriptions": subscriptions,
        "high_risk_vendors": vendor_risks,
        "over_budget_departments": over_budget,
        "estimated_savings": estimated_savings,
    }
