import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from supabase import create_client

import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

URL = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"

def scrape_laptops():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select(".thumbnail")
    rows = []

    for item in items:
        title_el = item.select_one(".title")
        price_el = item.select_one(".price")
        desc_el = item.select_one(".description")
        rating_el = item.select(".ratings .glyphicon-star")

        title = title_el.get("title") if title_el else None
        price_raw = price_el.get_text(strip=True).replace("$", "") if price_el else None
        desc = desc_el.get_text(strip=True) if desc_el else None
        rating = len(rating_el)

        price = float(price_raw) if price_raw else None

        rows.append({
            "title": title,
            "price": price,
            "rating": rating,
            "description": desc,
            "scraped_at": datetime.utcnow().isoformat()
        })

    return pd.DataFrame(rows)

def upload_to_supabase(df):
    records = df.to_dict(orient="records")
    supabase.table("laptops").insert(records).execute()
    print(f"Inserted {len(records)} rows.")

if __name__ == "__main__":
    df = scrape_laptops()
    upload_to_supabase(df)
