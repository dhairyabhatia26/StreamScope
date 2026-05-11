/**
 * app.js — StreamScope: Netflix Content Intelligence Dashboard
 * =============================================================
 * Connects to the FastAPI backend and populates:
 *   1. Executive Overview KPIs (6 cards)
 *   2. Movies vs TV Shows donut chart
 *   3. Yearly category stacked bar chart
 *   4. Top 10 genres bar chart
 *   5. Genre by category grouped bar chart
 *   6. Top 10 countries bar chart
 *   7. Rating distribution bar chart
 *   8. Titles added by year line chart
 *   9. Monthly content pattern bar chart
 *  10. Movie duration distribution bar chart
 *  11. Top directors bar chart
 *  12. Key Insights cards
 *  13. Content Explorer table with filters
 *  14. Keyword search with detail modal
 *
 * Uses Chart.js for all visualizations.
 * Dark-mode-first color scheme — professional, muted palette.
 */

const API = "http://127.0.0.1:8000/api/netflix";

// ── Dark-mode chart colors — professional, muted ──
const C = {
  grid:     "rgba(255,255,255,0.04)",
  tick:     "#5c6072",
  label:    "#8b8fa3",
  blue:     "#5b8def",
  green:    "#34d399",
  amber:    "#fbbf24",
  red:      "#f87171",
  purple:   "#a78bfa",
  cyan:     "#22d3ee",
  slate:    "#64748b",
  orange:   "#fb923c",
  rose:     "#fb7185",
  teal:     "#2dd4bf",
  card:     "#151821",
  // Palette for multi-bar charts
  bars: ["#5b8def","#34d399","#fbbf24","#f87171","#a78bfa","#22d3ee","#fb923c","#64748b","#fb7185","#2dd4bf"],
};

// ── Chart instances ──
let categoryChart      = null;
let yearCategoryChart  = null;
let genreChart         = null;
let genreCategoryChart = null;
let countryChart       = null;
let ratingChart        = null;
let yearlyChart        = null;
let monthlyChart       = null;
let durationChart      = null;
let directorChart      = null;

// Dark-mode scale defaults
function darkScaleOpts(horizontal = false) {
  const axis = {
    grid: { color: C.grid },
    ticks: { font: { size: 10 }, color: C.tick },
  };
  const category = {
    grid: { display: false },
    ticks: { font: { size: 10 }, color: C.label },
  };
  return horizontal
    ? { x: { ...axis, beginAtZero: true }, y: category }
    : { x: category, y: { ...axis, beginAtZero: true } };
}

function darkLegend() {
  return {
    position: "bottom",
    labels: { font: { size: 11 }, color: C.label, padding: 14 },
  };
}


// ═══════════════════════════════════════════════════════════════
//  INITIALIZATION
// ═══════════════════════════════════════════════════════════════

async function init() {
  if (window.lucide) lucide.createIcons();
  initNavbar();
  initSearch();
  await loadRatingsFilter();
  await refreshAll();

  // Filter events
  document.getElementById("filter-category").addEventListener("change", loadTitles);
  document.getElementById("filter-rating").addEventListener("change", loadTitles);
}

// ═══════════════════════════════════════════════════════════════
//  NAVBAR — smooth scroll, active tracking, hamburger
// ═══════════════════════════════════════════════════════════════

function initNavbar() {
  const tabs    = document.querySelectorAll(".tab-link");
  const tabMenu = document.getElementById("nav-tabs");
  const burger  = document.getElementById("hamburger");

  tabs.forEach(tab => {
    tab.addEventListener("click", e => {
      e.preventDefault();
      const section = document.getElementById(tab.getAttribute("data-section"));
      if (section) section.scrollIntoView({ behavior: "smooth", block: "start" });
      tabMenu.classList.remove("open");
    });
  });

  // Active tab tracking with IntersectionObserver
  const sections = document.querySelectorAll(".dashboard-section");
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        tabs.forEach(t => t.classList.toggle("active", t.getAttribute("data-section") === id));
      }
    });
  }, { rootMargin: "-30% 0px -60% 0px", threshold: 0 });
  sections.forEach(sec => observer.observe(sec));

  if (burger) burger.addEventListener("click", () => tabMenu.classList.toggle("open"));
}

