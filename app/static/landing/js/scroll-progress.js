// Scroll progress bar + breadcrumb navigation
class ScrollProgress {
  constructor() {
    this.progressBar = document.getElementById('scroll-progress');
    this.breadcrumbContainer = document.getElementById('scroll-breadcrumbs');
    this.sections = document.querySelectorAll('[id][data-breadcrumb]');

    if (this.progressBar && this.sections.length > 0) {
      this.init();
    }
  }

  init() {
    this.createBreadcrumbs();
    window.addEventListener('scroll', () => this.updateProgress());
    this.updateProgress(); // Initial call
  }

  createBreadcrumbs() {
    if (!this.breadcrumbContainer) return;

    this.breadcrumbContainer.innerHTML = '';

    this.sections.forEach((section, index) => {
      const label = section.getAttribute('data-breadcrumb');
      const id = section.id;

      const crumb = document.createElement('a');
      crumb.href = `#${id}`;
      crumb.className = 'breadcrumb-item';
      crumb.textContent = label;
      crumb.addEventListener('click', (e) => {
        e.preventDefault();
        section.scrollIntoView({ behavior: 'smooth' });
      });

      this.breadcrumbContainer.appendChild(crumb);

      if (index < this.sections.length - 1) {
        const separator = document.createElement('span');
        separator.className = 'breadcrumb-separator';
        separator.textContent = '/';
        this.breadcrumbContainer.appendChild(separator);
      }
    });
  }

  updateProgress() {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrolled = (window.scrollY / docHeight) * 100;

    if (this.progressBar) {
      this.progressBar.style.width = scrolled + '%';
    }

    // Update active breadcrumb
    let currentSection = null;
    this.sections.forEach(section => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= 150) {
        currentSection = section.id;
      }
    });

    document.querySelectorAll('.breadcrumb-item').forEach(crumb => {
      const href = crumb.getAttribute('href').slice(1);
      if (href === currentSection) {
        crumb.classList.add('breadcrumb-item--active');
      } else {
        crumb.classList.remove('breadcrumb-item--active');
      }
    });
  }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new ScrollProgress());
} else {
  new ScrollProgress();
}
