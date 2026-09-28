/**
 * main.js - public area (landing, blog, wiki). Vanilla JS, loaded with defer.
 */
(function () {
    'use strict';

    // --- Navigation menu ---
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.getElementById('main-nav-wrap');

    function setMenu(open) {
        if (!toggle || !nav) return;
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
        nav.classList.toggle('is-open', open);
    }

    if (toggle && nav) {
        toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
        nav.addEventListener('click', (e) => {
            if (e.target.closest('a')) setMenu(false);
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
                setMenu(false);
                toggle.focus();
            }
        });
    }

    const hasIO = 'IntersectionObserver' in window;

    // --- ScrollSpy (only in-page anchors) ---
    const spyLinks = nav ? nav.querySelectorAll('a[href^="#"]') : [];
    if (hasIO && spyLinks.length) {
        const spy = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                spyLinks.forEach((a) => {
                    a.parentElement.classList.toggle('current', a.getAttribute('href') === '#' + entry.target.id);
                });
            });
        }, { rootMargin: '-25% 0px -60% 0px' });
        document.querySelectorAll('main section[id]').forEach((s) => spy.observe(s));
    }

    // --- Content reveal (replaces AOS) ---
    const reveal = document.querySelectorAll('[data-reveal]');
    if (hasIO && reveal.length) {
        document.documentElement.classList.add('reveal-ready');
        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-revealed');
                    io.unobserve(entry.target);
                }
            });
        }, { rootMargin: '0px 0px -8% 0px' });
        reveal.forEach((el) => io.observe(el));
    } else {
        reveal.forEach((el) => el.classList.add('is-revealed'));
    }

    // --- Dialogs: [data-dialog-open="id"] opens <dialog id="id">; <form method="dialog"> closes it ---
    document.querySelectorAll('[data-dialog-open]').forEach((btn) => {
        const dialog = document.getElementById(btn.dataset.dialogOpen);
        if (!dialog || typeof dialog.showModal !== 'function') return;
        btn.addEventListener('click', () => dialog.showModal());
        // A click on the backdrop lands on the <dialog> element itself
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) dialog.close();
        });
    });

    // --- Back to top ---
    const goTop = document.getElementById('go-top');
    if (goTop) {
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(() => {
                goTop.classList.toggle('is-visible', window.scrollY > 300);
                ticking = false;
            });
        }, { passive: true });
    }
})();
