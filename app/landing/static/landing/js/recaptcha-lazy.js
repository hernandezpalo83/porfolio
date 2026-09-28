/**
 * Lazy reCAPTCHA v3 (see landing.forms.LazyReCaptchaV3): Google's script is only
 * downloaded when the form gets close, focused or submitted. Kept as a static
 * file so the strict CSP needs no inline script.
 */
(function () {
    'use strict';

    document.querySelectorAll('input[data-recaptcha-lazy]').forEach(function (field) {
        var form = field.form;
        if (!form) return;
        var loading = null;

        function load() {
            if (loading) return loading;
            loading = new Promise(function (resolve, reject) {
                var s = document.createElement('script');
                s.src = field.dataset.recaptchaSrc;
                s.async = true;
                s.onload = function () { window.grecaptcha.ready(resolve); };
                s.onerror = reject;
                document.head.appendChild(s);
            });
            return loading;
        }

        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                if (entries[0].isIntersecting) { load(); io.disconnect(); }
            }, { rootMargin: '600px 0px' });
            io.observe(form);
        }
        form.addEventListener('focusin', load, { once: true });

        form.addEventListener('submit', function (event) {
            event.preventDefault();
            var button = form.querySelector('[type="submit"]');
            if (button) button.disabled = true;
            var action = field.dataset.recaptchaAction;
            load().then(function () {
                return window.grecaptcha.execute(field.dataset.recaptchaKey, action ? { action: action } : {});
            }).then(function (token) {
                field.value = token;
                form.submit();
            }).catch(function () {
                if (button) button.disabled = false;
            });
        });
    });
})();
