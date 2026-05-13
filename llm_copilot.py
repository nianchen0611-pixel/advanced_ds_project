import json

from llm_client import call_llm
from finance_tools import (
    monthly_income_expense,
    top_expense_categories,
    category_monthly_spending,
    transaction_summary
)
from anomaly_detection import (
    get_default_anomaly_threshold,
    detect_anomalies,
    detect_category_relative_anomalies
)
from budget_tools import budget_check
from preprocessing import get_expenses


SUPPORTED_TOOLS = [
    "highest_expense_month",
    "highest_income_month",
    "monthly_total_spending",
    "top_expense_category",
    "category_month_highest_spending",
    "month_category_spending",
    "transaction_amount_summary",
    "income_expense_comparison",
    "general_spending_summary",
    "anomaly_detection",
    "budget_check",
    "categories_to_monitor",
    "unknown"
]

def format_amount(value):
    return f"{float(value):,.2f}"


def select_tool_with_llm(user_question):
    """
    Ask the LLM to choose one finance tool.
    The LLM only selects the tool. The actual calculation is done by Python tools.
    """
    prompt = f"""
You are a tool router for a personal finance app.

Choose exactly one tool from this list:
{SUPPORTED_TOOLS}

Tool meanings:
- highest_expense_month: find the month with the highest total expense
- highest_income_month: find the month with the highest total income
- monthly_total_spending: find total expense for a specific month, such as March 2025 or 2025-03
- top_expense_category: find the expense category with the highest total spending
- category_month_highest_spending: find which month had the highest spending for a specific category, such as Cafe, Food, Health, or Loan Given
- income_expense_comparison: compare total income and total expense
- general_spending_summary: summarize total expense, average expense, and transaction count
- anomaly_detection: find unusual expenses or outliers
- budget_check: check whether selected month/category is over budget
- categories_to_monitor: recommend categories to monitor based on high spending
- month_category_spending: find total spending for a specific category in a specific month, such as Cafe in March 2025
- transaction_amount_summary: summarize transaction amount statistics, such as average, median, maximum, minimum, and standard deviation
- unknown: use this if the question does not match any available tool


Examples:
- "Which month had the highest expense?" -> highest_expense_month
- "Which month had the highest income?" -> highest_income_month
- "How much did I spend in March 2025?" -> monthly_total_spending
- "What was my total expense in 2025-03?" -> monthly_total_spending
- "Which category did I spend the most on?" -> top_expense_category
- "Which month did I spend most on Cafe?" -> category_month_highest_spending
- "Were there any unusual expenses?" -> anomaly_detection
- "How do my income and expenses compare?" -> income_expense_comparison
- "Which categories should I monitor?" -> categories_to_monitor
- "Am I over budget?" -> budget_check
- "How much did I spend on Cafe in March 2025?" -> month_category_spending
- "What is my average transaction amount?" -> transaction_amount_summary

User question:
{user_question}

Return JSON only in this exact format:
{{
  "tool": "tool_name",
  "reason": "short reason"
}}
"""

    raw_response = call_llm(prompt)

    try:
        parsed = json.loads(raw_response)
        tool = parsed.get("tool", "unknown")
        reason = parsed.get("reason", "")
    except Exception:
        tool = "unknown"
        reason = "The LLM response was not valid JSON."

    if tool not in SUPPORTED_TOOLS:
        tool = "unknown"

    return tool, reason, raw_response


def match_month_from_question(user_question, available_months):
    """
    Match a month from the user's question.

    Supports:
    - exact format like 2025-03
    - English month names like March / Mar
    """
    q = user_question.lower()

    # Direct match: 2025-03
    for month in available_months:
        if str(month).lower() in q:
            return month

    month_name_map = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06",
        "july": "07",
        "august": "08",
        "september": "09",
        "october": "10",
        "november": "11",
        "december": "12",
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "sept": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }

    for name, number in month_name_map.items():
        if name in q:
            # If year is mentioned, use that year.
            for month in available_months:
                year, month_num = str(month).split("-")
                if month_num == number and year in q:
                    return month

            # If year is not mentioned, return the first matching month number.
            for month in available_months:
                _, month_num = str(month).split("-")
                if month_num == number:
                    return month

    return None


