/**
 * Dark Mode Toggle System
 * Maneja tema oscuro/claro con localStorage y CSS variables
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'hernandezpalo-theme';
  const DARK_CLASS = 'dark-mode';
  const html = document.documentElement;
  const toggle = document.getElementById('dark-mode-toggle');

  /**
   * Detecta tema preferido del sistema
   */
  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  /**
   * Obtiene tema actual: localStorage > sistema
   */
  function getTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored || getSystemTheme();
  }

  /**
   * Aplica tema al DOM y localStorage
   */
  function setTheme(theme) {
    const isDark = theme === 'dark';
    html.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    updateToggleIcon(isDark);
  }

  /**
   * Actualiza icono del botón
   */
  function updateToggleIcon(isDark) {
    if (toggle) {
      toggle.textContent = isDark ? '☀️' : '🌙';
      toggle.setAttribute('title', isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
    }
  }

  /**
   * Alterna tema
   */
  function toggleTheme() {
    const current = getTheme();
    const next = current === 'dark' ? 'light' : 'dark';
    setTheme(next);
  }

  // Aplicar tema al cargar
  setTheme(getTheme());

  // Event listener del toggle
  if (toggle) {
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      toggleTheme();
    });
  }

  // Sincronizar si el sistema cambia de tema (cuando está en auto)
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem(STORAGE_KEY)) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });
})();
