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

/*Hiding columns */
document.addEventListener('DOMContentLoaded', function() {
  const toggles = document.querySelectorAll('.column-toggle');
  
  toggles.forEach(toggle => {
      toggle.addEventListener('change', function() {
          const columnClass = 'col-' + this.dataset.column;
          const elements = document.querySelectorAll('.' + columnClass);
          const isVisible = this.checked;
          
          elements.forEach(el => {
              el.style.display = isVisible ? '' : 'none';
          });
      });
  });
});

function showCompetitionModal(competitionId) {
    document.getElementById('competitionModal').style.display = 'block';
      
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
    document.getElementById('competitionModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('competitionModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});