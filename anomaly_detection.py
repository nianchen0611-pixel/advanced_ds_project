from preprocessing import get_expenses


def get_default_anomaly_threshold(df):
    """
    Global anomaly threshold:
    mean expense amount + 1.5 * standard deviation.
    """
    expenses = get_expenses(df)

    if expenses.empty:
        return 0.0

    return float(expenses["amount"].mean() + 1.5 * expenses["amount"].std())


def detect_anomalies(df, threshold):
    """
    Global anomaly detection.

    A transaction is flagged as unusual if its amount is greater than
    or equal to the global threshold.
    """
    expenses = get_expenses(df)

    anomalies = expenses[expenses["amount"] >= threshold].copy()
    anomalies = anomalies.sort_values("amount", ascending=False)

    return anomalies


def detect_category_relative_anomalies(df, multiplier=1.5):
    """
    Category-relative anomaly detection.

    A transaction is flagged as unusual if it is much larger than the
    typical transaction amount within the same category.

    Rule:
    amount > category_mean + multiplier * category_std

    This helps detect transactions that may not be globally large,
    but are unusual compared with normal spending in that category.
    """
    expenses = get_expenses(df)

    if expenses.empty:
        return expenses.copy()

    category_stats = (
        expenses.groupby("category")["amount"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={
            "mean": "category_mean",
            "std": "category_std",
            "count": "category_count"
        })
    )

    category_stats["category_std"] = category_stats["category_std"].fillna(0)

    merged = expenses.merge(category_stats, on="category", how="left")

    merged["category_threshold"] = (
        merged["category_mean"] + multiplier * merged["category_std"]
    )

    merged["above_category_average"] = (
        merged["amount"] - merged["category_mean"]
    )

    anomalies = merged[
        (merged["category_count"] >= 2)
        & (merged["category_std"] > 0)
        & (merged["amount"] > merged["category_threshold"])
    ].copy()

    anomalies = anomalies.sort_values("above_category_average", ascending=False)

    return anomalies