document.querySelectorAll("#toggle-columns input").forEach(checkbox => {
    checkbox.addEventListener("change", function() {
        let columnIndex = this.dataset.col; // Get the column index from the checkbox
        let cells = document.querySelectorAll(`#results_table th:nth-child(${+columnIndex+1}), #results_table td:nth-child(${+columnIndex+1})`);

        // Show or hide the column based on checkbox state
        cells.forEach(cell => {
            cell.style.display = this.checked ? "" : "none";
        });
    });
});