def match_category_from_question(user_question, available_categories):
    """
    Match a category name from the user's question using simple string matching.

    Example:
    - question contains 'cafe' -> category 'Cafe'
    - question contains 'loan given' -> category 'Loan Given'
    """
    q = user_question.lower()

    # Direct category matching
    for category in available_categories:
        category_text = str(category).lower()
        if category_text in q:
            return category

    # A few simple aliases to improve user experience
    aliases = {
        "café": "Cafe",
        "coffee": "Cafe",
        "restaurant": "Food",
        "restaurants": "Food",
        "transport": "Public Transport",
        "bus": "Public Transport",
        "taxi": "Taxi",
        "gift": "Gifts",
        "gifts": "Gifts",
        "healthcare": "Health",
        "medical": "Health",
        "clothing": "Clothes",
        "clothes": "Clothes",
    }

    for keyword, category_name in aliases.items():
        if keyword in q and category_name in available_categories:
            return category_name

    return None


def run_selected_tool(tool_name, df, user_question="", budget_context=None, anomaly_multiplier=1.5):
    """
    Run the deterministic finance tool selected by the LLM.
    """
    monthly = monthly_income_expense(df)
    top_categories = top_expense_categories(df, top_n=10)
    expenses = get_expenses(df)

    if tool_name == "highest_expense_month":
        row = monthly.loc[monthly["Expense"].idxmax()]
        return {
            "tool": tool_name,
            "month": row["month"],
            "total_expense": float(row["Expense"])
        }

    if tool_name == "highest_income_month":
        row = monthly.loc[monthly["Income"].idxmax()]
        return {
            "tool": tool_name,
            "month": row["month"],
            "total_income": float(row["Income"])
        }

    if tool_name == "monthly_total_spending":
        available_months = sorted(monthly["month"].unique())

        matched_month = match_month_from_question(
            user_question,
            available_months
        )

        if matched_month is None:
            return {
                "tool": tool_name,
                "message": "Could not identify the month from the question.",
                "available_months": list(available_months)
            }

        row = monthly[monthly["month"] == matched_month].iloc[0]

        return {
            "tool": tool_name,
            "month": matched_month,
            "total_expense": float(row["Expense"]),
            "total_income": float(row["Income"])
        }

    if tool_name == "top_expense_category":
        if top_categories.empty:
            return {
                "tool": tool_name,
                "message": "No expense category data available."
            }

        row = top_categories.iloc[0]
        return {
            "tool": tool_name,
            "category": row["category"],
            "total_spending": float(row["total_expense"])
        }

    if tool_name == "category_month_highest_spending":
        available_categories = sorted(expenses["category"].dropna().unique())

        matched_category = match_category_from_question(
            user_question,
            available_categories
        )

        if matched_category is None:
            return {
                "tool": tool_name,
                "message": "Could not identify the category from the question.",
                "available_categories": list(available_categories)
            }

        category_month = category_monthly_spending(df)
        filtered = category_month[category_month["category"] == matched_category]

        if filtered.empty:
            return {
                "tool": tool_name,
                "category": matched_category,
                "message": "No monthly spending data is available for this category."
            }

        top_row = filtered.sort_values("amount", ascending=False).iloc[0]

        total_spending = float(top_row["amount"])

        return {
            "tool": tool_name,
            "category": matched_category,
            "month": top_row["month"],
            "total_spending": total_spending,
            "formatted_total_spending": format_amount(total_spending)
        }
    
    if tool_name == "month_category_spending":
        available_months = sorted(monthly["month"].unique())
        available_categories = sorted(expenses["category"].dropna().unique())

        matched_month = match_month_from_question(
            user_question,
            available_months
        )

        matched_category = match_category_from_question(
            user_question,
            available_categories
        )

        if matched_month is None:
            return {
                "tool": tool_name,
                "message": "Could not identify the month from the question.",
                "available_months": list(available_months)
            }

        if matched_category is None:
            return {
                "tool": tool_name,
                "message": "Could not identify the category from the question.",
                "available_categories": list(available_categories)
            }

        category_month = category_monthly_spending(df)

        filtered = category_month[
            (category_month["month"] == matched_month)
            & (category_month["category"] == matched_category)
        ]

        if filtered.empty:
            return {
                "tool": tool_name,
                "month": matched_month,
                "category": matched_category,
                "total_spending": 0.0,
                "message": "No spending was found for this month and category."
            }

        row = filtered.iloc[0]

        return {
            "tool": tool_name,
            "month": matched_month,
            "category": matched_category,
            "total_spending": float(row["amount"])
        }
    

    if tool_name == "income_expense_comparison":
        total_income = float(monthly["Income"].sum())
        total_expense = float(monthly["Expense"].sum())

        return {
            "tool": tool_name,
            "total_income": total_income,
            "total_expense": total_expense,
            "difference": total_income - total_expense,
            "status": "income_higher" if total_income >= total_expense else "expense_higher"
        }

    if tool_name == "general_spending_summary":
        if expenses.empty:
            return {
                "tool": tool_name,
                "message": "No expense data available."
            }

        return {
            "tool": tool_name,
            "expense_transaction_count": int(len(expenses)),
            "total_expense": float(expenses["amount"].sum()),
            "average_expense": float(expenses["amount"].mean())
        }
    

    if tool_name == "transaction_amount_summary":
        summary = transaction_summary(df)

        row = summary.iloc[0]

        return {
            "tool": tool_name,
            "count": float(row["count"]),
            "mean": float(row["mean"]),
            "std": float(row["std"]),
            "min": float(row["min"]),
            "q25": float(row["25%"]),
            "median": float(row["50%"]),
            "q75": float(row["75%"]),
            "max": float(row["max"])
        }

    if tool_name == "categories_to_monitor":
        rows = []

        for _, row in top_categories.head(3).iterrows():
            rows.append({
                "category": row["category"],
                "total_expense": float(row["total_expense"])
            })

        return {
            "tool": tool_name,
            "categories_to_monitor": rows
        }

    if tool_name == "budget_check":
        if budget_context is None:
            return {
                "tool": tool_name,
                "message": "Budget context is missing."
            }

        actual_spending, difference = budget_check(
            df,
            budget_context["selected_month"],
            budget_context["selected_category"],
            budget_context["budget_limit"]
        )

        return {
            "tool": tool_name,
            "selected_month": budget_context["selected_month"],
            "selected_category": budget_context["selected_category"],
            "budget_limit": float(budget_context["budget_limit"]),
            "actual_spending": float(actual_spending),
            "difference": float(difference),
            "status": "within_budget" if difference >= 0 else "over_budget"
        }

    if tool_name == "anomaly_detection":
        threshold = get_default_anomaly_threshold(df)

        global_anomalies = detect_anomalies(df, threshold)
        category_anomalies = detect_category_relative_anomalies(
            df,
            multiplier=anomaly_multiplier
        )

        result = {
            "tool": tool_name,
            "global_threshold": float(threshold),
            "largest_global_anomaly": None,
            "strongest_category_relative_anomaly": None
        }

        if not global_anomalies.empty:
            row = global_anomalies.iloc[0]
            result["largest_global_anomaly"] = {
                "date": str(row["date"].date()),
                "month": row["month"],
                "category": row["category"],
                "amount": float(row["amount"])
            }

        if not category_anomalies.empty:
            row = category_anomalies.iloc[0]
            result["strongest_category_relative_anomaly"] = {
                "date": str(row["date"].date()),
                "month": row["month"],
                "category": row["category"],
                "amount": float(row["amount"]),
                "category_mean": float(row["category_mean"]),
                "above_category_average": float(row["above_category_average"])
            }

        return result

    return {
        "tool": "unknown",
        "message": (
            "The question could not be matched to an available finance tool. "
            "Supported question types include monthly comparison, monthly total spending, "
            "category analysis, category-specific monthly spending, anomaly detection, "
            "income-expense comparison, general spending summary, budget checking, "
            "and categories to monitor."
        )
    }