/** Master refresh — fetches all sections in parallel. */
async function refreshAll() {
  await Promise.all([
    loadOverview(),
    loadInsights(),
    loadCategoryChart(),
    loadYearlyCategoryChart(),
    loadGenreChart(),
    loadGenreCategoryChart(),
    loadCountryChart(),
    loadRatingChart(),
    loadYearlyChart(),
    loadMonthlyChart(),
    loadDurationChart(),
    loadDirectorChart(),
    loadTitles(),
  ]);
}


// ═══════════════════════════════════════════════════════════════
//  EXECUTIVE OVERVIEW KPIs (6 cards)
// ═══════════════════════════════════════════════════════════════

async function loadOverview() {
  try {
    const res  = await fetch(`${API}/overview`);
    const data = await res.json();
    document.getElementById("kpi-total").textContent   = data.total_titles?.toLocaleString() || "—";
    document.getElementById("kpi-movies").textContent  = data.movies_count?.toLocaleString() || "—";
    document.getElementById("kpi-tvshows").textContent = data.tvshows_count?.toLocaleString() || "—";
    document.getElementById("kpi-country").textContent = data.top_country || "—";
    document.getElementById("kpi-genre").textContent   = data.top_genre || "—";
    document.getElementById("kpi-rating").textContent  = data.most_common_rating || "—";
  } catch (e) { console.error("Overview:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  RATINGS FILTER — populate dropdown
// ═══════════════════════════════════════════════════════════════

async function loadRatingsFilter() {
  try {
    const res  = await fetch(`${API}/ratings`);
    const data = await res.json();
    const sel  = document.getElementById("filter-rating");
    data.forEach(r => {
      const opt = document.createElement("option");
      opt.value       = r.rating;
      opt.textContent = r.rating;
      sel.appendChild(opt);
    });
  } catch (e) { console.error("Rating filter:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  KEY INSIGHTS
// ═══════════════════════════════════════════════════════════════

async function loadInsights() {
  try {
    const res  = await fetch(`${API}/key-insights`);
    const data = await res.json();
    const container = document.getElementById("insights-container");
    container.innerHTML = "";
    if (!data.length) {
      container.innerHTML = `<p style="color:var(--text-muted)">No insights available.</p>`;
      return;
    }
    data.forEach(f => {
      const div = document.createElement("div");
      div.className = `finding-card ${f.type}`;
      div.innerHTML = `
        <div class="finding-title">${esc(f.title)}</div>
        <div class="finding-detail">${esc(f.detail)}</div>
        <div class="finding-metric">📊 ${esc(f.metric)}</div>
      `;
      container.appendChild(div);
    });
  } catch (e) { console.error("Insights:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Movies vs TV Shows (Donut)
// ═══════════════════════════════════════════════════════════════

async function loadCategoryChart() {
  try {
    const res  = await fetch(`${API}/category-split`);
    const data = await res.json();
    const labels = data.map(d => d.category);
    const counts = data.map(d => d.count);
    const colors = [C.blue, C.amber];

    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(document.getElementById("categoryChart").getContext("2d"), {
      type: "doughnut",
      data: { labels, datasets: [{ data: counts, backgroundColor: colors, borderWidth: 0, borderColor: C.card }] },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: darkLegend() },
        cutout: "70%",
      },
    });
  } catch (e) { console.error("Category chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Movies vs TV Shows by Year (Stacked Bar)
// ═══════════════════════════════════════════════════════════════

async function loadYearlyCategoryChart() {
  try {
    const res  = await fetch(`${API}/yearly-by-category`);
    const data = await res.json();

    // Build unique years & datasets
    const years = [...new Set(data.map(d => d.year))].sort();
    const movieData  = years.map(y => { const x = data.find(d => d.year === y && d.category === "Movie");   return x ? x.count : 0; });
    const tvData     = years.map(y => { const x = data.find(d => d.year === y && d.category === "TV Show"); return x ? x.count : 0; });

    if (yearCategoryChart) yearCategoryChart.destroy();
    yearCategoryChart = new Chart(document.getElementById("yearCategoryChart").getContext("2d"), {
      type: "bar",
      data: {
        labels: years,
        datasets: [
          { label: "Movies",   data: movieData, backgroundColor: C.blue + "88", borderColor: C.blue, borderWidth: 1, borderRadius: 2 },
          { label: "TV Shows", data: tvData,    backgroundColor: C.amber + "88", borderColor: C.amber, borderWidth: 1, borderRadius: 2 },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: darkLegend() },
        scales: { ...darkScaleOpts(), x: { ...darkScaleOpts().x, stacked: true }, y: { ...darkScaleOpts().y, stacked: true } },
      },
    });
  } catch (e) { console.error("Yearly category chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Top 10 Genres (Horizontal Bar)
// ═══════════════════════════════════════════════════════════════

async function loadGenreChart() {
  try {
    const res  = await fetch(`${API}/top-genres`);
    const data = await res.json();
    if (genreChart) genreChart.destroy();
    genreChart = new Chart(document.getElementById("genreChart").getContext("2d"), {
      type: "bar",
      data: {
        labels: data.map(d => d.genre),
        datasets: [{
          label: "Titles",
          data: data.map(d => d.count),
          backgroundColor: C.bars.map(c => c + "44"),
          borderColor: C.bars,
          borderWidth: 1, borderRadius: 3,
        }],
      },
      options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: darkScaleOpts(true) },
    });
  } catch (e) { console.error("Genre chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Genre by Category (Grouped Bar)
// ═══════════════════════════════════════════════════════════════

async function loadGenreCategoryChart() {
  try {
    const res  = await fetch(`${API}/genre-by-category`);
    const data = await res.json();

    // Get unique genres (top ones) and group by category
    const genres = [...new Set(data.map(d => d.genre))].slice(0, 10);
    const movieCounts = genres.map(g => { const x = data.find(d => d.genre === g && d.category === "Movie");   return x ? x.count : 0; });
    const tvCounts    = genres.map(g => { const x = data.find(d => d.genre === g && d.category === "TV Show"); return x ? x.count : 0; });

    if (genreCategoryChart) genreCategoryChart.destroy();
    genreCategoryChart = new Chart(document.getElementById("genreCategoryChart").getContext("2d"), {
      type: "bar",
      data: {
        labels: genres,
        datasets: [
          { label: "Movies",   data: movieCounts, backgroundColor: C.blue + "55", borderColor: C.blue, borderWidth: 1, borderRadius: 2 },
          { label: "TV Shows", data: tvCounts,    backgroundColor: C.amber + "55", borderColor: C.amber, borderWidth: 1, borderRadius: 2 },
        ],
      },
      options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: { legend: darkLegend() }, scales: darkScaleOpts(true) },
    });
  } catch (e) { console.error("Genre category chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Top 10 Countries (Horizontal Bar)
// ═══════════════════════════════════════════════════════════════

async function loadCountryChart() {
  try {
    const res  = await fetch(`${API}/top-countries`);
    const data = await res.json();
    if (countryChart) countryChart.destroy();
    countryChart = new Chart(document.getElementById("countryChart").getContext("2d"), {
      type: "bar",
      data: {
        labels: data.map(d => d.country),
        datasets: [{
          label: "Titles",
          data: data.map(d => d.count),
          backgroundColor: C.bars.map(c => c + "44"),
          borderColor: C.bars,
          borderWidth: 1, borderRadius: 3,
        }],
      },
      options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: darkScaleOpts(true) },
    });
  } catch (e) { console.error("Country chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Rating Distribution (Vertical Bar)
// ═══════════════════════════════════════════════════════════════

async function loadRatingChart() {
  try {
    const res  = await fetch(`${API}/ratings`);
    const data = await res.json();
    if (ratingChart) ratingChart.destroy();
    ratingChart = new Chart(document.getElementById("ratingChart").getContext("2d"), {
      type: "bar",
      data: {
        labels: data.map(d => d.rating),
        datasets: [{
          label: "Titles",
          data: data.map(d => d.count),
          backgroundColor: C.purple + "44",
          borderColor: C.purple,
          borderWidth: 1, borderRadius: 3,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: darkScaleOpts() },
    });
  } catch (e) { console.error("Rating chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Titles Added by Year (Line)
// ═══════════════════════════════════════════════════════════════

async function loadYearlyChart() {
  try {
    const res  = await fetch(`${API}/yearly-trends`);
    const data = await res.json();
    if (yearlyChart) yearlyChart.destroy();
    yearlyChart = new Chart(document.getElementById("yearlyChart").getContext("2d"), {
      type: "line",
      data: {
        labels: data.map(d => d.year),
        datasets: [{
          label: "Titles Added",
          data: data.map(d => d.count),
          borderColor: C.blue, backgroundColor: C.blue + "18",
          tension: 0.4, fill: true, pointRadius: 2, pointHoverRadius: 5, borderWidth: 2,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: darkScaleOpts() },
    });
  } catch (e) { console.error("Yearly chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Monthly Content Pattern (Bar)
// ═══════════════════════════════════════════════════════════════

async function loadMonthlyChart() {
  try {
    const res  = await fetch(`${API}/monthly-trends`);
    const data = await res.json();
    if (monthlyChart) monthlyChart.destroy();
    monthlyChart = new Chart(document.getElementById("monthlyChart").getContext("2d"), {
      type: "bar",
      data: {
        labels: data.map(d => d.month_name),
        datasets: [{
          label: "Titles",
          data: data.map(d => d.count),
          backgroundColor: C.cyan + "44",
          borderColor: C.cyan,
          borderWidth: 1, borderRadius: 3,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: darkScaleOpts() },
    });
  } catch (e) { console.error("Monthly chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Movie Duration Distribution (Bar)
// ═══════════════════════════════════════════════════════════════

async function loadDurationChart() {
  try {
    const res  = await fetch(`${API}/movie-duration`);
    const data = await res.json();
    if (durationChart) durationChart.destroy();
    durationChart = new Chart(document.getElementById("durationChart").getContext("2d"), {
      type: "bar",
      data: {
        labels: data.map(d => d.bucket),
        datasets: [{
          label: "Movies",
          data: data.map(d => d.count),
          backgroundColor: C.green + "44",
          borderColor: C.green,
          borderWidth: 1, borderRadius: 3,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: darkScaleOpts() },
    });
  } catch (e) { console.error("Duration chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CHART: Top Directors (Horizontal Bar)
// ═══════════════════════════════════════════════════════════════

async function loadDirectorChart() {
  try {
    const res  = await fetch(`${API}/top-directors`);
    const data = await res.json();
    if (directorChart) directorChart.destroy();
    directorChart = new Chart(document.getElementById("directorChart").getContext("2d"), {
      type: "bar",
      data: {
        labels: data.map(d => d.director),
        datasets: [{
          label: "Titles",
          data: data.map(d => d.count),
          backgroundColor: C.orange + "44",
          borderColor: C.orange,
          borderWidth: 1, borderRadius: 3,
        }],
      },
      options: { indexAxis: "y", responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: darkScaleOpts(true) },
    });
  } catch (e) { console.error("Director chart:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  CONTENT EXPLORER TABLE
// ═══════════════════════════════════════════════════════════════

async function loadTitles() {
  try {
    const category = document.getElementById("filter-category").value;
    const rating   = document.getElementById("filter-rating").value;

    let url = `${API}/titles?limit=50`;
    if (category) url += `&category=${encodeURIComponent(category)}`;
    if (rating)   url += `&rating=${encodeURIComponent(rating)}`;

    const res  = await fetch(url);
    const data = await res.json();
    const tbody = document.getElementById("titles-tbody");
    tbody.innerHTML = "";

    data.forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${esc(r.title)}</strong></td>
        <td><span class="badge ${r.category === 'Movie' ? 'positive' : 'neutral'}">${esc(r.category)}</span></td>
        <td>${esc(r.director)}</td>
        <td>${esc(r.rating)}</td>
        <td>${r.release_year || "—"}</td>
        <td>${esc(r.duration)}</td>
        <td class="snippet" title="${esc(r.description)}">${esc(r.description)}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) { console.error("Titles:", e); }
}


// ═══════════════════════════════════════════════════════════════
//  SEARCH — keyword search + detail modal
// ═══════════════════════════════════════════════════════════════

function initSearch() {
  const input    = document.getElementById("search-input");
  const btn      = document.getElementById("search-btn");
  const clearBtn = document.getElementById("search-clear-btn");
  const modalClose = document.getElementById("modal-close");
  const overlay    = document.getElementById("title-modal");

  // Search on button click
  btn.addEventListener("click", () => performSearch());

  // Search on Enter key
  input.addEventListener("keydown", e => {
    if (e.key === "Enter") performSearch();
  });

  // Show/hide clear button as user types
  input.addEventListener("input", () => {
    clearBtn.style.display = input.value.trim() ? "flex" : "none";
  });

  // Clear search
  clearBtn.addEventListener("click", () => {
    input.value = "";
    clearBtn.style.display = "none";
    document.getElementById("search-status").style.display = "none";
    document.getElementById("search-results").innerHTML = "";
  });

  // Modal close
  if (modalClose) modalClose.addEventListener("click", closeModal);
  if (overlay) overlay.addEventListener("click", e => {
    if (e.target === overlay) closeModal();
  });

  // Close modal on Escape key
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeModal();
  });
}


async function performSearch() {
  const query     = document.getElementById("search-input").value.trim();
  const status    = document.getElementById("search-status");
  const container = document.getElementById("search-results");

  if (!query) {
    status.style.display = "none";
    container.innerHTML = "";
    return;
  }

  // Loading state
  status.style.display = "block";
  status.innerHTML = `<span style="color:var(--text-muted)">Searching for "${esc(query)}"...</span>`;
  container.innerHTML = "";

  try {
    const res  = await fetch(`${API}/search?q=${encodeURIComponent(query)}&limit=30`);
    const data = await res.json();

    if (!data.results || data.results.length === 0) {
      status.innerHTML = `No results for "<strong>${esc(query)}</strong>"`;
      container.innerHTML = `
        <div class="search-empty">
          <div>🎬</div>
          <p>No titles found for "${esc(query)}".<br/>Try a different keyword.</p>
        </div>`;
      return;
    }

    status.innerHTML = `Found <strong>${data.total_results}</strong> result${data.total_results !== 1 ? 's' : ''} for "<strong>${esc(query)}</strong>"`;
    renderSearchResults(data.results, container);

  } catch (e) {
    console.error("Search error:", e);
    status.innerHTML = `<span style="color:var(--danger)">Search failed. Is the API running?</span>`;
  }
}


function renderSearchResults(results, container) {
  results.forEach(r => {
    const card = document.createElement("div");
    card.className = "search-result-card";
    card.setAttribute("data-showid", r.show_id);

    const catClass = r.category === "Movie" ? "cat-movie" : "cat-tv";

    card.innerHTML = `
      <div class="sr-title">${esc(r.title)}</div>
      <div class="sr-meta">
        <span class="sr-tag ${catClass}">${esc(r.category)}</span>
        ${r.release_year ? `<span class="sr-tag">${r.release_year}</span>` : ''}
        ${r.rating ? `<span class="sr-tag">${esc(r.rating)}</span>` : ''}
        ${r.duration ? `<span class="sr-tag">${esc(r.duration)}</span>` : ''}
        ${r.country && r.country !== 'Unknown' ? `<span class="sr-tag">${esc(r.country.split(',')[0].trim())}</span>` : ''}
      </div>
      ${r.description ? `<div class="sr-desc">${esc(r.description)}</div>` : ''}
    `;

    // Click to open detail modal
    card.addEventListener("click", () => openTitleModal(r));
    container.appendChild(card);
  });

  // Re-create lucide icons inside new cards
  if (window.lucide) lucide.createIcons();
}


function openTitleModal(r) {
  const overlay = document.getElementById("title-modal");
  const body    = document.getElementById("modal-body");

  body.innerHTML = `
    <div class="modal-title">${esc(r.title)}</div>
    <dl class="modal-detail-grid">
      <dt>Category</dt>    <dd>${esc(r.category)}</dd>
      <dt>Director</dt>    <dd>${esc(r.director) || '—'}</dd>
      <dt>Cast</dt>        <dd>${esc(r.cast_members) || '—'}</dd>
      <dt>Country</dt>     <dd>${esc(r.country) || '—'}</dd>
      <dt>Year</dt>        <dd>${r.release_year || '—'}</dd>
      <dt>Rating</dt>      <dd>${esc(r.rating) || '—'}</dd>
      <dt>Duration</dt>    <dd>${esc(r.duration) || '—'}</dd>
      <dt>Genres</dt>      <dd>${esc(r.type) || '—'}</dd>
    </dl>
    ${r.description ? `<div class="modal-description">${esc(r.description)}</div>` : ''}
  `;

  overlay.style.display = "flex";
  // Re-create any lucide icons
  if (window.lucide) lucide.createIcons();
}


function closeModal() {
  const overlay = document.getElementById("title-modal");
  if (overlay) overlay.style.display = "none";
}


// ═══════════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════════

function esc(str) {
  if (!str) return "";
  const s = String(str);
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}


// ── Start ──
init();
