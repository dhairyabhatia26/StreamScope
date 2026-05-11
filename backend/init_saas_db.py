"""
init_saas_db.py — Creates the SaaS analytics schema and BI views
=================================================================
Run this BEFORE loading data. It is also called automatically
by load_saas_db.py so you rarely need to run it directly.

Tables created:
  - products          (product catalogue)
  - reviews           (raw review data)
  - review_analysis   (AI-generated analysis per review)

Views created:
  - bi_analytics_view (flattened join for Power BI / Tableau)
"""

from backend.db import get_conn


def init_db():
    """Creates all SaaS tables and the BI analytics view."""
    print("Initializing SaaS Database Tables...")
    conn = get_conn()
    cur = conn.cursor()

    # ── Products table ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id       INT AUTO_INCREMENT PRIMARY KEY,
            name     VARCHAR(255) UNIQUE NOT NULL,
            category VARCHAR(100)
        )
    """)
    print("  ✓ products table ensured")

    # ── Reviews table ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            product_id    INT,
            review_text   TEXT,
            rating        INT,
            reviewer_role VARCHAR(100),
            review_date   DATE,
            pros          TEXT,
            cons          TEXT,
            source_url    VARCHAR(255),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)
    print("  ✓ reviews table ensured")

    # ── Review Analysis table (AI output) ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_analysis (
            id                      INT AUTO_INCREMENT PRIMARY KEY,
            review_id               INT,
            sentiment               VARCHAR(50),
            pain_points             JSON,
            feature_requests        JSON,
            topic_classification    VARCHAR(100),
            business_priority_score FLOAT,
            short_business_summary  TEXT,
            FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
        )
    """)
    print("  ✓ review_analysis table ensured")

    # ── BI Analytics View (flattened for Power BI / Tableau) ──
    cur.execute("""
        CREATE OR REPLACE VIEW bi_analytics_view AS
        SELECT
            p.name                      AS product_name,
            p.category                  AS product_category,
            r.rating,
            r.reviewer_role,
            r.review_date,
            r.review_text,
            r.pros,
            r.cons,
            a.sentiment,
            a.topic_classification,
            a.business_priority_score,
            a.pain_points,
            a.feature_requests,
            a.short_business_summary
        FROM reviews r
        JOIN products p              ON r.product_id = p.id
        LEFT JOIN review_analysis a  ON r.id = a.review_id
    """)
    print("  ✓ bi_analytics_view ensured")

    cur.close()
    conn.close()
    print("Database initialization complete.\n")


if __name__ == "__main__":
    init_db()
