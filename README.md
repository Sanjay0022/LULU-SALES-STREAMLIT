# LuLu Sales Stakeholder Dashboard

A quick Streamlit dashboard for exploring a synthetic LuLu Hypermarket
sales dataset (UAE stores, Jan 2024 – Dec 2025).

## Files

- `app.py` — the Streamlit dashboard
- `data/lulu_sales.csv` — synthetic transaction-level sales data (~46k rows)
- `generate_data.py` — script used to generate the dataset (re-run to regenerate/refresh)
- `requirements.txt` — Python dependencies

## Dataset columns

| Column | Description |
|---|---|
| order_id | Unique transaction id |
| date | Transaction date |
| store | Store name |
| city | City (Dubai, Abu Dhabi, Sharjah, Al Ain, Ajman, Ras Al Khaimah) |
| category | Product category |
| product | Product name |
| units_sold | Units sold in the transaction |
| unit_price_aed | Unit price (AED) |
| gross_revenue_aed | units_sold × unit_price_aed |
| discount_pct | Discount percentage applied |
| discount_amount_aed | Discount amount (AED) |
| net_revenue_aed | gross_revenue_aed − discount_amount_aed |
| payment_method | Card / Cash / LuLu Gift Card / Digital Wallet |
| customer_segment | Walk-in / LuLu Loyalty Member / Corporate-Bulk / Online Pickup |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## What's in the dashboard

- KPI cards: net revenue, orders, units sold, average order value, discounts,
  with a period-over-period % change vs. the prior equivalent date range.
- Sidebar filters: date range, city, store, category, customer segment.
- Revenue trend chart (daily/weekly/monthly toggle).
- Revenue by category (donut chart).
- Store performance comparison (horizontal bar, colored by city).
- Top 10 products by revenue.
- Payment method mix, customer segment mix, weekday sales pattern.
- Expandable raw data table with CSV download of the filtered view.

## Notes / next steps

- The dataset is randomly generated for demo purposes — swap `data/lulu_sales.csv`
  with real exports (same column names) to go live.
- To deploy for stakeholders: push this folder to a GitHub repo and deploy for
  free on [Streamlit Community Cloud](https://streamlit.io/cloud), or run it
  on any internal server with `streamlit run app.py --server.port 8501`.
