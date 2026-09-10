document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const clearBtn = document.getElementById('clear-btn');
    const autocompleteDropdown = document.getElementById('autocomplete-dropdown');
    const typoAlert = document.getElementById('typo-alert');
    const typoSuggestion = document.getElementById('typo-suggestion');
    const metricsStrip = document.getElementById('metrics-strip');
    const resultsCount = document.getElementById('results-count');
    const execTime = document.getElementById('exec-time');
    const resultsContainer = document.getElementById('results-container');

    let debounceTimer = null;

    // Load initial corpus documents
    performSearch('');

    // Input event for real-time search and autocomplete
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        if (query.length > 0) {
            clearBtn.classList.remove('hidden');
        } else {
            clearBtn.classList.add('hidden');
        }

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            performSearch(query);
            fetchAutocomplete(query);
        }, 150);
    });

    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        clearBtn.classList.add('hidden');
        autocompleteDropdown.classList.add('hidden');
        typoAlert.classList.add('hidden');
        performSearch('');
        searchInput.focus();
    });

    // Close autocomplete on external click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-wrapper')) {
            autocompleteDropdown.classList.add('hidden');
        }
    });

    // Typo link click
    typoSuggestion.addEventListener('click', () => {
        const suggestedWord = typoSuggestion.textContent;
        searchInput.value = suggestedWord;
        typoAlert.classList.add('hidden');
        performSearch(suggestedWord);
    });

    async function performSearch(query) {
        try {
            const url = query.trim() 
                ? `/api/v1/search?q=${encodeURIComponent(query.trim())}`
                : `/api/v1/documents`;

            const res = await fetch(url);
            const data = await res.json();

            renderResults(data, query.trim());
        } catch (err) {
            console.error('Search error:', err);
        }
    }

    async function fetchAutocomplete(query) {
        if (!query || query.length < 2) {
            autocompleteDropdown.classList.add('hidden');
            return;
        }

        // Use the last word typed for prefix autocomplete
        const words = query.trim().split(/\s+/);
        const lastWord = words[words.length - 1];

        try {
            const res = await fetch(`/api/v1/autocomplete?prefix=${encodeURIComponent(lastWord)}`);
            const data = await res.json();
            const suggestions = data.suggestions || [];

            if (suggestions.length === 0) {
                autocompleteDropdown.classList.add('hidden');
                return;
            }

            autocompleteDropdown.innerHTML = suggestions.map(s => {
                const fullSuggestion = words.slice(0, -1).concat(s).join(' ');
                return `<div class="autocomplete-item" data-val="${fullSuggestion}">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <span>${fullSuggestion}</span>
                </div>`;
            }).join('');

            autocompleteDropdown.classList.remove('hidden');

            // Item selection
            autocompleteDropdown.querySelectorAll('.autocomplete-item').forEach(el => {
                el.addEventListener('click', () => {
                    const val = el.getAttribute('data-val');
                    searchInput.value = val;
                    autocompleteDropdown.classList.add('hidden');
                    performSearch(val);
                });
            });
        } catch (err) {
            console.error('Autocomplete error:', err);
        }
    }

    function renderResults(data, query) {
        const results = data.results || [];
        const duration = data.execution_time_ms !== undefined ? data.execution_time_ms : 0;

        // Telemetry Strip
        if (query) {
            metricsStrip.classList.remove('hidden');
            resultsCount.textContent = `${results.length} result${results.length === 1 ? '' : 's'}`;
            execTime.textContent = `${duration.toFixed(2)} ms`;

            // Handle Typo Suggestion
            if (data.did_you_mean) {
                typoSuggestion.textContent = data.did_you_mean;
                typoAlert.classList.remove('hidden');
            } else {
                typoAlert.classList.add('hidden');
            }
        } else {
            metricsStrip.classList.add('hidden');
            typoAlert.classList.add('hidden');
        }

        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No results found</h3>
                    <p>Try searching for broader terms like "consensus", "caching", or "streams".</p>
                </div>
            `;
            return;
        }

        resultsContainer.innerHTML = results.map(item => {
            const scoreTag = item.score !== undefined 
                ? `<div class="score-tag">BM25: ${item.score}</div>` 
                : '';

            const breakdownHtml = item.score_breakdown && Object.keys(item.score_breakdown).length > 0
                ? `<div class="breakdown-strip">
                    <span>Relevance Breakdown:</span>
                    ${Object.entries(item.score_breakdown).map(([term, score]) => 
                        `<span class="breakdown-term">${term}: <strong>${score}</strong></span>`
                    ).join(' ')}
                   </div>`
                : '';

            const category = item.metadata?.category || item.category || 'Article';
            const url = item.metadata?.url || item.url || '#';

            return `
                <article class="result-card">
                    <div class="result-header">
                        <a href="${url}" target="_blank" class="result-title">${item.title}</a>
                        ${scoreTag}
                    </div>
                    <p class="result-snippet">${item.snippet || item.content}</p>
                    <div class="result-meta">
                        <span class="meta-category">${category}</span>
                    </div>
                    ${breakdownHtml}
                </article>
            `;
        }).join('');
    }
});
