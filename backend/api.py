"""
api.py — FastAPI REST endpoints for StreamScope: Netflix Content Intelligence
==============================================================================
This file exposes all data and analytics endpoints consumed by the frontend
dashboard and available for external BI tools.

Endpoint groups:
  /api/netflix/overview          — Executive KPIs
  /api/netflix/titles            — Paginated title listing
  /api/netflix/category-split    — Movies vs TV Shows counts
  /api/netflix/top-genres        — Top 10 genres by count
  /api/netflix/top-countries     — Top 10 countries by count
  /api/netflix/ratings           — Rating distribution
  /api/netflix/yearly-trends     — Titles added per year
  /api/netflix/monthly-trends    — Titles added per month
  /api/netflix/movie-duration    — Movie duration distribution
  /api/netflix/top-directors     — Top 10 directors by title count
  /api/netflix/genre-by-category — Genre breakdown by Movie/TV Show
  /api/netflix/key-insights      — AI-style business insights
  /api/netflix/search            — Keyword search across titles
  /api/netflix/export-csv        — CSV download for Power BI / Tableau
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import csv
from backend.db import get_conn
from decimal import Decimal

app = FastAPI(
    title="StreamScope — Netflix Content Intelligence API",
    description="Business Intelligence & Content Analytics platform for Netflix data.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
#  HELPER — convert Decimal to float
# ============================================================

def dec(val):
    """Safely convert Decimal or None to float."""
    if val is None:
        return 0
    return float(val) if isinstance(val, Decimal) else val


# ============================================================
#  OVERVIEW — Executive KPI Summary (6 cards)
# ============================================================

@app.get("/api/netflix/overview")
def get_overview():
    """
    Returns 6 KPI values:
      - total_titles, movies_count, tvshows_count
      - top_country, top_genre, most_common_rating
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Total titles
    cur.execute("SELECT COUNT(*) AS cnt FROM netflix_titles")
    total = cur.fetchone()["cnt"]

    # Movies vs TV Shows
    cur.execute("""
        SELECT category, COUNT(*) AS cnt
        FROM netflix_titles
        GROUP BY category
    """)
    cats = {r["category"]: r["cnt"] for r in cur.fetchall()}
    movies  = cats.get("Movie", 0)
    tvshows = cats.get("TV Show", 0)

    # Top country
    cur.execute("""
        SELECT country, COUNT(*) AS cnt
        FROM title_countries
        GROUP BY country
        ORDER BY cnt DESC LIMIT 1
    """)
    row = cur.fetchone()
    top_country = row["country"] if row else "—"

    # Top genre
    cur.execute("""
        SELECT genre, COUNT(*) AS cnt
        FROM title_genres
        GROUP BY genre
        ORDER BY cnt DESC LIMIT 1
    """)
    row = cur.fetchone()
    top_genre = row["genre"] if row else "—"

    # Most common rating
    cur.execute("""
        SELECT rating, COUNT(*) AS cnt
        FROM netflix_titles
        WHERE rating IS NOT NULL AND rating != 'Unknown'
        GROUP BY rating
        ORDER BY cnt DESC LIMIT 1
    """)
    row = cur.fetchone()
    top_rating = row["rating"] if row else "—"

    cur.close()
    conn.close()

    return {
        "total_titles":       total,
        "movies_count":       movies,
        "tvshows_count":      tvshows,
        "top_country":        top_country,
        "top_genre":          top_genre,
        "most_common_rating": top_rating,
    }


# ============================================================
#  TITLES — Paginated listing with optional filters
# ============================================================

