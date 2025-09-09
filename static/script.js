/*
 * GYMNASTICS COMPETITION MANAGEMENT SYSTEM - JAVASCRIPT
 * =====================================================
 * This file contains all the interactive functionality for the website.
 * It handles modals, search features, and dynamic form controls.
 */

// Wait for the entire page to load before running any JavaScript
document.addEventListener("DOMContentLoaded", () => {
  
  /*
   * MODAL FUNCTIONALITY (for Calendar Page)
   * =====================================
   * This section handles popup windows that show competition details
   * when you click on competitions in the calendar view.
   */
  
  // Find the modal window and its content area in the HTML
  const modal = document.getElementById("competitionModal");
  const body  = document.getElementById("modalBody");

  // Only run modal code if modal exists (this only happens on calendar page)
  if (modal && body) {
    
    // Find all elements that have competition data and can be clicked
    document.querySelectorAll("[data-competition-id]").forEach(el => {
      
      // Add a click listener to each competition element
      el.addEventListener("click", () => {
        
        // When clicked, fetch the competition details from the server
        // This makes an HTTP request to get the competition information
        fetch(`/competition/${el.dataset.competitionId}`)
          .then(r => r.text())  // Convert the response to text/HTML
          .then(html => {
            // Put the received HTML into the modal body
            body.innerHTML = html;
            // Show the modal by adding the "show" CSS class
            modal.classList.add("show");
          });
      });
    });

    // Handle the close button (X) in the modal
    const closeBtn = document.querySelector("#competitionModal .close");
    if (closeBtn) {
      // When close button is clicked, hide the modal
      closeBtn.onclick = () => modal.classList.remove("show");
    }
    
    // Handle clicking outside the modal to close it
    window.onclick = e => { 
      // If user clicks on the background (not the modal content), close it
      if (e.target === modal) {
        modal.classList.remove("show");
      }
    };
  }

  /*
   * INITIALIZE PAGE-SPECIFIC FUNCTIONALITY
   * ====================================
   * These functions set up different features depending on which page you're on
   */

  // Set up the entries page search functionality
  initializeEntriesPage();

  // Set up the scoring page judge input functionality
  initializeScoringPage();

  // Set up the results page column toggle functionality
  initializeResultsPage();
});

/*
 * ENTRIES PAGE SEARCH FUNCTIONALITY
 * ================================
 * This allows users to search for gymnasts by typing in a search box
 * instead of scrolling through a long dropdown list.
 */
function initializeEntriesPage() {
  
  // Find the search input box and the gymnast dropdown list
  const gymnastSearch = document.getElementById('gymnast_search');
  const gymnastSelect = document.getElementById('gymnast_id');
  
  // Only run this code if we're on the entries page (these elements exist)
  if (!gymnastSearch || !gymnastSelect) return;
  
  // Listen for when the user types in the search box
  gymnastSearch.addEventListener('input', function () {
    
    // Get what the user typed and convert to lowercase for easier searching
    const searchTerm = this.value.toLowerCase();
    
    // Get all the gymnast options from the dropdown
    const options = gymnastSelect.getElementsByTagName('option');

    // Go through each option (skip the first empty one)
    for (let i = 1; i < options.length; i++) {
      const option = options[i];
      
      // Get the gymnast information stored in the option
      const name = option.getAttribute('data-name') || '';
      const club = option.getAttribute('data-club') || '';
      const level = option.getAttribute('data-level') || '';
      const text = option.textContent.toLowerCase();

      // Check if the search term matches any of the gymnast information
      if (text.includes(searchTerm) || name.includes(searchTerm) ||
          club.includes(searchTerm) || level.includes(searchTerm)) {
        // Show this option if it matches
        option.style.display = '';
      } else {
        // Hide this option if it doesn't match
        option.style.display = 'none';
      }
    }

    // Smart auto-selection: if only one gymnast matches, select them automatically
    const visibleOptions = Array.from(options).filter(opt => opt.style.display !== 'none' && opt.value !== '');
    if (searchTerm && visibleOptions.length === 1) {
      // Automatically select the only matching gymnast
      gymnastSelect.value = visibleOptions[0].value;
    }
  });

  // Clear the search box when a gymnast is manually selected from dropdown
  gymnastSelect.addEventListener('change', function () {
    if (this.value) {
      // If a gymnast was selected, clear the search box
      gymnastSearch.value = '';
    }
  });
}

/*
 * SCORING PAGE JUDGE FUNCTIONALITY
 * ===============================
 * This allows judges to be added/removed dynamically on the scoring page
 * and automatically calculates average scores.
 */
