const API = "http://127.0.0.1:8000/api/quotes";
const tbody = document.getElementById("tbody");
const input = document.getElementById("search");
const btn = document.getElementById("btn");

async function loadQuotes(query="") {
  const url = query
    ? `${API}?q=${encodeURIComponent(query)}&limit=50`
    : `${API}?limit=50`;

  const res = await fetch(url);
  const data = await res.json();

  tbody.innerHTML = "";
  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.text}</td>
      <td>${row.author}</td>
      <td>${row.tags || ""}</td>
    `;
    tbody.appendChild(tr);
  });
}

btn.addEventListener("click", () => loadQuotes(input.value));
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") loadQuotes(input.value);
});

loadQuotes();
