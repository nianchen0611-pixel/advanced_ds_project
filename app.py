import streamlit as st
import pandas as pd
import html

from ui_style import setup_page
from preprocessing import (
    load_default_data,
    standardize_columns,
    get_expenses,
    get_income
)
from finance_tools import (
    transaction_summary,
    monthly_income_expense,
    top_expense_categories
)
from llm_copilot import answer_with_llm_copilot
from llm_client import get_llm_provider_info


def format_llm_text(text):
    """
    Safely display LLM text inside custom HTML.
    This prevents markdown symbols like * or ** from changing the visual style.
    It also preserves line breaks.
    """
    safe_text = html.escape(str(text))
    safe_text = safe_text.replace("\n", "<br>")
    return safe_text


# -------------------------------------------------------
# Page setup
# -------------------------------------------------------

setup_page()

st.title("💰 Personal Finance Copilot")

provider_info = get_llm_provider_info()
st.caption(
    f"Current LLM backend: {provider_info['provider']} | Model: {provider_info['model']}"
)

st.markdown(
    """
    This app uses a **local LLM-powered tool-calling workflow** for personal finance analysis.
    The local LLM runs through Ollama and helps understand the user's natural-language question,
    while deterministic Python tools perform the numerical calculations.
    """
)


# -------------------------------------------------------
# Sidebar: data input
# -------------------------------------------------------

st.sidebar.header("Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload a combined transaction CSV",
    type=["csv"]
)

st.sidebar.markdown("Required columns: `date`, `type`, `category`, `amount`.")
st.sidebar.markdown("Optional columns: `account`, `currency`, `description`.")

try:
    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
        st.sidebar.success("Uploaded file successfully.")
    else:
        raw_df = load_default_data()
        st.sidebar.info("Using combined_transactions.csv.")

    df = standardize_columns(raw_df)

except Exception as e:
    st.error(f"Data loading error: {e}")
    st.stop()

expenses = get_expenses(df)
income = get_income(df)


# -------------------------------------------------------
# Part 1: Dataset Overview
# -------------------------------------------------------

st.header("1. Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Transactions", f"{len(df):,}")

with col2:
    st.metric("Expense Transactions", f"{len(expenses):,}")

with col3:
    st.metric("Income Transactions", f"{len(income):,}")

with col4:
    st.metric("Average Amount", f"{df['amount'].mean():.2f}")

st.subheader("Processed Data Preview")
st.dataframe(df.head(10), use_container_width=True, height=260)


# -------------------------------------------------------
# Part 2: Spending Lookup
# -------------------------------------------------------

st.header("2. Spending Lookup by Month and Category")

st.markdown(
    """
    Use this section to manually check spending for a selected month and category.
    This helps users verify the LLM Copilot's answers with the underlying transaction data.
    """
)

if expenses.empty:
    st.warning("No expense transactions are available.")
else:
    months = sorted(df["month"].unique())
    categories = ["Total"] + sorted(expenses["category"].unique())

    lookup_col1, lookup_col2 = st.columns(2)

    with lookup_col1:
        selected_month = st.selectbox(
            "Choose a month",
            months,
            key="lookup_month"
        )

    with lookup_col2:
        selected_category = st.selectbox(
            "Choose a category",
            categories,
            key="lookup_category"
        )

    if selected_category == "Total":
        lookup_data = expenses[expenses["month"] == selected_month]
    else:
        lookup_data = expenses[
            (expenses["month"] == selected_month)
            & (expenses["category"] == selected_category)
        ]

    actual_spending = lookup_data["amount"].sum()
    transaction_count = len(lookup_data)

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.metric("Selected Month", selected_month)

    with result_col2:
        st.metric("Selected Category", selected_category)

    with result_col3:
        st.metric("Actual Spending", f"{actual_spending:.2f}")

    st.caption(f"Number of matching transactions: {transaction_count}")

    st.dataframe(
        lookup_data[
            ["date", "type", "category", "amount", "account", "currency", "description"]
        ].head(20),
        use_container_width=True,
        height=260
    )



# -------------------------------------------------------
# Part 3: Ask the LLM Finance Copilot
# -------------------------------------------------------

st.header("3. Ask the LLM Finance Copilot")

st.markdown(
    """
    Ask a natural-language finance question.  
    The LLM will select a finance tool, the tool will compute the result,
    and the LLM will explain the result.
    """
)

example_questions = [
    "Which month had the highest expense?",
    "Which month had the highest income?",
    "Which category did I spend the most on?",
    "Which month did I spend most on Cafe?",
    "Were there any unusual expenses?",
    "How do my income and expenses compare over time?",
    "Give me a general spending summary.",
    "Which expense categories should I monitor more carefully?",
    "How much did I spend in the selected month and category?"
]