def build_tool_grounded_answer(selected_tool, tool_result):
    """
    Build a deterministic final answer for exact numerical questions.
    This prevents local LLMs from changing or misformatting financial numbers.
    """
    if selected_tool == "highest_expense_month":
        return (
            f"The month with the highest expense was {tool_result['month']}, "
            f"with total expenses of {format_amount(tool_result['total_expense'])}."
        )

    if selected_tool == "highest_income_month":
        return (
            f"The month with the highest income was {tool_result['month']}, "
            f"with total income of {format_amount(tool_result['total_income'])}."
        )

    if selected_tool == "monthly_total_spending":
        return (
            f"In {tool_result['month']}, total expense was "
            f"{format_amount(tool_result['total_expense'])}."
        )

    if selected_tool == "top_expense_category":
        return (
            f"The highest spending category was {tool_result['category']}, "
            f"with total spending of {format_amount(tool_result['total_spending'])}."
        )

    if selected_tool == "category_month_highest_spending":
        return (
            f"The month with the highest spending on {tool_result['category']} was "
            f"{tool_result['month']}, with total spending of "
            f"{format_amount(tool_result['total_spending'])}."
        )

    if selected_tool == "month_category_spending":
        return (
            f"In {tool_result['month']}, total spending on "
            f"{tool_result['category']} was {format_amount(tool_result['total_spending'])}."
        )

    if selected_tool == "transaction_amount_summary":
        return (
            f"The average transaction amount was {format_amount(tool_result['mean'])}, "
            f"the median was {format_amount(tool_result['median'])}, and the maximum "
            f"transaction amount was {format_amount(tool_result['max'])}."
        )

    return None


