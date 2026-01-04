from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.db import get_conn

app = FastAPI(title="WebScrape Dashboard API (MySQL)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/quotes")
def get_quotes(q: str | None = Query(default=None), limit: int = 50):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    if q:
        like = f"%{q}%"
        cur.execute("""
            SELECT id, text, author, tags, source_page, scraped_at
            FROM quotes
            WHERE text LIKE %s OR author LIKE %s
            ORDER BY scraped_at DESC
            LIMIT %s
        """, (like, like, limit))
    else:
        cur.execute("""
            SELECT id, text, author, tags, source_page, scraped_at
            FROM quotes
            ORDER BY scraped_at DESC
            LIMIT %s
        """, (limit,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
