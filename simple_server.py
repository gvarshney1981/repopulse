"""
Simple RepoPulse Server for Railway
"""

from flask import Flask, send_file, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main page"""
    try:
        return send_file('index.html')
    except Exception as e:
        return f"Error loading index.html: {str(e)}", 500

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'RepoPulse is running!'
    })

@app.route('/script.js')
def script():
    """Serve JavaScript"""
    try:
        return send_file('script.js')
    except Exception as e:
        return f"Error loading script.js: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting simple RepoPulse server on port {port}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    app.run(host='0.0.0.0', port=port, debug=False) 