from __future__ import annotations

from copy import deepcopy

from app.data_loader import load_all_data, reload_all_data
from app import tools


def test_budget_change_updates_overrun_output() -> None:
    data = deepcopy(load_all_data())
    results = tools.get_budget_vs_actual_by_department(data, "Q2-2026")
    it_row = next(item for item in results if item["department"] == "IT")
    assert it_row["variance"] == 160000

    data["budgets"][0]["actual_spend"] = 700000
    data["budgets"][0]["pending_commitments"] = 100000
    updated = tools.get_budget_vs_actual_by_department(data, "Q2-2026")
    it_updated = next(item for item in updated if item["department"] == "IT")
    assert it_updated["variance"] == -200000
    assert it_updated["status"] == "WITHIN"


def test_stuck_workflow_output_filters_days_stuck() -> None:
    data = reload_all_data()
    stuck = tools.get_stuck_workflows(data, 3)
    assert any(item["workflow_id"] == "WF-006" for item in stuck)
    assert all(item["days_stuck"] > 3 for item in stuck)


def test_vendor_ranking_prefers_high_delay_and_exception_rate() -> None:
    data = reload_all_data()
    ranked = tools.get_vendor_performance(data)
    assert ranked[0]["vendor"] == "HP India Pvt Ltd"
    assert ranked[0]["risk_score"] >= ranked[1]["risk_score"]


def test_profitability_changes_reflect_revenue_and_payroll() -> None:
    data = reload_all_data()
    analysis = tools.analyze_profitability(data, "Q2-2026")
    assert analysis["current_profit"] == -516600
    assert analysis["previous_profit"] == 2622000
    assert analysis["revenue_change"] < 0
    assert analysis["payroll_change"] > 0
    assert analysis["profit_delta"] < 0


def test_savings_include_subscriptions_and_discretionary_requests() -> None:
    data = reload_all_data()
    savings = tools.get_savings_opportunities(data)
    assert savings["unused_subscriptions"]
    assert any(item["is_discretionary"] for item in savings["discretionary_purchases"])


def test_cash_outflow_excludes_payment_backed_workflows_from_pending_commitments() -> None:
    data = reload_all_data()
    forecast = tools.forecast_purchase_cash_outflow(data)
    assert forecast["payment_outflow_total"] == 2443600
    assert forecast["pending_commitments"] == 1190000
    assert forecast["expected_total_outflow"] == 3633600
    assert "PR-1001" in forecast["excluded_request_ids_with_existing_payments"]
    assert "PR-1006" in forecast["excluded_request_ids_with_existing_payments"]
