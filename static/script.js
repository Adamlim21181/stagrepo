
let searchTimeout;

document.getElementById("search").addEventListener("keyup", function() {
    clearTimeout(searchTimeout);  // Cancel previous timeout if typing continues

    searchTimeout = setTimeout(() => {  // Delay execution to prevent overload
        let filter = this.value.toLowerCase();
        let rows = document.querySelectorAll("#resultsTable tbody tr");

        rows.forEach(row => {
            let text = row.innerText.toLowerCase();
            row.style.display = text.includes(filter) ? "" : "none";
        });
    }, 300);  // 300ms delay (adjust as needed)
});


