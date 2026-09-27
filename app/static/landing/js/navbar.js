// Navbar inteligente: sticky + collapse dinámico en scroll
class SmartNavbar {
  constructor() {
    this.navbar = document.querySelector('header.navbar-header');
    this.lastScrollY = 0;
    this.isHidden = false;
    this.scrollThreshold = 50;

    if (this.navbar) {
      this.init();
    }
  }

  init() {
    window.addEventListener('scroll', () => this.handleScroll());
    window.addEventListener('click', (e) => this.handleNavClick(e));
  }

  handleScroll() {
    const currentScrollY = window.scrollY;
    const scrollDelta = currentScrollY - this.lastScrollY;

    if (currentScrollY < this.scrollThreshold) {
      this.navbar.classList.remove('navbar-hidden');
      this.isHidden = false;
    } else if (scrollDelta > 5 && !this.isHidden) {
      // Scroll DOWN: hide navbar
      this.navbar.classList.add('navbar-hidden');
      this.isHidden = true;
    } else if (scrollDelta < -5 && this.isHidden) {
      // Scroll UP: show navbar
      this.navbar.classList.remove('navbar-hidden');
      this.isHidden = false;
    }

    this.lastScrollY = currentScrollY;
  }

  handleNavClick(e) {
    // Close mobile menu on link click
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('nav');

    if (navToggle && navLinks.classList.contains('nav-active')) {
      const target = e.target.closest('a[href^="#"]');
      if (target) {
        navToggle.click();
      }
    }

    // Update active nav indicator
    this.updateActiveSection();
  }

  updateActiveSection() {
    const sections = document.querySelectorAll('[id]');
    const navLinks = document.querySelectorAll('nav a[href^="#"]');

    let currentSection = null;

    sections.forEach(section => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= 100 && rect.bottom >= 0) {
        currentSection = section.id;
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('nav-active');
      if (currentSection && link.getAttribute('href') === `#${currentSection}`) {
        link.classList.add('nav-active');
      }
    });
  }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new SmartNavbar());
} else {
  new SmartNavbar();
}
