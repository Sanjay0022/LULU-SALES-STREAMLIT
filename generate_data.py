"""
Generates a synthetic LuLu Hypermarket-style sales dataset for a
Streamlit stakeholder sales dashboard.

Output: data/lulu_sales.csv
"""

import numpy as np
import pandas as pd

np.random.seed(42)

# ---------------------------------------------------------------
# Reference dimensions
# ---------------------------------------------------------------
stores = [
    ("LuLu Hypermarket - Al Barsha", "Dubai"),
    ("LuLu Hypermarket - Deira City Centre", "Dubai"),
    ("LuLu Hypermarket - Silicon Oasis", "Dubai"),
    ("LuLu Hypermarket - Khalidiyah", "Abu Dhabi"),
    ("LuLu Hypermarket - Mushrif", "Abu Dhabi"),
    ("LuLu Hypermarket - Al Wahda", "Abu Dhabi"),
    ("LuLu Hypermarket - Sahara Centre", "Sharjah"),
    ("LuLu Hypermarket - Al Qasimia", "Sharjah"),
    ("LuLu Hypermarket - Al Ain Mall", "Al Ain"),
    ("LuLu Hypermarket - Ajman City Centre", "Ajman"),
    ("LuLu Hypermarket - RAK Mall", "Ras Al Khaimah"),
]

categories = {
    "Fresh Produce": ["Bananas", "Tomatoes", "Apples", "Onions", "Potatoes", "Cucumbers"],
    "Bakery": ["White Bread", "Brown Bread", "Croissant", "Arabic Bread", "Muffins"],
    "Beverages": ["Mineral Water", "Soft Drinks", "Fresh Juice", "Tea", "Coffee"],
    "Groceries": ["Basmati Rice", "Cooking Oil", "Sugar", "Flour", "Pasta", "Lentils"],
    "Dairy": ["Full Cream Milk", "Yogurt", "Cheese Slices", "Butter", "Labneh"],
    "Electronics": ["LED TV 43\"", "Bluetooth Speaker", "Microwave Oven", "Blender", "Air Fryer"],
    "Fashion": ["Men's T-Shirt", "Women's Abaya", "Kids Sneakers", "Formal Shirt", "Denim Jeans"],
    "Home & Living": ["Cookware Set", "Bed Sheets", "Storage Boxes", "Curtains", "Cushions"],
    "Beauty & Personal Care": ["Shampoo", "Face Cream", "Body Lotion", "Toothpaste", "Perfume"],
    "Household Cleaning": ["Dishwash Liquid", "Floor Cleaner", "Laundry Detergent", "Tissue Rolls"],
}

payment_methods = ["Card", "Cash", "LuLu Gift Card", "Digital Wallet"]
payment_weights = [0.48, 0.27, 0.10, 0.15]

customer_segments = ["Walk-in", "LuLu Loyalty Member", "Corporate/Bulk", "Online Pickup"]
segment_weights = [0.40, 0.38, 0.07, 0.15]

# Approx category price ranges (AED) -> (unit_cost_low, unit_cost_high, unit_price_low, unit_price_high)
price_ranges = {
    "Fresh Produce": (2, 12),
    "Bakery": (3, 15),
    "Beverages": (2, 25),
    "Groceries": (5, 60),
    "Dairy": (4, 30),
    "Electronics": (80, 1800),
    "Fashion": (25, 250),
    "Home & Living": (30, 400),
    "Beauty & Personal Care": (10, 120),
    "Household Cleaning": (8, 45),
}

# Seasonal boost months (Ramadan/EOSS/Back-to-school/holidays) - illustrative
seasonal_boost = {1: 1.05, 2: 1.0, 3: 1.15, 4: 1.25, 5: 1.05, 6: 0.95,
                  7: 0.90, 8: 1.0, 9: 1.10, 10: 1.05, 11: 1.15, 12: 1.30}

# ---------------------------------------------------------------
# Generate transactions
# ---------------------------------------------------------------
date_range = pd.date_range("2024-01-01", "2025-12-31", freq="D")
rows = []
order_id = 100000

for date in date_range:
    month_factor = seasonal_boost[date.month]
    weekend_factor = 1.25 if date.dayofweek in (4, 5) else 1.0  # Fri/Sat weekend in UAE
    n_orders = int(np.random.poisson(55) * month_factor * weekend_factor)

    for _ in range(n_orders):
        store_name, city = stores[np.random.randint(len(stores))]
        category = np.random.choice(list(categories.keys()))
        product = np.random.choice(categories[category])
        low, high = price_ranges[category]
        unit_price = round(np.random.uniform(low, high), 2)
        units = np.random.choice([1, 1, 1, 2, 2, 3, 4, 5], p=[0.30, 0.20, 0.15, 0.15, 0.10, 0.05, 0.03, 0.02])
        discount_pct = np.random.choice([0, 0, 0, 5, 10, 15, 20], p=[0.5, 0.15, 0.05, 0.1, 0.1, 0.06, 0.04])
        gross_revenue = round(unit_price * units, 2)
        discount_amount = round(gross_revenue * discount_pct / 100, 2)
        net_revenue = round(gross_revenue - discount_amount, 2)
        payment = np.random.choice(payment_methods, p=payment_weights)
        segment = np.random.choice(customer_segments, p=segment_weights)

        order_id += 1
        rows.append({
            "order_id": order_id,
            "date": date.strftime("%Y-%m-%d"),
            "store": store_name,
            "city": city,
            "category": category,
            "product": product,
            "units_sold": units,
            "unit_price_aed": unit_price,
            "gross_revenue_aed": gross_revenue,
            "discount_pct": discount_pct,
            "discount_amount_aed": discount_amount,
            "net_revenue_aed": net_revenue,
            "payment_method": payment,
            "customer_segment": segment,
        })

df = pd.DataFrame(rows)
df.sort_values("date", inplace=True)
df.reset_index(drop=True, inplace=True)

print(f"Generated {len(df):,} transaction rows")
print(df.head())

import os
os.makedirs("data", exist_ok=True)
df.to_csv("data/lulu_sales.csv", index=False)
print("Saved to data/lulu_sales.csv")
