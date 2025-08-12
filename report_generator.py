"""
RepoPulse Report Generator
Generate HTML reports from analysis results
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from jinja2 import Template

class RepoPulseReportGenerator:
    """Generate HTML reports from RepoPulse analysis results"""
    
    def __init__(self):
        pass
    

    
    def generate_html_report(self, analysis_data: Dict[str, Any], output_path: str = None) -> str:
        """Generate an HTML report from analysis data"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"repopulse_report_{timestamp}.html"
        
        # Debug: Print the structure of analysis_data
        print(f"DEBUG: analysis_data keys: {list(analysis_data.keys())}")
        if 'results' in analysis_data:
            print(f"DEBUG: Number of results: {len(analysis_data['results'])}")
            if analysis_data['results']:
                print(f"DEBUG: First result keys: {list(analysis_data['results'][0].keys())}")
                if 'developerStats' in analysis_data['results'][0]:
                    print(f"DEBUG: First developer keys: {list(analysis_data['results'][0]['developerStats'][0].keys()) if analysis_data['results'][0]['developerStats'] else 'No developers'}")
        
        # HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RepoPulse Analysis Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .title {
            color: #007bff;
            font-size: 2.5em;
            margin: 0;
        }
        .subtitle {
            color: #6c757d;
            font-size: 1.2em;
            margin: 10px 0 0 0;
        }
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .metadata-item {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .metadata-label {
            font-weight: bold;
            color: #495057;
        }
        .metadata-value {
            color: #212529;
            margin-top: 5px;
        }
        .summary-section {
            margin: 30px 0;
        }
        .section-title {
            color: #007bff;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .repo-section {
            margin: 40px 0;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }
        .repo-header {
            background-color: #007bff;
            color: white;
            padding: 20px;
        }
        .repo-name {
            font-size: 1.3em;
            margin: 0;
        }
        .repo-path {
            font-size: 0.9em;
            opacity: 0.8;
            margin: 5px 0 0 0;
        }
        .repo-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .repo-stat {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .repo-stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }
        .repo-stat-label {
            font-size: 0.8em;
            color: #6c757d;
            margin-top: 5px;
        }
        .dev-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .dev-table th {
            background-color: #007bff;
            color: white;
            padding: 12px;
            text-align: left;
        }
        .dev-table td {
            padding: 10px;
            border-bottom: 1px solid #e9ecef;
        }
        .dev-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .ai-highlight {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #6c757d;
        }
        @media print {
            body { background-color: white; }
            .container { box-shadow: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🫀 RepoPulse</h1>
            <p class="subtitle">Professional Repository Analysis & AI Detection Report</p>
        </div>
        
        <div class="metadata">
            <div class="metadata-item">
                <div class="metadata-label">Report Generated</div>
                <div class="metadata-value">{{ generation_time }}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Total Repositories</div>
                <div class="metadata-value">{{ total_repos }}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Valid Repositories</div>
                <div class="metadata-value">{{ valid_repos }}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Analysis Period</div>
                <div class="metadata-value">{{ start_date }} to {{ end_date }}</div>
            </div>
        </div>
        
        <div class="summary-section">
            <h2 class="section-title">📊 Analysis Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{{ total_commits }}</div>
                    <div class="stat-label">Total Commits</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ total_lines_added }}</div>
                    <div class="stat-label">Lines Added</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ total_lines_removed }}</div>
                    <div class="stat-label">Lines Removed</div>
                </div>

                <div class="stat-card">
                    <div class="stat-value">{{ total_ai_lines }}</div>
                    <div class="stat-label">AI Lines</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ ai_percentage }}%</div>
                    <div class="stat-label">AI Percentage</div>
                </div>
            </div>
        </div>
        
        {% for repo in repositories %}
        <div class="repo-section">
            <div class="repo-header">
                <h3 class="repo-name">📁 {{ repo.name }}</h3>
                <p class="repo-path">{{ repo.path }}</p>
            </div>
            <div style="padding: 20px;">
                <div class="repo-stats">
                    <div class="repo-stat">
                        <div class="repo-stat-value">{{ repo.totalCommits }}</div>
                        <div class="repo-stat-label">Total Commits</div>
                    </div>
                    <div class="repo-stat">
                        <div class="repo-stat-value">{{ repo.totalLinesAdded }}</div>
                        <div class="repo-stat-label">Lines Added</div>
                    </div>
                    <div class="repo-stat">
                        <div class="repo-stat-value">{{ repo.totalLinesRemoved }}</div>
                        <div class="repo-stat-label">Lines Removed</div>
                    </div>

                    <div class="repo-stat">
                        <div class="repo-stat-value">{{ repo.totalAiLinesAdded }}</div>
                        <div class="repo-stat-label">AI Lines</div>
                    </div>
                    <div class="repo-stat">
                        <div class="repo-stat-value">{{ "%.1f"|format(repo.overallAiPercentage) }}%</div>
                        <div class="repo-stat-label">AI Percentage</div>
                    </div>
                </div>
                
                {% if repo.developerStats %}
                <h4 style="color: #007bff; margin: 30px 0 15px 0;">👥 Developer Contributions</h4>
                <table class="dev-table">
                    <thead>
                        <tr>
                            <th>Developer</th>
                            <th>Commits</th>
                            <th>Lines Added</th>
                            <th>Lines Removed</th>
                            <th>AI Lines</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for dev in repo.developerStats[:10] %}
                        <tr>
                            <td>{{ dev.name }}</td>
                            <td>{{ dev.commits }}</td>
                            <td>{{ dev.linesAdded }}</td>
                            <td>{{ dev.linesRemoved }}</td>
                            <td>{{ dev.aiLinesAdded }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
            </div>
        </div>
        {% endfor %}
        
        <div class="footer">
            <p>Generated by RepoPulse - Professional Repository Analysis & AI Detection</p>
            <p>Report generated on {{ generation_time }}</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Prepare template data
        results = analysis_data.get('results', [])
        valid_results = [r for r in results if 'error' not in r]
        
        # Calculate totals
        total_commits = sum(r.get('totalCommits', 0) for r in valid_results)
        total_lines_added = sum(r.get('totalLinesAdded', 0) for r in valid_results)
        total_lines_removed = sum(r.get('totalLinesRemoved', 0) for r in valid_results)
        total_ai_lines = sum(r.get('totalAiLinesAdded', 0) for r in valid_results)
        ai_percentage = (total_ai_lines / max(total_lines_added, 1)) * 100
        
        template_data = {
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_repos': analysis_data.get('totalRepos', 0),
            'valid_repos': analysis_data.get('validRepos', 0),
            'start_date': analysis_data.get('startDate', 'N/A'),
            'end_date': analysis_data.get('endDate', 'N/A'),
            'total_commits': total_commits,
            'total_lines_added': total_lines_added,
            'total_lines_removed': total_lines_removed,
            'total_ai_lines': total_ai_lines,
            'ai_percentage': f"{ai_percentage:.1f}",
            'repositories': valid_results
        }
        
        # Render template
        template = Template(html_template)
        html_content = template.render(**template_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
# Global instance
report_generator = RepoPulseReportGenerator() 