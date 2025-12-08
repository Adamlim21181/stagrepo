
/*
 * MAIN JAVASCRIPT - STAG COMPETE
 * ==============================
 * All interactive functionality for the gymnastics competition management system.
 * Includes modal systems, search functionality, dynamic scoring, and results filtering.
 */
/*
 * MODAL SYSTEM FOR COMPETITION DETAILS
 * ====================================
 */
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("competitionModal");
  const body  = document.getElementById("modalBody");

  if (modal && body) {
    // Ensure modal is hidden on page load
    modal.classList.remove("show");
    modal.style.display = "none";
    document.body.classList.remove("modal-open");
    
    document.querySelectorAll("[data-competition-id]").forEach(el => {
      el.addEventListener("click", () => {
        fetch(`/competition/${el.dataset.competitionId}`)
          .then(r => r.text())
          .then(html => {
            body.innerHTML = html;
            modal.classList.add("show");
            document.body.classList.add("modal-open");
          });
      });
    });

    const closeBtn = document.querySelector("#competitionModal .close");
    if (closeBtn) {
      closeBtn.onclick = () => {
        modal.classList.remove("show");
        document.body.classList.remove("modal-open");
      };
    }
    
    window.onclick = e => { 
      if (e.target === modal) {
        modal.classList.remove("show");
        document.body.classList.remove("modal-open");
      }
    };
  }

  initializeEntriesPage();
  initializeScoringPage();
  initializeResultsPage();
});

/*
 * ENTRIES PAGE GYMNAST SEARCH
 * ===========================
 * Provides a simple search functionality for the entries page that filters gymnast options
 * in the dropdown as the user types. Searches through name, club, and level information
 * and automatically selects the only match when search narrows down to one result.
 */
function initializeEntriesPage() {
  const gymnastSearch = document.getElementById('gymnast_search');
  const gymnastSelect = document.getElementById('gymnast_id');
  
  if (!gymnastSearch || !gymnastSelect) return;
  
  gymnastSearch.addEventListener('input', function () {
    const searchTerm = this.value.toLowerCase();
    const options = gymnastSelect.getElementsByTagName('option');

    for (let i = 1; i < options.length; i++) {
      const option = options[i];
      const name = option.getAttribute('data-name') || '';
      const club = option.getAttribute('data-club') || '';
      const level = option.getAttribute('data-level') || '';
      const text = option.textContent.toLowerCase();

      if (text.includes(searchTerm) || name.includes(searchTerm) ||
          club.includes(searchTerm) || level.includes(searchTerm)) {
        option.style.display = '';
      } else {
        option.style.display = 'none';
      }
    }

    const visibleOptions = Array.from(options).filter(opt => opt.style.display !== 'none' && opt.value !== '');
    if (searchTerm && visibleOptions.length === 1) {
      gymnastSelect.value = visibleOptions[0].value;
    }
  });

  gymnastSelect.addEventListener('change', function () {
    if (this.value) {
      gymnastSearch.value = '';
    }
  });
}

/*
 * SCORING PAGE JUDGE MANAGEMENT
 * =============================
 * Allows judges to be dynamically added and removed on the scoring page with automatic
 * average calculation. Maintains proper numbering when judges are removed and provides
 * real-time score averaging with a minimum of 2 judges required for display.
 */
function initializeScoringPage() {
  const addJudgeBtn = document.getElementById('add-judge-btn');
  
  if (!addJudgeBtn) return;
  
  let judgeCount = 1;
  const maxJudges = 6;

  addJudgeBtn.addEventListener('click', function () {
    if (judgeCount < maxJudges) {
      judgeCount++;
      addJudgeInput();
      updateRemoveButtons();
      updateAverage();
    }
  });

  function addJudgeInput() {
    const container = document.getElementById('execution-scores-container');
    
    const newRow = document.createElement('div');
    newRow.className = 'execution-score-row';
    newRow.setAttribute('data-judge', judgeCount);

    newRow.innerHTML = `
      <div class="judge-label">Judge ${judgeCount}:</div>
      <input type="number" name="execution_scores" step="0.001" min="0" max="10" 
             placeholder="8.5" required class="execution-input">
      <button type="button" class="remove-judge-btn">×</button>
    `;

    container.appendChild(newRow);

    newRow.querySelector('.remove-judge-btn').addEventListener('click', function () {
      removeJudgeInput(newRow);
    });

    newRow.querySelector('.execution-input').addEventListener('input', updateAverage);
  }

  function removeJudgeInput(row) {
    row.remove();
    judgeCount--;
    updateJudgeLabels();
    updateRemoveButtons();
    updateAverage();
  }

  function updateJudgeLabels() {
    const rows = document.querySelectorAll('.execution-score-row');
    rows.forEach((row, index) => {
      row.querySelector('.judge-label').textContent = `Judge ${index + 1}:`;
      row.setAttribute('data-judge', index + 1);
    });
  }

  function updateRemoveButtons() {
    const removeButtons = document.querySelectorAll('.remove-judge-btn');
    removeButtons.forEach(btn => {
      btn.style.display = judgeCount > 1 ? 'inline-block' : 'none';
    });
  }

  function updateAverage() {
    const inputs = document.querySelectorAll('.execution-input');
    
    const values = Array.from(inputs)
      .map(input => parseFloat(input.value))
      .filter(val => !isNaN(val));

    if (values.length > 1) {
      const average = values.reduce((sum, val) => sum + val, 0) / values.length;
      
      document.getElementById('average-value').textContent = average.toFixed(3);
      document.getElementById('average-display').style.display = 'block';
    } else {
      document.getElementById('average-display').style.display = 'none';
    }
  }

  document.querySelectorAll('.execution-input').forEach(input => {
    input.addEventListener('input', updateAverage);
  });
}

