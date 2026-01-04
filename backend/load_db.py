from backend.db import get_conn
from scraper.scrape_quotes import scrape_quotes

def upsert_quotes(rows):
    conn = get_conn()
    cur = conn.cursor()

    sql = """
    INSERT INTO quotes (text, author, tags, source_page)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        tags = VALUES(tags),
        source_page = VALUES(source_page),
        scraped_at = CURRENT_TIMESTAMP
    """

    data = [(r["text"], r["author"], r["tags"], r["source_page"]) for r in rows]
    cur.executemany(sql, data)

    cur.close()
    conn.close()

if __name__ == "__main__":
    rows = scrape_quotes(max_pages=10)
    upsert_quotes(rows)
    print("Loaded/updated rows:", len(rows))
