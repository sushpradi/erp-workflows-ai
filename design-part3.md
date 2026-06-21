---

# IMPLEMENTATION RULES — CRITICAL

These rules are mandatory.

## 1. JSON is the source of truth

All business data must come from JSON files under:

```text
sample_data/
```

Do not hardcode business facts in Python code.

Allowed:

- sample JSON data
- prompt templates
- tool names
- UI labels

Not allowed:

- hardcoded final answers
- hardcoded metrics
- hardcoded rankings
- hardcoded recommendations

---

## 2. Dynamic answer requirement

Changing JSON values must automatically change answers.

Example:

If `budgets.json` says:

```json
{
  "department": "IT",
  "budget": 1000000,
  "actual_spend": 840000,
  "pending_commitments": 320000
}
```

Then the answer should say IT is projected to exceed budget by ₹1.6L.

If changed to:

```json
{
  "department": "IT",
  "budget": 1000000,
  "actual_spend": 700000,
  "pending_commitments": 100000
}
```

Then the answer should say IT is within budget.

No Python code should need to change.

---

## 3. Cross-functional answers

Questions must combine multiple data sources where needed.

Examples:

### Why are we seeing losses this quarter?

Must combine:

```text
revenue.json
payroll.json
budgets.json
payments.json
receivables.json
```

### Where can we cut spending?

Must combine:

```text
budgets.json
workflows.json
vendors.json
subscriptions.json
payments.json
```

### Which workflows are stuck and who is blocking them?

Must combine:

```text
workflows.json
approvals.json
payments.json
```

---

## 4. LLM mode and fallback mode

The app should support two modes:

```text
Rule-based mode
LLM mode
```

Rule-based mode must work without any API key.

LLM mode can be enabled using environment variable:

```bash
LLM_API_KEY=...
```

If no API key is available, app should still run.

---

# STREAMLIT UI REQUIREMENTS

## Layout

Use Streamlit.

Sidebar:

- title: Suggested Questions
- list the 10 questions
- clicking a question sends it to the chat input

Main area:

- title: Workflow Intelligence Copilot
- short problem statement
- chat input
- answer display
- optional tool output expander

---

## Sidebar questions

Use exactly these:

```text
1. Why are purchases taking longer this quarter?
2. Which workflows are stuck and who is blocking them?
3. Which departments are likely to exceed their purchase budget this quarter?
4. How much cash outflow should we expect from approved and pending purchases?
5. Which vendors are causing the most delays or exceptions?
6. Are there any purchases above approval limits without proper approval?
7. Where are we spending more than usual compared to last quarter?
8. What should I follow up on today?
9. Why are we seeing losses this quarter?
10. Where can we cut spending without affecting operations?
```

---

# EXPECTED ANSWER BEHAVIOR

## 1. Purchases taking longer

Should calculate:

- current quarter cycle time
- previous quarter cycle time
- stage delays
- top bottleneck

Answer should mention:

- average cycle time increased/decreased
- top bottleneck stage
- owner/team causing most delays
- recommendation

---

## 2. Stuck workflows

Should calculate:

- workflows stuck more than 3 days
- current stage
- current owner
- reason if available

Answer should mention:

- count of stuck workflows
- top stuck items
- who needs to act
- next action

---

## 3. Budget overrun

Should calculate:

```text
projected_spend = actual_spend + pending_commitments
variance = projected_spend - budget
```

Answer should mention:

- departments projected over budget
- projected overrun amount
- drivers

---

## 4. Cash outflow

Should calculate:

- unpaid approved invoices
- pending PO commitments
- likely pending approvals
- due in 7/30/45 days if dates exist

Answer should mention:

- expected cash outflow
- largest upcoming payment
- next 7/30/45 day view

---

## 5. Vendor delays

Should calculate:

- vendor delivery delay
- invoice exception rate
- workflow delays by vendor

Answer should rank vendors by risk.

---

