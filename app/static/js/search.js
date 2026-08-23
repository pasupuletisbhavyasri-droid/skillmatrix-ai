document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('[data-search-suggest]');
    if (!input) return;

    const resultsBox = document.getElementById('search-suggestions');
    let debounceTimer = null;

    input.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        const query = input.value.trim();
        if (query.length < 2) { hideSuggestions(); return; }
        debounceTimer = setTimeout(() => fetchSuggestions(query), 300);
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && resultsBox && !resultsBox.contains(e.target)) hideSuggestions();
    });

    async function fetchSuggestions(query) {
        try {
            const res = await fetch(`/careers/api/suggest?q=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error('Suggestion request failed');
            const data = await res.json();
            renderSuggestions(data.results || []);
        } catch (err) {
            console.error('Search suggestion error:', err);
            hideSuggestions();
        }
    }

    function renderSuggestions(results) {
        if (!resultsBox) return;
        if (results.length === 0) {
            resultsBox.innerHTML = `<div class="suggestion-empty">No careers found</div>`;
            resultsBox.classList.add('show');
            return;
        }
        resultsBox.innerHTML = results.map(item => `
            <a href="${item.url}" class="suggestion-item">
                <span class="suggestion-title">${escapeHtml(item.title)}</span>
                <span class="suggestion-category">${escapeHtml(item.category)}</span>
            </a>
        `).join('');
        resultsBox.classList.add('show');
    }

    function hideSuggestions() {
        if (resultsBox) resultsBox.classList.remove('show');
    }
});
