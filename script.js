// Elements
        const resumeFile = document.getElementById('resumeFile');
        const resumeLabel = document.getElementById('resumeLabel');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const errorMessage = document.getElementById('errorMessage');
        const resultsSection = document.getElementById('resultsSection');
        const resultsContent = document.getElementById('resultsContent');
        const emptyState = document.getElementById('emptyState');

        // File input handler
        resumeFile.addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                resumeLabel.textContent = `✓ ${fileName}`;
                resumeLabel.classList.add('has-file');
            } else {
                resumeLabel.textContent = '📄 Choose PDF File';
                resumeLabel.classList.remove('has-file');
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

        // Analyze button handler
        analyzeBtn.addEventListener('click', async function() {
            // Validation
            if (!resumeFile.files.length) {
                showError('Please upload a resume PDF file');
                return;
            }

            // Prepare FormData
            const formData = new FormData();
            formData.append('file', resumeFile.files[0]);

            // Show loading state
            analyzeBtn.classList.add('loading');
            analyzeBtn.disabled = true;
            emptyState.style.display = 'none';
            resultsSection.classList.remove('show');

            try {
                const response = await fetch('http://127.0.0.1:8000/upload/', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                displayResults(data);

            } catch (error) {
                showError('Failed to analyze resume. Please check your connection and try again.');
                console.error('Error:', error);
                emptyState.style.display = 'block';
            } finally {
                analyzeBtn.classList.remove('loading');
                analyzeBtn.disabled = false;
            }
        });

        // Display results function
        function displayResults(data) {
            const filename = data.filename || 'Unknown';
            const score = data.score || 0;
            const skillsFound = data.skills_found || [];
            const warnings = data.warnings || [];

            let html = `
                <div class="result-header">
                    <div class="filename-display">
                        <strong>File:</strong> ${filename}
                    </div>
                    <div class="score-badge">
                        ${score}<span>/100</span>
                    </div>
                </div>

                <div class="info-section">
                    <h3>
                        <span>✨</span> Skills Found
                        <span style="background: #667eea; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; margin-left: 8px;">${skillsFound.length}</span>
                    </h3>
                    <div class="skills-container">
                        ${skillsFound.length > 0 
                            ? skillsFound.map(skill => `<div class="skill-tag">${skill}</div>`).join('') 
                            : '<p style="color: #a0aec0;">No skills detected</p>'}
                    </div>
                </div>

                ${warnings.length > 0 ? `
                    <div class="warnings-section">
                        <h3>⚠️ Warnings</h3>
                        ${warnings.map(warning => `<div class="warning-item">• ${warning}</div>`).join('')}
                    </div>
                ` : ''}
            `;

            resultsContent.innerHTML = html;
            resultsSection.classList.add('show');
            
            // Smooth scroll to results
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }