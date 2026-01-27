document.addEventListener('DOMContentLoaded', () => {
    const circles = document.querySelectorAll('.progress-ring__circle');

    // Check if the browser supports IntersectionObserver
    // --- Skill Bars Animation (Linear) ---
    const skillBars = document.querySelectorAll('.skill-bars .progress');

    if ('IntersectionObserver' in window) {
        // Observer for Metrics Rings
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
