import pandas as pd


def load_default_data(file_path="combined_transactions.csv"):
    """
    Load the combined transaction data generated from Expenses_clean.csv and Income_clean.csv.
    """
    return pd.read_csv(file_path)


def standardize_columns(df):
    """
    Standardize column names and basic data types.

    Expected core fields:
    date, type, category, amount

    Optional fields:
    account, currency, description
    """
    df = df.copy()

    df.columns = [c.strip().lower() for c in df.columns]

    rename_map = {
        "date_time": "date",
        "datetime": "date",
        "transaction_date": "date",
        "transaction type": "type",
        "transaction_type": "type",
        "transactiontype": "type",
        "amount($)": "amount",
        "expense_category": "category",
        "income_category": "category",
        "merchant": "description",
        "details": "description",
        "tags": "description"
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    required_cols = ["date", "type", "category", "amount"]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required column(s): {missing_cols}")

    if "description" not in df.columns:
        df["description"] = ""

    if "account" not in df.columns:
        df["account"] = ""

    if "currency" not in df.columns:
        df["currency"] = ""

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    df = df.dropna(subset=["date", "amount"])

    df["type"] = df["type"].astype(str).str.strip().str.title()
    df["category"] = df["category"].astype(str).str.strip().str.title()
    df["description"] = df["description"].astype(str)
    df["account"] = df["account"].astype(str)
    df["currency"] = df["currency"].astype(str)

    df["month"] = df["date"].dt.to_period("M").astype(str)

    return df


def get_expenses(df):
    return df[df["type"].str.lower() == "expense"].copy()


def get_income(df):
    return df[df["type"].str.lower() == "income"].copy()