"""
RepoPulse - Production Application Entry Point
This file is used for deployment platforms like Railway, Heroku, etc.
"""

from server import app

if __name__ == '__main__':
    app.run() 