@app.get("/api/netflix/titles")
def get_titles(
    category: str = Query(None),
    rating: str = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
):
    """Returns paginated Netflix titles with optional filters."""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    where  = []
    params = []
    if category:
        where.append("category = %s")
        params.append(category)
    if rating:
        where.append("rating = %s")
        params.append(rating)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    params += [limit, offset]

    cur.execute(f"""
        SELECT show_id, category, title, director, rating,
               release_year, duration, duration_minutes, seasons,
               SUBSTRING(description, 1, 200) AS description
        FROM netflix_titles
        {where_sql}
        ORDER BY release_year DESC, title ASC
        LIMIT %s OFFSET %s
    """, params)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  CATEGORY SPLIT — Movies vs TV Shows (donut chart)
# ============================================================

@app.get("/api/netflix/category-split")
def get_category_split():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT category, COUNT(*) AS count
        FROM netflix_titles
        GROUP BY category
        ORDER BY count DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  TOP GENRES — Top 10 genres by count
# ============================================================

@app.get("/api/netflix/top-genres")
def get_top_genres(limit: int = Query(10)):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT genre, COUNT(*) AS count
        FROM title_genres
        GROUP BY genre
        ORDER BY count DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  TOP COUNTRIES — Top 10 content-producing countries
# ============================================================

@app.get("/api/netflix/top-countries")
def get_top_countries(limit: int = Query(10)):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT country, COUNT(*) AS count
        FROM title_countries
        GROUP BY country
        ORDER BY count DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  RATINGS — Distribution of content ratings
# ============================================================

@app.get("/api/netflix/ratings")
def get_ratings():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT rating, COUNT(*) AS count
        FROM netflix_titles
        WHERE rating IS NOT NULL AND rating != 'Unknown'
        GROUP BY rating
        ORDER BY count DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  YEARLY TRENDS — Titles added per year
# ============================================================

@app.get("/api/netflix/yearly-trends")
def get_yearly_trends():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT release_year AS year, COUNT(*) AS count
        FROM netflix_titles
        WHERE release_year IS NOT NULL
        GROUP BY release_year
        ORDER BY release_year ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  YEARLY TRENDS BY CATEGORY — Stacked bar: Movies vs TV Shows per year
# ============================================================

@app.get("/api/netflix/yearly-by-category")
def get_yearly_by_category():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT release_year AS year, category, COUNT(*) AS count
        FROM netflix_titles
        WHERE release_year IS NOT NULL
        GROUP BY release_year, category
        ORDER BY release_year ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  MONTHLY TRENDS — Content additions by month
# ============================================================

@app.get("/api/netflix/monthly-trends")
def get_monthly_trends():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT release_month AS month, COUNT(*) AS count
        FROM netflix_titles
        WHERE release_month IS NOT NULL
        GROUP BY release_month
        ORDER BY release_month ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Map month numbers to names
    month_names = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    for r in rows:
        m = r["month"]
        r["month_name"] = month_names[m] if m and 1 <= m <= 12 else "Unknown"
    return rows


# ============================================================
#  MOVIE DURATION — Duration distribution for movies
# ============================================================

@app.get("/api/netflix/movie-duration")
def get_movie_duration():
    """Returns movie count grouped into duration buckets."""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            CASE
                WHEN duration_minutes < 60  THEN 'Under 60 min'
                WHEN duration_minutes < 90  THEN '60-89 min'
                WHEN duration_minutes < 120 THEN '90-119 min'
                WHEN duration_minutes < 150 THEN '120-149 min'
                ELSE '150+ min'
            END AS bucket,
            COUNT(*) AS count
        FROM netflix_titles
        WHERE category = 'Movie' AND duration_minutes IS NOT NULL
        GROUP BY bucket
        ORDER BY MIN(duration_minutes) ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  TOP DIRECTORS — Directors with most titles
# ============================================================

@app.get("/api/netflix/top-directors")
def get_top_directors(limit: int = Query(10)):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT director, COUNT(*) AS count
        FROM netflix_titles
        WHERE director IS NOT NULL AND director != 'Unknown'
        GROUP BY director
        ORDER BY count DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  GENRE BY CATEGORY — Genre breakdown per content type
# ============================================================

