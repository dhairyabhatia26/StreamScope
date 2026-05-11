"""
load_saas_db.py — Populates the MySQL database with synthetic SaaS review data
================================================================================
Usage:
    python -m backend.load_saas_db

This script:
  1. Ensures the schema exists (calls init_saas_db.init_db)
  2. Clears old data (safe to re-run)
  3. Generates 200 synthetic reviews with AI analysis
  4. Inserts everything into MySQL
"""

import sys
import os

# Ensure project root is on the path for direct execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_conn
from backend.init_saas_db import init_db
from scraper.simulate_saas_reviews import generate_dataset


def load_saas_data(num_reviews=300):
    """Generates synthetic data and loads it into the database."""

    # Step 1 — Ensure schema exists
    init_db()

    # Step 2 — Generate data
    print(f"Generating {num_reviews} simulated reviews...")
    products, reviews, analyses = generate_dataset(num_reviews)
    print(f"  → {len(products)} products, {len(reviews)} reviews, {len(analyses)} analyses\n")

    # Step 3 — Connect and load
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Clear old data (order matters due to foreign keys)
        print("Clearing previous data...")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        cur.execute("TRUNCATE TABLE review_analysis")
        cur.execute("TRUNCATE TABLE reviews")
        cur.execute("TRUNCATE TABLE products")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Insert products
        print("Loading products...")
        for product in products:
            cur.execute(
                "INSERT INTO products (name, category) VALUES (%s, %s)",
                (product["name"], product["category"]),
            )

        # Build a name → id lookup
        cur.execute("SELECT id, name FROM products")
        product_map = {name: pid for pid, name in cur.fetchall()}

        # Insert reviews and their analyses
        print("Loading reviews and analysis...")
        for idx, review in enumerate(reviews):
            # Look up the actual product_id from the DB
            product_name = products[review["product_id"] - 1]["name"]
            db_product_id = product_map[product_name]

            cur.execute(
                """INSERT INTO reviews
                   (product_id, review_text, rating, reviewer_role, review_date, pros, cons, source_url)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    db_product_id,
                    review["review_text"],
                    review["rating"],
                    review["reviewer_role"],
                    review["review_date"],
                    review["pros"],
                    review["cons"],
                    review["source_url"],
                ),
            )
            review_id = cur.lastrowid

            analysis = analyses[idx]
            cur.execute(
                """INSERT INTO review_analysis
                   (review_id, sentiment, pain_points, feature_requests,
                    topic_classification, business_priority_score, short_business_summary)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    review_id,
                    analysis["sentiment"],
                    analysis["pain_points"],
                    analysis["feature_requests"],
                    analysis["topic_classification"],
                    analysis["business_priority_score"],
                    analysis["short_business_summary"],
                ),
            )

        conn.commit()
        print(f"\n✅ Successfully loaded {len(reviews)} reviews into the database.")
        print("   Run: python -m uvicorn backend.api:app --reload")
        print("   Then open frontend/index.html\n")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error loading data: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_saas_data()
