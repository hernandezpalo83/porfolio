/**
 * main.js - HernandezPalo Portfolio
 * Refactored to Vanilla JS (No jQuery) - Performance Optimized
 */

document.addEventListener('DOMContentLoaded', () => {
    'use strict';

    // --- 2. Navigation Menu ---
    const toggleButton = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.main-navigation');
    const navLinks = document.querySelectorAll('.main-navigation li a');

    if (toggleButton && nav) {
        toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            toggleButton.classList.toggle('is-clicked');

            if (nav.style.display === 'block') {
                nav.style.display = 'none';
            } else {
                nav.style.display = 'block';
            }
        });

        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.getComputedStyle(toggleButton).display !== 'none') {
                    toggleButton.classList.remove('is-clicked');
                    nav.style.display = 'none';
                }
            });
        });
    }

    // --- 3. Highlight Current Section (ScrollSpy) ---
    const sections = document.querySelectorAll('section');
    const navItems = document.querySelectorAll('#main-nav-wrap li a');

    const observerOptions = {
        root: null,
        rootMargin: '-25% 0px -25% 0px', // Offset match
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                const activeLink = document.querySelector(`#main-nav-wrap a[href="#${id}"]`);

                navItems.forEach(item => item.parentElement.classList.remove('current'));
                if (activeLink) {
                    activeLink.parentElement.classList.add('current');
                }
            }
        });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));

    // --- 4. Smooth Scrolling ---
    const smoothScrollLinks = document.querySelectorAll('.smoothscroll');

    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                history.pushState(null, null, targetId);
            }
        });
    });

    // --- 5. Back to Top ---
    const goTopBtn = document.getElementById('go-top');
    const pxShow = 300;

    window.addEventListener('scroll', () => {
        if (!goTopBtn) return;

        if (window.scrollY >= pxShow) {
            goTopBtn.style.display = 'block';
            // Simple fade in effect via CSS transition is recommended, but basic display works
            goTopBtn.style.opacity = '1';
        } else {
            goTopBtn.style.opacity = '0';
            setTimeout(() => {
                if (window.scrollY < pxShow) goTopBtn.style.display = 'none';
            }, 400);
        }
    }, { passive: true });
});