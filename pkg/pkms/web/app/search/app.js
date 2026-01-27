const LIMIT = 10;
let currentQuery = "";
let currentOffset = 0;

async function doSearch(offset) {
    const query = document.getElementById("queryInput").value.trim();
    if (!query) return;

    currentQuery = query;
    currentOffset = offset;

    const url = `/api/search?q=${encodeURIComponent(query)}&limit=${LIMIT}&offset=${offset}`;
    const resp = await fetch(url);
    const data = await resp.json();

    renderResultHits(data.hits);
    updatePagination(data.hits.length);
}

function renderResultHits(hits) {
    const container = document.getElementById("result");
    container.innerHTML = "";

    if (hits.length === 0) {
        container.innerHTML = "<p>No results found.</p>";
        return;
    }

    for (const r of hits) {
        const div = document.createElement("div");
        div.className = "result-item";

        div.innerHTML = 
`<div class="result-title">
    <a href="/api/view/${r.file_id}${r.file_extension}">${r.title}</a>
</div>
${r.snippet ? `<div class="result-snippet">${r.snippet}</div>` : ""}
<div class="result-meta">pkms:///file/id:${r.file_id}${r.file_extension}</div>
`;

        container.appendChild(div);
    }
}

function updatePagination(resultCount) {
    const pagination = document.getElementById("pagination");
    pagination.style.display = "block";

    // Disable prev if at first page
    pagination.querySelector("button:nth-child(1)").disabled =
        currentOffset === 0;

    // Disable next if less than limit
    pagination.querySelector("button:nth-child(2)").disabled =
        resultCount < LIMIT;
}

function prevPage() {
    if (currentOffset === 0) return;
    doSearch(currentOffset - LIMIT);
}

function nextPage() {
    doSearch(currentOffset + LIMIT);
}

// Enter key triggers search
document
    .getElementById("queryInput")
    .addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            doSearch(0);
        }
    });