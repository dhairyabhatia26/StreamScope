"""
init_netflix_db.py — Creates the Netflix analytics schema and BI views
=======================================================================
Run this BEFORE loading data. It is also called automatically
by load_netflix_db.py so you rarely need to run it directly.

Tables created:
  - netflix_titles    (main content table)
  - title_genres      (many-to-many genre mapping)
  - title_countries   (many-to-many country mapping)

Views created:
  - bi_netflix_view   (flattened join for Power BI / Tableau)
"""

from backend.db import get_conn


def init_db():
    """Creates all Netflix tables and the BI analytics view."""
    print("Initializing Netflix Database Tables...")
    conn = get_conn()
    cur = conn.cursor()

    # ── Main titles table ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS netflix_titles (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            show_id          VARCHAR(20) UNIQUE NOT NULL,
            category         VARCHAR(20),
            title            VARCHAR(500),
            director         VARCHAR(500),
            cast_members     TEXT,
            country          VARCHAR(500),
            release_date     DATE,
            release_year     INT,
            release_month    INT,
            rating           VARCHAR(20),
            duration         VARCHAR(50),
            duration_minutes INT,
            seasons          INT,
            type             TEXT,
            description      TEXT
        )
    """)
    print("  ✓ netflix_titles table ensured")

    # ── Genre mapping (normalized from comma-separated Type column) ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS title_genres (
            id       INT AUTO_INCREMENT PRIMARY KEY,
            show_id  VARCHAR(20) NOT NULL,
            genre    VARCHAR(200) NOT NULL,
            INDEX idx_show_id (show_id),
            INDEX idx_genre (genre)
        )
    """)
    print("  ✓ title_genres table ensured")

    # ── Country mapping (normalized from comma-separated Country column) ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS title_countries (
            id       INT AUTO_INCREMENT PRIMARY KEY,
            show_id  VARCHAR(20) NOT NULL,
            country  VARCHAR(200) NOT NULL,
            INDEX idx_show_id (show_id),
            INDEX idx_country (country)
        )
    """)
    print("  ✓ title_countries table ensured")

    # ── BI View (flattened for Power BI / Tableau) ──
    cur.execute("""
        CREATE OR REPLACE VIEW bi_netflix_view AS
        SELECT
            nt.title,
            nt.category,
            tc.country,
            tg.genre,
            nt.rating,
            nt.release_year,
            nt.release_month,
            nt.duration_minutes,
            nt.seasons
        FROM netflix_titles nt
        LEFT JOIN title_genres    tg ON nt.show_id = tg.show_id
        LEFT JOIN title_countries tc ON nt.show_id = tc.show_id
    """)
    print("  ✓ bi_netflix_view ensured")

    cur.close()
    conn.close()
    print("Netflix database initialization complete.\n")


if __name__ == "__main__":
    init_db()
