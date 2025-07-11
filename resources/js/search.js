let pages = {};

fetch('/pages.json')
  .then(response => {
    if (!response.ok) throw new Error("Failed to load pages.json");
    return response.json();
  })
  .then(data => {
    pages = data;
  });


const searchInput = document.getElementById("searchInput");
const results = document.getElementById("results");

searchInput.addEventListener("input", () => {
  const query = searchInput.value.toLowerCase();
  results.innerHTML = "";

  if (query.trim() === "") {
    results.style.display = "none";
    return;
  }

  const filtered = pages.filter(page => page.name.toLowerCase().includes(query));

  if (filtered.length === 0) {
    results.innerHTML = "<li>No results found.</li>";
  } else {
    filtered.forEach(page => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = page.path;
      a.textContent = page.name;
      li.appendChild(a);
      results.appendChild(li);
    });
  }

  // Show the results box
  results.style.display = "block";
});

// Hide the results if the user clicks outside the search area
document.addEventListener("click", (e) => {
  const container = document.querySelector(".search-container");
  if (!container.contains(e.target)) {
    results.style.display = "none";
  }
});
