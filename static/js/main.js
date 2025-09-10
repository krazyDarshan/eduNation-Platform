// Main JavaScript for EcoLearn Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize application
    initializeApp();
    
    // Initialize components
    initializeQuiz();
    initializeProgressBars();
    initializeGamification();
    initializeTooltips();
});

function initializeApp() {
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeProgressBars() {
    // Animate progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
}

function initializeGamification() {
    // Points counter animation
    const pointsDisplays = document.querySelectorAll('.points-display');
    pointsDisplays.forEach(display => {
        const finalValue = parseInt(display.textContent);
        if (!isNaN(finalValue)) {
            animateCounter(display, finalValue);
        }
    });
    
    // Achievement badge hover effects
    const achievementBadges = document.querySelectorAll('.badge-achievement');
    achievementBadges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) rotate(10deg)';
        });
        
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    });
}

function animateCounter(element, finalValue, duration = 1000) {
    const startValue = 0;
    const increment = finalValue / (duration / 16); // 60 FPS
    let currentValue = startValue;
    
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= finalValue) {
            currentValue = finalValue;
            clearInterval(timer);
        }
        element.textContent = Math.floor(currentValue);
    }, 16);
}

// Quiz functionality
function initializeQuiz() {
    const quizOptions = document.querySelectorAll('.quiz-option');
    
    quizOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options in this question
            const questionContainer = this.closest('.quiz-question');
            const allOptions = questionContainer.querySelectorAll('.quiz-option');
            allOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Enable submit button if available
            const submitBtn = questionContainer.querySelector('.quiz-submit');
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        });
    });
}

function submitQuiz(quizId) {
    const selectedOptions = document.querySelectorAll('.quiz-option.selected');
    const answers = {};
    
    selectedOptions.forEach(option => {
        const questionId = option.dataset.questionId;
        const answerId = option.dataset.answerId;
        answers[questionId] = answerId;
    });
    
    // Show loading spinner
    const submitBtn = document.querySelector('.quiz-submit');
    if (submitBtn) {
        submitBtn.innerHTML = '<span class="loading-spinner"></span> Submitting...';
        submitBtn.disabled = true;
    }
    
    // Submit quiz via AJAX
    fetch(`/api/quiz/${quizId}/submit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({answers: answers})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showQuizResults(data);
            updatePoints(data.points_earned);
        } else {
            showAlert('Error submitting quiz', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error submitting quiz', 'danger');
    });
}

function showQuizResults(data) {
    const resultsContainer = document.getElementById('quiz-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="alert alert-success">
                <h5><i class="fas fa-trophy me-2"></i>Quiz Complete!</h5>
                <p>Score: ${data.score}/${data.total_questions}</p>
                <p>Points Earned: <span class="badge bg-warning text-dark">${data.points_earned}</span></p>
            </div>
        `;
        resultsContainer.scrollIntoView({behavior: 'smooth'});
    }
    
    // Show correct answers
    data.correct_answers.forEach(answer => {
        const option = document.querySelector(`[data-answer-id="${answer}"]`);
        if (option) {
            option.classList.add('correct');
        }
    });
    
    // Show incorrect answers
    const selectedOptions = document.querySelectorAll('.quiz-option.selected');
    selectedOptions.forEach(option => {
        const answerId = option.dataset.answerId;
        if (!data.correct_answers.includes(parseInt(answerId))) {
            option.classList.add('incorrect');
        }
    });
}

function updatePoints(pointsEarned) {
    const pointsDisplay = document.querySelector('.navbar .badge');
    if (pointsDisplay) {
        const currentPoints = parseInt(pointsDisplay.textContent.split(' ')[0]);
        const newPoints = currentPoints + pointsEarned;
        pointsDisplay.textContent = `${newPoints} pts`;
        
        // Animate points increase
        pointsDisplay.style.transform = 'scale(1.2)';
        setTimeout(() => {
            pointsDisplay.style.transform = 'scale(1)';
        }, 300);
    }
}

function getCsrfToken() {
    return document.querySelector('meta[name=csrf-token]').getAttribute('content');
}

function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertContainer, container.firstChild);
    }
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertContainer.remove();
    }, 5000);
}

// Course progress tracking
function updateLessonProgress(lessonId, completed = true) {
    fetch(`/api/lesson/${lessonId}/progress`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({completed: completed})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update progress bar
            const progressBar = document.querySelector('.course-progress .progress-bar');
            if (progressBar) {
                progressBar.style.width = `${data.progress_percentage}%`;
                progressBar.setAttribute('aria-valuenow', data.progress_percentage);
            }
            
            // Show points earned
            if (data.points_earned > 0) {
                showAlert(`Lesson completed! You earned ${data.points_earned} points.`, 'success');
                updatePoints(data.points_earned);
            }
            
            // Check for new achievements
            if (data.new_achievements && data.new_achievements.length > 0) {
                showAchievementModal(data.new_achievements);
            }
        }
    })
    .catch(error => {
        console.error('Error updating progress:', error);
    });
}

function showAchievementModal(achievements) {
    const modalHtml = `
        <div class="modal fade" id="achievementModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-trophy me-2"></i>New Achievement${achievements.length > 1 ? 's' : ''}!
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        ${achievements.map(achievement => `
                            <div class="achievement-item mb-3">
                                <div class="badge-achievement mx-auto mb-2">
                                    <i class="fas ${achievement.icon}"></i>
                                </div>
                                <h6>${achievement.name}</h6>
                                <p class="text-muted">${achievement.description}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('achievementModal'));
    modal.show();
    
    // Remove modal after it's hidden
    document.getElementById('achievementModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                searchResults.innerHTML = '';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
    }
}

function performSearch(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        displaySearchResults(data.results);
    })
    .catch(error => {
        console.error('Search error:', error);
    });
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('search-results');
    
    if (results.length === 0) {
        searchResults.innerHTML = '<p class="text-muted">No results found.</p>';
        return;
    }
    
    const resultsHtml = results.map(result => `
        <div class="search-result-item border-bottom pb-2 mb-2">
            <h6><a href="${result.url}">${result.title}</a></h6>
            <p class="text-muted mb-0">${result.description}</p>
        </div>
    `).join('');
    
    searchResults.innerHTML = resultsHtml;
}

// Utility functions
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Export functions for use in other scripts
window.EcoLearn = {
    submitQuiz,
    updateLessonProgress,
    showAlert,
    formatDuration,
    formatDate
};
