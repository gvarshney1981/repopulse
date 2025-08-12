// Global variables
let analysisResults = [];
let repositoryHistory = [];

// Repository history management
function loadRepositoryHistory() {
    const saved = localStorage.getItem('gitanalyser_history');
    if (saved) {
        repositoryHistory = JSON.parse(saved);
        updateHistoryDisplay();
    }
}

function saveRepositoryHistory() {
    localStorage.setItem('gitanalyser_history', JSON.stringify(repositoryHistory));
}

function addToHistory(repoPaths) {
    const paths = repoPaths.split('\n').filter(path => path.trim());
    const timestamp = new Date().toISOString();
    
    // Add new entry to history
    const historyEntry = {
        paths: paths,
        timestamp: timestamp,
        date: new Date().toLocaleString()
    };
    
    // Remove duplicates and keep only last 10 entries
    repositoryHistory = repositoryHistory.filter(entry => 
        JSON.stringify(entry.paths) !== JSON.stringify(paths)
    );
    repositoryHistory.unshift(historyEntry);
    repositoryHistory = repositoryHistory.slice(0, 10);
    
    saveRepositoryHistory();
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
    const historyContainer = document.getElementById('historyContainer');
    if (!historyContainer) return;
    
    if (repositoryHistory.length === 0) {
        historyContainer.innerHTML = '<p class="text-muted">No previous searches</p>';
        return;
    }
    
    let html = '<h6 class="mb-2">Recent Searches:</h6>';
    repositoryHistory.forEach((entry, index) => {
        const pathsText = entry.paths.join(', ');
        html += `
            <div class="history-item mb-2 p-2 border rounded">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <small class="text-muted">${entry.date}</small>
                        <div class="mt-1">
                            <strong>Repositories:</strong> ${pathsText}
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary ms-2" onclick="loadFromHistory(${index})">
                        <i class="fas fa-undo"></i> Load
                    </button>
                </div>
            </div>
        `;
    });
    
    historyContainer.innerHTML = html;
}

function loadFromHistory(index) {
    if (index >= 0 && index < repositoryHistory.length) {
        const entry = repositoryHistory[index];
        document.getElementById('repoPaths').value = entry.paths.join('\n');
    }
}

function getAiBadgeColor(percentage) {
    if (percentage >= 70) return 'bg-danger';      // High AI: Red
    if (percentage >= 40) return 'bg-warning';     // Medium AI: Yellow
    if (percentage >= 20) return 'bg-info';        // Low AI: Blue
    return 'bg-secondary';                         // Very Low AI: Gray
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set default dates (last 30 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
    document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
    
    // Load repository history
    loadRepositoryHistory();
});

// Main analysis function
async function analyzeRepositories() {
    const repoPaths = document.getElementById('repoPaths').value.trim();
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!repoPaths) {
        showError('Please enter at least one repository path');
        return;
    }

    if (!startDate || !endDate) {
        showError('Please select both start and end dates');
        return;
    }

    const paths = repoPaths.split('\n').filter(path => path.trim());
    
    showLoading(true);
    hideError();

    try {
        analysisResults = [];
        
        for (const path of paths) {
            const result = await analyzeRepository(path.trim(), startDate, endDate);
            if (result) {
                analysisResults.push(result);
            }
        }

        if (analysisResults.length > 0) {
            displayResults();
        } else {
            showError('No valid repositories found or no data available for the specified date range');
        }
    } catch (error) {
        showError('Error analyzing repositories: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Analyze repositories using the backend API
async function analyzeRepositories() {
    const repoPaths = document.getElementById('repoPaths').value.trim();
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!repoPaths) {
        showError('Please enter at least one repository path');
        return;
    }

    if (!startDate || !endDate) {
        showError('Please select both start and end dates');
        return;
    }

    const paths = repoPaths.split('\n').filter(path => path.trim());
    
    showLoading(true);
    hideError();

    try {
        const response = await fetch('http://localhost:5001/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                repoPaths: paths,
                startDate: startDate,
                endDate: endDate
            })
        });

        const data = await response.json();
        
        if (data.success) {
            analysisResults = data.validResults || data.results.filter(result => !result.error);
            if (analysisResults.length > 0) {
                // Save to history on successful analysis
                addToHistory(repoPaths);
                displayResults();
            } else {
                // Show detailed error information
                let errorMessage = 'No valid repositories found or no data available for the specified date range.';
                if (data.totalRepos > 0 && data.validRepos === 0) {
                    errorMessage = `Analyzed ${data.totalRepos} repositories but found no data in the specified date range (${startDate} to ${endDate}).`;
                }
                showError(errorMessage);
            }
        } else {
            // Show detailed error information
            let errorMessage = data.error || 'Failed to analyze repositories';
            if (data.results && data.results.length > 0) {
                const errors = data.results.filter(r => r.error).map(r => `${r.name}: ${r.error}`).join(', ');
                errorMessage = `Repository errors: ${errors}`;
            }
            showError(errorMessage);
        }
    } catch (error) {
        showError('Error connecting to analysis server. Make sure the backend is running.');
        console.error('Error:', error);
    } finally {
        showLoading(false);
    }
}

