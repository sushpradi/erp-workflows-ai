# DESIGN.md

# Workflow Intelligence Copilot

## Vision

Traditional ERP systems are document-centric.

Users need to navigate multiple modules:

- Purchase Requests
- Purchase Orders
- Goods Receipts
- Invoices
- Payments
- Budgets
- Approval History
- Vendors

But users don't think in documents.

They ask:

- Why are purchases taking longer?
- Which workflows are stuck?
- Which teams are over budget?
- Where can we cut spending?
- Why are we seeing losses?

This project demonstrates a Workflow Intelligence Layer.

The ERP remains the system of record.

Python performs deterministic calculations.

AI provides:

- conversational access
- summarization
- explanation
- recommendations

---

# Core Principle

Transactions remain deterministic.

AI is an intelligence layer.

AI never invents facts.

AI only explains facts computed by tools.

---

# Architecture

```text
Question
    ↓
Intent Classification
    ↓
Tool Selection
    ↓
Python Tools
    ↓
Structured Facts
    ↓
LLM
    ↓
Business Answer
```

---

# Tech Stack

Frontend:

- Streamlit

Language:

- Python 3.11+

Storage:

- JSON files

AI:

- OpenAI / Gemini / Claude (optional)

Fallback:

- Rule-based mode without LLM

---

# Repository Structure

workflow-intelligence-copilot/

README.md

DESIGN.md

ARCHITECTURE.md

BRAIN.md

DEMO_QUESTIONS.md

app/

    ui.py

    chat_engine.py

    tools.py

    data_loader.py

    prompts.py

    models.py

sample_data/

    workflows.json

    budgets.json

    vendors.json

    invoices.json

    approvals.json

    payments.json

    revenue.json

    payroll.json

    receivables.json

    subscriptions.json

tests/

---

# Streamlit UI

Two-column layout.

------------------------------------------------

| Suggested Questions | Chat Window |

------------------------------------------------

| Question 1 | |

| Question 2 | |

| Question 3 | |

| ... | |

------------------------------------------------

Clicking a question should populate the chat box.

Users can also type their own questions.

---

# Sidebar Questions

## Question 1

Why are purchases taking longer this quarter?

Purpose:

Identify bottlenecks.

---

## Question 2

Which workflows are stuck and who is blocking them?

Purpose:

Visibility and accountability.

---

## Question 3

Which departments are likely to exceed their purchase budget this quarter?

Purpose:

Budget planning.

---

## Question 4

How much cash outflow should we expect from approved and pending purchases?

Purpose:

Cash forecasting.

---

## Question 5

Which vendors are causing the most delays or exceptions?

Purpose:

Vendor performance.

---

## Question 6

Are there any purchases above approval limits without proper approval?

Purpose:

Compliance.

---

## Question 7

Where are we spending more than usual compared to last quarter?

Purpose:

Trend analysis.

---

## Question 8

What should I follow up on today?

Purpose:

Operational prioritization.

---

## Question 9

Why are we seeing losses this quarter?

Purpose:

Cross-functional business analysis.

---

## Question 10

Where can we cut spending without affecting operations?

Purpose:

Executive recommendations.

---

# Answer Format

Every answer should contain:

## Direct Answer

Short executive summary.

## Supporting Evidence

Numbers and facts.

## Root Cause

Why it happened.

## Recommendation

Suggested next action.

Example:

Direct Answer

IT is projected to exceed budget.

Supporting Evidence

Budget: ₹10L

Current spend: ₹8.4L

Pending commitments: ₹3.2L

Projected spend: ₹11.6L

Root Cause

Laptop purchases and pending requests.

Recommendation

Require CFO approval for further purchases.

---

# Demo Goal

Demonstrate that AI can provide cross-functional intelligence over workflow and finance data.

This is not a chatbot over ERP.

This is a Workflow Intelligence Layer.
