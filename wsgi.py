"""
WSGI entry point for RepoPulse
This file is used by gunicorn for production deployment
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from server import app

# For direct execution
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 