@app.get("/api/netflix/genre-by-category")
def get_genre_by_category():
    """Top genres split by Movie / TV Show for grouped bar chart."""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT tg.genre, nt.category, COUNT(*) AS count
        FROM title_genres tg
        JOIN netflix_titles nt ON tg.show_id = nt.show_id
        GROUP BY tg.genre, nt.category
        ORDER BY COUNT(*) DESC
        LIMIT 30
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ============================================================
#  KEY INSIGHTS — Data-driven business-style findings
# ============================================================

@app.get("/api/netflix/key-insights")
def get_key_insights():
    """
    Generates business insights from actual data.
    Each insight has: title, detail, metric, type (positive/neutral/negative).
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    insights = []

    # 1. Content split
    cur.execute("""
        SELECT category, COUNT(*) AS cnt FROM netflix_titles GROUP BY category
    """)
    cats = {r["category"]: r["cnt"] for r in cur.fetchall()}
    total = sum(cats.values())
    movie_pct = round(cats.get("Movie", 0) / total * 100, 1) if total else 0
    insights.append({
        "title": "Content Mix",
        "detail": f"Movies represent {movie_pct}% of the catalog ({cats.get('Movie', 0)} titles), significantly outnumbering TV Shows ({cats.get('TV Show', 0)}).",
        "metric": f"{movie_pct}% Movies",
        "type": "neutral",
    })

    # 2. Peak year
    cur.execute("""
        SELECT release_year AS year, COUNT(*) AS cnt
        FROM netflix_titles
        WHERE release_year IS NOT NULL
        GROUP BY release_year ORDER BY cnt DESC LIMIT 1
    """)
    peak = cur.fetchone()
    if peak:
        insights.append({
            "title": "Peak Content Year",
            "detail": f"Content additions peaked in {peak['year']} with {peak['cnt']} titles added — the highest single-year intake in Netflix history.",
            "metric": f"{peak['year']}: {peak['cnt']} titles",
            "type": "positive",
        })

    # 3. Top producing countries
    cur.execute("""
        SELECT country, COUNT(*) AS cnt
        FROM title_countries
        GROUP BY country ORDER BY cnt DESC LIMIT 3
    """)
    top_countries = cur.fetchall()
    if top_countries:
        names = ", ".join([r["country"] for r in top_countries])
        insights.append({
            "title": "Global Content Origins",
            "detail": f"The top content-producing countries are {names}. These markets dominate Netflix's content pipeline.",
            "metric": f"#{1}: {top_countries[0]['country']} ({top_countries[0]['cnt']} titles)",
            "type": "positive",
        })

    # 4. Top genre
    cur.execute("""
        SELECT genre, COUNT(*) AS cnt
        FROM title_genres
        GROUP BY genre ORDER BY cnt DESC LIMIT 1
    """)
    g = cur.fetchone()
    if g:
        insights.append({
            "title": "Dominant Genre",
            "detail": f'"{g["genre"]}" is the most prevalent genre with {g["cnt"]} titles. This reflects Netflix\'s heavy investment in cross-cultural content.',
            "metric": f'{g["genre"]}: {g["cnt"]}',
            "type": "neutral",
        })

    # 5. Most common rating
    cur.execute("""
        SELECT rating, COUNT(*) AS cnt
        FROM netflix_titles
        WHERE rating IS NOT NULL AND rating != 'Unknown'
        GROUP BY rating ORDER BY cnt DESC LIMIT 1
    """)
    rt = cur.fetchone()
    if rt:
        insights.append({
            "title": "Audience Targeting",
            "detail": f'{rt["rating"]} is the most common maturity rating ({rt["cnt"]} titles), indicating Netflix\'s primary audience skews toward mature content.',
            "metric": f'{rt["rating"]}: {rt["cnt"]} titles',
            "type": "neutral",
        })

    # 6. Average movie duration
    cur.execute("""
        SELECT ROUND(AVG(duration_minutes)) AS avg_dur
        FROM netflix_titles
        WHERE category = 'Movie' AND duration_minutes IS NOT NULL
    """)
    dur = cur.fetchone()
    if dur and dur["avg_dur"]:
        insights.append({
            "title": "Average Movie Length",
            "detail": f"The average movie on Netflix runs {int(dur['avg_dur'])} minutes. Most content falls in the 90-120 minute sweet spot for streaming.",
            "metric": f"{int(dur['avg_dur'])} minutes",
            "type": "neutral",
        })

    # 7. Recent vs older content
    cur.execute("""
        SELECT
            SUM(CASE WHEN release_year >= 2018 THEN 1 ELSE 0 END) AS recent,
            SUM(CASE WHEN release_year < 2018 THEN 1 ELSE 0 END) AS older
        FROM netflix_titles
        WHERE release_year IS NOT NULL
    """)
    age = cur.fetchone()
    if age and age["recent"]:
        recent_pct = round(age["recent"] / (age["recent"] + age["older"]) * 100, 1)
        insights.append({
            "title": "Content Recency",
            "detail": f"{recent_pct}% of all content was added from 2018 onwards, showing Netflix's aggressive recent expansion strategy.",
            "metric": f"{recent_pct}% post-2018",
            "type": "positive",
        })

    cur.close()
    conn.close()
    return insights


# ============================================================
#  SEARCH — Keyword search across multiple columns
# ============================================================

@app.get("/api/netflix/search")
def search_titles(
    q: str = Query(""),
    limit: int = Query(20),
    offset: int = Query(0),
):
    """
    Full-text keyword search across Netflix titles.

    Splits the query into individual words and checks if ANY word
    appears in any of the searchable columns (title, category,
    director, cast, country, rating, type, description).

    Uses SQL LIKE with parameterized queries (safe from injection).
    """
    # If the query is empty or whitespace, return nothing
    q = q.strip()
    if not q:
        return {"results": [], "total_results": 0, "limit": limit, "offset": offset}

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # The columns we search against
    searchable_cols = [
        "title", "category", "director", "cast_members",
        "country", "rating", "type", "description",
    ]

    # Split multi-word queries into individual keywords.
    # A row matches if ANY keyword appears in ANY searchable column.
    words = q.split()

    # Build WHERE: (col1 LIKE %word1% OR col2 LIKE %word1% ...) AND (...word2...)
    # This means ALL words must appear somewhere in the row (AND logic),
    # but each word can be in any column (OR logic within a word).
    word_clauses = []
    params = []
    for word in words:
        col_clauses = [f"{col} LIKE %s" for col in searchable_cols]
        word_clauses.append("(" + " OR ".join(col_clauses) + ")")
        # Each column gets the same %word% parameter
        for _ in searchable_cols:
            params.append(f"%{word}%")

    where_sql = " AND ".join(word_clauses)

    # Count total matching rows (for pagination metadata)
    cur.execute(
        f"SELECT COUNT(*) AS total FROM netflix_titles WHERE {where_sql}",
        params,
    )
    total = cur.fetchone()["total"]

    # Fetch the paginated result set
    cur.execute(f"""
        SELECT show_id, title, category, director, cast_members,
               country, release_year, rating, duration, type,
               SUBSTRING(description, 1, 250) AS description
        FROM netflix_titles
        WHERE {where_sql}
        ORDER BY release_year DESC, title ASC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "results": rows,
        "total_results": total,
        "limit": limit,
        "offset": offset,
    }


# ============================================================
#  EXPORT — CSV download for Power BI / Tableau
# ============================================================

@app.get("/api/netflix/export-csv")
def export_csv():
    """
    Streams the bi_netflix_view as a CSV download.
    Suitable for direct import into Power BI or Tableau.
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM bi_netflix_view")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=netflix_bi_export.csv"},
    )
