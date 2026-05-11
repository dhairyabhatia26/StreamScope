# StreamScope — Streaming Content Intelligence Dashboard

A full-stack Business Intelligence platform that analyzes the Netflix content catalog using data cleaning, MySQL storage, REST APIs, interactive visualizations, and BI-ready exports.

**Built for a Business Analyst / Data Analyst portfolio.**

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI |
| **Database** | MySQL |
| **Frontend** | HTML, CSS, JavaScript, Chart.js |
| **Data** | Netflix Dataset (7,700+ titles) |
| **BI Export** | CSV + MySQL view for Power BI / Tableau |

---

## Architecture

```
CSV Dataset → Pandas Cleaning → MySQL Database → FastAPI REST API → Interactive Dashboard
                                       ↓
                               bi_netflix_view → Power BI / Tableau
```

---

## Features

### Data Pipeline
- CSV ingestion with pandas
- Missing value handling (Director, Cast, Country, Rating)
- Date parsing (Release_Date → date, year, month)
- Duration splitting (minutes for movies, seasons for TV shows)
- Genre & country normalization into relational tables

### Dashboard Sections
1. **Executive Overview** — 6 KPI cards (Total Titles, Movies, TV Shows, Top Country, Top Genre, Top Rating)
2. **Key Insights** — Data-driven business findings calculated from real data
3. **Content Mix** — Movies vs TV Shows donut + stacked bar by year
4. **Genre Intelligence** — Top 10 genres + genre breakdown by content type
5. **Geography** — Top 10 content-producing countries
6. **Rating Analysis** — Maturity rating distribution
7. **Time Trends** — Yearly additions + monthly patterns
8. **Duration Analysis** — Movie duration distribution + top directors
9. **Content Explorer** — Filterable title listing
10. **BI Export** — CSV download + MySQL view for Power BI/Tableau

### Analytics Charts (10 total)
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
pip install fastapi uvicorn mysql-connector-python python-dotenv pandas

# Configure database
cp .env.example .env
# Edit .env with your MySQL credentials
```

### Database Setup

```bash
# Load the Netflix dataset into MySQL
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

## Power BI / Tableau

This project is BI-ready:

- **CSV Export**: Download at `/api/netflix/export-csv`
- **MySQL View**: `bi_netflix_view` available for direct database connection
- **Setup Guides**: See `docs/POWER_BI_SETUP.md` and `docs/TABLEAU_SETUP.md`

---

## Business Value

This project demonstrates:

| Skill | Evidence |
|---|---|
| **Data Cleaning** | Handling nulls, date parsing, duration splitting |
| **Database Design** | Normalized schema with indexes and BI views |
| **API Development** | RESTful endpoints with query parameters |
| **Data Visualization** | 10 interactive Chart.js visualizations |
| **Business Insights** | Data-driven findings with KPI storytelling |
| **BI Integration** | Power BI / Tableau ready exports |
| **Full-Stack** | End-to-end: CSV → MySQL → API → Dashboard |

---

## Project Structure

```
webscrape-dashboard/
├── backend/
│   ├── api.py              # FastAPI endpoints
│   ├── db.py               # MySQL connection
│   ├── init_netflix_db.py  # Schema creation
│   └── load_netflix_db.py  # CSV ingestion & cleaning
├── frontend/
│   ├── index.html          # Dashboard layout
│   ├── style.css           # Dark-mode styling
│   └── app.js              # Chart.js visualizations
├── docs/
│   ├── 8. Netflix Dataset.csv
│   ├── POWER_BI_SETUP.md
│   └── TABLEAU_SETUP.md
├── .env                    # Database credentials
└── README.md
```

---

## Screenshots

> Dashboard screenshots will be added after deployment.

---

## License

MIT
