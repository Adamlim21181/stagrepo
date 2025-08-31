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

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("competitionModal");
  const body  = document.getElementById("modalBody");

  // Only run modal code if modal exists (on calendar page)
  if (modal && body) {
    document.querySelectorAll("[data-competition-id]").forEach(el => {
      el.addEventListener("click", () => {
        fetch(`/competition/${el.dataset.competitionId}`)
          .then(r => r.text())
          .then(html => {
            body.innerHTML = html;
            modal.classList.add("show");
          });
      });
    });

    const closeBtn = document.querySelector("#competitionModal .close");
    if (closeBtn) {
      closeBtn.onclick = () => modal.classList.remove("show");
    }
    
    window.onclick = e => { 
      if (e.target === modal) {
        modal.classList.remove("show");
      }
    };
  }
});

// Global function for close button onclick in HTML
function closeModal() {
  const modal = document.getElementById("competitionModal");
  if (modal) {
    modal.classList.remove("show");
  }
}

