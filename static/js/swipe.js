document.addEventListener('DOMContentLoaded', () => {
    const swipeContainer = document.getElementById('swipeContainer');
    let jobsList = [];
    let currentJobIndex = 0;

    // Fetch jobs from backend
    async function fetchJobs() {
        try {
            const response = await fetch('/api/jobs');
            const data = await response.json();
            
            if (data.jobs && data.jobs.length > 0) {
                jobsList = data.jobs;
                renderCurrentJob();
            } else {
                renderNoJobsMessage();
            }
        } catch (error) {
            console.error('Error fetching jobs:', error);
            renderNoJobsMessage('Failed to load jobs. Please try again later.');
        }
    }

    function renderNoJobsMessage(msg = 'No more jobs available right now. Check back later!') {
        swipeContainer.innerHTML = `
            <div class="no-jobs glass-panel">
                <h3>All Caught Up!</h3>
                <p style="color: var(--text-muted);">${msg}</p>
            </div>
        `;
    }

    function renderCurrentJob() {
        if (currentJobIndex >= jobsList.length) {
            renderNoJobsMessage();
            return;
        }

        const job = jobsList[currentJobIndex];
        const tagsHtml = job.skills.split(',')
            .map(skill => `<span class="skill-tag">${skill.trim()}</span>`)
            .join('');

        const cardHtml = `
            <div class="job-card" id="currentCard">
                <div>
                    <a href="/job/${job.id}" style="text-decoration: none;">
                        <h2 class="job-title">${job.title}</h2>
                    </a>
                    <div class="company-name">${job.company_name}</div>
                    <div class="skills-tags">${tagsHtml}</div>
                    <div class="job-description">${job.description}</div>
                </div>
                <div class="action-buttons">
                    <button class="btn-circle btn-dislike" onclick="handleSwipe(false)">✕</button>
                    <!-- <a href="/job/${job.id}" class="btn-circle" style="font-size: 1rem; color: #cbd5e1; border-color: #cbd5e1;">ℹ️</a> -->
                    <button class="btn-circle btn-like" onclick="handleSwipe(true)">♥</button>
                </div>
            </div>
        `;

        // We replace the innerHTML for simplicity (no multi-card stack mapping yet)
        swipeContainer.innerHTML = cardHtml;
    }

    window.handleSwipe = async function(liked) {
        const card = document.getElementById('currentCard');
        if (!card) return;

        // Animate
        if (liked) {
            card.classList.add('swiped-right');
        } else {
            card.classList.add('swiped-left');
        }

        const job = jobsList[currentJobIndex];
        
        // Disable buttons immediately
        const buttons = card.querySelectorAll('button');
        buttons.forEach(btn => btn.disabled = true);

        // Send to backend
        try {
            const action = liked ? 'like' : 'dislike';
            await fetch(`/swipe/${job.id}/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Failed to register swipe:', error);
        }

        // Wait for animation then load next
        setTimeout(() => {
            currentJobIndex++;
            renderCurrentJob();
        }, 300); // 300ms matches CSS transition
    };

    // Initial load
    fetchJobs();
});
