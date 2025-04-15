var btns = document.querySelectorAll("#toggle-columns .btn");

// Attach listeners to column filter buttons
btns.forEach(function(btn) {
  if (!btn.hasAttribute("onclick")) {  // skip 'Show All' button
    btn.addEventListener("click", function() {
      var colIndex = parseInt(this.getAttribute("data-col"));
      toggleColumn(colIndex);
      this.classList.toggle("active");
    });
  }
});

// Function to show/hide a column by index
function toggleColumn(index) {
  var table = document.getElementById("results_table");
  var rows = table.rows;

  for (var i = 0; i < rows.length; i++) {
    var cell = rows[i].cells[index - 1];
    if (cell) {
      cell.style.display = (cell.style.display === "none") ? "" : "none";
    }
  }
}

// Show all columns and reset buttons
function show_all() {
  var table = document.getElementById("results_table");
  var rows = table.rows;

  for (var i = 0; i < rows.length; i++) {
    for (var j = 0; j < rows[i].cells.length; j++) {
      rows[i].cells[j].style.display = "";
    }
  }

  // Remove 'active' class from all buttons
  var btns = document.querySelectorAll("#toggle-columns .btn");
  btns.forEach(function(btn) {
    btn.classList.remove("active");
  });
}

