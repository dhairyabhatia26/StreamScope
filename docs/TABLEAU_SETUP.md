# Tableau Setup Guide — StreamScope

Connect StreamScope's Netflix analytics data to Tableau for advanced visual analytics.

---

## Option 1: CSV Import (Recommended for Quick Start)

### Step 1: Export CSV
Download the BI-ready CSV from the running API:
```
http://127.0.0.1:8000/api/netflix/export-csv
```

### Step 2: Import into Tableau
1. Open Tableau Desktop or Tableau Public
2. Click **Connect → Text file**
3. Select the downloaded `netflix_bi_export.csv`
4. Tableau will auto-detect data types
5. Click **Sheet 1** to begin building visuals

### Step 3: Build Visuals
Recommended worksheets:
- **Treemap**: Top genres by title count
- **Map**: Content by country (use `country` field)
- **Bar Chart**: Rating distribution
- **Line Chart**: Titles added by year
- **Stacked Bar**: Category split by year
- **Heatmap**: Genre by category matrix

---

## Option 2: Direct MySQL Connection

### Step 1: Connect
1. Open Tableau Desktop
2. Click **Connect → MySQL**
3. Enter:
   - Server: `localhost`
   - Port: from your `.env` file
   - Database: from your `.env` file
   - Username / Password: from your `.env` file
4. Click **Sign In**

### Step 2: Select Data
1. From the left pane, find the **bi_netflix_view** view
2. Drag it to the canvas
3. Click **Sheet 1** to start building

---

## Recommended Dashboard Layout

### Page 1: Executive Summary
- KPI cards: Total, Movies, TV Shows
- Category donut chart
- Yearly additions line chart
- Top 10 countries bar chart

### Page 2: Genre Deep Dive
- Top genres bar chart
- Genre by category heatmap
- Genre trends over time

### Page 3: Content Details
- Interactive title table
- Rating distribution
- Duration analysis

---

## Suggested Filters / Parameters

| Filter | Column | Type |
|---|---|---|
| Content Type | `category` | Dropdown |
| Country | `country` | Multi-select |
| Genre | `genre` | Multi-select |
| Rating | `rating` | Dropdown |
| Year Range | `release_year` | Range slider |

---

## Calculated Fields

```
// Movies Percentage
IF [category] = "Movie" THEN 1 ELSE 0 END

// Content Age
2024 - [release_year]

// Duration Bucket
IF [duration_minutes] < 60 THEN "Short (<60 min)"
ELSEIF [duration_minutes] < 90 THEN "Medium (60-89 min)"
ELSEIF [duration_minutes] < 120 THEN "Standard (90-119 min)"
ELSE "Long (120+ min)"
END
```
