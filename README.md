# Workflow Intelligence Copilot

Workflow Intelligence Copilot is a demo of an AI intelligence layer over ERP and workflow data.

It is not a full ERP.
It does not execute real financial transactions.

The key idea is simple:
- Python calculates.
- AI explains.
- JSON is the source of truth.

## How this maps to a real ERP

This demo uses JSON files in `sample_data/` as a stand-in for ERP data.

In a real Frappe or ERPNext deployment, the JSON-backed data loader would be replaced with Frappe table reads or API queries. The deterministic Python tool layer would stay responsible for calculations such as cash forecasting, budget checks, workflow bottleneck detection, vendor ranking, and profitability analysis. The LLM layer would continue to handle intent fallback and concise answer generation over those computed facts.

## What this includes

- Streamlit chat UI with 10 suggested questions
- Deterministic Python tools over JSON sample data
- Hybrid intent routing: rules first, LLM fallback when configured
- Optional LLM answer phrasing
- Rule-based fallback mode without any API key

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

## LLM configuration

The app works without any API key.

To enable LLM-backed intent fallback and answer phrasing, set:

```bash
export LLM_API_KEY=your_key
export LLM_BASE_URL=https://api.groq.com/openai/v1
export LLM_MODEL=llama-3.3-70b-versatile
```

This uses an OpenAI-compatible client, so you can also point it to another compatible provider by changing `LLM_BASE_URL` and `LLM_MODEL`.

## How to try

Open the app.
Click suggested questions in the sidebar.
Or type your own question.

Good demo questions:
- Which workflows are stuck and who is blocking them?
- Which departments are likely to exceed their purchase budget this quarter?
- How much cash outflow should we expect from approved and pending purchases?
- Why are we seeing losses this quarter?
- Where can we cut spending without affecting operations?

## Architecture

1. User asks a question.
2. Rules try to classify intent first.
3. If confidence is weak and `LLM_API_KEY` is present, the LLM classifies intent into strict JSON.
4. Python tools compute facts from `sample_data/`.
5. The app renders the answer using the LLM if available, otherwise a rule-based formatter.

## Tests

```bash
pytest
```
