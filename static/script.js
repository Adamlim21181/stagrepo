// Select all buttons inside the #toggle-columns container
var btns = document.querySelectorAll("#toggle-columns .button");

// Loop through each button to set up its initial state and click behavior
btns.forEach(function(btn) {

  // Skip the "Show All" button (it has an inline 'onclick' attribute)
  if (!btn.hasAttribute("onclick")) {

        // Add the 'active' class to mark the button as ON (column is visible)
        btn.classList.add("active");

        // When the user clicks the button:
        btn.addEventListener("click", function () {

            // Toggle the 'active' class (green = active = column shown)
            this.classList.toggle("active");

            // Get the column number from the data-col attribute (e.g., data-col="2" for 2nd column)
            var colIndex = parseInt(this.getAttribute("data-col"));

            // Show or hide the column based on its new state
            toggleColumn(colIndex);

            // Recalculate the ranks after a column has been toggled
            updateRanks();
        });
    }
});

// Show or hide a table column based on its index (1-based)
function toggleColumn(index) {
    var table = document.getElementById("results_table");
    var rows = table.rows; // Includes header row and all data rows
  
    // Get the corresponding button to check its state
    var btn = document.querySelector(`.button[data-col="${index}"]`);
  
    // If the button has the 'active' class, we want to show the column
    var show = btn.classList.contains("active");
  
    // Loop through all rows in the table (header + data)
    for (var i = 0; i < rows.length; i++) {
        var cell = rows[i].cells[index - 1]; // Index is 1-based, JavaScript uses 0-based
        if (cell) {
            // If show = true, make cell visible; otherwise, hide it
            cell.style.display = show ? "" : "none";
        }
    }
}

  // Reset the table to show all columns and reset all buttons
function show_all() {
    var table = document.getElementById("results_table");
    var rows = table.rows;
  
    // Loop through all rows and cells to make every cell visible
    for (var i = 0; i < rows.length; i++) {
        for (var j = 0; j < rows[i].cells.length; j++) {
            rows[i].cells[j].style.display = "";
        }
    }
  
    // Re-activate all toggle buttons
    btns.forEach(function(btn) {
        if (!btn.hasAttribute("onclick")) {
            btn.classList.add("active");
        }
    });
  
        // Update the ranks since all data is now visible again
        updateRanks();
  }

  // Update the ranking column dynamically based on visible columns
function updateRanks() {
    const table = document.getElementById("results_table");
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.rows); // Convert rows from HTMLCollection to an array
  
    // If there are no rows, stop the function
    if (rows.length === 0) return;
  
    // Use the first row to determine which columns are currently visible
    const sampleRow = rows[0];
    const visibleCols = sampleRow.cells;
  
    // Define which columns we can use to rank people
    // Each has an index and sort order (desc = higher is better, asc = lower is better)
    const metricOptions = [
        { index: 10, order: "desc" }, // Total Score
        { index: 8, order: "desc" },  // Execution
        { index: 9, order: "desc" },  // Difficulty
        { index: 7, order: "asc" }    // Penalty (smaller is better)
    ];
  
    let metricIndex = null;  // Column we'll use to rank
    let sortOrder = "desc";  // Sort order (default is descending)
  
    // Find the first visible ranking column based on priority
    for (const option of metricOptions) {
        if (visibleCols[option.index].style.display !== "none") {
            metricIndex = option.index;
            sortOrder = option.order;
            break;
        }
    }
  
    // If no ranking metric column is visible, clear ranks and stop
    if (metricIndex === null) {
        rows.forEach(row => row.cells[11].textContent = "");
        return;
    }
  
    // Check if we should group rankings (by Club or Competition)
    let groupBy = null;
    if (visibleCols[3].style.display !== "none") groupBy = 3; // Club column
    if (visibleCols[4].style.display !== "none") groupBy = 4; // Competition column
  
    // Organize rows into groups
    const groups = {};
    rows.forEach(row => {
        // Skip rows that are hidden
        if (row.style.display === "none") return;
    
        // Group key is either the club/competition name or "all" if no grouping
        const key = groupBy !== null ? row.cells[groupBy].textContent : "all";
    
        // Add the row to the appropriate group
        if (!groups[key]) groups[key] = [];
        groups[key].push(row);
    });
  
    // Sort and rank each group individually
    Object.values(groups).forEach(groupRows => {
  
        // Sort rows within the group based on the ranking metric
        groupRows.sort((a, b) => {
            const valA = parseFloat(a.cells[metricIndex].textContent);
            const valB = parseFloat(b.cells[metricIndex].textContent);
    
            if (isNaN(valA) || isNaN(valB)) return 0;
    
            // Ascending or descending order
            return sortOrder === "asc" ? valA - valB : valB - valA;
        });
  
        // Assign rank numbers (1-based)
        groupRows.forEach((row, index) => {
            row.cells[11].textContent = index + 1; // Rank column is index 11
        });
    });
}
  
// Call the updateRanks function once when the page loads
document.addEventListener("DOMContentLoaded", updateRanks);

  