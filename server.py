"""
RepoPulse - Professional Repository Analysis & AI Detection
A Flask-based web application for analyzing Git repositories and detecting AI-generated code.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import json
from datetime import datetime
import re
from datetime import datetime, date
from config import config
from report_generator import report_generator




# Import the conservative detector
try:
    from conservative_detector import detect_ai_conservative
    CONSERVATIVE_DETECTOR_AVAILABLE = True
except ImportError:
    CONSERVATIVE_DETECTOR_AVAILABLE = False
    print("Warning: Conservative detector not available. Using fallback detection.")

# Import the AI keyword detector (highest priority)
try:
    from ai_keyword_detector import detect_ai_keywords
    KEYWORD_DETECTOR_AVAILABLE = True
except ImportError:
    KEYWORD_DETECTOR_AVAILABLE = False
    print("Warning: AI keyword detector not available. Using fallback detection.")

# Import the multi-language detector
try:
    from multi_language_analyzer import detect_ai_multi_language
    MULTI_LANGUAGE_DETECTOR_AVAILABLE = True
except ImportError:
    MULTI_LANGUAGE_DETECTOR_AVAILABLE = False
    print("Warning: Multi-language detector not available. Using fallback detection.")



app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

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
    """Normalize author names using dynamic configuration"""
    if not name:
        return name
    
    # Convert to lowercase and remove extra spaces
    normalized = name.lower().strip()
    
    # Apply normalization rules from config
    normalization_rules = config.get("name_mappings.normalization_rules", [])
    for rule in normalization_rules:
        pattern = rule.get("pattern", "")
        replacement = rule.get("replacement", "")
        if pattern:
            normalized = re.sub(pattern, replacement, normalized)
    
    # Get name mappings from config
    name_mappings = config.get_name_mappings()
    
    # Check if the normalized version matches any known mapping
    if normalized in name_mappings:
        return name_mappings[normalized]
    
    # If no special handling applies, return the original name
    return name

def detect_ai_code(commit_message, commit_date, file_path):
    """
    Dynamic AI detection using configuration
    Returns: (is_ai, confidence_score, confidence_breakdown)
    """
    if not commit_message:
        return False, 0.0, {}
    
    # Get AI keywords from config
    high_confidence_keywords = config.get_ai_keywords("high_confidence")
    medium_confidence_keywords = config.get_ai_keywords("medium_confidence")
    low_confidence_keywords = config.get_ai_keywords("low_confidence")
    
    # Get confidence thresholds from config
    thresholds = config.get("ai_detection.confidence_thresholds", {})
    high_threshold = thresholds.get("high", 0.8)
    medium_threshold = thresholds.get("medium", 0.6)
    low_threshold = thresholds.get("low", 0.4)
    minimum_threshold = thresholds.get("minimum", 0.25)
    
    # Convert to lowercase for case-insensitive matching
    message_lower = commit_message.lower()
    
    # Count AI indicators by confidence level
    high_indicators = sum(1 for keyword in high_confidence_keywords if keyword in message_lower)
    medium_indicators = sum(1 for keyword in medium_confidence_keywords if keyword in message_lower)
    low_indicators = sum(1 for keyword in low_confidence_keywords if keyword in message_lower)
    
    # Calculate confidence score
    confidence = 0.0
    
    if high_indicators >= 2:
        confidence = high_threshold
    elif high_indicators >= 1 or medium_indicators >= 2:
        confidence = medium_threshold
    elif medium_indicators >= 1 or low_indicators >= 3:
        confidence = low_threshold
    elif low_indicators >= 1:
        confidence = low_threshold * 0.5
    
    # File type analysis using config
    code_extensions = config.get_code_extensions()
    is_code_file = any(file_path.lower().endswith(ext) for ext in code_extensions) if file_path else False
    
    if not is_code_file:
        confidence *= 0.5  # Reduce confidence for non-code files
    
    # Cap confidence at 95% to account for uncertainty
    confidence = min(confidence, 0.95)
    
    # Consider AI if confidence > minimum threshold
    is_ai = confidence > minimum_threshold
    
    # Confidence breakdown for compatibility
    confidence_breakdown = {
        'message_patterns': confidence * 0.7,
        'time_based': confidence * 0.2,
        'file_type': confidence * 0.1,
        'commit_size': 0.0,
        'total': confidence
    }
    
    return is_ai, confidence, confidence_breakdown

def get_git_file_content(repo_path, commit_hash, file_path):
    """Get file content from Git for a specific commit"""
    try:
        # Clean up file path - remove any problematic characters
        clean_file_path = file_path.replace('}', '').replace('{', '')
        
        command = f'git show {commit_hash}:{clean_file_path}'
        stdout, stderr, returncode = run_git_command(repo_path, command)
        
        if returncode == 0:
            return stdout
        else:
            # Don't print every error to avoid spam - only log if it's a real issue
            if "does not exist" not in stderr and "No such file" not in stderr:
                print(f"Error getting file content: {stderr}")
            return None
    except Exception as e:
        print(f"Exception getting file content: {e}")
        return None



def is_code_file(filename):
    """Check if file is a code file using dynamic configuration"""
    if not filename:
        return False
    
    # Get file type configuration
    code_extensions = config.get_code_extensions()
    exclude_patterns = config.get_exclude_patterns()
    
    filename_lower = filename.lower()
    
    # Check if it's a code file
    is_code = any(filename_lower.endswith(ext) for ext in code_extensions)
    
    # Check if it should be excluded
    is_excluded = any(pattern in filename_lower for pattern in exclude_patterns)
    
    return is_code and not is_excluded

def analyze_repository_git(repo_path, start_date, end_date):
    """Analyze a Git repository and return developer statistics with AI detection and time-series data"""
    if not os.path.exists(repo_path):
        return {"error": f"Repository path does not exist: {repo_path}"}
    
    if not os.path.exists(os.path.join(repo_path, '.git')):
        return {"error": f"Not a Git repository: {repo_path}"}
    
    try:
        # Get repository name
        repo_name = os.path.basename(repo_path)
        
        # Get detailed git log with commit messages, dates, and file changes
        git_log_cmd = f'git log --since="{start_date}" --until="{end_date}" --format="%H|%an|%ad|%s" --date=short --numstat'
        stdout, stderr, returncode = run_git_command(repo_path, git_log_cmd)
        
        if returncode != 0:
            return {"error": f"Git command failed: {stderr}"}
        
        # Parse the output
        lines = stdout.split('\n')
        developer_stats = {}
        time_series_data = {}  # Daily AI statistics
        current_commit = None
        current_author = None
        current_date = None
        current_message = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a commit header line (contains commit hash)
            if '|' in line and len(line.split('|')) >= 4:
                # Parse commit header: hash|author|date|message
                parts = line.split('|')
                current_commit = parts[0]
                current_author = normalize_author_name(parts[1])
                current_date = parts[2]
                current_message = parts[3]
                
                # Initialize developer stats if not exists
                if current_author not in developer_stats:
                    developer_stats[current_author] = {
                        'commits': 0,
                        'linesAdded': 0,
                        'linesRemoved': 0,
                        'aiLinesAdded': 0,
                        'aiLinesRemoved': 0,
                        'aiCommits': 0,
                        'totalConfidence': 0.0,
                        'confidenceBreakdown': {
                            'message_patterns': 0.0,
                            'time_based': 0.0,
                            'file_type': 0.0,
                            'commit_size': 0.0
                        }
                    }
                
                developer_stats[current_author]['commits'] += 1
                
            elif current_author and re.match(r'^\d+\s+\d+', line):
                # This is a numstat line: added\tremoved\tfilename
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        added = int(parts[0]) if parts[0].isdigit() else 0
                        removed = int(parts[1]) if parts[1].isdigit() else 0
                        filename = parts[2] if len(parts) > 2 else ''
                        
                        # Only analyze code files
                        if is_code_file(filename):
                            # PRIORITY 1: Check for explicit AI keywords first (most reliable)
                            if KEYWORD_DETECTOR_AVAILABLE:
                                # Get file content for keyword analysis
                                file_content = get_git_file_content(repo_path, current_commit, filename)
                                
                                # Use keyword detector (highest priority)
                                keyword_result = detect_ai_keywords(current_message, file_content)
                                
                                if keyword_result.is_ai:
                                    # If keywords found, use this result
                                    is_ai = True
                                    confidence = keyword_result.confidence
                                    confidence_breakdown = {
                                        'keyword_analysis': confidence * 0.8,
                                        'message_patterns': confidence * 0.2,
                                        'time_based': 0.0,
                                        'file_type': 0.0,
                                        'commit_size': 0.0,
                                        'reasoning': keyword_result.reasoning,
                                        'keywords_found': keyword_result.keywords_found,
                                        'source': keyword_result.source
                                    }
                                else:
                                    # No keywords found, fall through to other detectors
                                    is_ai = False
                                    confidence = 0.0
                                    confidence_breakdown = {
                                        'keyword_analysis': 0.0,
                                        'message_patterns': 0.0,
                                        'time_based': 0.0,
                                        'file_type': 0.0,
                                        'commit_size': 0.0,
                                        'reasoning': keyword_result.reasoning,
                                        'keywords_found': [],
                                        'source': 'none'
                                    }
                            # PRIORITY 2: Use multi-language AI detection (supports C#, JavaScript, React)
                            elif MULTI_LANGUAGE_DETECTOR_AVAILABLE:
                                # Get file content for analysis
                                file_content = get_git_file_content(repo_path, current_commit, filename)
                                
                                # Use multi-language detector
                                is_ai, confidence, reasoning, language = detect_ai_multi_language(
                                    current_message, current_date, filename, file_content
                                )
                                
                                # Create confidence breakdown for multi-language analysis
                                confidence_breakdown = {
                                    'message_patterns': confidence * 0.3,
                                    'time_based': 0.0,
                                    'file_type': 0.0,
                                    'commit_size': 0.0,
                                    'multi_language_analysis': confidence * 0.7,
                                    'reasoning': reasoning,
                                    'language': language
                                }
                            elif CONSERVATIVE_DETECTOR_AVAILABLE:
                                # Fallback to conservative detector
                                file_content = get_git_file_content(repo_path, current_commit, filename)
                                is_ai, confidence, reasoning = detect_ai_conservative(
                                    current_message, current_date, filename, file_content
                                )
                                confidence_breakdown = {
                                    'message_patterns': confidence * 0.3,
                                    'time_based': 0.0,
                                    'file_type': 0.0,
                                    'commit_size': 0.0,
                                    'conservative_analysis': confidence * 0.7,
                                    'reasoning': reasoning
                                }
                            else:
                                # Fallback to simple analysis
                                is_ai, confidence, confidence_breakdown = detect_ai_code(current_message, current_date, filename)
                            
                            if is_ai:
                                ai_added = int(added * confidence)
                                ai_removed = int(removed * confidence)
                                
                                developer_stats[current_author]['aiLinesAdded'] += ai_added
                                developer_stats[current_author]['aiLinesRemoved'] += ai_removed
                                developer_stats[current_author]['totalConfidence'] += confidence
                                
                                # Update confidence breakdown
                                for key in confidence_breakdown:
                                    if key in developer_stats[current_author]['confidenceBreakdown']:
                                        developer_stats[current_author]['confidenceBreakdown'][key] += confidence_breakdown[key]
                                
                                # Count as AI commit if significant AI contribution
                                if ai_added > 0 or ai_removed > 0:
                                    developer_stats[current_author]['aiCommits'] += 1
                            
                            developer_stats[current_author]['linesAdded'] += added
                            developer_stats[current_author]['linesRemoved'] += removed
                            
                            # Collect time-series data
                            if current_date:
                                if current_date not in time_series_data:
                                    time_series_data[current_date] = {
                                        'totalLinesAdded': 0,
                                        'totalLinesRemoved': 0,
                                        'aiLinesAdded': 0,
                                        'aiLinesRemoved': 0,
                                        'commits': 0,
                                        'aiCommits': 0
                                    }
                                
                                time_series_data[current_date]['totalLinesAdded'] += added
                                time_series_data[current_date]['totalLinesRemoved'] += removed
                                time_series_data[current_date]['commits'] += 1
                                
                                if is_ai:
                                    time_series_data[current_date]['aiLinesAdded'] += ai_added
                                    time_series_data[current_date]['aiLinesRemoved'] += ai_removed
                                    time_series_data[current_date]['aiCommits'] += 1
                            
                    except ValueError:
                        continue
        
        # Convert to list and calculate percentages
        developer_list = []
        total_commits = 0
        total_lines_added = 0
        total_lines_removed = 0
        total_ai_lines_added = 0
        total_ai_lines_removed = 0
        total_ai_commits = 0
        
        for author, stats in developer_stats.items():
            # Calculate AI percentage
            ai_percentage = 0.0
            if stats['linesAdded'] > 0:
                ai_percentage = (stats['aiLinesAdded'] / stats['linesAdded']) * 100
            
            # Calculate average confidence breakdown
            avg_confidence_breakdown = {}
            if 'confidenceBreakdown' in stats:
                for key in stats['confidenceBreakdown']:
                    try:
                        avg_confidence_breakdown[key] = round(stats['confidenceBreakdown'][key] / max(stats['commits'], 1), 3)
                    except (KeyError, TypeError, ZeroDivisionError):
                        avg_confidence_breakdown[key] = 0.0
            
            developer_list.append({
                'name': author,
                'commits': stats['commits'],
                'linesAdded': stats['linesAdded'],
                'linesRemoved': stats['linesRemoved'],
                'aiLinesAdded': stats['aiLinesAdded'],
                'aiLinesRemoved': stats['aiLinesRemoved'],
                'aiCommits': stats['aiCommits'],
                'aiPercentage': round(ai_percentage, 1),
                'avgConfidence': round(stats['totalConfidence'] / max(stats['commits'], 1), 2),
                'confidenceBreakdown': avg_confidence_breakdown
            })
            
            total_commits += stats['commits']
            total_lines_added += stats['linesAdded']
            total_lines_removed += stats['linesRemoved']
            total_ai_lines_added += stats['aiLinesAdded']
            total_ai_lines_removed += stats['aiLinesRemoved']
            total_ai_commits += stats['aiCommits']
        
        # Calculate overall AI percentage
        overall_ai_percentage = 0.0
        if total_lines_added > 0:
            overall_ai_percentage = (total_ai_lines_added / total_lines_added) * 100
        
        # Sort by lines added (descending)
        developer_list.sort(key=lambda x: x['linesAdded'], reverse=True)
        
        # Process time-series data
        time_series_list = []
        for date_str in sorted(time_series_data.keys()):
            daily_data = time_series_data[date_str]
            ai_percentage = 0.0
            if daily_data['totalLinesAdded'] > 0:
                ai_percentage = (daily_data['aiLinesAdded'] / daily_data['totalLinesAdded']) * 100
            
            time_series_list.append({
                'date': date_str,
                'totalLinesAdded': daily_data['totalLinesAdded'],
                'totalLinesRemoved': daily_data['totalLinesRemoved'],
                'aiLinesAdded': daily_data['aiLinesAdded'],
                'aiLinesRemoved': daily_data['aiLinesRemoved'],
                'commits': daily_data['commits'],
                'aiCommits': daily_data['aiCommits'],
                'aiPercentage': round(ai_percentage, 1)
            })
        
        return {
            'name': repo_name,
            'path': repo_path,
            'startDate': start_date,
            'endDate': end_date,
            'totalCommits': total_commits,
            'totalLinesAdded': total_lines_added,
            'totalLinesRemoved': total_lines_removed,
            'totalAiLinesAdded': total_ai_lines_added,
            'totalAiLinesRemoved': total_ai_lines_removed,
            'totalAiCommits': total_ai_commits,
            'overallAiPercentage': round(overall_ai_percentage, 1),
            'developerStats': developer_list,
            'timeSeriesData': time_series_list
        }
        
    except Exception as e:
        return {"error": f"Error analyzing repository: {str(e)}"}

@app.route('/api/analyze', methods=['POST'])
def analyze_repositories():
    """API endpoint to analyze multiple repositories"""
    try:
        data = request.get_json()
        # Handle both 'repoPaths' (frontend) and 'repositories' (legacy)
        repo_paths = data.get('repoPaths', data.get('repositories', []))
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        
        if not repo_paths:
            return jsonify({"error": "No repository paths provided"}), 400
        
        if not start_date or not end_date:
            return jsonify({"error": "Start and end dates are required"}), 400
        
        results = []
        valid_results = []
        
        for repo_path in repo_paths:
            # Validate repository path
            if not os.path.exists(repo_path):
                results.append({
                    "error": f"Repository path does not exist: {repo_path}",
                    "name": os.path.basename(repo_path) if repo_path else "Unknown"
                })
                continue
                
            if not os.path.exists(os.path.join(repo_path, '.git')):
                results.append({
                    "error": f"Not a Git repository: {repo_path}",
                    "name": os.path.basename(repo_path) if repo_path else "Unknown"
                })
                continue
            
            result = analyze_repository_git(repo_path, start_date, end_date)
            results.append(result)
            
            # Check if this is a valid result (no error and has data)
            if 'error' not in result and result.get('totalCommits', 0) > 0:
                valid_results.append(result)
        
        # Return success if we have any valid results
        success = len(valid_results) > 0
        
        return jsonify({
            'success': success,
            'results': results,
            'validResults': valid_results,
            'totalRepos': len(repo_paths),
            'validRepos': len(valid_results)
        })
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "index.html not found", 404

@app.route('/<filename>')
def serve_static(filename):
    """Serve static files like script.js"""
    try:
        with open(filename, 'r') as f:
            if filename.endswith('.js'):
                return f.read(), 200, {'Content-Type': 'application/javascript'}
            return f.read()
    except FileNotFoundError:
        return f"{filename} not found", 404

@app.route('/api/ai-config', methods=['GET'])
def get_ai_config():
    """Get AI detection configuration and patterns"""
    ai_config = {
        'patterns': {
            'high_confidence': config.get_ai_keywords("high_confidence"),
            'medium_confidence': config.get_ai_keywords("medium_confidence"),
            'low_confidence': config.get_ai_keywords("low_confidence")
        },
        'file_confidence': {
            'high': config.get_code_extensions()[:5],  # First 5 extensions
            'medium': config.get_code_extensions()[5:10],  # Next 5 extensions
            'low': config.get_exclude_patterns()[:5]  # First 5 exclude patterns
        },
        'time_settings': {
            'time_bias_removed': True,
            'note': 'All commits treated equally regardless of date'
        },
        'confidence_thresholds': config.get("ai_detection.confidence_thresholds", {}),
        'keyword_detector': {
            'available': KEYWORD_DETECTOR_AVAILABLE,
            'priority': 'highest',
            'description': 'Detects explicit AI mentions in commit messages and file content',
            'high_confidence_keywords': config.get_ai_keywords("high_confidence") if KEYWORD_DETECTOR_AVAILABLE else [],
            'medium_confidence_keywords': config.get_ai_keywords("medium_confidence") if KEYWORD_DETECTOR_AVAILABLE else [],
            'total_keywords': len(config.get_ai_keywords("high_confidence")) + len(config.get_ai_keywords("medium_confidence")) if KEYWORD_DETECTOR_AVAILABLE else 0
        },
        'config_source': 'dynamic',
        'config_file': config.config_file
    }
    return jsonify(ai_config)



@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        'success': True,
        'config': config.config
    })

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update configuration
        for key, value in data.items():
            config.set(key, value)
        
        # Save configuration
        if config.save_config():
            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Configuration update failed: {str(e)}'}), 500

@app.route('/api/config/name-mappings', methods=['POST'])
def add_name_mapping():
    """Add a new name mapping"""
    try:
        data = request.get_json()
        normalized_name = data.get('normalized_name')
        display_name = data.get('display_name')
        
        if not normalized_name or not display_name:
            return jsonify({'error': 'normalized_name and display_name are required'}), 400
        
        if config.add_name_mapping(normalized_name, display_name):
            return jsonify({
                'success': True,
                'message': f'Name mapping added: {normalized_name} -> {display_name}'
            })
        else:
            return jsonify({'error': 'Failed to add name mapping'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to add name mapping: {str(e)}'}), 500

@app.route('/api/config/ai-keywords', methods=['POST'])
def add_ai_keyword():
    """Add a new AI keyword"""
    try:
        data = request.get_json()
        keyword = data.get('keyword')
        confidence_level = data.get('confidence_level', 'medium')
        
        if not keyword:
            return jsonify({'error': 'keyword is required'}), 400
        
        if confidence_level not in ['high', 'medium', 'low']:
            return jsonify({'error': 'confidence_level must be high, medium, or low'}), 400
        
        if config.add_ai_keyword(keyword, confidence_level):
            return jsonify({
                'success': True,
                'message': f'AI keyword added: {keyword} (confidence: {confidence_level})'
            })
        else:
            return jsonify({'error': 'Failed to add AI keyword'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to add AI keyword: {str(e)}'}), 500

@app.route('/api/config/reload', methods=['POST'])
def reload_config():
    """Reload configuration from file"""
    try:
        if config.reload():
            return jsonify({
                'success': True,
                'message': 'Configuration reloaded successfully'
            })
        else:
            return jsonify({'error': 'Failed to reload configuration'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to reload configuration: {str(e)}'}), 500

@app.route('/api/download/html', methods=['POST'])
def download_html_report():
    """Generate and download HTML report"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        # Generate HTML report
        html_path = report_generator.generate_html_report(data)
        
        if html_path and os.path.exists(html_path):
            return send_from_directory(
                directory=os.path.dirname(html_path),
                path=os.path.basename(html_path),
                as_attachment=True,
                download_name=os.path.basename(html_path)
            )
        else:
            return jsonify({'error': 'Failed to generate HTML report'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to generate HTML report: {str(e)}'}), 500



@app.route('/')
def index():
    """Serve the main application page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'config_loaded': True,
        'report_generator': {
            'html': 'available'
        }
    })

if __name__ == '__main__':
    host = config.get('server.host', '0.0.0.0')
    port = config.get('server.port', 5001)
    debug = config.get('server.debug', False)
    app.run(host=host, port=port, debug=debug) 