// Display results
function displayResults() {
    displaySummaryCards();
    displayRepositoryResults();
    displayAiTrendChart();
    displayCombinedStats();
    document.getElementById('resultsSection').style.display = 'block';
    
    // Show download button
    document.getElementById('downloadBtn').style.display = 'inline-block';
}

// Display summary cards
function displaySummaryCards() {
    const summaryCards = document.getElementById('summaryCards');
    const totalRepos = analysisResults.length;
    const totalCommits = analysisResults.reduce((sum, repo) => sum + repo.totalCommits, 0);
    const totalLinesAdded = analysisResults.reduce((sum, repo) => sum + repo.totalLinesAdded, 0);
    const totalLinesRemoved = analysisResults.reduce((sum, repo) => sum + repo.totalLinesRemoved, 0);
    
    // Calculate AI statistics
    const totalAiLinesAdded = analysisResults.reduce((sum, repo) => sum + (repo.totalAiLinesAdded || 0), 0);
    const totalAiLinesRemoved = analysisResults.reduce((sum, repo) => sum + (repo.totalAiLinesRemoved || 0), 0);
    const totalAiCommits = analysisResults.reduce((sum, repo) => sum + (repo.totalAiCommits || 0), 0);
    const overallAiPercentage = totalLinesAdded > 0 ? ((totalAiLinesAdded / totalLinesAdded) * 100) : 0;

    summaryCards.innerHTML = `
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-folder fa-2x text-primary mb-2"></i>
                    <h4 class="card-title">${totalRepos}</h4>
                    <p class="card-text">Repositories</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-code-commit fa-2x text-success mb-2"></i>
                    <h4 class="card-title">${totalCommits.toLocaleString()}</h4>
                    <p class="card-text">Total Commits</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-plus-circle fa-2x text-info mb-2"></i>
                    <h4 class="card-title">${totalLinesAdded.toLocaleString()}</h4>
                    <p class="card-text">Lines Added</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-minus-circle fa-2x text-warning mb-2"></i>
                    <h4 class="card-title">${totalLinesRemoved.toLocaleString()}</h4>
                    <p class="card-text">Lines Removed</p>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <div class="card-body text-center text-white">
                    <i class="fas fa-robot fa-2x mb-2"></i>
                    <h4 class="card-title">${overallAiPercentage.toFixed(1)}%</h4>
                    <p class="card-text">AI Generated</p>
                    <small class="text-white-50">${totalAiLinesAdded.toLocaleString()} lines</small>
                </div>
            </div>
        </div>
    `;
}

