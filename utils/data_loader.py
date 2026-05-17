import os
import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "supermarket_sales.csv")

def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    df.columns = [c.strip() for c in df.columns]

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_cols = ["Unit price", "Quantity", "Tax 5%", "Total", "cogs", "gross income", "Rating"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def get_filter_options(df: pd.DataFrame) -> dict:
    return {
        "Branch":        ["All"] + sorted(df["Branch"].dropna().unique().tolist()),
        "City":          ["All"] + sorted(df["City"].dropna().unique().tolist()),
        "Customer type": ["All"] + sorted(df["Customer type"].dropna().unique().tolist()),
        "Gender":        ["All"] + sorted(df["Gender"].dropna().unique().tolist()),
        "Product line":  ["All"] + sorted(df["Product line"].dropna().unique().tolist()),
        "Payment":       ["All"] + sorted(df["Payment"].dropna().unique().tolist()),
    }

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    result = df.copy()
    for col, val in filters.items():
        if val and val != "All":
            result = result[result[col] == val]
    return result
