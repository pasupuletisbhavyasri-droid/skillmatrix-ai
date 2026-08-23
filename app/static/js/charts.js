const SMX_CHART_COLORS = {
    primary: '#4F46E5',
    secondary: '#7C3AED',
    accent: '#06B6D4',
    success: '#16A34A',
    warning: '#F59E0B',
    danger: '#DC2626',
    track: 'rgba(124, 58, 237, 0.08)',
};

function renderScoreRing(canvasId, score, options = {}) {
    const ctx = document.getElementById(canvasId);

    if (!ctx) return null;

    const color = options.color || SMX_CHART_COLORS.secondary;
    const trackColor = options.trackColor || SMX_CHART_COLORS.track;
    const duration = options.animationDuration || 1600;

    score = Number(score) || 0;
    score = Math.max(0, Math.min(100, score));

    return new Chart(ctx, {
        type: 'doughnut',

        data: {
            datasets: [{
                data: [
                    score,
                    100 - score
                ],

                backgroundColor: [
                    color,
                    trackColor
                ],

                borderWidth: 0,

                borderRadius: 12,

                cutout: '78%'
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            rotation: -90,
            circumference: 360,

            animation: {
                animateRotate: true,
                animateScale: true,
                duration: duration,
                easing: 'easeOutCubic'
            },

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    enabled: false
                }
            }
        }
    });
}

function renderSkillGapChart(canvasId, labels, matchedData, missingData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets: [
            { label: 'Matched', data: matchedData, backgroundColor: SMX_CHART_COLORS.success, borderRadius: 6 },
            { label: 'Missing', data: missingData, backgroundColor: SMX_CHART_COLORS.danger, borderRadius: 6 },
        ]},
        options: { indexAxis: 'y', responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { x: { stacked: true, max: 100 }, y: { stacked: true } } },
    });
}

function renderProgressLineChart(canvasId, labels, dataPoints, label = 'Progress') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(79, 70, 229, 0.25)');
    gradient.addColorStop(1, 'rgba(79, 70, 229, 0)');
    return new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: [{ label, data: dataPoints, borderColor: SMX_CHART_COLORS.primary, backgroundColor: gradient, fill: true, tension: 0.35, pointRadius: 3 }] },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100 } } },
    });
}

function renderCareerCompareRadar(canvasId, labels, seriesA, seriesB, nameA, nameB) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: 'radar',
        data: { labels, datasets: [
            { label: nameA, data: seriesA, borderColor: SMX_CHART_COLORS.primary, backgroundColor: 'rgba(79, 70, 229, 0.15)' },
            { label: nameB, data: seriesB, borderColor: SMX_CHART_COLORS.accent, backgroundColor: 'rgba(6, 182, 212, 0.15)' },
        ]},
        options: { responsive: true, scales: { r: { beginAtZero: true, max: 100 } } },
    });
}
