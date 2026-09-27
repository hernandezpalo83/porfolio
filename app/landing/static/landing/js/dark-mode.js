/**
 * Dark mode switch. The initial theme is applied by an inline script in
 * <head> (base.html) to avoid a flash; this file wires up the switch.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'hernandezpalo-theme';
  var html = document.documentElement;
  var toggle = document.getElementById('dark-mode-toggle');
  var media = window.matchMedia('(prefers-color-scheme: dark)');

  function readStored() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }

  function currentTheme() {
    return html.getAttribute('data-theme') || readStored() || (media.matches ? 'dark' : 'light');
  }

  function apply(theme, persist) {
    var isDark = theme === 'dark';
    html.setAttribute('data-theme', theme);
    if (persist) {
      try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) { /* storage unavailable */ }
    }
    if (toggle) {
      toggle.setAttribute('aria-checked', isDark ? 'true' : 'false');
      toggle.setAttribute('title', isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
    }
  }

  apply(currentTheme(), false);

  if (toggle) {
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      apply(currentTheme() === 'dark' ? 'light' : 'dark', true);
    });
  }

  var onSystemChange = function (e) {
    if (!readStored()) apply(e.matches ? 'dark' : 'light', false);
  };
  if (media.addEventListener) {
    media.addEventListener('change', onSystemChange);
  } else if (media.addListener) {
    media.addListener(onSystemChange);
  }
})();
