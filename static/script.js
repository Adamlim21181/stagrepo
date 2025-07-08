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