function filter_table() {
    let checkboxes = document.querySelectorAll("input[name='filter']:checked");
    let selectedFilters = Array.from(checkboxes).map(cb => cb.value.toLowerCase());

    let table = document.getElementById("results_table");
    let rows = table.querySelectorAll("tbody tr");

    rows.forEach(row => {
        let cells = row.getElementsByTagName("td");
        let matchesFilter = selectedFilters.some(filter => {
            return row.innerText.toLowerCase().includes(filter);
        });

        row.style.display = matchesFilter || selectedFilters.length === 0 ? "" : "none";
    });
}