// Display repository results
function displayRepositoryResults() {
    const repoResults = document.getElementById('repoResults');
    
    let html = '';
    
    analysisResults.forEach((repo, index) => {
        html += `
            <div class="card repo-card mb-4">
                <div class="card-header">
                    <h6 class="mb-0">
                        <i class="fas fa-folder me-2"></i>
                        ${repo.name}
                    </h6>
                    <small class="text-muted">${repo.path}</small>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <strong>Total Commits:</strong> ${repo.totalCommits.toLocaleString()}
                        </div>
                        <div class="col-md-3">
                            <strong>Lines Added:</strong> ${repo.totalLinesAdded.toLocaleString()}
                        </div>
                        <div class="col-md-3">
                            <strong>Lines Removed:</strong> ${repo.totalLinesRemoved.toLocaleString()}
                        </div>
                        <div class="col-md-3">
                            <strong>AI Generated:</strong> 
                            <span class="badge bg-primary">${(repo.overallAiPercentage || 0).toFixed(1)}%</span>
                            <small class="text-muted">(${(repo.totalAiLinesAdded || 0).toLocaleString()} lines)</small>
                        </div>
                        <div class="col-md-3">
                            <strong>Net Change:</strong> ${(repo.totalLinesAdded - repo.totalLinesRemoved).toLocaleString()}
                        </div>
                    </div>
                    
                    <h6>Developer Contributions:</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Developer</th>
                                    <th>Commits</th>
                                    <th>Lines Added</th>
                                    <th>Lines Removed</th>
                                    <th>Net Change</th>
                                    <th>AI Generated</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${repo.developerStats.map(dev => `
                                    <tr>
                                        <td>${dev.name}</td>
                                        <td>${dev.commits}</td>
                                        <td class="text-success">+${dev.linesAdded.toLocaleString()}</td>
                                        <td class="text-danger">-${dev.linesRemoved.toLocaleString()}</td>
                                        <td class="${dev.linesAdded - dev.linesRemoved >= 0 ? 'text-success' : 'text-danger'}">
                                            ${dev.linesAdded - dev.linesRemoved >= 0 ? '+' : ''}${(dev.linesAdded - dev.linesRemoved).toLocaleString()}
                                        </td>
                                        <td>
                                            <span class="badge ${getAiBadgeColor(dev.aiPercentage || 0)}">${(dev.aiPercentage || 0).toFixed(1)}%</span>
                                            <small class="text-muted">(${(dev.aiLinesAdded || 0).toLocaleString()} lines)</small>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="chart-${index}"></canvas>
                    </div>
                </div>
            </div>
        `;
    });
    
    repoResults.innerHTML = html;
    
    // Create charts after DOM is updated
    setTimeout(() => {
        analysisResults.forEach((repo, index) => {
            createChart(`chart-${index}`, repo.developerStats);
        });
    }, 100);
}

// Display combined statistics
function displayCombinedStats() {
    const combinedStats = document.getElementById('combinedStats');
    
    // Aggregate developer stats across all repositories
    const developerMap = new Map();
    
    analysisResults.forEach(repo => {
        repo.developerStats.forEach(dev => {
            // Normalize the developer name for consistent merging
            const normalizedName = normalizeDeveloperName(dev.name);
            
            if (developerMap.has(normalizedName)) {
                const existing = developerMap.get(normalizedName);
                existing.commits += dev.commits;
                existing.linesAdded += dev.linesAdded;
                existing.linesRemoved += dev.linesRemoved;
                existing.aiLinesAdded += (dev.aiLinesAdded || 0);
                existing.aiLinesRemoved += (dev.aiLinesRemoved || 0);
                existing.aiCommits += (dev.aiCommits || 0);
            } else {
                developerMap.set(normalizedName, {
                    name: normalizedName,
                    commits: dev.commits,
                    linesAdded: dev.linesAdded,
                    linesRemoved: dev.linesRemoved,
                    aiLinesAdded: dev.aiLinesAdded || 0,
                    aiLinesRemoved: dev.aiLinesRemoved || 0,
                    aiCommits: dev.aiCommits || 0
                });
            }
        });
    });
    
    const combinedDeveloperStats = Array.from(developerMap.values())
        .sort((a, b) => b.linesAdded - a.linesAdded);
    
    let html = `
        <div class="table-responsive">
            <table class="table table-light">
                <thead>
                    <tr>
                        <th>Developer</th>
                        <th>Total Commits</th>
                        <th>Total Lines Added</th>
                        <th>Total Lines Removed</th>
                        <th>Net Change</th>
                        <th>AI Generated</th>
                        <th>Contribution %</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    const totalLinesAdded = combinedDeveloperStats.reduce((sum, dev) => sum + dev.linesAdded, 0);
    
    combinedDeveloperStats.forEach(dev => {
        const netChange = dev.linesAdded - dev.linesRemoved;
        const contributionPercent = totalLinesAdded > 0 ? ((dev.linesAdded / totalLinesAdded) * 100).toFixed(1) : 0;
        const aiPercentage = dev.linesAdded > 0 ? ((dev.aiLinesAdded / dev.linesAdded) * 100) : 0;
        
        html += `
            <tr>
                <td><strong>${dev.name}</strong></td>
                <td>${dev.commits.toLocaleString()}</td>
                <td class="text-success">+${dev.linesAdded.toLocaleString()}</td>
                <td class="text-danger">-${dev.linesRemoved.toLocaleString()}</td>
                <td class="${netChange >= 0 ? 'text-success' : 'text-danger'}">
                    ${netChange >= 0 ? '+' : ''}${netChange.toLocaleString()}
                </td>
                <td>
                    <span class="badge ${getAiBadgeColor(aiPercentage)}">${aiPercentage.toFixed(1)}%</span>
                    <small class="text-muted">(${dev.aiLinesAdded.toLocaleString()} lines)</small>
                </td>
                <td><span class="badge bg-primary">${contributionPercent}%</span></td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    combinedStats.innerHTML = html;
}

// Normalize developer names for consistent merging
function normalizeDeveloperName(name) {
    if (!name) return name;
    
    // Convert to lowercase and remove extra spaces
    const normalized = name.toLowerCase().trim().replace(/\s+/g, '');
    
    // Handle common variations
    const nameMappings = {
        'sonikumari': 'Soni Kumari',
        'mukundsingh': 'Mukund Singh',
        'vaibhavbhatia': 'Vaibhav Bhatia',
        'siddharthvatsal': 'Siddharth Vatsal',
        'shiwanshukashyap': 'Shiwanshu Kashyap',
        'nidhibansal': 'Nidhi Bansal',
        'nikhilmanglik': 'Nikhil Manglik',
        'akashgupta1': 'Akash Gupta'
    };
    
    return nameMappings[normalized] || name;
}

// Create chart for repository
function createChart(canvasId, developerStats) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const labels = developerStats.map(dev => dev.name);
    const data = developerStats.map(dev => dev.linesAdded);
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
    ];
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Lines Added',
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Lines of Code'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Developers'
                    }
                }
            }
        }
    });
}

// Utility functions
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function clearResults() {
    analysisResults = [];
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('repoPaths').value = '';
    
    // Hide download button
    document.getElementById('downloadBtn').style.display = 'none';
    
    hideError();
}

// AI Trend Chart Functions
let aiTrendChart = null;

function displayAiTrendChart() {
    if (aiTrendChart) {
        aiTrendChart.destroy();
    }
    
    const ctx = document.getElementById('aiTrendChart');
    if (!ctx) return;
    
    // Collect all time series data from repositories
    const allTimeData = [];
    analysisResults.forEach(repo => {
        if (repo.timeSeriesData) {
            repo.timeSeriesData.forEach(dayData => {
                allTimeData.push({
                    date: dayData.date,
                    repoName: repo.name,
                    ...dayData
                });
            });
        }
    });
    
    if (allTimeData.length === 0) {
        ctx.style.display = 'none';
        return;
    }
    
    ctx.style.display = 'block';
    
    // Sort by date
    allTimeData.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Aggregate data based on selected aggregation
    const aggregation = document.getElementById('trendAggregation').value;
    const aggregatedData = aggregateTimeData(allTimeData, aggregation);
    
    // Get chart type
    const chartType = document.getElementById('trendChartType').value;
    
    // Create chart
    aiTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: aggregatedData.labels,
            datasets: aggregatedData.datasets.map((dataset, index) => ({
                label: dataset.label,
                data: dataset.data,
                borderColor: getChartColor(index),
                backgroundColor: getChartColor(index) + '20',
                borderWidth: 2,
                fill: false,
                tension: 0.4
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `AI Generation Trend (${aggregation}) - ${chartType}`
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: chartType === 'percentage' ? 'AI Percentage (%)' : 
                              chartType === 'lines' ? 'AI Lines Added' : 'AI Commits'
                    }
                }
            }
        }
    });
}

function aggregateTimeData(timeData, aggregation) {
    const aggregated = {};
    const labels = [];
    
    timeData.forEach(data => {
        let key;
        const date = new Date(data.date);
        
        switch (aggregation) {
            case 'weekly':
                const weekStart = new Date(date);
                weekStart.setDate(date.getDate() - date.getDay());
                key = weekStart.toISOString().split('T')[0];
                break;
            case 'monthly':
                key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                break;
            default: // daily
                key = data.date;
        }
        
        if (!aggregated[key]) {
            aggregated[key] = {
                totalLinesAdded: 0,
                aiLinesAdded: 0,
                commits: 0,
                aiCommits: 0,
                repos: new Set()
            };
            labels.push(key);
        }
        
        aggregated[key].totalLinesAdded += data.totalLinesAdded;
        aggregated[key].aiLinesAdded += data.aiLinesAdded;
        aggregated[key].commits += data.commits;
        aggregated[key].aiCommits += data.aiCommits;
        aggregated[key].repos.add(data.repoName);
    });
    
    // Calculate percentages and prepare datasets
    const chartType = document.getElementById('trendChartType').value;
    const datasets = [];
    
    if (chartType === 'percentage') {
        const percentageData = labels.map(label => {
            const data = aggregated[label];
            return data.totalLinesAdded > 0 ? 
                (data.aiLinesAdded / data.totalLinesAdded) * 100 : 0;
        });
        
        datasets.push({
            label: 'AI Percentage',
            data: percentageData
        });
    } else if (chartType === 'lines') {
        const linesData = labels.map(label => aggregated[label].aiLinesAdded);
        datasets.push({
            label: 'AI Lines Added',
            data: linesData
        });
    } else if (chartType === 'commits') {
        const commitsData = labels.map(label => aggregated[label].aiCommits);
        datasets.push({
            label: 'AI Commits',
            data: commitsData
        });
    }
    
    return { labels, datasets };
}

function updateTrendChart() {
    if (analysisResults.length > 0) {
        displayAiTrendChart();
    }
}

function getChartColor(index) {
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
    ];
    return colors[index % colors.length];
}

// Download report functionality
async function downloadReport() {
    if (!analysisResults || analysisResults.length === 0) {
        showError('No analysis results available for download.');
        return;
    }

    try {
        // Show loading state
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Generating...';
        button.disabled = true;

        // Prepare analysis data for download
        const downloadData = {
            results: analysisResults,
            totalRepos: analysisResults.length,
            validRepos: analysisResults.filter(r => !r.error).length,
            startDate: document.getElementById('startDate').value,
            endDate: document.getElementById('endDate').value,
            generationTime: new Date().toISOString()
        };

        // Make the download request
        const response = await fetch('/api/download/html', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(downloadData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Download failed');
        }

        // Get the filename from the response headers
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `repopulse_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.html`;
        
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="(.+)"/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        // Create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // Show success message
        showSuccessMessage(`HTML report downloaded successfully!`);

    } catch (error) {
        console.error('Download error:', error);
        showError(`Failed to download report: ${error.message}`);
    } finally {
        // Restore button state
        const button = event.target;
        button.innerHTML = '<i class="fas fa-download me-1"></i>Download Report';
        button.disabled = false;
    }
}

// Show success message
function showSuccessMessage(message) {
    // Create success alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
} 