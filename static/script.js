
function myFunction() {
  // Get input field and table
  var input = document.getElementById("search");
  var filter = input.value.toUpperCase();
  var table = document.getElementById("resultsTable");
  var tr = table.getElementsByTagName("tr");

  // Loop through all table rows
  for (let i = 1; i < tr.length; i++) { // Start from index 1 to skip the header
    let tds = tr[i].getElementsByTagName("td");
    let match = false;

    // Check each cell in the row
    for (let td of tds) {
      if (td) {
        let txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().includes(filter)) {
          match = true;
          break; // Stop checking once a match is found
        }
      }
    }

    // Show or hide row based on match
    tr[i].style.display = match ? "" : "none";
  }
}




