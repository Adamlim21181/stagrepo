var btns = document.querySelectorAll("#toggle-columns .button");

// Attach listeners to column filter buttons
btns.forEach(function(btn) {
  if (!btn.hasAttribute("onclick")) {  // skip 'Show All' button
    btn.classList.add("active"); // Set initial state to active
    
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

  var btn = document.querySelector(`.button[data-col="${index}"]`);
  var show = btn.classList.contains("active");

  for (var i = 0; i < rows.length; i++) {
    var cell = rows[i].cells[index - 1];
    if (cell) {
      cell.style.display = show ? "" : "none";
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
  
    var btns = document.querySelectorAll("#toggle-columns .button");
    btns.forEach(function(btn) {
      if (!btn.hasAttribute("onclick")) {
        btn.classList.add("active"); // Reset to active
      }
    });
  }
  