/*
 * GLOBAL MODAL UTILITY
 * ====================
 * Provides a globally accessible function for closing modal popups, typically called
 * from HTML onclick attributes for modal close buttons and overlay backgrounds.
 */
function closeModal() {
  const modal = document.getElementById("competitionModal");
  if (modal) {
    modal.classList.remove("show");
    document.body.classList.remove("modal-open");
  }
}

/*
 * RESULTS PAGE COLUMN VISIBILITY
 * ==============================
 * Enables dynamic showing/hiding of table columns in the results view through checkbox
 * controls. Allows users to customize which data columns are displayed for better
 * viewing experience and reduced visual clutter.
 */
function initializeResultsPage() {
  const toggles = document.querySelectorAll('.column-toggle');
  const table = document.getElementById('resultsTable');

  if (!toggles.length || !table) return;

  toggles.forEach(toggle => {
    toggle.addEventListener('change', function () {
      const column = this.getAttribute('data-column');
      const isChecked = this.checked;

      const headers = table.querySelectorAll(`.col-${column}`);
      
      headers.forEach(header => {
        header.style.display = isChecked ? '' : 'none';
      });
    });
  });
}

/*
 * ADVANCED SEARCHABLE GYMNAST SELECTOR
 * ====================================
 * Implements a sophisticated search interface for the entries page that replaces the
 * standard dropdown with a searchable input field. Features include real-time filtering,
 * keyboard navigation, ID-based search, exact matching validation, and visual feedback.
 * Handles both name searches and numeric ID lookups with intelligent result prioritization.
 */
