from preprocessing import get_expenses


def budget_check(df, selected_month, selected_category, budget_limit):
    """
    Check whether spending is within budget.

    If selected_category is "Total", the function checks total expenses
    for the selected month instead of one category.
    """
    expenses = get_expenses(df)

    if selected_category == "Total":
        filtered = expenses[expenses["month"] == selected_month]
    else:
        filtered = expenses[
            (expenses["month"] == selected_month)
            & (expenses["category"] == selected_category)
        ]

    actual_spending = filtered["amount"].sum()
    difference = budget_limit - actual_spending

    return actual_spending, difference


def reallocation_suggestion(df, selected_month, selected_category, overspent_amount):
    """
    Simple heuristic:
    If one category is over budget, suggest reducing spending from the top other
    expense categories in the same month.

    If selected_category is "Total", suggest reducing spending from the top
    expense categories in that month.
    """
    expenses = get_expenses(df)

    if selected_category == "Total":
        month_data = expenses[expenses["month"] == selected_month]
    else:
        month_data = expenses[
            (expenses["month"] == selected_month)
            & (expenses["category"] != selected_category)
        ]

    category_totals = (
        month_data.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    if category_totals.empty:
        return "No categories are available for reallocation in this month."

    top_categories = category_totals.head(3)
    reduction_each = overspent_amount / len(top_categories)

    suggestions = []
    for category in top_categories.index:
        suggestions.append(f"reduce about {reduction_each:.2f} from {category}")

    return "To offset the overspending, you could " + "; ".join(suggestions) + "."