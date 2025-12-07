#!/var/www/yourusername_pythonanywhere_com_wsgi.py
"""
WSGI configuration for Flask application on PythonAnywhere.

This file contains the WSGI callable as a module-level variable named 'application'.
Replace 'yourusername' in the paths below with your actual PythonAnywhere username.
"""

import sys
import os

# Add your project directory to the Python path
path = '/home/Food123/stagcode'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables if needed
os.environ.setdefault('FLASK_ENV', 'production')

# Import your Flask application
from create_app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()