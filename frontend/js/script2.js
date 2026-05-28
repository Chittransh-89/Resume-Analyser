// Elements
        const resumeFile = document.getElementById('resumeFile');
        const resumeLabel = document.getElementById('resumeLabel');
        const jdFile = document.getElementById('jdFile');
        const jdLabel = document.getElementById('jdLabel');
        const compareBtn = document.getElementById('compareBtn');
        const errorMessage = document.getElementById('errorMessage');
        const resultsSection = document.getElementById('resultsSection');
        const resultsContent = document.getElementById('resultsContent');
        const emptyState = document.getElementById('emptyState');

        // File input handlers
        resumeFile.addEventListener('change', function() {
            if (this.files.length > 0) {
                resumeLabel.textContent = `✓ ${this.files[0].name}`;
                resumeLabel.classList.add('has-file');
            } else {
                resumeLabel.textContent = '📄 Choose Resume PDF';
                resumeLabel.classList.remove('has-file');
            }
        });

        jdFile.addEventListener('change', function() {
            if (this.files.length > 0) {
                jdLabel.textContent = `✓ ${this.files[0].name}`;
                jdLabel.classList.add('has-file');
            } else {
                jdLabel.textContent = '📄 Choose JD PDF';
                jdLabel.classList.remove('has-file');
            }
        });

        // Show error function
        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.classList.add('show');
            setTimeout(() => {
                errorMessage.classList.remove('show');
            }, 5000);
        }

        // Compare button handler
        compareBtn.addEventListener('click', async function() {
            // Validation
            if (!resumeFile.files.length) {
                showError('Please upload a resume PDF file');
                return;
            }

            if (!jdFile.files.length) {
                showError('Please upload a job description PDF file');
                return;
            }

            // Prepare FormData
            const formData = new FormData();
            formData.append('file', resumeFile.files[0]);
            formData.append('jd', jdFile.files[0]);

            // Show loading state
            compareBtn.classList.add('loading');
            compareBtn.disabled = true;
            emptyState.style.display = 'none';
            resultsSection.classList.remove('show');

            try {
                const response = await fetch('http://127.0.0.1:8000/analyze/', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                displayResults(data);

            } catch (error) {
                showError('Failed to compare files. Please check your connection and try again.');
                console.error('Error:', error);
                emptyState.style.display = 'block';
            } finally {
                compareBtn.classList.remove('loading');
                compareBtn.disabled = false;
            }
        });

        // Display results function
        function displayResults(data) {
            const matchScore = data.match_score || '0%';
            const skillsInResume = data.skills_in_resume || [];
            const skillsRequired = data.skills_required || [];
            const missingSkills = data.missing_skills || [];

            let html = `
                <div class="match-score-card">
                    <div class="match-label">Match Score</div>
                    <div class="match-value">${matchScore}</div>
                    <div class="match-subtitle">Resume compatibility with job requirements</div>
                </div>

                <div class="skills-grid">
                    <div class="skill-card">
                        <h3>
                            <span>✓</span> 
                            Skills in Resume
                            <span class="skill-count">${skillsInResume.length}</span>
                        </h3>
                        <div class="skills-container">
                            ${skillsInResume.length > 0 
                                ? skillsInResume.map(skill => `<div class="skill-tag">${skill}</div>`).join('') 
                                : '<p style="color: #a0aec0;">No skills detected</p>'}
                        </div>
                    </div>

                    <div class="skill-card required">
                        <h3>
                            <span>📋</span> 
                            Required Skills
                            <span class="skill-count">${skillsRequired.length}</span>
                        </h3>
                        <div class="skills-container">
                            ${skillsRequired.length > 0 
                                ? skillsRequired.map(skill => `<div class="skill-tag">${skill}</div>`).join('') 
                                : '<p style="color: #a0aec0;">No requirements found</p>'}
                        </div>
                    </div>

                    <div class="skill-card missing">
                        <h3>
                            <span>⚠️</span> 
                            Missing Skills
                            <span class="skill-count">${missingSkills.length}</span>
                        </h3>
                        <div class="skills-container">
                            ${missingSkills.length > 0 
                                ? missingSkills.map(skill => `<div class="skill-tag">${skill}</div>`).join('') 
                                : '<p style="color: #48bb78; font-weight: 600;">🎉 You have all required skills!</p>'}
                        </div>
                    </div>
                </div>
            `;

            resultsContent.innerHTML = html;
            resultsSection.classList.add('show');
            
            // Smooth scroll to results
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }