/**
 * ============================================
 * TABLE CONTROLLER - COMPLETE EXPLANATION
 * ============================================
 * 
 * This script controls an interactive table with:
 * - Column show/hide toggles
 * - Multi-select filters per column
 * - Sorting (numeric and alphabetical)
 * - Reset functionality
 */

// Wait until the HTML document is fully loaded before running our script
document.addEventListener('DOMContentLoaded', function() {
    // =================================
    // 1. SETUP AND INITIALIZATION
    // =================================
    
    // Get reference to our data table in the HTML
    const table = document.getElementById('data-table');
    
    /**
     * filters object will track active filters like this:
     * {
     *   0: ["value1", "value2"], // Filters for column 0
     *   1: ["valueA"]            // Filters for column 1
     * }
     */
    const filters = {};
    
    /**
     * currentSort tracks which column is sorted and direction:
     * {
     *   column: 2,       // Column index being sorted
     *   direction: "asc" // Sort direction (asc/desc/alpha)
     * }
     */
    let currentSort = { column: null, direction: null };
    
    // =================================
    // 2. COLUMN VISIBILITY SYSTEM
    // =================================
    
    // Find all column toggle buttons in the HTML
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    
    // Loop through each toggle button to set it up
    toggleButtons.forEach(function(button) {
        // Add click event listener to each button
        button.addEventListener('click', function() {
            // Toggle the 'active' class - adds it if missing, removes if present
            this.classList.toggle('active');
            
            // Get which column this button controls from data attribute
            const colIndex = this.dataset.colIndex;
            
            // Check if button is now active (column should be visible)
            const isVisible = this.classList.contains('active');
            
            // Call function to actually show/hide the column
            toggleColumnVisibility(colIndex, isVisible);
        });
    });
    
    /**
     * Shows or hides an entire table column
     * @param {string} colIndex - Which column to toggle (0-based index)
     * @param {boolean} show - true to show, false to hide
     */
    function toggleColumnVisibility(colIndex, show) {
        // Find the table header for this column
        const header = table.querySelector(`th[data-col-index="${colIndex}"]`);
        
        // If header exists, set its display style
        if (header) {
            header.style.display = show ? '' : 'none';
        }
        
        // Find all data cells in this column
        const cells = table.querySelectorAll(`td[data-col-index="${colIndex}"]`);
        
        // Loop through each cell and set visibility
        cells.forEach(function(cell) {
            cell.style.display = show ? '' : 'none';
        });
        
        // If we're hiding the column that's currently sorted...
        if (!show && currentSort.column === parseInt(colIndex)) {
            // Clear the current sort
            resetSort();
        }
    }
    
    // =================================
    // 3. FILTERING SYSTEM SETUP
    // =================================
    
    // Find all filter dropdown menus in the table headers
    const filterSelects = table.querySelectorAll('.column-filter');
    
    // Set up each filter dropdown
    filterSelects.forEach(function(select) {
        // Get which column this filter controls (from data-column attribute)
        const columnIndex = parseInt(select.dataset.column);
        
        // Initialize empty filter array for this column
        filters[columnIndex] = [];
        
        // Add event listener for when selection changes
        select.addEventListener('change', function() {
            // Get all selected options (as array)
            const selectedOptions = Array.from(this.selectedOptions);
            
            // Extract just the values from selected options
            filters[columnIndex] = selectedOptions.map(option => option.value);
            
            // Re-apply filters and sorting with new selections
            applyFiltersAndSort();
        });
    });
    
    // =================================
    // 4. SORTING SYSTEM SETUP
    // =================================
    
    // Find all sort buttons in the table
    const sortButtons = table.querySelectorAll('.sort-btn');
    
    // Set up each sort button
    sortButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Get column index - closest('th') finds the header cell containing this button
            // cellIndex gives us the column number (0-based)
            const columnIndex = this.closest('th').cellIndex;
            
            // Get sort direction from data-sort attribute (asc/desc/alpha)
            const sortType = this.dataset.sort;
            
            // Find all sort buttons in this column and remove 'active' class
            this.closest('.sort-buttons')
                .querySelectorAll('.sort-btn')
                .forEach(btn => btn.classList.remove('active'));
            
            // Mark clicked button as active
            this.classList.add('active');
            
            // Update global sort state
            currentSort = { 
                column: columnIndex, 
                direction: sortType 
            };
            
            // Re-apply filters and sorting
            applyFiltersAndSort();
        });
    });
    
    // =================================
    // 5. RESET FUNCTIONALITY
    // =================================
    
    // Find all reset buttons (except "Reset All")
    const resetButtons = table.querySelectorAll('.reset-btn:not(.reset-all)');
    
    // Set up individual column reset buttons
    resetButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Get column index from parent header
            const columnIndex = this.closest('th').cellIndex;
            
            // Call reset function for this column
            resetColumn(columnIndex);
        });
    });
    
    // Set up "Reset All" button
    document.querySelector('.reset-all').addEventListener('click', function() {
        // Reset all filter dropdowns
        table.querySelectorAll('.column-filter').forEach(function(select) {
            // Unselect all options
            select.querySelectorAll('option').forEach(option => {
                option.selected = false;
            });
        });
        
        // Reset all column visibility toggles
        document.querySelectorAll('.toggle-btn').forEach(function(btn) {
            if (!btn.classList.contains('active')) {
                btn.classList.add('active');
                toggleColumnVisibility(btn.dataset.colIndex, true);
            }
        });
        
        // Reset sorting
        resetSort();
        
        // Re-apply filters/sorting (will show all data in original order)
        applyFiltersAndSort();
    });
    
    /**
     * Resets a single column's filter and sort state
     * @param {number} columnIndex - Index of column to reset (0-based)
     */
    function resetColumn(columnIndex) {
        // Find filter dropdown for this column
        const select = table.querySelector(`.column-filter[data-column="${columnIndex}"]`);
        
        // If dropdown exists, clear selections
        if (select) {
            select.querySelectorAll('option').forEach(option => {
                option.selected = false;
            });
            
            // Clear filter for this column
            filters[columnIndex] = [];
        }
        
        // Find all sort buttons in this column
        const sortButtons = table.querySelectorAll('th')[columnIndex]
                          .querySelectorAll('.sort-btn');
        
        // Remove active class from all sort buttons
        sortButtons.forEach(btn => btn.classList.remove('active'));
        
        // If this column was being sorted, clear sort state
        if (currentSort.column === columnIndex) {
            resetSort();
        }
    }
    
    /**
     * Clears the current sort state
     */
    function resetSort() {
        currentSort = { column: null, direction: null };
    }
    
    // =================================
    // 6. CORE FILTER/SORT LOGIC
    // =================================
    
    /**
     * Main function that applies all active filters and sorting
     * This does the heavy lifting of actually modifying the table
     */
    function applyFiltersAndSort() {
        // Get all table rows (convert NodeList to Array for easier manipulation)
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        
        // ======================
        // A. APPLY FILTERS
        // ======================
        rows.forEach(function(row) {
            // Start by assuming row should be visible
            let shouldShow = true;
            
            // Check against all active filters
            for (const [columnIndex, filterValues] of Object.entries(filters)) {
                // Skip if no filters for this column
                if (filterValues && filterValues.length > 0) {
                    // Get cell value for this column
                    const cellValue = row.cells[columnIndex].textContent.trim();
                    
                    // If cell value isn't in filter values, hide row
                    if (!filterValues.includes(cellValue)) {
                        shouldShow = false;
                        break; // No need to check other filters
                    }
                }
            }
            
            // Set row visibility
            row.style.display = shouldShow ? '' : 'none';
        });
        
        // ======================
        // B. APPLY SORTING
        // ======================
        if (currentSort.column !== null && currentSort.direction !== null) {
            // Get only visible rows after filtering
            const visibleRows = rows.filter(row => row.style.display !== 'none');
            
            // Get sort type (numeric or alpha) from column header
            const sortType = table.querySelectorAll('th')[currentSort.column].dataset.sortType;
            
            // Sort the visible rows
            visibleRows.sort(function(a, b) {
                // Get values from the cells we're sorting by
                const aValue = a.cells[currentSort.column].textContent.trim();
                const bValue = b.cells[currentSort.column].textContent.trim();
                
                // Numeric sorting (for Execution, Difficulty, etc.)
                if (sortType === 'numeric') {
                    // Convert to numbers
                    const aNum = parseFloat(aValue);
                    const bNum = parseFloat(bValue);
                    
                    // Handle ascending/descending order
                    if (currentSort.direction === 'asc') {
                        return aNum - bNum; // Lower numbers first
                    } else {
                        return bNum - aNum; // Higher numbers first
                    }
                }
                // Text sorting (for Name, Club, etc.)
                else {
                    // Use localeCompare for proper string comparison
                    return aValue.localeCompare(bValue);
                }
            });
            
            // ======================
            // C. REBUILD TABLE
            // ======================
            
            // Get reference to table body
            const tbody = table.querySelector('tbody');
            
            // First remove all existing rows
            while (tbody.firstChild) {
                tbody.removeChild(tbody.firstChild);
            }
            
            // Add back sorted rows
            visibleRows.forEach(function(row) {
                tbody.appendChild(row);
            });
        }
    }
});

  