def generate_final_answer_with_llm(user_question, selected_tool, tool_result):
    """
    Ask the LLM to write the final user-facing answer from the deterministic tool result.
    """
    prompt = f"""
You are a personal finance copilot.

The user asked:
{user_question}

The selected tool is:
{selected_tool}

The deterministic tool result is:
{json.dumps(tool_result, indent=2)}

Write a clear, concise answer for the user.

Rules:
- Use only the numbers from the tool result.
- Do not invent extra data.
- Do not assume the currency is USD.
- Do not use "$" unless the tool result explicitly says the currency is USD.
- If currency is not provided, write numbers without a currency symbol.
- If the selected tool is unknown, explain what types of questions the system can answer.
- If the result includes anomalies, explain why they are unusual.
- Keep the answer practical and easy to understand.
- Do not use markdown formatting such as **bold**, *italics*, or tables.
- If the tool result contains zero spending, explain that no matching spending was found for that month and category.
- Format money-like numbers with commas and two decimal places.
- Example: write 3291.0 as 3,291.00.
- Do not add a currency symbol unless the tool result explicitly provides a currency.
- Write in plain text with short paragraphs.
"""

    return call_llm(prompt)


def answer_with_llm_copilot(user_question, df, budget_context=None, anomaly_multiplier=1.5):
    """
    Full LLM-powered copilot pipeline.

    Workflow:
    1. LLM selects a finance tool.
    2. Python runs the selected deterministic tool.
    3. LLM explains the computed result.
    """
    selected_tool, tool_reason, raw_router_response = select_tool_with_llm(user_question)

    tool_result = run_selected_tool(
        selected_tool,
        df,
        user_question=user_question,
        budget_context=budget_context,
        anomaly_multiplier=anomaly_multiplier
    )

    template_answer = build_tool_grounded_answer(selected_tool, tool_result)

    if template_answer is not None:
        final_answer = template_answer
    else:
        final_answer = generate_final_answer_with_llm(
            user_question=user_question,
            selected_tool=selected_tool,
            tool_result=tool_result
        )
        

    return {
        "selected_tool": selected_tool,
        "tool_reason": tool_reason,
        "raw_router_response": raw_router_response,
        "tool_result": tool_result,
        "final_answer": final_answer
    }