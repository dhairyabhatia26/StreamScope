# StreamScope: Netflix Content Intelligence Dashboard

A full-stack Business Intelligence platform that analyzes the Netflix content catalog using data cleaning, MySQL storage, REST APIs, interactive visualizations, and BI-ready exports.

**Built as a Business Analyst / Data Analyst portfolio project.**

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.8+, FastAPI, Uvicorn |
| **Database** | MySQL 8.0+ |
| **Frontend** | HTML, CSS, JavaScript, Chart.js |
| **Data** | Netflix Dataset (7,700+ titles) |
| **BI Export** | CSV + MySQL view for Power BI / Tableau |

---

## Architecture

```
Netflix CSV Dataset
        │
        ▼
  Pandas Cleaning & Parsing
        │
        ▼
  MySQL Database (3 tables + 1 BI view)
        │
        ▼
  FastAPI REST API (15 endpoints)
        │
        ▼
  Interactive Dashboard (10 charts, search, export)
        │
        ▼
  Power BI / Tableau (CSV or direct MySQL)
```

---

## Features

### Data Pipeline
- CSV ingestion with pandas
- Missing value handling (Director, Cast, Country, Rating)
- Date parsing (`Release_Date` → date, year, month)
- Duration splitting (minutes for movies, seasons for TV shows)
- Genre & country normalization into relational tables
- Duplicate `Show_Id` detection and removal

### Dashboard Sections
1. **Executive Overview** — 6 KPI cards (Total Titles, Movies, TV Shows, Top Country, Top Genre, Top Rating)
2. **Key Insights** — 7 data-driven business findings calculated from real data
3. **Content Mix** — Movies vs TV Shows donut + stacked bar by year
4. **Genre Intelligence** — Top 10 genres + genre breakdown by content type
5. **Geography** — Top 10 content-producing countries
6. **Rating Analysis** — Maturity rating distribution
7. **Time Trends** — Yearly additions + monthly patterns
8. **Duration Analysis** — Movie duration distribution + top directors
9. **Titles & Search** — Keyword search + filterable browse table + detail modal
10. **BI Export** — CSV download + MySQL view for Power BI / Tableau

### Charts (10 interactive visualizations)
| # | Chart | Type |
|---|---|---|
| 1 | Movies vs TV Shows | Donut |
| 2 | Content by Year & Category | Stacked Bar |
| 3 | Top 10 Genres | Horizontal Bar |
| 4 | Genre by Category | Grouped Bar |
| 5 | Top 10 Countries | Horizontal Bar |
| 6 | Rating Distribution | Bar |
| 7 | Titles Added by Year | Line |
| 8 | Monthly Content Pattern | Bar |
| 9 | Movie Duration Distribution | Bar |
| 10 | Top Directors | Horizontal Bar |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/netflix/overview` | Executive KPI summary |
| GET | `/api/netflix/titles` | Paginated titles with filters |
| GET | `/api/netflix/category-split` | Movies vs TV Shows counts |
| GET | `/api/netflix/top-genres` | Top 10 genres |
| GET | `/api/netflix/top-countries` | Top 10 countries |
| GET | `/api/netflix/ratings` | Rating distribution |
| GET | `/api/netflix/yearly-trends` | Titles per year |
| GET | `/api/netflix/yearly-by-category` | Yearly split by Movie/TV Show |
| GET | `/api/netflix/monthly-trends` | Monthly addition pattern |
| GET | `/api/netflix/movie-duration` | Duration distribution |
| GET | `/api/netflix/top-directors` | Top 10 directors |
| GET | `/api/netflix/genre-by-category` | Genre split by content type |
| GET | `/api/netflix/key-insights` | Data-driven business insights |
| GET | `/api/netflix/search` | Keyword search (title, cast, director, country, genre) |
| GET | `/api/netflix/export-csv` | CSV download for BI tools |

---

## Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd webscrape-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with your MySQL credentials:
#   MYSQL_HOST=localhost
#   MYSQL_PORT=3306
#   MYSQL_USER=root
#   MYSQL_PASSWORD=yourpassword
#   MYSQL_DATABASE=yourdb
```

### Load Data

```bash
python -m backend.load_netflix_db
```

### Run

```bash
# Start the API server
python -m uvicorn backend.api:app --reload

# Open the dashboard
# Navigate to frontend/index.html in your browser
```

---

## Database Schema

| Table | Purpose |
|---|---|
| `netflix_titles` | Main content table (title, category, director, rating, duration, etc.) |
| `title_genres` | Normalized genres (many-to-many mapping) |
| `title_countries` | Normalized countries (many-to-many mapping) |
| `bi_netflix_view` | Flattened join view for Power BI / Tableau |

---

## Power BI / Tableau Integration

This project is BI-ready out of the box:

- **CSV Export**: Download at `/api/netflix/export-csv`
- **MySQL View**: `bi_netflix_view` available for direct database connection
- **Setup Guides**: See `docs/POWER_BI_SETUP.md` and `docs/TABLEAU_SETUP.md`

---

## Business Value

This project demonstrates:

| Skill | Evidence |
|---|---|
| **Data Cleaning** | Handling nulls, date parsing, duration splitting, deduplication |
| **Database Design** | Normalized schema with indexes and BI views |
| **API Development** | 15 RESTful endpoints with query parameters and pagination |
| **Data Visualization** | 10 interactive Chart.js visualizations |
| **Business Insights** | Data-driven findings with KPI storytelling |
| **Search & Discovery** | Multi-column keyword search with detail modal |
| **BI Integration** | Power BI / Tableau ready CSV and MySQL view |
| **Full-Stack** | End-to-end: CSV → MySQL → API → Dashboard → BI Export |

---

## Project Structure

```
StreamScope/
├── backend/
│   ├── __init__.py
│   ├── api.py              # FastAPI endpoints (15 routes)
│   ├── db.py               # MySQL connection helper
│   ├── init_netflix_db.py  # Schema creation (tables + BI view)
│   └── load_netflix_db.py  # CSV ingestion & data cleaning
├── frontend/
│   ├── index.html          # Dashboard layout (10 sections)
│   ├── style.css           # Dark-mode enterprise styling
│   └── app.js              # Chart.js visualizations & search
├── docs/
│   ├── 8. Netflix Dataset.csv
│   ├── POWER_BI_SETUP.md
│   └── TABLEAU_SETUP.md
├── .env                    # Database credentials (not committed)
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

---

## License

MIT