function initSearchableSelect() {
  const searchInput = document.getElementById('gymnast_search');
  const dropdown = document.getElementById('gymnast-dropdown');
  const gymnastsDataScript = document.getElementById('gymnasts-data');
  
  if (!searchInput || !dropdown || !gymnastsDataScript) {
    return;
  }

  let gymnasts = [];
  try {
    const rawData = JSON.parse(gymnastsDataScript.textContent);
    
    gymnasts = rawData.map(gymnast => ({
      id: gymnast.id,
      name: gymnast.name,
      club: gymnast.clubs.name,
      level: gymnast.level,
      display: `#${gymnast.id.toString().padStart(3, '0')} - ${gymnast.name} - ${gymnast.clubs.name} (${gymnast.level})`
    }));
  } catch (e) {
    console.error('Failed to parse gymnasts data:', e);
    return;
  }

  let selectedGymnastId = null;
  let currentHighlight = -1;
  let currentResults = [];

  function showDropdown(items) {
    dropdown.innerHTML = '';
    dropdown.style.display = 'block';
    currentResults = items;
    currentHighlight = -1;

    if (items.length === 0) {
      const noResults = document.createElement('div');
      noResults.className = 'dropdown-item no-results';
      noResults.textContent = 'No gymnasts found';
      dropdown.appendChild(noResults);
      return;
    }

    items.slice(0, 10).forEach((gymnast, index) => {
      const item = document.createElement('div');
      item.className = 'dropdown-item';
      item.textContent = gymnast.display;
      item.setAttribute('data-index', index);
      item.onclick = () => selectGymnast(gymnast);
      dropdown.appendChild(item);
    });
  }

  function hideDropdown() {
    setTimeout(() => {
      dropdown.style.display = 'none';
      currentHighlight = -1;
    }, 200);
  }

  function selectGymnast(gymnast) {
    searchInput.value = gymnast.name;
    selectedGymnastId = gymnast.id;
    dropdown.style.display = 'none';
    currentHighlight = -1;

    searchInput.style.borderColor = 'var(--success-color)';
    setTimeout(() => {
      searchInput.style.borderColor = '';
    }, 1000);
  }

  function highlightItem(index) {
    const items = dropdown.querySelectorAll('.dropdown-item:not(.no-results)');
    items.forEach((item, i) => {
      item.classList.toggle('active', i === index);
    });
    currentHighlight = index;
  }

  function searchGymnasts(query) {
    if (!query) return [];

    query = query.toLowerCase();
    
    const isNumericQuery = /^\d+$/.test(query.trim());
    
    return gymnasts.filter(gymnast => {
      const nameMatch = gymnast.name.toLowerCase().includes(query);
      const clubMatch = gymnast.club.toLowerCase().includes(query);
      const levelMatch = gymnast.level.toLowerCase().includes(query);
      
      let idMatch = false;
      if (isNumericQuery) {
        const queryNum = parseInt(query);
        idMatch = gymnast.id === queryNum;
      }
      
      return nameMatch || clubMatch || levelMatch || idMatch;
    }).sort((a, b) => {
      const aIdMatch = isNumericQuery && a.id === parseInt(query);
      const bIdMatch = isNumericQuery && b.id === parseInt(query);
      const aNameMatch = a.name.toLowerCase().includes(query);
      const bNameMatch = b.name.toLowerCase().includes(query);
      
      if (aIdMatch && !bIdMatch) return -1;
      if (!aIdMatch && bIdMatch) return 1;
      if (aNameMatch && !bNameMatch) return -1;
      if (!aNameMatch && bNameMatch) return 1;
      return a.name.localeCompare(b.name);
    });
  }

  searchInput.addEventListener('input', function () {
    const query = this.value.trim();
    
    selectedGymnastId = null;
    this.style.borderColor = '';

    if (query.length >= 1) {
      const results = searchGymnasts(query);
      showDropdown(results);
    } else {
      hideDropdown();
    }
  });

  searchInput.addEventListener('keydown', function (e) {
    const items = dropdown.querySelectorAll('.dropdown-item:not(.no-results)');

    if (dropdown.style.display === 'none' || items.length === 0) {
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        currentHighlight = Math.min(currentHighlight + 1, items.length - 1);
        highlightItem(currentHighlight);
        break;

      case 'ArrowUp':
        e.preventDefault();
        currentHighlight = Math.max(currentHighlight - 1, -1);
        if (currentHighlight === -1) {
          items.forEach(item => item.classList.remove('active'));
        } else {
          highlightItem(currentHighlight);
        }
        break;

      case 'Enter':
        e.preventDefault();
        if (currentHighlight >= 0 && currentResults[currentHighlight]) {
          selectGymnast(currentResults[currentHighlight]);
        }
        break;

      case 'Escape':
        hideDropdown();
        break;
    }
  });

  searchInput.addEventListener('focus', function () {
    const query = this.value.trim();
    if (query.length >= 1) {
      const results = searchGymnasts(query);
      showDropdown(results);
    }
  });

  searchInput.addEventListener('blur', hideDropdown);

  const form = searchInput.closest('form');
  form.addEventListener('submit', function (e) {
    const query = searchInput.value.trim();

    if (!query) {
      e.preventDefault();
      searchInput.focus();
      searchInput.style.borderColor = 'var(--error-color)';
      alert('Please enter a gymnast name.');
      return false;
    }

    const exactMatch = gymnasts.find(gymnast =>
      gymnast.name.toLowerCase() === query.toLowerCase()
    );

    if (!exactMatch) {
      e.preventDefault();
      searchInput.focus();
      searchInput.style.borderColor = 'var(--error-color)';

      const partialMatches = searchGymnasts(query);
      if (partialMatches.length > 0) {
        const suggestions = partialMatches.slice(0, 3).map(g => g.name).join(', ');
        alert(`Gymnast "${query}" not found. Did you mean: ${suggestions}?`);
        showDropdown(partialMatches);
      } else {
        alert('No gymnast found with that name. Please check the spelling or add the gymnast first.');
      }
      return false;
    }

    selectedGymnastId = exactMatch.id;
  });
}

document.addEventListener('DOMContentLoaded', initSearchableSelect);

/*
 * MOBILE NAVIGATION TOGGLE
 * ========================
 */
function toggleMobileMenu() {
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileToggle = document.getElementById('mobileMenuToggle');
  
  if (mobileMenu) {
    mobileMenu.classList.toggle('active');
  }
  
  if (mobileToggle) {
    mobileToggle.classList.toggle('active');
  }
  
  // lock body scroll when menu open
  if (mobileMenu && mobileMenu.classList.contains('active')) {
    document.body.classList.add('menu-open');
  } else {
    document.body.classList.remove('menu-open');
  }
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileToggle = document.getElementById('mobileMenuToggle');
  
  if (mobileMenu && mobileToggle) {
    if (!mobileToggle.contains(event.target) && !mobileMenu.contains(event.target)) {
      mobileMenu.classList.remove('active');
      mobileToggle.classList.remove('active');
      document.body.classList.remove('menu-open');
    }
  }
});

// Close mobile menu when window is resized to desktop
window.addEventListener('resize', function() {
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileToggle = document.getElementById('mobileMenuToggle');
  
  if (window.innerWidth > 768 && mobileMenu && mobileToggle) {
    mobileMenu.classList.remove('active');
    mobileToggle.classList.remove('active');
    document.body.classList.remove('menu-open');
  }
});
