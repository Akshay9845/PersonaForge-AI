/**
 * PersonaForge AI - Award-Winning Dashboard
 * Modern, cinematic experience with welcome screen and theme toggle
 * Enhanced with animated MBTI radar chart and glassmorphic visualizations
 */

class PersonaDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentPersona = null;
        this.searchHistory = JSON.parse(localStorage.getItem('personaHistory') || '[]');
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.userName = localStorage.getItem('userName') || '';
        this.lottieAnimations = new Map();
        this.init();
    }

    init() {
        this.setTheme(this.currentTheme);
        this.render();
        this.bindEvents();
        
        // Show welcome screen if no user name
        if (!this.userName) {
            this.showWelcomeScreen();
        } else {
            this.hideWelcomeScreen();
        }
    }

    render() {
        this.container.innerHTML = `
            <!-- Sidebar Drawer -->
            <div class="sidebar-drawer" id="sidebar-drawer">
                <h3 class="sidebar-title">Search History</h3>
                <div class="history-list" id="history-list">
                    ${this.renderHistory()}
                </div>
            </div>
            <button class="sidebar-toggle-btn" id="sidebar-toggle-btn" title="Show/Hide History" style="left:0;right:auto;">
                <!-- Modern clock SVG icon -->
                <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </button>

            <!-- Chatbot Floating Button -->
            <button class="chatbot-fab" id="chatbot-fab" title="Ask Persona AI">
                <!-- Modern chat bubble SVG icon -->
                <svg width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </button>
            <div class="chatbot-panel" id="chatbot-panel">
                <div class="chatbot-header">
                    <span class="chatbot-title">Persona QA Agent</span>
                    <button class="chatbot-close-btn" id="chatbot-close-btn">&times;</button>
                </div>
                <div class="chatbot-body" id="chatbot-body">
                    <div style="color: var(--text-secondary); font-size: 1rem; margin-bottom: 1.5rem;">Wanna ask something about this user?</div>
                    <!-- Chat messages will go here -->
                </div>
                <form class="chatbot-input-row" id="chatbot-form">
                    <input type="text" class="chatbot-input" id="chatbot-input" placeholder="Ask about this persona..." autocomplete="off" />
                    <button type="submit" class="chatbot-send-btn">Send</button>
                </form>
            </div>

            <!-- Main Dashboard -->
            <div class="persona-dashboard" id="main-dashboard">
                <!-- Header -->
                <header class="dashboard-header">
                    <div class="header-left">
                        <div class="header-logo">🚀 PersonaForge AI</div>
                        <div class="header-subtitle">Advanced Reddit User Analysis</div>
                    </div>
                    <div class="header-controls">
                        <button class="theme-toggle" id="theme-toggle" title="Toggle theme">
                            <span class="theme-icon" id="theme-icon">🌙</span>
                        </button>
                    </div>
                </header>

                <!-- Main Layout -->
                <div class="dashboard-layout">
                    <!-- Main Panel -->
                    <main class="main-panel">
                        <!-- Search Section -->
                        <section class="search-section">
                            <h2 class="search-title">Generate Reddit Persona</h2>
                            <p class="search-subtitle">Enter a Reddit username to create a detailed AI-powered persona</p>
                            <form class="search-form" id="search-form">
                                <input type="text" id="username-input" 
                                       placeholder="Enter Reddit username (e.g., spez, GallowBoob)" 
                                       class="username-input" required>
                                <button type="submit" id="generate-btn" class="generate-btn">
                                    Generate Persona
                                </button>
                            </form>
                            <div class="status-indicator" id="status-indicator">
                                <span class="status-text">Ready to generate personas</span>
                            </div>
                        </section>

                        <!-- Loading Container -->
                        <div class="loading-container" id="loading-container" style="display: none;">
                            <div class="loading-spinner"></div>
                            <div class="loading-text" id="loading-text">Analyzing Reddit behaviors...</div>
                        </div>

                        <!-- Persona Display -->
                        <div class="persona-display" id="persona-display" style="display: none;">
                            <div class="persona-header">
                                <div class="persona-basic-info">
                                    <div class="avatar-section">
                                        <div class="avatar" id="persona-avatar">👤</div>
                                        <div class="personality-badge" id="personality-badge">XXXX</div>
                                    </div>
                                    <div class="info-section">
                                        <h2 id="persona-name">User Name</h2>
                                        <p id="persona-username" style="font-size: 1em; color: #888; margin: 0 0 4px 0;">@reddit_user</p>
                                        <p id="persona-occupation">Occupation</p>
                                        <p id="persona-location">Location</p>
                                        <div class="score-badge" id="analysis-score">0%</div>
                                    </div>
                                </div>
                                <div class="persona-quote">
                                    <blockquote id="persona-quote">Loading quote...</blockquote>
                                </div>
                            </div>

                            <div class="persona-grid">
                                <div class="persona-section traits-section">
                                    <h3>🎭 Personality Traits</h3>
                                    <div class="traits-list" id="traits-list"></div>
                                </div>

                                <div class="persona-section motivations-section">
                                    <h3>🎯 Motivations</h3>
                                    <div class="motivations-chart" id="motivations-chart"></div>
                                </div>

                                <div class="persona-section personality-section">
                                    <h3>🧠 MBTI Personality Profile</h3>
                                    <div class="mbti-radar-container" id="mbti-radar-container">
                                        <canvas id="mbti-radar-chart" width="400" height="400"></canvas>
                                        <div class="mbti-overlay" id="mbti-overlay"></div>
                                    </div>
                                </div>

                                <div class="persona-section behavior-section">
                                    <h3>📝 Behavior Habits</h3>
                                    <div class="behavior-list" id="behavior-list"></div>
                                </div>

                                <div class="persona-section frustrations-section">
                                    <h3>⚠️ Frustrations</h3>
                                    <div class="frustrations-list" id="frustrations-list"></div>
                                </div>

                                <div class="persona-section goals-section">
                                    <h3>🎯 Goals</h3>
                                    <div class="goals-list" id="goals-list"></div>
                                </div>
                            </div>

                            <div class="persona-footer">
                                <div class="data-sources">
                                    <h3>📊 Data Sources</h3>
                                    <div class="sources-list" id="sources-list"></div>
                                </div>
                                <div class="export-section">
                                    <button id="export-json" class="export-btn">📄 Export JSON</button>
                                    <button id="export-html" class="export-btn">🔗 Export HTML Report</button>
                                </div>
                            </div>
                        </div>
                    </main>
                </div>
            </div>
        `;
    }

    renderHistory() {
        if (this.searchHistory.length === 0) {
            return '<p style="color: var(--text-secondary); text-align: center; font-style: italic;">No search history yet</p>';
        }

        return this.searchHistory.slice(0, 5).map(item => `
            <div class="history-item" data-username="${item.username}">
                <div class="history-username">u/${item.username}</div>
                <div class="history-time">${this.formatTime(item.timestamp)}</div>
                <div class="history-score">${item.score}%</div>
            </div>
        `).join('');
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }

    bindEvents() {
        // Sidebar drawer logic
        const sidebarDrawer = document.getElementById('sidebar-drawer');
        const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
        let sidebarOpen = false;
        const openSidebar = () => {
            sidebarDrawer.classList.add('open');
            sidebarToggleBtn.style.right = '350px';
            sidebarOpen = true;
        };
        const closeSidebar = () => {
            sidebarDrawer.classList.remove('open');
            sidebarToggleBtn.style.right = '0';
            sidebarOpen = false;
        };
        sidebarToggleBtn.addEventListener('click', () => {
            if (sidebarOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
        // Start closed by default
        closeSidebar();

        // Chatbot panel logic
        const chatbotFab = document.getElementById('chatbot-fab');
        const chatbotPanel = document.getElementById('chatbot-panel');
        const chatbotCloseBtn = document.getElementById('chatbot-close-btn');
        let chatbotOpen = false;
        const openChatbot = () => {
            chatbotPanel.classList.add('open');
            chatbotOpen = true;
            // Optionally close sidebar if open
            closeSidebar();
        };
        const closeChatbot = () => {
            chatbotPanel.classList.remove('open');
            chatbotOpen = false;
        };
        chatbotFab.addEventListener('click', openChatbot);
        chatbotCloseBtn.addEventListener('click', closeChatbot);

        // Welcome screen
        const welcomeForm = document.getElementById('welcome-form');
        if (welcomeForm) {
            welcomeForm.addEventListener('submit', (e) => this.handleWelcomeSubmit(e));
        }
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        // Search form
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => this.handleSearchSubmit(e));
        }
        // Export buttons
        const exportJson = document.getElementById('export-json');
        if (exportJson) {
            exportJson.addEventListener('click', () => this.exportJSON());
        }
        const exportHtml = document.getElementById('export-html');
        if (exportHtml) {
            exportHtml.addEventListener('click', () => this.exportHTML());
        }
        // History items
        this.bindHistoryEvents();
        // Chatbot form (placeholder, no backend yet)
        const chatbotForm = document.getElementById('chatbot-form');
        const chatbotInput = document.getElementById('chatbot-input');
        const chatbotBody = document.getElementById('chatbot-body');
        if (chatbotForm && chatbotInput && chatbotBody) {
            chatbotForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const question = chatbotInput.value.trim();
                if (question) {
                    const msg = document.createElement('div');
                    msg.style.margin = '0 0 1rem 0';
                    msg.style.color = 'var(--text-primary)';
                    msg.innerHTML = `<b>You:</b> ${question}`;
                    chatbotBody.appendChild(msg);
                    chatbotInput.value = '';
                    chatbotBody.scrollTop = chatbotBody.scrollHeight;
                    // Placeholder: echo response
                    setTimeout(() => {
                        const resp = document.createElement('div');
                        resp.style.margin = '0 0 1.5rem 0';
                        resp.style.color = 'var(--accent)';
                        resp.innerHTML = `<b>Persona AI:</b> <i>This is a placeholder response about the user.</i>`;
                        chatbotBody.appendChild(resp);
                        chatbotBody.scrollTop = chatbotBody.scrollHeight;
                    }, 600);
                }
            });
        }
    }

    bindHistoryEvents() {
        const historyItems = document.querySelectorAll('.history-item');
        historyItems.forEach(item => {
            item.addEventListener('click', () => {
                const username = item.dataset.username;
                document.getElementById('username-input').value = username;
                // Try to find cached persona
                const cached = this.searchHistory.find(h => h.username === username && h.persona);
                if (cached && cached.persona) {
                    this.currentPersona = cached.persona;
                    this.displayPersona(cached.persona);
                    this.setStatus('Loaded from history cache', 'info');
                } else {
                    this.generatePersona(username);
                }
            });
        });
    }

    handleWelcomeSubmit(e) {
        e.preventDefault();
        const input = document.getElementById('welcome-input');
        const name = input.value.trim();
        
        if (name) {
            this.userName = name;
            localStorage.setItem('userName', name);
            this.hideWelcomeScreen();
            this.showSuccessMessage(`Welcome back, ${name}!`);
        }
    }

    handleSearchSubmit(e) {
        e.preventDefault();
        const input = document.getElementById('username-input');
        const username = input.value.trim();
        
        if (username) {
            this.generatePersona(username);
        }
    }

    showWelcomeScreen() {
        const welcomeScreen = document.getElementById('welcome-screen');
        const mainDashboard = document.getElementById('main-dashboard');
        
        if (welcomeScreen && mainDashboard) {
            welcomeScreen.classList.remove('hidden');
            mainDashboard.style.display = 'none';
        }
    }

    hideWelcomeScreen() {
        const welcomeScreen = document.getElementById('welcome-screen');
        const mainDashboard = document.getElementById('main-dashboard');
        
        if (welcomeScreen && mainDashboard) {
            welcomeScreen.classList.add('hidden');
            mainDashboard.style.display = 'block';
        }
    }

    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    async generatePersona(username) {
        this.setStatus('Generating persona...', 'loading');
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/generate-persona', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, max_posts: 5, max_comments: 5 })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.currentPersona = data.persona;
                this.displayPersona(data.persona);
                this.addToHistory(username, data.persona.analysis_score || 0, data.persona); // Pass persona for caching
                this.setStatus('Persona generated successfully!', 'success');
                this.showSuccessMessage(`Persona for u/${username} created!`);
            } else {
                throw new Error(data.error || 'Failed to generate persona');
            }
        } catch (error) {
            console.error('Error generating persona:', error);
            this.setStatus('Error generating persona. Please try again.', 'error');
            this.showErrorMessage('Failed to generate persona. Please check the username and try again.');
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        const loadingContainer = document.getElementById('loading-container');
        const searchSection = document.querySelector('.search-section');
        const personaDisplay = document.getElementById('persona-display');
        
        if (loadingContainer && searchSection && personaDisplay) {
            if (show) {
                loadingContainer.style.display = 'flex';
                searchSection.style.display = 'none';
                personaDisplay.style.display = 'none';
            } else {
                loadingContainer.style.display = 'none';
                searchSection.style.display = 'block';
            }
        }
    }

    addToHistory(username, score, persona = null) {
        // Remove any existing entry for this username
        this.searchHistory = this.searchHistory.filter(item => item.username !== username);
        const historyItem = {
            username,
            score: Math.round(score),
            timestamp: new Date().toISOString(),
            persona: persona || this.currentPersona || null
        };
        this.searchHistory.unshift(historyItem);
        this.searchHistory = this.searchHistory.slice(0, 10); // Keep only last 10
        localStorage.setItem('personaHistory', JSON.stringify(this.searchHistory));
        // Update history display
        const historyList = document.getElementById('history-list');
        if (historyList) {
            historyList.innerHTML = this.renderHistory();
            this.bindHistoryEvents();
        }
    }

    displayPersona(persona) {
        const display = document.getElementById('persona-display');
        if (display) {
            display.style.display = '';
            display.classList.add('discord-reveal');
        }

        // Update basic info
        document.getElementById('persona-name').textContent = persona.name || 'Unknown User';
        document.getElementById('persona-username').textContent = persona.reddit_user || '';
        document.getElementById('persona-occupation').textContent = persona.occupation || 'Unknown';
        document.getElementById('persona-location').textContent = persona.location || 'Unknown';
        document.getElementById('personality-badge').textContent = persona.personality_type || 'XXXX';
        document.getElementById('analysis-score').textContent = `${persona.analysis_score?.toFixed(1) || 0}%`;
        document.getElementById('persona-quote').textContent = persona.quote || 'No quote available';

        // Update traits
        this.updateTraits(persona.traits || []);

        // Update motivations chart
        this.updateMotivationsChart(persona.motivations || {});

        // Update personality chart
        this.updatePersonalityChart(persona.personality || {});

        // Update lists
        this.updateList('behavior-list', persona.behavior_habits || []);
        this.updateList('frustrations-list', persona.frustrations || []);
        this.updateList('goals-list', persona.goals || []);

        // Update data sources
        this.updateDataSources(persona.data_sources || []);
    }

    updateTraits(traits) {
        const traitToLottie = {
            'Curious': '/animations/Thinking (colors adapted).json',
            'Open-minded': '/animations/Remote Work and Productivity.json',
            'Privacy-focused': '/animations/Cats in a box.json',
            'Creative': '/animations/Artist.json',
            'Introvert': '/animations/Scared 2D character.json',
            'Musical': '/animations/Singing and playing Music with Guitar.json',
            'Analytical': '/animations/Thinking (colors adapted).json',
            'Social': '/animations/Remote Work and Productivity.json',
            'Innovative': '/animations/Artist.json',
            'Cautious': '/animations/Scared 2D character.json',
            'Tech-savvy': '/animations/Thinking (colors adapted).json',
            'Community-focused': '/animations/Remote Work and Productivity.json'
        };
        const defaultLottie = '/animations/Thinking (colors adapted).json';
        const container = document.getElementById('traits-list');
        if (container) {
            container.innerHTML = traits.map((trait, index) => {
                const lottiePath = traitToLottie[trait] || defaultLottie;
                return `
                    <div class="trait-item glassmorphic-card discord-reveal" style="display: flex; align-items: center; gap: 16px; padding: 16px; border-radius: 12px;">
                        <div class="lottie-animation" data-lottie="${lottiePath}" style="width: 56px; height: 56px; border-radius: 8px; overflow: hidden;"></div>
                        <span style="font-weight: 500; color: var(--text-primary);">${trait}</span>
                    </div>
                `;
            }).join('');
            setTimeout(() => {
                this.initializeLottieTraitAnimations();
                // Stagger trait-item reveal
                const traitItems = container.querySelectorAll('.trait-item.discord-reveal');
                traitItems.forEach((item, i) => {
                    item.style.animationDelay = (i * 0.08) + 's';
                });
            }, 100);
        }
    }

    initializeLottieTraitAnimations() {
        const lottieElements = document.querySelectorAll('.lottie-animation');
        lottieElements.forEach((element, index) => {
            const lottiePath = element.getAttribute('data-lottie');
            if (lottiePath) {
                lottie.loadAnimation({
                    container: element,
                    renderer: 'svg',
                    loop: true,
                    autoplay: true,
                    path: lottiePath
                });
            }
        });
    }

    updateMotivationsChart(motivations) {
        const container = document.getElementById('motivations-chart');
        if (!container) return;
        
        if (Object.keys(motivations).length === 0) {
            container.innerHTML = '<p class="no-data">No motivation data available</p>';
            return;
        }

        const sortedMotivations = Object.entries(motivations)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 6);

        const motivationColors = [
            'linear-gradient(135deg, #667eea, #764ba2)',
            'linear-gradient(135deg, #f093fb, #f5576c)',
            'linear-gradient(135deg, #4facfe, #00f2fe)',
            'linear-gradient(135deg, #43e97b, #38f9d7)',
            'linear-gradient(135deg, #fa709a, #fee140)',
            'linear-gradient(135deg, #a8edea, #fed6e3)'
        ];

        const chartHTML = sortedMotivations.map(([motivation, score], index) => {
            const percentage = score;
            const label = motivation.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            const color = motivationColors[index % motivationColors.length];
            
            return `
                <div class="motivation-bar glassmorphic-card" style="padding: 16px; border-radius: 12px; backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 12px; transition: all 0.3s ease; animation: fadeInUp 0.6s ease ${index * 0.1}s both;">
                    <div class="motivation-label" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 500; color: var(--text-primary);">${label}</span>
                        <span class="motivation-score" style="font-weight: 600; color: var(--accent);">${score}%</span>
                    </div>
                    <div class="motivation-bar-container" style="height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; position: relative;">
                        <div class="motivation-bar-fill" style="height: 100%; background: ${color}; border-radius: 4px; width: 0%; transition: width 1s ease ${index * 0.1}s; position: relative;">
                            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent); animation: shimmer 2s infinite;"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = chartHTML;
        
        // Animate the bars after a short delay
        setTimeout(() => {
            sortedMotivations.forEach(([motivation, score], index) => {
                const barFill = container.querySelectorAll('.motivation-bar-fill')[index];
                if (barFill) {
                    barFill.style.width = `${score}%`;
                }
            });
        }, 200);
    }

    updatePersonalityChart(personality) {
        this.renderMBTIRadarChart(personality);
    }

    renderMBTIRadarChart(personality) {
        const canvas = document.getElementById('mbti-radar-chart');
        const overlay = document.getElementById('mbti-overlay');
        
        if (!canvas || !overlay) return;
        
        if (Object.keys(personality).length === 0) {
            overlay.innerHTML = '<p class="no-data">No MBTI data available</p>';
            return;
        }

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 40;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // MBTI dimensions mapping
        const mbtiDimensions = {
            'extraversion': { label: 'Extraversion', color: '#10b981', opposite: 'introversion' },
            'introversion': { label: 'Introversion', color: '#3b82f6', opposite: 'extraversion' },
            'sensing': { label: 'Sensing', color: '#f59e0b', opposite: 'intuition' },
            'intuition': { label: 'Intuition', color: '#8b5cf6', opposite: 'sensing' },
            'thinking': { label: 'Thinking', color: '#ef4444', opposite: 'feeling' },
            'feeling': { label: 'Feeling', color: '#ec4899', opposite: 'thinking' },
            'judging': { label: 'Judging', color: '#06b6d4', opposite: 'perceiving' },
            'perceiving': { label: 'Perceiving', color: '#84cc16', opposite: 'judging' }
        };

        // Draw radar grid
        this.drawRadarGrid(ctx, centerX, centerY, radius);

        // Prepare data for radar chart
        const dataPoints = [];
        const labels = [];
        const colors = [];
        let angleStep = (2 * Math.PI) / 4; // 4 main dimensions

        Object.entries(personality).forEach(([dimension, score], index) => {
            if (mbtiDimensions[dimension]) {
                const angle = index * angleStep - Math.PI / 2; // Start from top
                const normalizedScore = Math.min(score, 100) / 100;
                const x = centerX + Math.cos(angle) * radius * normalizedScore;
                const y = centerY + Math.sin(angle) * radius * normalizedScore;
                
                dataPoints.push({ x, y, score, dimension });
                labels.push(mbtiDimensions[dimension].label);
                colors.push(mbtiDimensions[dimension].color);
            }
        });

        // Draw radar area
        if (dataPoints.length > 0) {
            this.drawRadarArea(ctx, dataPoints, colors);
        }

        // Draw data points
        dataPoints.forEach((point, index) => {
            this.drawDataPoint(ctx, point.x, point.y, colors[index], point.score);
        });

        // Create overlay with labels and scores
        this.createMBTIOverlay(overlay, dataPoints, labels, colors);
    }

    drawRadarGrid(ctx, centerX, centerY, radius) {
        // Draw concentric circles
        for (let i = 1; i <= 5; i++) {
            const currentRadius = (radius * i) / 5;
            ctx.strokeStyle = 'rgba(128, 90, 213, 0.1)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(centerX, centerY, currentRadius, 0, 2 * Math.PI);
            ctx.stroke();
        }

        // Draw radial lines
        ctx.strokeStyle = 'rgba(128, 90, 213, 0.2)';
        ctx.lineWidth = 1;
        for (let i = 0; i < 4; i++) {
            const angle = (i * Math.PI) / 2 - Math.PI / 2;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.stroke();
        }
    }

    drawRadarArea(ctx, dataPoints, colors) {
        if (dataPoints.length < 3) return;

        // Create gradient
        const gradient = ctx.createRadialGradient(
            dataPoints[0].x, dataPoints[0].y, 0,
            dataPoints[0].x, dataPoints[0].y, 100
        );
        gradient.addColorStop(0, 'rgba(128, 90, 213, 0.3)');
        gradient.addColorStop(1, 'rgba(128, 90, 213, 0.1)');

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.moveTo(dataPoints[0].x, dataPoints[0].y);
        
        for (let i = 1; i < dataPoints.length; i++) {
            ctx.lineTo(dataPoints[i].x, dataPoints[i].y);
        }
        ctx.closePath();
        ctx.fill();

        // Draw border
        ctx.strokeStyle = 'rgba(128, 90, 213, 0.6)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(dataPoints[0].x, dataPoints[0].y);
        
        for (let i = 1; i < dataPoints.length; i++) {
            ctx.lineTo(dataPoints[i].x, dataPoints[i].y);
        }
        ctx.closePath();
        ctx.stroke();
    }

    drawDataPoint(ctx, x, y, color, score) {
        // Draw outer glow
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 15);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, 15, 0, 2 * Math.PI);
        ctx.fill();

        // Draw point
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, 2 * Math.PI);
        ctx.fill();

        // Draw white center
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.fill();
    }

    createMBTIOverlay(overlay, dataPoints, labels, colors) {
        overlay.innerHTML = `
            <div class="mbti-overlay-content">
                <div class="mbti-dimensions">
                    ${dataPoints.map((point, index) => `
                        <div class="mbti-dimension" style="animation: fadeInUp 0.6s ease ${index * 0.1}s both;">
                            <div class="dimension-label" style="color: ${colors[index]}">${labels[index]}</div>
                            <div class="dimension-score" style="color: ${colors[index]}">${point.score}%</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    updateList(containerId, items) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        if (items.length === 0) {
            container.innerHTML = '<p class="no-data">No data available</p>';
            return;
        }

        container.innerHTML = items.map(item => 
            `<div class="list-item">${item}</div>`
        ).join('');
    }

    updateDataSources(sources) {
        const container = document.getElementById('sources-list');
        if (!container) return;
        
        if (sources.length === 0) {
            container.innerHTML = '<p class="no-data">No data sources available</p>';
            return;
        }

        const sourcesHTML = sources.slice(0, 3).map(source => `
            <div class="source-item">
                <div class="source-type">${source.type}</div>
                <div class="source-text">${source.text?.substring(0, 100)}...</div>
                <div class="source-subreddit">r/${source.subreddit}</div>
            </div>
        `).join('');

        container.innerHTML = sourcesHTML;
    }

    setStatus(message, type = 'info') {
        const indicator = document.getElementById('status-indicator');
        if (!indicator) return;
        
        const statusText = indicator.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = message;
        }
        
        indicator.className = `status-indicator ${type}`;
    }

    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }

    showErrorMessage(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    exportJSON() {
        if (!this.currentPersona) {
            this.showErrorMessage('No persona to export');
            return;
        }

        const dataStr = JSON.stringify(this.currentPersona, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `${this.currentPersona.reddit_user || 'persona'}_data.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showSuccessMessage('JSON exported successfully!');
    }

    exportHTML() {
        if (!this.currentPersona) {
            this.showErrorMessage('No persona to export');
            return;
        }

        // Create a simple HTML report
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Persona Report - ${this.currentPersona.name}</title>
                <style>
                    body { 
                        font-family: 'Inter', sans-serif; 
                        margin: 40px; 
                        line-height: 1.6;
                        color: #333;
                    }
                    .header { text-align: center; margin-bottom: 30px; }
                    .section { margin: 20px 0; }
                    .trait { background: #f0f0f0; padding: 10px; margin: 5px 0; border-radius: 5px; }
                    .quote { font-style: italic; background: #f9f9f9; padding: 20px; border-left: 4px solid #667eea; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Persona Report</h1>
                    <h2>${this.currentPersona.name}</h2>
                    <p>${this.currentPersona.occupation} • ${this.currentPersona.location}</p>
                    <p><strong>Reddit:</strong> ${this.currentPersona.reddit_user}</p>
                </div>
                
                <div class="section">
                    <h3>Quote</h3>
                    <div class="quote">${this.currentPersona.quote}</div>
                </div>
                
                <div class="section">
                    <h3>Personality Traits</h3>
                    ${(this.currentPersona.traits || []).map(trait => `<div class="trait">${trait}</div>`).join('')}
                </div>
                
                <div class="section">
                    <h3>Goals</h3>
                    ${(this.currentPersona.goals || []).map(goal => `<div class="trait">${goal}</div>`).join('')}
                </div>
                
                <div class="section">
                    <h3>Behavior Habits</h3>
                    ${(this.currentPersona.behavior_habits || []).map(habit => `<div class="trait">${habit}</div>`).join('')}
                </div>
            </body>
            </html>
        `;

        const dataBlob = new Blob([htmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `${this.currentPersona.reddit_user || 'persona'}_report.html`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showSuccessMessage('HTML report exported successfully!');
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', function() {
    new PersonaDashboard('persona-dashboard');
}); 