// Portfolio filtering: by technology, category, and search
class PortfolioFilters {
  constructor() {
    this.projects = document.querySelectorAll('[data-portfolio-item]');
    this.filterContainer = document.getElementById('portfolio-filters');
    this.searchInput = document.getElementById('portfolio-search');

    if (this.projects.length > 0) {
      this.init();
    }
  }

  init() {
    // Extract unique technologies
    const techs = new Set();
    this.projects.forEach(project => {
      const techStr = project.getAttribute('data-tech') || '';
      techStr.split(',').forEach(tech => {
        const trimmed = tech.trim().toLowerCase();
        if (trimmed) techs.add(trimmed);
      });
    });

    // Create filter buttons
    if (this.filterContainer) {
      const allBtn = document.createElement('button');
      allBtn.className = 'filter-btn filter-btn--active';
      allBtn.textContent = 'Todos';
      allBtn.dataset.filter = 'all';
      this.filterContainer.appendChild(allBtn);

      techs.forEach(tech => {
        const btn = document.createElement('button');
        btn.className = 'filter-btn';
        btn.textContent = tech.charAt(0).toUpperCase() + tech.slice(1);
        btn.dataset.filter = tech;
        this.filterContainer.appendChild(btn);
      });

      // Event listeners
      this.filterContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('filter-btn')) {
          this.handleFilter(e.target);
        }
      });
    }

    // Search input listener
    if (this.searchInput) {
      this.searchInput.addEventListener('input', (e) => {
        this.handleSearch(e.target.value.toLowerCase());
      });
    }
  }

  handleFilter(btn) {
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('filter-btn--active'));
    btn.classList.add('filter-btn--active');

    const filter = btn.dataset.filter;
    this.filterProjects(filter, this.searchInput?.value || '');
  }

  handleSearch(query) {
    const activeFilter = document.querySelector('.filter-btn--active');
    const filter = activeFilter?.dataset.filter || 'all';
    this.filterProjects(filter, query);
  }

  filterProjects(tech, query) {
    this.projects.forEach(project => {
      const projectTechs = (project.getAttribute('data-tech') || '').toLowerCase().split(',').map(t => t.trim());
      const title = (project.getAttribute('data-title') || '').toLowerCase();
      const description = (project.getAttribute('data-description') || '').toLowerCase();

      const matchesTech = tech === 'all' || projectTechs.some(t => t.includes(tech));
      const matchesQuery = !query || title.includes(query) || description.includes(query);
      const shouldShow = matchesTech && matchesQuery;

      // Animate
      if (shouldShow) {
        project.style.display = '';
        setTimeout(() => project.classList.add('fade-in'), 10);
        project.classList.remove('fade-out');
      } else {
        project.classList.add('fade-out');
        setTimeout(() => {
          project.style.display = 'none';
        }, 200);
      }
    });
  }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new PortfolioFilters());
} else {
  new PortfolioFilters();
}
