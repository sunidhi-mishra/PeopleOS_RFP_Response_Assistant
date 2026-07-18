const API_URL = (window.RFP_MATCH_CONFIG && window.RFP_MATCH_CONFIG.API_URL) || "http://127.0.0.1:8000/match";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("rfp-form");
    const questionInput = document.getElementById("rfp-question");
    const submitBtn = document.getElementById("submit-btn");
    const btnText = submitBtn.querySelector(".btn-text");
    const spinner = submitBtn.querySelector(".spinner");
    
    const emptyState = document.getElementById("empty-state");
    const errorState = document.getElementById("error-state");
    const errorMessage = document.getElementById("error-message");
    const matchesList = document.getElementById("matches-list");
    const infoBox = document.getElementById("info-box");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        if (!question) return;

        // Enter loading state
        submitBtn.disabled = true;
        btnText.textContent = "Finding Matches...";
        spinner.classList.remove("hidden");
        
        // Hide only empty state & error state, keeping previous matches list visible to avoid flickering
        emptyState.classList.add("hidden");
        errorState.classList.add("hidden");

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ question })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server returned status ${response.status}`);
            }

            const data = await response.json();
            renderResults(data.results);
            
        } catch (error) {
            console.error("Fetch error:", error);
            // If there's an error, hide results and show error state
            matchesList.classList.add("hidden");
            infoBox.classList.add("hidden");
            errorState.classList.remove("hidden");
            errorMessage.textContent = "Could not connect to the matching service. Please ensure the backend is running.";
        } finally {
            // Exit loading state
            submitBtn.disabled = false;
            btnText.textContent = "Find Matches";
            spinner.classList.add("hidden");
        }
    });

    function renderResults(results) {
        // Clear previous entries
        matchesList.innerHTML = "";

        if (!results || results.length === 0) {
            emptyState.classList.remove("hidden");
            matchesList.classList.add("hidden");
            infoBox.classList.add("hidden");
            return;
        }

        results.forEach((match) => {
            const card = document.createElement("div");
            card.className = "result-card";
            
            // Map category CSS classes
            const categoryClass = match.category.toLowerCase().replace(/[^a-z0-t]/g, "");
            
            // Format score as percentage
            const scorePercentage = Math.round(match.similarity_score * 100);
            
            card.innerHTML = `
                <div class="card-header">
                    <div class="card-header-left">
                        <span class="rank-badge">${match.rank}</span>
                        <span class="card-category-badge ${categoryClass}">${match.category}</span>
                    </div>
                    <span class="decision-badge ${match.decision_color}">${match.decision_label}</span>
                </div>
                <div class="card-body">
                    <div class="matched-question-sec">
                        <div class="section-label">Matched Question</div>
                        <p class="matched-question-text">${match.matched_question}</p>
                    </div>
                    <div class="answer-sec">
                        <div class="section-label">Answer</div>
                        <p class="answer-text">${match.answer}</p>
                    </div>
                    
                    ${match.is_stale ? `
                    <div class="stale-warning">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                        <span>Answer may be outdated — review before use</span>
                    </div>
                    ` : ''}

                    <div class="card-meta-row">
                        <div class="score-wrapper">
                            <span class="score-text">${scorePercentage}% match</span>
                            <div class="score-bar-bg">
                                <div class="score-bar-fill ${match.decision_color}" style="width: ${scorePercentage}%;"></div>
                            </div>
                        </div>
                        <div class="meta-field">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                            <span>${match.owner}</span>
                        </div>
                        <div class="meta-field">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="16" y1="2" x2="16" y2="6"></line>
                                <line x1="8" y1="2" x2="8" y2="6"></line>
                                <line x1="3" y1="10" x2="21" y2="10"></line>
                            </svg>
                            <span>${match.last_updated}</span>
                        </div>
                    </div>
                </div>
                <div class="card-actions">
                    <button class="btn-secondary mark-used-btn">Mark as Used</button>
                </div>
            `;
            
            // "Mark as Used" interactive effect
            const usedBtn = card.querySelector(".mark-used-btn");
            usedBtn.addEventListener("click", () => {
                usedBtn.classList.add("used");
                usedBtn.textContent = "Noted ✓";
                
                setTimeout(() => {
                    usedBtn.classList.remove("used");
                    usedBtn.textContent = "Mark as Used";
                }, 3000);
            });

            matchesList.appendChild(card);
        });

        matchesList.classList.remove("hidden");
        infoBox.classList.remove("hidden");
    }
});
