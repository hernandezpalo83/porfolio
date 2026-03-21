document.addEventListener('DOMContentLoaded', () => {
    const circles = document.querySelectorAll('.progress-ring__circle');
    const skillBars = document.querySelectorAll('.skill-bars .progress');

    /** Anima un número desde 0 hasta target en duration ms */
    function animateCounter(el, target, duration) {
        const start = performance.now();
        const step = (now) => {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // ease-out cuadrático
            const eased = 1 - (1 - progress) * (1 - progress);
            el.textContent = Math.round(eased * target);
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }

    if ('IntersectionObserver' in window) {
        // Observer for Metrics Rings + Counters
        const metricsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const circle = entry.target;
                    const radius = circle.r.baseVal.value;
                    const circumference = radius * 2 * Math.PI;
                    const percent = circle.getAttribute('data-percent');

                    const offset = circumference - ((percent / 100) * circumference);

                    circle.style.strokeDasharray = `${circumference} ${circumference}`;
                    circle.style.strokeDashoffset = offset;

                    // Animar el contador numérico del mismo metric-item
                    const metricItem = circle.closest('.metric-item');
                    if (metricItem) {
                        const numEl = metricItem.querySelector('.animate-num');
                        if (numEl) {
                            const target = parseInt(numEl.getAttribute('data-target'), 10);
                            animateCounter(numEl, target, 1200);
                        }
                    }

                    metricsObserver.unobserve(circle);
                }
            });
        }, { threshold: 0.5 });

        circles.forEach(circle => {
            const radius = circle.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            circle.style.strokeDasharray = `${circumference} ${circumference}`;
            circle.style.strokeDashoffset = circumference;
            metricsObserver.observe(circle);
        });

        // Observer for Skill Bars
        const skillsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const percent = bar.getAttribute('data-percent');
                    bar.style.width = percent;
                    skillsObserver.unobserve(bar);
                }
            });
        }, { threshold: 0.1 });

        skillBars.forEach(bar => {
            bar.style.width = '0%';
            skillsObserver.observe(bar);
        });

    } else {
        // Fallback for very old browsers
        circles.forEach(circle => {
            const radius = circle.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            const percent = circle.getAttribute('data-percent');
            const offset = circumference - ((percent / 100) * circumference);
            circle.style.strokeDasharray = `${circumference} ${circumference}`;
            circle.style.strokeDashoffset = offset;
        });

        skillBars.forEach(bar => {
            const percent = bar.getAttribute('data-percent');
            bar.style.width = percent;
        });
    }
});
