"""WSGI configuration for PythonAnywhere deployment.

This exposes the Flask WSGI callable as `application`.
Ensure the `PROJECT_PATH` points to your project folder.
"""

import os
import sys

# Configure project path
PROJECT_PATH = os.environ.get('PROJECT_PATH', '/home/Food123/stagcode')
if PROJECT_PATH and PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

from create_app import create_app

# Production environment defaults
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', '0')

application = create_app()

if __name__ == "__main__":
    application.run()
