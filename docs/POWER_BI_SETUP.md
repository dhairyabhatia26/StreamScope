# Power BI Setup Guide — StreamScope

Connect StreamScope's Netflix analytics data to Microsoft Power BI for advanced reporting.

---

## Option 1: CSV Import (Recommended for Quick Start)

### Step 1: Export CSV
Download the BI-ready CSV from the running API:
```
http://127.0.0.1:8000/api/netflix/export-csv
```

### Step 2: Import into Power BI
1. Open Power BI Desktop
2. Click **Get Data → Text/CSV**
3. Select the downloaded `netflix_bi_export.csv`
4. Click **Transform Data** to preview
5. Click **Load**

### Step 3: Build Visuals
Recommended visuals:
- **Card**: Total titles, Movies count, TV Shows count
- **Donut Chart**: Movies vs TV Shows split
- **Bar Chart**: Top 10 genres, Top 10 countries
- **Line Chart**: Titles added by year
- **Stacked Bar**: Genre breakdown by category
- **Table**: Title details with conditional formatting

---

## Option 2: Direct MySQL Connection

### Step 1: Install MySQL Connector
Power BI requires the MySQL ODBC driver:
- Download from: https://dev.mysql.com/downloads/connector/odbc/

### Step 2: Connect
1. Open Power BI Desktop
2. Click **Get Data → MySQL Database**
3. Enter:
   - Server: `localhost` (or your MySQL host)
   - Database: your database name from `.env`
4. Enter credentials
5. Select the **bi_netflix_view** view

### Step 3: Configure
- Set **Release Year** as a Date hierarchy slicer
- Create measures for:
  - `Total Titles = COUNTROWS(bi_netflix_view)`
  - `Movie Count = CALCULATE(COUNTROWS(bi_netflix_view), bi_netflix_view[category] = "Movie")`

---

## Recommended Slicers

| Slicer | Column |
|---|---|
| Content Type | `category` |
| Country | `country` |
| Genre | `genre` |
| Rating | `rating` |
| Year | `release_year` |

---

## KPI Definitions

| KPI | Formula |
|---|---|
| Total Titles | COUNT of distinct titles |
| Movies % | Movies / Total × 100 |
| TV Shows % | TV Shows / Total × 100 |
| Avg Duration | AVG of duration_minutes (Movies only) |
| Top Genre | Genre with highest COUNT |
| Top Country | Country with highest COUNT |
