"""
LuLu Hypermarket — Sales Stakeholder Dashboard
Run with: streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).parent
_candidate_paths = [
    APP_DIR / "data" / "lulu_sales.csv",  # expected location
    APP_DIR / "lulu_sales.csv",           # fallback: file sitting in repo root
]
DATA_PATH = next((p for p in _candidate_paths if p.exists()), _candidate_paths[0])

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="LuLu Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["weekday"] = df["date"].dt.day_name()
    df["year"] = df["date"].dt.year
    return df


if not DATA_PATH.exists():
    checked = "\n".join(f"- `{p}`" for p in _candidate_paths)
    st.error(
        f"Data file not found. Checked:\n{checked}\n\n"
        "This usually means `lulu_sales.csv` wasn't pushed to your GitHub "
        "repo (check it isn't excluded by .gitignore and that it was "
        "actually committed).\n\n"
        f"Files found next to app.py: {[p.name for p in APP_DIR.iterdir()]}"
    )
    st.stop()

df = load_data(DATA_PATH)

# ------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------
st.sidebar.title("🛒 LuLu Sales Dashboard")
st.sidebar.caption("Filter the data to explore performance across stores, "
                    "cities, categories and time.")

min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

cities = sorted(df["city"].unique())
selected_cities = st.sidebar.multiselect("City", cities, default=cities)

stores_available = sorted(df[df["city"].isin(selected_cities)]["store"].unique())
selected_stores = st.sidebar.multiselect("Store", stores_available, default=stores_available)

categories = sorted(df["category"].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

segments = sorted(df["customer_segment"].unique())
selected_segments = st.sidebar.multiselect("Customer segment", segments, default=segments)

# Apply filters
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date, end_date = min_date, max_date

mask = (
    (df["date"] >= start_date)
    & (df["date"] <= end_date)
    & (df["city"].isin(selected_cities))
    & (df["store"].isin(selected_stores))
    & (df["category"].isin(selected_categories))
    & (df["customer_segment"].isin(selected_segments))
)
fdf = df.loc[mask].copy()

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(fdf):,}** of {len(df):,} transactions")

if fdf.empty:
    st.warning("No data matches the current filters. Please adjust your selection.")
    st.stop()

# ------------------------------------------------------------------
# Header + KPIs
# ------------------------------------------------------------------
st.title("Sales Performance Dashboard")
st.caption(
    f"{start_date.date()} → {end_date.date()}  |  "
    f"{len(selected_cities)} cities · {len(selected_stores)} stores · "
    f"{len(selected_categories)} categories"
)

total_revenue = fdf["net_revenue_aed"].sum()
total_orders = fdf["order_id"].nunique()
total_units = fdf["units_sold"].sum()
aov = total_revenue / total_orders if total_orders else 0
total_discount = fdf["discount_amount_aed"].sum()

# Period-over-period comparison (previous period of equal length)
period_len = (end_date - start_date).days + 1
prev_start = start_date - pd.Timedelta(days=period_len)
prev_end = start_date - pd.Timedelta(days=1)
prev_mask = (
    (df["date"] >= prev_start)
    & (df["date"] <= prev_end)
    & (df["city"].isin(selected_cities))
    & (df["store"].isin(selected_stores))
    & (df["category"].isin(selected_categories))
    & (df["customer_segment"].isin(selected_segments))
)
prev_revenue = df.loc[prev_mask, "net_revenue_aed"].sum()
revenue_delta = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Net Revenue (AED)", f"{total_revenue:,.0f}", f"{revenue_delta:+.1f}% vs prior period")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Units Sold", f"{total_units:,}")
col4.metric("Avg. Order Value (AED)", f"{aov:,.2f}")
col5.metric("Total Discounts (AED)", f"{total_discount:,.0f}")

st.markdown("---")

# ------------------------------------------------------------------
# Row 1: Revenue trend + Category split
# ------------------------------------------------------------------
r1c1, r1c2 = st.columns((2, 1))

with r1c1:
    st.subheader("Revenue Trend")
    granularity = st.radio("Granularity", ["Daily", "Weekly", "Monthly"], horizontal=True, index=2)
    ts = fdf.set_index("date")["net_revenue_aed"]
    if granularity == "Daily":
        trend = ts.resample("D").sum()
    elif granularity == "Weekly":
        trend = ts.resample("W").sum()
    else:
        trend = ts.resample("MS").sum()
    fig_trend = px.area(
        trend.reset_index(), x="date", y="net_revenue_aed",
        labels={"date": "Date", "net_revenue_aed": "Net Revenue (AED)"},
    )
    fig_trend.update_traces(line_color="#4CAF50", fillcolor="rgba(76,175,80,0.2)")
    fig_trend.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=380)
    st.plotly_chart(fig_trend, use_container_width=True)

with r1c2:
    st.subheader("Revenue by Category")
    cat_rev = fdf.groupby("category")["net_revenue_aed"].sum().sort_values(ascending=False).reset_index()
    fig_cat = px.pie(cat_rev, names="category", values="net_revenue_aed", hole=0.45)
    fig_cat.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=380, showlegend=True)
    st.plotly_chart(fig_cat, use_container_width=True)

# ------------------------------------------------------------------
# Row 2: Store performance + Top products
# ------------------------------------------------------------------
r2c1, r2c2 = st.columns(2)

with r2c1:
    st.subheader("Store Performance")
    store_rev = (
        fdf.groupby(["store", "city"])["net_revenue_aed"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig_store = px.bar(
        store_rev, x="net_revenue_aed", y="store", color="city", orientation="h",
        labels={"net_revenue_aed": "Net Revenue (AED)", "store": ""},
    )
    fig_store.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420)
    st.plotly_chart(fig_store, use_container_width=True)

with r2c2:
    st.subheader("Top 10 Products")
    top_products = (
        fdf.groupby("product")["net_revenue_aed"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values(ascending=True)
        .reset_index()
    )
    fig_top = px.bar(
        top_products, x="net_revenue_aed", y="product", orientation="h",
        labels={"net_revenue_aed": "Net Revenue (AED)", "product": ""},
        color_discrete_sequence=["#2E7D32"],
    )
    fig_top.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420)
    st.plotly_chart(fig_top, use_container_width=True)

# ------------------------------------------------------------------
# Row 3: Payment methods, Customer segments, Weekday pattern
# ------------------------------------------------------------------
r3c1, r3c2, r3c3 = st.columns(3)

with r3c1:
    st.subheader("Payment Methods")
    pay = fdf.groupby("payment_method")["net_revenue_aed"].sum().reset_index()
    fig_pay = px.pie(pay, names="payment_method", values="net_revenue_aed", hole=0.45)
    fig_pay.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320)
    st.plotly_chart(fig_pay, use_container_width=True)

with r3c2:
    st.subheader("Customer Segments")
    seg = fdf.groupby("customer_segment")["net_revenue_aed"].sum().reset_index()
    fig_seg = px.bar(seg, x="customer_segment", y="net_revenue_aed",
                      labels={"net_revenue_aed": "Net Revenue (AED)", "customer_segment": ""},
                      color_discrete_sequence=["#1565C0"])
    fig_seg.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320)
    st.plotly_chart(fig_seg, use_container_width=True)

with r3c3:
    st.subheader("Sales by Weekday")
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wd = fdf.groupby("weekday")["net_revenue_aed"].sum().reindex(weekday_order).reset_index()
    fig_wd = px.bar(wd, x="weekday", y="net_revenue_aed",
                     labels={"net_revenue_aed": "Net Revenue (AED)", "weekday": ""},
                     color_discrete_sequence=["#EF6C00"])
    fig_wd.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320)
    st.plotly_chart(fig_wd, use_container_width=True)

# ------------------------------------------------------------------
# Data table + download
# ------------------------------------------------------------------
st.markdown("---")
with st.expander("🔍 View filtered transaction data"):
    st.dataframe(fdf.drop(columns=["month", "weekday", "year"]), use_container_width=True)
    st.download_button(
        "Download filtered data as CSV",
        data=fdf.drop(columns=["month", "weekday", "year"]).to_csv(index=False).encode("utf-8"),
        file_name="lulu_sales_filtered.csv",
        mime="text/csv",
    )

st.caption("Data is synthetic and generated for demonstration purposes only.")
