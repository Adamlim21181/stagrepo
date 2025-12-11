"""WSGI configuration for PythonAnywhere deployment.

This exposes the Flask WSGI callable as `application`.
Ensure the `PROJECT_PATH` points to your project folder.
"""

import os
import sys

# Configure project path
PROJECT_PATH = os.environ.get('PROJECT_PATH', '/home/yourusername/stagcode')
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Production environment defaults
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', '0')

from create_app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
