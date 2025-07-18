function showCompetitionModal(competitionId) {
    const modal = document.getElementById('competitionModal');
    
    // Show modal and add show class for animations
    modal.style.display = 'block';
    // Force a reflow to ensure the display change is processed
    modal.offsetHeight;
    // Add the show class to trigger opacity and transform transitions
    modal.classList.add('show');
      
    // Fetch competition details
    fetch(`/competition/${competitionId}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('modalBody').innerHTML = html;
        })
        .catch(error => {
            document.getElementById('modalBody').innerHTML = '<p>Error loading competition details.</p>';
        });
}

function closeModal() {
    const modal = document.getElementById('competitionModal');
    
    // Remove show class to trigger fade out
    modal.classList.remove('show');
    
    // Wait for transition to complete before hiding
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300); // Match the transition duration
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('competitionModal');
    if (event.target == modal) {
        closeModal();
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Column visibility functionality for results table
document.addEventListener('DOMContentLoaded', function() {
    // Login page body overflow fix
    const loginPage = document.querySelector('.login-page');
    if (loginPage) {
        document.body.classList.add('login-body');
        document.body.style.overflow = 'hidden';
        document.body.style.height = '100vh';
        document.body.style.margin = '0';
        document.body.style.padding = '0';
        
        // Prevent scrolling on touch devices
        document.addEventListener('touchmove', function(e) {
            e.preventDefault();
        }, { passive: false });
        
        // Prevent scroll on wheel/keyboard
        document.addEventListener('wheel', function(e) {
            e.preventDefault();
        }, { passive: false });
        
        document.addEventListener('keydown', function(e) {
            // Prevent arrow keys, page up/down, home/end, space from scrolling
            if([32, 33, 34, 35, 36, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
                e.preventDefault();
            }
        });
    }
    
    // Get all column toggle checkboxes
    const columnToggles = document.querySelectorAll('.column-toggle');
    
    // Add event listeners to each checkbox
    columnToggles.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const columnName = this.getAttribute('data-column');
            const isChecked = this.checked;
            
            // Find all elements with the corresponding column class
            const columnElements = document.querySelectorAll(`.col-${columnName}`);
            
            // Show or hide the column elements
            columnElements.forEach(function(element) {
                if (isChecked) {
                    element.style.display = '';
                } else {
                    element.style.display = 'none';
                }
            });
        });
    });
    
    // Initialize column visibility based on checkbox states
    columnToggles.forEach(function(checkbox) {
        const columnName = checkbox.getAttribute('data-column');
        const isChecked = checkbox.checked;
        const columnElements = document.querySelectorAll(`.col-${columnName}`);
        
        columnElements.forEach(function(element) {
            if (isChecked) {
                element.style.display = '';
            } else {
                element.style.display = 'none';
            }
        });
    });
});