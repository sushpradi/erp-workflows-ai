from __future__ import annotations

import json

import streamlit as st

from app.chat_engine import SUGGESTED_QUESTIONS, answer_question


st.set_page_config(page_title="Workflow Intelligence Copilot", layout="wide")

st.title("Workflow Intelligence Copilot")
st.caption(
    "An intelligence layer over ERP workflow and finance data. Python calculates. AI explains."
)

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("Suggested Questions")
    for question in SUGGESTED_QUESTIONS:
        if st.button(question, use_container_width=True):
            st.session_state.selected_question = question

default_value = st.session_state.selected_question
question = st.text_input("Ask a workflow or finance question", value=default_value)

if st.button("Ask", type="primary") and question.strip():
    response = answer_question(question.strip())
    st.session_state.history.append(response)
    st.session_state.selected_question = question.strip()

for response in reversed(st.session_state.history):
    st.subheader(response.question)
    st.markdown(response.answer)
    st.caption(
        f"Intent: {response.intent.intent} | intent via {response.intent.source} | "
        f"LLM answer: {'yes' if response.used_llm_for_answer else 'no'}"
    )
    with st.expander("Tool Output"):
        st.code(
            json.dumps(
                {
                    "intent": response.intent.intent,
                    "tools_used": response.tool_result.tools_used,
                    "facts": response.tool_result.facts,
                },
                indent=2,
            ),
            language="json",
        )
