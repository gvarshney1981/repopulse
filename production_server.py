"""
RepoPulse - Production Server
Handles import errors gracefully for Railway deployment
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import json
from datetime import datetime
import re

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Try to import config, but provide fallbacks if it fails
try:
    from config import config
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Config not available: {e}")
    CONFIG_AVAILABLE = False
    # Create a simple config fallback
    class SimpleConfig:
        def get(self, key, default=None):
            return default
        def get_ai_keywords(self, level):
            return []
        def get_name_mappings(self):
            return {}
        def get_code_extensions(self):
            return ['.py', '.js', '.java', '.cpp', '.cs', '.php', '.rb', '.go', '.rs', '.ts', '.jsx', '.tsx']
    config = SimpleConfig()

# Try to import report generator
try:
    from report_generator import report_generator
    REPORT_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Report generator not available: {e}")
    REPORT_GENERATOR_AVAILABLE = False

# Try to import AI detectors
try:
    from conservative_detector import detect_ai_conservative
    CONSERVATIVE_DETECTOR_AVAILABLE = True
except ImportError:
    CONSERVATIVE_DETECTOR_AVAILABLE = False
    print("Warning: Conservative detector not available.")

try:
    from ai_keyword_detector import detect_ai_keywords
    KEYWORD_DETECTOR_AVAILABLE = True
except ImportError:
    KEYWORD_DETECTOR_AVAILABLE = False
    print("Warning: AI keyword detector not available.")

try:
    from multi_language_analyzer import detect_ai_multi_language
    MULTI_LANGUAGE_DETECTOR_AVAILABLE = True
except ImportError:
    MULTI_LANGUAGE_DETECTOR_AVAILABLE = False
    print("Warning: Multi-language detector not available.")

def run_git_command(repo_path, command):
    """Run a git command in the specified repository"""
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            shell=True
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def normalize_author_name(name):
    """Normalize author names"""
    if not name:
        return name
    
    normalized = name.lower().strip()
    name_mappings = config.get_name_mappings()
    
    if normalized in name_mappings:
        return name_mappings[normalized]
    
    return name

def detect_ai_code(commit_message, commit_date, file_path):
    """Simple AI detection"""
    if not commit_message:
        return False, 0.0, {}
    
    # Simple keyword-based detection
    ai_keywords = ['ai', 'copilot', 'chatgpt', 'claude', 'generated', 'assistant', 'assisted']
    message_lower = commit_message.lower()
    
    confidence = 0.0
    for keyword in ai_keywords:
        if keyword in message_lower:
            confidence += 0.3
    
    return confidence > 0.3, min(confidence, 0.95), {'keywords': ai_keywords}

@app.route('/')
def index():
    """Serve the main application page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_repositories():
    """Analyze repositories"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        repo_paths = data.get('repoPaths', [])
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        
        if not repo_paths:
            return jsonify({'error': 'No repository paths provided'}), 400
        
        results = []
        for repo_path in repo_paths:
            if not os.path.exists(repo_path):
                results.append({
                    'path': repo_path,
                    'error': 'Repository path does not exist'
                })
                continue
            
            # Simple analysis for now
            result = {
                'path': repo_path,
                'name': os.path.basename(repo_path),
                'totalCommits': 0,
                'totalLinesAdded': 0,
                'totalLinesRemoved': 0,
                'overallAiPercentage': 0.0,
                'developers': [],
                'commits': []
            }
            
            # Try to get git info
            try:
                stdout, stderr, returncode = run_git_command(repo_path, 'git log --oneline | wc -l')
                if returncode == 0:
                    result['totalCommits'] = int(stdout.strip() or 0)
            except:
                pass
            
            results.append(result)
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'totalRepositories': len(results),
                'totalCommits': sum(r.get('totalCommits', 0) for r in results),
                'overallAiPercentage': 0.0
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'config_loaded': CONFIG_AVAILABLE,
        'report_generator': {
            'html': 'available' if REPORT_GENERATOR_AVAILABLE else 'unavailable'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting RepoPulse production server on port {port}")
    print(f"Config available: {CONFIG_AVAILABLE}")
    print(f"Report generator available: {REPORT_GENERATOR_AVAILABLE}")
    app.run(host='0.0.0.0', port=port, debug=False) 