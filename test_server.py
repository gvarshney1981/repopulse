"""
Minimal test server for Railway deployment debugging
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "RepoPulse is running! 🚀"

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'port': os.environ.get('PORT', 'not set')
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting test server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 