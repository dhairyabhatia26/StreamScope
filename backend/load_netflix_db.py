"""
load_netflix_db.py — Ingests the Netflix CSV into MySQL
========================================================
Usage:
    python -m backend.load_netflix_db

This script:
  1. Ensures the schema exists (calls init_netflix_db.init_db)
  2. Clears old data (safe to re-run)
  3. Reads & cleans the Netflix CSV with pandas
  4. Inserts into netflix_titles, title_genres, title_countries

Data cleaning performed:
  - Missing Director, Cast, Country, Rating → 'Unknown'
  - Release_Date parsed into date + release_year + release_month
  - Duration split into duration_minutes (Movies) / seasons (TV Shows)
  - Comma-separated Type → normalized genre rows
  - Comma-separated Country → normalized country rows
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Ensure project root is on the path for direct execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_conn
from backend.init_netflix_db import init_db


def clean_and_load():
    """Reads the Netflix CSV, cleans it, and loads into MySQL."""

    # ── Step 1: Ensure schema exists ──
    init_db()

    # ── Step 2: Read CSV ──
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs",
        "8. Netflix Dataset.csv",
    )
    print(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8")
    raw_count = len(df)
    print(f"  → {raw_count} rows loaded from CSV")

    # Remove duplicate Show_Id rows.
    # The Netflix CSV contains a few entries with the same Show_Id.
    # Since show_id is a UNIQUE key in MySQL, duplicates would cause
    # an insert error.  We keep the first occurrence and drop the rest.
    df = df.drop_duplicates(subset=["Show_Id"], keep="first")
    dupes_removed = raw_count - len(df)
    if dupes_removed:
        print(f"  ⚠ Removed {dupes_removed} duplicate Show_Id rows")
    print(f"  → {len(df)} unique titles to load\n")

    # ── Step 3: Clean data ──
    print("Cleaning data...")

    # Fill missing text fields
    text_cols = ["Director", "Cast", "Country", "Rating", "Description"]
    for col in text_cols:
        df[col] = df[col].fillna("Unknown")

    # Parse Release_Date into date, year, month
    def parse_date(val):
        """Parse date strings like 'August 14, 2020' into datetime."""
        if pd.isna(val) or str(val).strip() == "":
            return None, None, None
        try:
            dt = pd.to_datetime(str(val).strip(), format="%B %d, %Y")
            return dt.date(), dt.year, dt.month
        except Exception:
            # Try flexible parsing as fallback
            try:
                dt = pd.to_datetime(str(val).strip())
                return dt.date(), dt.year, dt.month
            except Exception:
                return None, None, None

    dates = df["Release_Date"].apply(parse_date)
    df["parsed_date"]   = dates.apply(lambda x: x[0])
    df["release_year"]  = dates.apply(lambda x: x[1])
    df["release_month"] = dates.apply(lambda x: x[2])

    # Parse Duration into minutes / seasons
    def parse_duration(row):
        """Extract duration_minutes for Movies, seasons for TV Shows."""
        dur = str(row.get("Duration", "")).strip()
        if pd.isna(dur) or dur == "" or dur == "nan":
            return None, None
        if "min" in dur.lower():
            try:
                return int(dur.lower().replace("min", "").strip()), None
            except ValueError:
                return None, None
        if "season" in dur.lower():
            try:
                return None, int(dur.lower().replace("seasons", "").replace("season", "").strip())
            except ValueError:
                return None, None
        return None, None

    durations = df.apply(parse_duration, axis=1)
    df["duration_minutes"] = durations.apply(lambda x: x[0])
    df["seasons"]          = durations.apply(lambda x: x[1])

    # Fill NaN for numeric columns
    df["release_year"]     = df["release_year"].where(df["release_year"].notna(), None)
    df["release_month"]    = df["release_month"].where(df["release_month"].notna(), None)
    df["duration_minutes"] = df["duration_minutes"].where(df["duration_minutes"].notna(), None)
    df["seasons"]          = df["seasons"].where(df["seasons"].notna(), None)

    print(f"  ✓ Parsed dates for {df['parsed_date'].notna().sum()} / {len(df)} rows")
    print(f"  ✓ Parsed duration for {df['duration_minutes'].notna().sum()} movies, {df['seasons'].notna().sum()} TV shows")

    # ── Step 4: Connect and load ──
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Clear old data
        print("\nClearing previous Netflix data...")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        cur.execute("TRUNCATE TABLE title_countries")
        cur.execute("TRUNCATE TABLE title_genres")
        cur.execute("TRUNCATE TABLE netflix_titles")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Insert titles
        print("Loading titles...")
        # INSERT IGNORE silently skips any row whose show_id already
        # exists in the table.  This is a safety net — the pandas
        # deduplication above should have already handled duplicates,
        # but INSERT IGNORE keeps the loader crash-proof.
        insert_title = """
            INSERT IGNORE INTO netflix_titles
            (show_id, category, title, director, cast_members, country,
             release_date, release_year, release_month, rating, duration,
             duration_minutes, seasons, type, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        genre_rows   = []
        country_rows = []

        for _, row in df.iterrows():
            show_id = str(row["Show_Id"]).strip()

            # Convert numpy types to Python native for MySQL
            release_year  = int(row["release_year"])  if pd.notna(row["release_year"])  else None
            release_month = int(row["release_month"]) if pd.notna(row["release_month"]) else None
            dur_min       = int(row["duration_minutes"]) if pd.notna(row["duration_minutes"]) else None
            seasons       = int(row["seasons"])       if pd.notna(row["seasons"])       else None

            cur.execute(insert_title, (
                show_id,
                str(row["Category"]).strip() if pd.notna(row["Category"]) else None,
                str(row["Title"]).strip()    if pd.notna(row["Title"])    else None,
                str(row["Director"]).strip() if pd.notna(row["Director"]) else None,
                str(row["Cast"]).strip()     if pd.notna(row["Cast"])     else None,
                str(row["Country"]).strip()  if pd.notna(row["Country"])  else None,
                row["parsed_date"],
                release_year,
                release_month,
                str(row["Rating"]).strip()   if pd.notna(row["Rating"])   else None,
                str(row["Duration"]).strip() if pd.notna(row["Duration"]) else None,
                dur_min,
                seasons,
                str(row["Type"]).strip()     if pd.notna(row["Type"])     else None,
                str(row["Description"]).strip() if pd.notna(row["Description"]) else None,
            ))

            # Normalize genres (from Type column — comma separated)
            type_val = str(row["Type"]) if pd.notna(row["Type"]) else ""
            for genre in type_val.split(","):
                g = genre.strip()
                if g and g != "nan":
                    genre_rows.append((show_id, g))

            # Normalize countries
            country_val = str(row["Country"]) if pd.notna(row["Country"]) else ""
            for country in country_val.split(","):
                c = country.strip()
                if c and c != "nan" and c != "Unknown":
                    country_rows.append((show_id, c))

        # Bulk insert genres
        print(f"Loading {len(genre_rows)} genre mappings...")
        cur.executemany(
            "INSERT INTO title_genres (show_id, genre) VALUES (%s, %s)",
            genre_rows,
        )

        # Bulk insert countries
        print(f"Loading {len(country_rows)} country mappings...")
        cur.executemany(
            "INSERT INTO title_countries (show_id, country) VALUES (%s, %s)",
            country_rows,
        )

        conn.commit()

        # Final counts — confirm what actually landed in each table
        cur2 = conn.cursor()
        cur2.execute("SELECT COUNT(*) FROM netflix_titles")
        title_count = cur2.fetchone()[0]
        cur2.execute("SELECT COUNT(*) FROM title_genres")
        genre_count = cur2.fetchone()[0]
        cur2.execute("SELECT COUNT(*) FROM title_countries")
        country_count = cur2.fetchone()[0]
        cur2.close()

        print(f"\n✅ Load complete!")
        print(f"   netflix_titles  : {title_count} rows")
        print(f"   title_genres    : {genre_count} rows")
        print(f"   title_countries : {country_count} rows")
        print("\n   Run: python -m uvicorn backend.api:app --reload")
        print("   Then open frontend/index.html\n")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    clean_and_load()