function initializeScoringPage() {
  
  // Find the "Add Judge" button
  const addJudgeBtn = document.getElementById('add-judge-btn');
  
  // Only run this code if we're on the scoring page (button exists)
  if (!addJudgeBtn) return;
  
  // Keep track of how many judges we have
  let judgeCount = 1;
  const maxJudges = 6; // Don't allow more than 6 judges (reasonable limit)

  // When the "Add Judge" button is clicked
  addJudgeBtn.addEventListener('click', function () {
    // Only add a judge if we haven't reached the maximum
    if (judgeCount < maxJudges) {
      judgeCount++; // Increase the count
      addJudgeInput(); // Create a new input field
      updateRemoveButtons(); // Update which remove buttons are visible
      updateAverage(); // Recalculate the average score
    }
  });

  /*
   * CREATE A NEW JUDGE INPUT FIELD
   * =============================
   * This function creates the HTML for a new judge score input
   */
  function addJudgeInput() {
    // Find the container where judge inputs go
    const container = document.getElementById('execution-scores-container');
    
    // Create a new div element for this judge
    const newRow = document.createElement('div');
    newRow.className = 'execution-score-row';
    newRow.setAttribute('data-judge', judgeCount);

    // Set the HTML content for this judge input
    newRow.innerHTML = `
      <div class="judge-label">Judge ${judgeCount}:</div>
      <input type="number" name="execution_scores" step="0.001" min="0" max="10" 
             placeholder="8.5" required class="execution-input">
      <button type="button" class="remove-judge-btn">×</button>
    `;

    // Add this new judge input to the page
    container.appendChild(newRow);

    // Set up the remove button to work
    newRow.querySelector('.remove-judge-btn').addEventListener('click', function () {
      removeJudgeInput(newRow);
    });

    // Set up the input field to update the average when scores are entered
    newRow.querySelector('.execution-input').addEventListener('input', updateAverage);
  }

  /*
   * REMOVE A JUDGE INPUT FIELD
   * =========================
   * This function removes a judge and updates everything accordingly
   */
  function removeJudgeInput(row) {
    row.remove(); // Remove the HTML element from the page
    judgeCount--; // Decrease the count
    updateJudgeLabels(); // Renumber the remaining judges
    updateRemoveButtons(); // Update which remove buttons are visible
    updateAverage(); // Recalculate the average
  }

  /*
   * UPDATE JUDGE LABELS
   * ==================
   * When a judge is removed, renumber the remaining judges (Judge 1, Judge 2, etc.)
   */
  function updateJudgeLabels() {
    const rows = document.querySelectorAll('.execution-score-row');
    rows.forEach((row, index) => {
      row.querySelector('.judge-label').textContent = `Judge ${index + 1}:`;
      row.setAttribute('data-judge', index + 1);
    });
  }

  /*
   * UPDATE REMOVE BUTTONS VISIBILITY
   * ===============================
   * Hide/show the × buttons next to judge inputs.
   * Always keep at least one judge (can't remove the last one).
   */
  function updateRemoveButtons() {
    const removeButtons = document.querySelectorAll('.remove-judge-btn');
    removeButtons.forEach(btn => {
      // Show remove buttons only if there's more than one judge
      btn.style.display = judgeCount > 1 ? 'inline-block' : 'none';
    });
  }

  /*
   * CALCULATE AND DISPLAY AVERAGE SCORE
   * ===================================
   * This automatically calculates the average of all judge scores
   * and displays it on the page.
   */
  function updateAverage() {
    // Get all the judge input fields
    const inputs = document.querySelectorAll('.execution-input');
    
    // Get all the scores that have been entered (convert text to numbers)
    const values = Array.from(inputs)
      .map(input => parseFloat(input.value)) // Convert to number
      .filter(val => !isNaN(val)); // Only keep valid numbers

    // Only show average if there are at least 2 scores
    if (values.length > 1) {
      // Calculate the average: add all scores together and divide by count
      const average = values.reduce((sum, val) => sum + val, 0) / values.length;
      
      // Display the average (rounded to 3 decimal places)
      document.getElementById('average-value').textContent = average.toFixed(3);
      document.getElementById('average-display').style.display = 'block';
    } else {
      // Hide the average display if less than 2 scores
      document.getElementById('average-display').style.display = 'none';
    }
  }

  // Set up existing judge inputs to update the average when scores change
  document.querySelectorAll('.execution-input').forEach(input => {
    input.addEventListener('input', updateAverage);
  });
}

/*
 * GLOBAL MODAL CLOSE FUNCTION
 * ===========================
 * This function can be called from HTML onclick attributes
 * to close any modal popup window.
 */
function closeModal() {
  const modal = document.getElementById("competitionModal");
  if (modal) {
    // Remove the "show" class to hide the modal
    modal.classList.remove("show");
  }
}

/*
 * RESULTS PAGE COLUMN TOGGLE FUNCTIONALITY
 * =======================================
 * This allows users to show/hide different columns in the results table
 * by checking/unchecking the checkboxes above the table.
 */
function initializeResultsPage() {
  
  // Find the column toggle checkboxes and the results table
  const toggles = document.querySelectorAll('.column-toggle');
  const table = document.getElementById('resultsTable');

  // Only run this code if we're on the results page (these elements exist)
  if (!toggles.length || !table) return;

  // Set up each checkbox to control column visibility
  toggles.forEach(toggle => {
    toggle.addEventListener('change', function () {
      // Get which column this checkbox controls (e.g., "id", "name", "club")
      const column = this.getAttribute('data-column');
      const isChecked = this.checked;

      // Find all elements with this column's CSS class (headers and data cells)
      const headers = table.querySelectorAll(`.col-${column}`);
      
      // Show or hide the column based on checkbox state
      headers.forEach(header => {
        header.style.display = isChecked ? '' : 'none';
      });
    });
  });
}

