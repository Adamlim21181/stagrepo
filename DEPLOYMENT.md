Deployment Guide

Local Development
- Create virtual environment: `python -m venv env`
- Activate (PowerShell): `./env/Scripts/Activate.ps1`
- Install deps: `pip install -r requirements.txt`
- Optional env vars:
   - `FLASK_DEBUG=1` to enable debug
   - `FLASK_HOST=0.0.0.0` and `FLASK_PORT=5000` to customize run
   - `SECRET_KEY` set to a strong random value
- Run app: `python run.py`

.env Support
- Create a `.env` file in project root to store secrets safely (not committed):
   - Example:
      - `SECRET_KEY=super-long-random-string`
      - `FLASK_DEBUG=1`
      - `MYSQL_USER=...`, `MYSQL_PASSWORD=...`, `MYSQL_HOST=...`, `MYSQL_DATABASE=...`
- `create_app.py` will auto-load `.env` if `python-dotenv` is installed.

Database Configuration
- MySQL (PythonAnywhere paid): set env vars `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_DATABASE`
- SQLite fallback: created at `stagdata.db` in project root

PythonAnywhere Deployment
- Set `PROJECT_PATH` env to your project directory (e.g., `/home/<username>/stagcode`)
- Ensure `FLASK_ENV=production` and `FLASK_DEBUG=0`
- WSGI file uses `create_app()` from `create_app.py`
- After updating code, reload the web app via PythonAnywhere dashboard

Environment Variables Reference
- `SECRET_KEY`: required in production; do not hardcode
- `FLASK_DEBUG`: `0` or `1`
- `FLASK_HOST`, `FLASK_PORT`: local run overrides
- `PROJECT_PATH`: PythonAnywhere project path
- `MYSQL_*`: MySQL connection settings for production

Notes
- Avoid committing secrets; use environment or platform config.
- Ensure `requirements.txt` is up to date after adding packages.
# Deploying Your Flask App to PythonAnywhere

## Step-by-Step Deployment Guide

### 1. Create a PythonAnywhere Account
- Go to https://www.pythonanywhere.com/
- Sign up for a free account (Beginner account supports one web app)
- Note your username - you'll need it for configuration

### 2. Upload Your Project Files

#### Option A: Using Git (Recommended)
1. Push your project to GitHub (if not already done)
2. In PythonAnywhere, open a Bash console
3. Clone your repository:
   ```bash
   git clone https://github.com/Adamlim21181/stagrepo.git stagcode
   cd stagcode
   ```

#### Option B: Upload Files Manually
1. Go to the "Files" tab in PythonAnywhere dashboard
2. Navigate to your home directory (`/home/yourusername/`)
3. Create a new folder called `stagcode`
4. Upload all your project files to this folder

### 3. Set Up Virtual Environment
In a PythonAnywhere Bash console:
```bash
cd ~/stagcode
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure the Web App
1. Go to the "Web" tab in your PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10
5. Click "Next"

### 5. Configure WSGI File
1. In the Web tab, find the "Code" section
2. Click on the WSGI configuration file link
3. Replace the entire content with the content from your `wsgi.py` file
4. **IMPORTANT**: Change `yourusername` in the paths to your actual PythonAnywhere username

### 6. Set Virtual Environment Path
1. In the Web tab, find the "Virtualenv" section
2. Enter the path to your virtual environment:
   ```
   /home/yourusername/stagcode/venv
   ```
   (Replace `yourusername` with your actual username)

### 7. Initialize Database
In a PythonAnywhere Bash console:
```bash
cd ~/stagcode
source venv/bin/activate

# Create a temporary database initialization script
cat > init_db.py << 'EOF'
from extensions import db
import models
from flask import Flask
import os

# Create a minimal app for database initialization
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "stagdata.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
EOF

# Run the initialization script
python3.10 init_db.py

# Clean up the temporary script
rm init_db.py
```

### 8. Set Static Files (Optional)
If you have custom static files:
1. In the Web tab, go to the "Static files" section
2. Add a new static file mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/stagcode/static/`

### 9. Reload and Test
1. Click the green "Reload" button in the Web tab
2. Visit your app at: `https://yourusername.pythonanywhere.com`

## MySQL Database Setup (Paid Accounts Only)

If you have a PythonAnywhere Hacker account or higher, you can use MySQL instead of SQLite:

### 1. Create MySQL Database
1. Go to the "Databases" tab in your PythonAnywhere dashboard
2. Create a new MySQL database (e.g., `Food123$stagdata`)
3. Note the database details provided

### 2. Set Environment Variables
In your PythonAnywhere Bash console:
```bash
# Add these to your .bashrc file for persistence
echo 'export MYSQL_USER="Food123"' >> ~/.bashrc
echo 'export MYSQL_PASSWORD="Food123$stagdata"' >> ~/.bashrc
echo 'export MYSQL_HOST="Food123.mysql.pythonanywhere-services.com"' >> ~/.bashrc
echo 'export MYSQL_DATABASE="Food123$default"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Initialize MySQL Database
```bash
cd ~/stagcode
source venv/bin/activate

# Create MySQL initialization script
cat > init_mysql.py << 'EOF'
from extensions import db
import models
from flask import Flask
import os

# Create app with MySQL configuration
app = Flask(__name__)
mysql_user = os.environ.get('MYSQL_USER')
mysql_password = os.environ.get('MYSQL_PASSWORD')
mysql_host = os.environ.get('MYSQL_HOST') 
mysql_database = os.environ.get('MYSQL_DATABASE')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print('MySQL database tables created successfully!')
EOF

# Run the MySQL initialization
python3.10 init_mysql.py
rm init_mysql.py
```

## Important Configuration Notes

### Database Choice
- **SQLite (Free accounts):** Simple, works great for small to medium sites
- **MySQL (Paid accounts):** Better for larger sites, multiple concurrent users, production scaling

### Security Considerations
- Change the `SECRET_KEY` in `create_app.py` to something more secure for production
- Consider using environment variables for sensitive data

### Database Location
The app is configured to create the SQLite database in your project directory. The database file will be at:
`/home/yourusername/stagcode/stagdata.db`

### Debugging
- If something goes wrong, check the error logs in the Web tab
- Make sure all file paths in `wsgi.py` use your actual username
- Ensure the virtual environment path is correct

### Free Account Limitations
- One web app only
- Limited CPU time per day
- App goes to sleep after inactivity (wakes up when accessed)
- Custom domains not available on free accounts

## Troubleshooting Common Issues

1. **ImportError**: Check that all dependencies are installed in the virtual environment
2. **Database errors**: Make sure you've run the database initialization step
3. **Static files not loading**: Check the static files configuration in the Web tab
4. **404 errors**: Ensure your WSGI file paths are correct

Your Flask gymnastics application should now be live on PythonAnywhere!