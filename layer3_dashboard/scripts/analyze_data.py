"""Temporary script to analyze target customer pool."""
import pandas as pd

orders = pd.read_parquet("EDA/outputs_finals/orders.parquet")
orders["order_date"] = pd.to_datetime(orders["order_date"])
print("Order date range:", orders["order_date"].min(), "to", orders["order_date"].max())


def norm_id(x):
    if pd.isna(x):
        return None
    s = str(x).strip().lstrip("'")
    if "E" in s.upper():
        try:
            s = str(int(float(s)))
        except ValueError:
            pass
    return s


orders["cid"] = orders["customer_id"].apply(norm_id)
oc = orders.groupby("cid").size().reset_index(name="order_count")
print("Customers with 1 order:", (oc["order_count"] == 1).sum())

ref = orders["order_date"].max()
cutoff = ref - pd.Timedelta(days=30)
recent = orders[orders["order_date"] >= cutoff]
print("Recent orders (30d):", len(recent))

first_orders = orders.sort_values("order_date").groupby("cid").first().reset_index()
first_orders = first_orders.merge(oc, on="cid")
target = first_orders[(first_orders["order_count"] == 1) & (first_orders["order_date"] >= cutoff)]
print("Target customers (1 order, last 30d):", len(target))
print(target["product_category"].value_counts().head(10))
print(target[["cid", "order_date", "product_category", "Line: Title"]].head(5))