if "finance_question" not in st.session_state:
    st.session_state.finance_question = ""

if "llm_result" not in st.session_state:
    st.session_state.llm_result = None

if "last_asked_question" not in st.session_state:
    st.session_state.last_asked_question = ""

with st.form("llm_question_form", clear_on_submit=False):
    user_question = st.text_input(
        "Type your finance question",
        key="finance_question",
        placeholder="Example: Which month did I spend most on Cafe?"
    )

    submitted = st.form_submit_button("Ask LLM Copilot")

with st.expander("Example questions you can ask"):
    st.markdown(
        """
        <div style="font-size: 0.88rem; line-height: 1.45;">
        • Which month had the highest expense?<br>
        • Which month had the highest income?<br>
        • Which category did I spend the most on?<br>
        • Which month did I spend most on Cafe?<br>
        • Were there any unusual expenses?<br>
        • How do my income and expenses compare over time?<br>
        • Give me a general spending summary.<br>
        • Which expense categories should I monitor more carefully?<br>
        • How much did I spend on Cafe in April 2025?
        </div>
        """,
        unsafe_allow_html=True
    )

# This budget_context is now based on the manual lookup section.
# Since we removed budget limit from the UI, we use 0.0 as a placeholder.
# Budget-over/under questions should be avoided unless you add a budget limit back.
budget_context = {
    "selected_month": selected_month if "selected_month" in locals() else df["month"].iloc[0],
    "selected_category": selected_category if "selected_category" in locals() else "Total",
    "budget_limit": 0.0
}

if submitted:
    if not st.session_state.finance_question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            st.session_state.last_asked_question = st.session_state.finance_question

            with st.spinner("Calling LLM and running finance tools..."):
                result = answer_with_llm_copilot(
                    user_question=st.session_state.finance_question,
                    df=df,
                    budget_context=budget_context,
                    anomaly_multiplier=1.5
                )

            st.session_state.llm_result = result

        except Exception as e:
            st.error(f"LLM Copilot error: {e}")
            st.info(
                "Please check that the selected LLM backend is running. "
                "If using Ollama, make sure Ollama is installed and the model has been pulled locally."
            )

if st.session_state.llm_result is not None:
    result = st.session_state.llm_result

    safe_answer = format_llm_text(result["final_answer"])
    safe_question = format_llm_text(st.session_state.last_asked_question)
    safe_reason = format_llm_text(result["tool_reason"])
    safe_selected_tool = format_llm_text(result["selected_tool"])

    st.markdown(
        f"""
        <div class="copilot-answer-box">
            <div class="copilot-answer-title">🤖 LLM Copilot Answer</div>
            <div>{safe_answer}</div>
        </div>
        <div class="copilot-tool-box">
            Last question: <code>{safe_question}</code><br>
            LLM selected tool: <code>{safe_selected_tool}</code><br>
            Reason: {safe_reason}
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.expander("Show deterministic tool result"):
        st.json(result["tool_result"])

    with st.expander("Show raw LLM router response"):
        st.write(result["raw_router_response"])

# -------------------------------------------------------
# Part 4: How this app works
# -------------------------------------------------------

st.header("4. How This App Uses LLM + Tools")

st.markdown(
    """
    This version is different from the earlier rule-based prototype.

    Earlier version:
    User question → keyword-based router → pandas tool → template answer

    Current version:
    User question → local Ollama LLM selects a finance tool → deterministic Python tool computes the result → grounded answer is generated from the tool result

    The local LLM is used for language understanding and tool selection, while financial numbers are still computed by deterministic Python tools. This design allows the app to run without relying on an external LLM API.
    """
)


# -------------------------------------------------------
# Part 5: Notes and Limitations
# -------------------------------------------------------

st.header("5. Notes and Limitations")

st.markdown(
    """
    - TThis app uses a local LLM backend through Ollama with qwen2.5:3b.

    - The project uses a pretrained local LLM for inference, not local fine-tuning.

    - Numerical calculations are performed by deterministic Python tools, not by the LLM directly.

    - The local LLM is mainly used for natural-language understanding, tool selection, and explanation.

    - For exact financial numbers, the app uses tool-grounded outputs and deterministic templates to reduce hallucination and formatting errors.

    - Smaller local models may be less stable than larger API-based models, especially for strict JSON tool routing.

    - This is not financial advice; it is a personal finance analysis prototype.
    """
)