import streamlit as st


def setup_page():
    st.set_page_config(
        page_title="Personal Finance Copilot",
        page_icon="💰",
        layout="wide"
    )

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1150px;
        }

        h1 {
            font-size: 2.2rem !important;
            margin-bottom: 0.4rem;
        }

        h2, h3 {
            margin-top: 1.4rem;
            margin-bottom: 0.8rem;
        }

        [data-testid="stMetric"] {
            background-color: #f8fafc;
            padding: 14px;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }

        [data-testid="stMetricLabel"] {
            color: #374151 !important;
        }

        [data-testid="stMetricValue"] {
            color: #111827 !important;
        }

        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }

        .small-note {
            color: #c7c7c7;
            font-size: 0.92rem;
            line-height: 1.4;
        }

        .section-note {
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 14px;
            padding: 0.8rem 1rem;
            margin-bottom: 1rem;
            color: #f3f4f6;
        }

        .copilot-answer-box {
            background-color: #ecfdf5;
            border: 1px solid #22c55e;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin-top: 1rem;
            margin-bottom: 0.8rem;
            color: #064e3b;
            font-size: 1.05rem;
            line-height: 1.6;
        }

        .copilot-answer-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #047857;
            margin-bottom: 0.5rem;
        }

        .copilot-tool-box {
            background-color: #f8fafc;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 0.6rem 0.9rem;
            color: #374151;
            font-size: 0.9rem;
            margin-top: 0.4rem;
        }

        .copilot-tool-box code {
            background-color: #e8f5e9;
            color: #047857;
            border-radius: 5px;
            padding: 2px 5px;
        }


        </style>
        """,
        unsafe_allow_html=True
    )


def show_title():
    st.title("💰 Personal Finance Copilot")
    st.markdown(
        """
        <div class="small-note">
        A Streamlit prototype for structured personal finance analysis, including monthly trend analysis,
        category-level spending summaries, anomaly detection, budget checking, and simple reallocation suggestions.
        </div>
        """,
        unsafe_allow_html=True
    )