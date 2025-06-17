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

function changeRowsPerPage() {
    /**
     * Redirects to the results page while modifying the 'per_page' parameter.
     * Ensures the page resets to the first page when changing row count.
     */
    let selectedRows = document.getElementById("rows_per_page").value;

    // Debugging: Log selected value
    console.log("Selected Rows Per Page:", selectedRows);

    // Build the URL manually since we can't use url_for in separate JS files
    let newUrl = "/results?page=1&per_page=" + selectedRows;
    console.log("Redirecting to URL:", newUrl);

    window.location.href = newUrl;
}


/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function gymnastSelection() {
  document.getElementById("gymnastDropdown").classList.toggle("show");
}

function filterFunction() {
  const input = document.getElementById("myInput");
  const filter = input.value.toUpperCase();
  const div = document.getElementById("myDropdown");
  const a = div.getElementsByTagName("a");
  for (let i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } else {
      a[i].style.display = "none";
    }
  }
}
