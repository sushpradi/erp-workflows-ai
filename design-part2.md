---

# DATA MODEL

All business data resides in JSON files.

JSON is the ONLY source of truth.

No business metrics should be hardcoded.

---

## workflows.json

Represents workflow instances.

Example:

```json
{
  "workflow_id":"WF-001",
  "request_id":"PR-1001",
  "title":"Purchase 10 Dell laptops",
  "department":"IT",
  "requester":"Alice",
  "vendor":"Dell India Pvt Ltd",
  "amount":613600,
  "category":"IT Equipment",
  "created_date":"2026-06-01",
  "current_stage":"FINANCE_APPROVAL",
  "current_owner":"Carol",
  "status":"WAITING_FOR_APPROVAL",
  "days_stuck":2,
  "is_blocked":false
}
```

Minimum records:

- 15 workflows

Include:

- completed workflows
- blocked workflows
- approval waiting workflows
- payment pending workflows

---

## budgets.json

Example:

```json
{
  "department":"IT",
  "quarter":"Q2-2026",
  "budget":1000000,
  "actual_spend":840000,
  "pending_commitments":320000
}
```

Departments:

- IT
- Facilities
- Sales
- Admin
- Engineering

---

## vendors.json

Example:

```json
{
  "vendor":"HP India Pvt Ltd",
  "avg_delivery_delay_days":6.5,
  "invoice_exception_rate_percent":28
}
```

Include:

- Dell
- HP
- Lenovo
- OfficeWorks Interiors

---

## invoices.json

Example:

```json
{
  "invoice_id":"INV-1001",
  "request_id":"PR-1001",
  "invoice_amount":613600,
  "po_amount":613600,
  "quantity_invoice":10,
  "quantity_po":10,
  "quantity_received":10,
  "match_status":"PASSED"
}
```

Include some mismatch invoices.

---

## approvals.json

Example:

```json
{
  "request_id":"PR-1031",
  "amount":780000,
  "required_approvals":[
    "Department Manager",
    "Finance Manager",
    "CFO"
  ],
  "actual_approvals":[
    "Department Manager",
    "Finance Manager"
  ],
  "policy_violation":true
}
```

---

## payments.json

Contains:

- due date
- payment amount
- payment status

---

## revenue.json

Quarter-wise revenue.

---

## payroll.json

Quarter-wise payroll.

---

## receivables.json

Outstanding customer receivables.

---

## subscriptions.json

Unused software licenses.

Example:

```json
{
  "product":"Jira",
  "licenses":100,
  "used":80,
  "annual_cost":240000
}
```

---

# TOOL LAYER

File:

```text
app/tools.py
```

Tools perform calculations.

Tools must never call LLM.

Tools return structured dictionaries.

---

## Delay Analysis

```python
get_average_purchase_cycle_time(period)

get_stage_delay_breakdown(period)

get_top_bottleneck_stages(period)
```

---

## Workflow Analysis

```python
get_stuck_workflows(min_days)

get_current_owner(workflow_id)

get_last_action(workflow_id)
```

---

## Budget Analysis

```python
get_budget_vs_actual_by_department()

project_budget_utilization()
```

---

## Cash Forecasting

```python
forecast_purchase_cash_outflow(days)
```

---

## Vendor Analysis

```python
get_vendor_performance()
```

---

## Compliance

```python
get_policy_violations()
```

---

## Trend Analysis

```python
compare_spend_by_category()
```

---

## Operational Attention

```python
get_items_requiring_attention()
```

---

## Profitability

```python
analyze_profitability()
```

Should combine:

- revenue
- payroll
- purchases
- receivables

---

## Savings Opportunities

```python
get_savings_opportunities()
```

Should combine:

- pending purchases
- subscriptions
- vendor trends
- discretionary spend

---

# CHAT ENGINE

File:

```text
app/chat_engine.py
```

Flow:

Question

↓

Intent Classification

↓

Tool Selection

↓

Tool Execution

↓

Structured Facts

↓

LLM

↓

Business Answer

---

# Rule Based Intent Classification

Examples:

If question contains:

delay

taking longer

slow

Then use:

```python
get_average_purchase_cycle_time()

get_stage_delay_breakdown()
```

---

If question contains:

budget

exceed

over budget

Then use:

```python
get_budget_vs_actual_by_department()
```

---

If question contains:

loss

profit

Then use:

```python
analyze_profitability()
```

---

If question contains:

cut spending

save money

Then use:

```python
get_savings_opportunities()
```

---

# PROMPT

File:

```text
app/prompts.py
```

System prompt:

You are Workflow Intelligence Copilot.

Rules:

Never invent numbers.

Only use facts returned by tools.

Always answer in four sections:

1. Direct Answer

2. Supporting Evidence

3. Root Cause

4. Recommendation

If information is unavailable, say so.

---

# BRAIN.md

Philosophy

ERP remains the system of record.

Python tools calculate.

AI explains.

AI summarizes.

AI recommends.

AI never invents facts.

This is not a chatbot over ERP.

This is a Workflow Intelligence Layer.

AI should not perform calculations.

Calculations belong to tools.

LLM is responsible only for:

- explanation
- summarization
- recommendations
- formatting
