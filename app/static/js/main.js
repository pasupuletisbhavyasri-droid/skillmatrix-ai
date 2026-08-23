document.addEventListener('DOMContentLoaded', function () {
    initThemeToggle();
    initSidebarToggle();
    initBootstrapWidgets();
    initAOS();
    initCountUps();
    hideLoadingScreen();
});

function initAOS() {
    if (window.AOS) {
        AOS.init({ duration: 600, once: true, offset: 60 });
    }
}

function initCountUps() {
    // Any element with data-countup="123" animates its number from 0 -> 123
    // on load — used for stat cards / hero numbers across the dashboard.
    if (!window.countUp || !window.countUp.CountUp) return;
    document.querySelectorAll('[data-countup]').forEach(el => {
        const target = parseFloat(el.getAttribute('data-countup'));
        if (isNaN(target)) return;
        const decimals = el.getAttribute('data-countup-decimals') ? parseInt(el.getAttribute('data-countup-decimals')) : 0;
        const suffix = el.getAttribute('data-countup-suffix') || '';
        const counter = new window.countUp.CountUp(el, target, { duration: 1.4, decimalPlaces: decimals, suffix: suffix });
        if (!counter.error) counter.start();
    });
}

function hideLoadingScreen() {
    const loader = document.getElementById('smx-loading-screen');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('smx-loading-hide');
            setTimeout(() => loader.remove(), 400);
        }, 250);
    }
}

function initThemeToggle() {
    const root = document.getElementById('html-root');
    const toggleButtons = document.querySelectorAll('#theme-toggle');
    const stored = localStorage.getItem('smx-theme');

    if (stored) {
        root.setAttribute('data-bs-theme', stored);
        updateThemeIcon(stored);
    }

    toggleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const current = root.getAttribute('data-bs-theme') || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-bs-theme', next);
            localStorage.setItem('smx-theme', next);
            updateThemeIcon(next);
        });
    });
}

function updateThemeIcon(theme) {
    document.querySelectorAll('#theme-toggle i').forEach(icon => {
        icon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    });
}

function initSidebarToggle() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    if (!sidebar || !toggleBtn) return;

    toggleBtn.addEventListener('click', () => sidebar.classList.toggle('show'));

    document.addEventListener('click', (e) => {
        if (window.innerWidth < 992 &&
            sidebar.classList.contains('show') &&
            !sidebar.contains(e.target) &&
            !toggleBtn.contains(e.target)) {
            sidebar.classList.remove('show');
        }
    });
}

function initBootstrapWidgets() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));
}

function setButtonLoading(button, isLoading, loadingText = 'Please wait...') {
    if (isLoading) {
        button.dataset.originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${loadingText}`;
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}