## 6. Approval policy violations

Should detect:

- amount above approval threshold
- missing required approval
- policy violation

Answer should mention:

- request id
- amount
- missing approval
- risk

---

## 7. Spend increase

Should compare category spend current vs previous quarter.

Answer should mention:

- categories with highest increase
- amount increase
- likely driver

---

## 8. Follow up today

Should combine:

- overdue approvals
- blocked workflows
- payments due soon
- budget risk

Answer should produce action list.

---

## 9. Loss analysis

Should combine:

- revenue decline
- payroll increase
- purchase spend increase
- receivables aging

Answer should mention:

- main causes of loss
- quantified impact
- recommendation

---

## 10. Cut spending

Should calculate savings opportunities from:

- discretionary pending purchases
- unused subscriptions
- high-price vendors
- budget overruns
- non-critical workflows

Answer should mention:

- specific cut/postpone opportunities
- estimated savings
- operational impact
- recommendation

---

# TEST REQUIREMENTS

Create tests in:

```text
tests/test_tools.py
```

Tests should verify:

## Budget test

Changing budget data changes overrun output.

## Stuck workflow test

Workflow with `days_stuck > 3` appears in stuck workflow output.

## Vendor test

Vendor with highest delay or exception rate ranks higher.

## Profitability test

Revenue drop and payroll increase affect loss analysis.

## Savings test

Unused subscriptions and discretionary requests appear in savings opportunities.

---

# README REQUIREMENTS

`README.md` must include:

## What this is

Workflow Intelligence Copilot is a demo of an AI intelligence layer over ERP/workflow data.

## What this is not

It is not a full ERP.

It does not execute real financial transactions.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/ui.py
```

For Windows:

```bash
.venv\Scripts\activate
streamlit run app/ui.py
```

## How to try

Open the app.

Click suggested questions in sidebar.

Or type your own questions.

## Key idea

Python calculates.

AI explains.

JSON is source of truth.

---

# DEMO SCRIPT

Use this script while presenting.

## Opening

This demo shows a Workflow Intelligence Layer for ERP.

The real business problem is not only automation.

The real problem is lack of visibility, accountability, and decision support across functions.

---

## Demo Question 1

Ask:

```text
Which workflows are stuck and who is blocking them?
```

Say:

This shows cross-functional visibility and accountability.

---

## Demo Question 2

Ask:

```text
Which departments are likely to exceed their purchase budget this quarter?
```

Say:

This combines budget, actual spend, and pending commitments.

---

## Demo Question 3

Ask:

```text
How much cash outflow should we expect from approved and pending purchases?
```

Say:

This helps finance plan cash outflow from procurement activity.

---

## Demo Question 4

Ask:

```text
Why are we seeing losses this quarter?
```

Say:

This goes beyond purchase workflows and combines revenue, payroll, purchases, and receivables.

---

## Demo Question 5

Ask:

```text
Where can we cut spending without affecting operations?
```

Say:

This converts ERP data into decision support.

---

# ACCEPTANCE CRITERIA

Implementation is complete only if:

- Streamlit app runs locally.
- Sidebar shows 10 suggested questions.
- User can ask free-form questions.
- Answers are generated from JSON-backed tools.
- No final answers are hardcoded.
- Changing JSON changes answers.
- Rule-based mode works without LLM API.
- Optional LLM mode works if API key is present.
- Tool outputs can be inspected in UI.
- Tests pass.
- README explains how to run and demo.
- Code clearly separates:
  - data loading
  - tool calculations
  - chat orchestration
  - UI
  - prompts

---

# FINAL POSITIONING

This is not a chatbot over ERP.

This is a Workflow Intelligence Layer.

The ERP remains the system of record.

Workflow and finance calculations remain deterministic.

AI provides:

- natural language access
- explanation
- summarization
- recommendations

The demo should prove that business users can ask complex cross-functional questions and get useful answers without navigating multiple ERP modules.
