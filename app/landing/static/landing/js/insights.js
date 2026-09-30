/**
 * insights.js - anonymous reading metrics and events for the site's own analytics
 * (no cookies, no third parties). Sends to /a/beacon/ with navigator.sendBeacon:
 *  - active reading time (tab visible) and maximum scroll of the page;
 *  - CV downloads, clicks to external sites, case studies opened, project filters.
 * Also removes ?src= / utm_* from the address bar so shared links do not carry them.
 */
(function () {
    'use strict';

    var ENDPOINT = '/a/beacon/';
    var pageview = document.body.getAttribute('data-pv');

    function send(payload) {
        var body = JSON.stringify(payload);
        try {
            if (navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, new Blob([body], { type: 'text/plain' }))) return;
            fetch(ENDPOINT, { method: 'POST', body: body, keepalive: true, headers: { 'Content-Type': 'text/plain' } });
        } catch (e) { /* analytics must never break the page */ }
    }

    // --- Clean tracking parameters from the visible URL ---
    try {
        var url = new URL(window.location.href);
        var tracking = ['src', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
        var changed = false;
        tracking.forEach(function (key) {
            if (url.searchParams.has(key)) { url.searchParams.delete(key); changed = true; }
        });
        if (changed) history.replaceState(history.state, '', url.pathname + url.search + url.hash);
    } catch (e) { /* old browsers */ }

    // --- Reading time (only while the tab is visible) and scroll depth ---
    var active = 0;
    var since = Date.now();
    var visible = !document.hidden;
    var maxScroll = 0;
    var sent = { t: -1, s: -1 };

    function tick() {
        var now = Date.now();
        if (visible) active += now - since;
        since = now;
    }

    function measureScroll() {
        var doc = document.documentElement;
        var scrollable = doc.scrollHeight - window.innerHeight;
        var pct = scrollable > 0 ? Math.round((window.scrollY / scrollable) * 100) : 100;
        if (pct > maxScroll) maxScroll = Math.min(100, pct);
    }

    function flush() {
        tick();
        var seconds = Math.round(active / 1000);
        if (!pageview || (seconds === sent.t && maxScroll === sent.s)) return;
        sent = { t: seconds, s: maxScroll };
        send({ type: 'read', pv: pageview, t: seconds, s: maxScroll });
    }

    var scrollTicking = false;
    window.addEventListener('scroll', function () {
        if (scrollTicking) return;
        scrollTicking = true;
        requestAnimationFrame(function () { measureScroll(); scrollTicking = false; });
    }, { passive: true });

    document.addEventListener('visibilitychange', function () {
        tick();
        visible = !document.hidden;
        if (document.hidden) flush();
    });
    window.addEventListener('pagehide', flush);
    measureScroll();

    // --- Events ---
    function event(kind, label) {
        send({ type: 'event', kind: kind, label: (label || '').trim().slice(0, 200), path: window.location.pathname });
    }

    document.addEventListener('click', function (e) {
        var target = e.target.closest('[data-track], [data-dialog-open], [data-filter], a[href]');
        if (!target) return;

        if (target.hasAttribute('data-track')) {
            event(target.getAttribute('data-track'), target.getAttribute('data-track-label') || target.textContent);
        } else if (target.hasAttribute('data-dialog-open')) {
            var card = target.closest('.pf-card');
            var title = card && card.querySelector('.pf-title');
            event('case_open', title ? title.textContent : target.getAttribute('data-dialog-open'));
        } else if (target.hasAttribute('data-filter')) {
            event('filter_use', target.getAttribute('data-label') || 'Todos');
        } else if (target.hostname && target.hostname !== window.location.hostname && /^https?:$/.test(target.protocol)) {
            var host = target.hostname.replace(/^www\./, '');
            var text = (target.getAttribute('aria-label') || target.textContent || '').replace(/\s+/g, ' ').trim();
            event('outbound_click', text ? host + ' · ' + text : host);
        }
    }, true);
})();
