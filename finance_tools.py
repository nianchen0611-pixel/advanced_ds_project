from preprocessing import get_expenses


def monthly_income_expense(df):
    monthly = (
        df.groupby(["month", "type"])["amount"]
        .sum()
        .reset_index()
        .pivot(index="month", columns="type", values="amount")
        .fillna(0)
    )

    if "Income" not in monthly.columns:
        monthly["Income"] = 0

    if "Expense" not in monthly.columns:
        monthly["Expense"] = 0

    monthly = monthly.reset_index()
    monthly = monthly.sort_values("month")

    return monthly


def top_expense_categories(df, top_n=10):
    expenses = get_expenses(df)

    return (
        expenses.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
        .rename(columns={"amount": "total_expense"})
    )


def category_monthly_spending(df):
    expenses = get_expenses(df)

    category_month = (
        expenses.groupby(["month", "category"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["month", "amount"], ascending=[True, False])
    )

    return category_month


def transaction_summary(df):
    return df["amount"].describe().to_frame().T