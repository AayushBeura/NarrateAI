class NarrateAI {
    constructor() {
        this.initializeEventListeners();
        this.currentAudioUrl = null;
        this.isGenerating = false;
    }

    initializeEventListeners() {
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const regenerateBtn = document.getElementById('regenerateBtn');
        const dismissError = document.getElementById('dismissError');

        generateBtn.addEventListener('click', () => this.generateStory());
        downloadBtn.addEventListener('click', () => this.downloadAudio());
        regenerateBtn.addEventListener('click', () => this.regenerateStory());
        dismissError.addEventListener('click', () => this.hideError());

        // Auto-select at least one mood if none selected
        const moodCheckboxes = document.querySelectorAll('input[name="moods"]');
        moodCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.validateMoodSelection());
        });

        // Enter key support for keywords input
        document.getElementById('keywords').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isGenerating) {
                this.generateStory();
            }
        });
    }

    validateMoodSelection() {
        const selectedMoods = document.querySelectorAll('input[name="moods"]:checked');
        if (selectedMoods.length === 0) {
            // Auto-select calm mood if none selected
            document.querySelector('input[value="calm"]').checked = true;
        }
    }

    async generateStory() {
        if (this.isGenerating) return;

        const keywords = document.getElementById('keywords').value.trim();
        const theme = document.getElementById('theme').value;
        const duration = document.getElementById('duration').value;
        const selectedMoods = Array.from(document.querySelectorAll('input[name="moods"]:checked'))
            .map(checkbox => checkbox.value);

        // Validation
        if (!keywords) {
            this.showError('Please enter some keywords for your story.');
            return;
        }

        if (selectedMoods.length === 0) {
            selectedMoods.push('calm'); // Default mood
        }

        const keywordArray = keywords.split(',').map(k => k.trim()).filter(k => k);

        if (keywordArray.length === 0) {
            this.showError('Please enter valid keywords separated by commas.');
            return;
        }

        if (keywordArray.length > 10) {
            this.showError('Please enter no more than 10 keywords.');
            return;
        }

        // Show loading
        this.showLoading();
        this.isGenerating = true;

        try {
            const response = await fetch('/api/generate-story', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    keywords: keywordArray,
                    theme: theme,
                    duration: parseInt(duration),
                    moods: selectedMoods
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayStory(data);
            } else {
                this.showError(data.error || 'An error occurred while generating your story.');
            }
        } catch (error) {
            this.showError('Network error. Please check your connection and try again.');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
            this.isGenerating = false;
        }
    }

    regenerateStory() {
        this.hideOutput();
        this.generateStory();
    }

    showLoading() {
        document.getElementById('generateBtn').disabled = true;
        document.getElementById('generateBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
        document.getElementById('loadingSection').style.display = 'block';
        document.getElementById('outputSection').style.display = 'none';
        this.hideError();

        // Animate loading steps
        this.animateLoadingSteps();
    }

    animateLoadingSteps() {
        const steps = ['step1', 'step2', 'step3'];
        let currentStep = 0;

        const interval = setInterval(() => {
            // Remove active class from all steps
            steps.forEach(step => {
                const element = document.getElementById(step);
                if (element) element.classList.remove('active');
            });

            // Add active class to current step
            if (currentStep < steps.length) {
                const element = document.getElementById(steps[currentStep]);
                if (element) element.classList.add('active');
                currentStep++;
            } else {
                currentStep = 0; // Loop back to start
            }
        }, 2000);

        // Store interval to clear it later
        this.loadingInterval = interval;
    }

    hideLoading() {
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
        }

        document.getElementById('generateBtn').disabled = false;
        document.getElementById('generateBtn').innerHTML = '<i class="fas fa-magic"></i> Create My Story';
        document.getElementById('loadingSection').style.display = 'none';
    }

    displayStory(data) {
        // Update story info
        document.getElementById('durationInfo').textContent = `Duration: ${data.duration_estimate}`;
        document.getElementById('emotionsInfo').textContent = `Emotions: ${data.emotions_used.join(', ')}`;
        document.getElementById('wordCountInfo').textContent = `Words: ${data.word_count}`;

        // Display story text
        document.getElementById('storyText').textContent = data.story;

        // Setup audio player
        const audioPlayer = document.getElementById('storyAudio');
        audioPlayer.src = data.audio_url;
        this.currentAudioUrl = data.audio_url;

        // Show output section
        document.getElementById('outputSection').style.display = 'block';

        // Scroll to output
        document.getElementById('outputSection').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });

        // Auto-play audio after a short delay
        setTimeout(() => {
            audioPlayer.play().catch(error => {
                console.log('Auto-play prevented by browser:', error);
            });
        }, 1000);
    }

    hideOutput() {
        document.getElementById('outputSection').style.display = 'none';
    }

    downloadAudio() {
        if (this.currentAudioUrl) {
            const link = document.createElement('a');
            link.href = this.currentAudioUrl;
            link.download = `narrate-ai-story-${Date.now()}.mp3`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            this.showError('No audio available to download.');
        }
    }

    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        errorText.textContent = message;
        errorMessage.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        document.getElementById('errorMessage').style.display = 'none';
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new NarrateAI();
});

// Add some interactive effects
document.addEventListener('DOMContentLoaded', () => {
    // Add hover effects to mood tags
    const moodTags = document.querySelectorAll('.mood-tag');
    moodTags.forEach(tag => {
        tag.addEventListener('mouseenter', function() {
            if (!this.previousElementSibling.checked) {
                this.style.transform = 'scale(1.02)';
            }
        });
        
        tag.addEventListener('mouseleave', function() {
            if (!this.previousElementSibling.checked) {
                this.style.transform = 'scale(1)';
            }
        });
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.generate-btn, .download-btn, .regenerate-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});
