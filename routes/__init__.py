from flask import Blueprint, session

# Create the main blueprint that all other route modules will use
main = Blueprint('main', __name__)


@main.context_processor  # Ensures this is run before any other routes
def inject_user():
    """Inject user session data into all templates."""
    return dict(
        logged_in='user_id' in session,
        user_roles=session.get('roles', []),
        is_admin='admin' in session.get('roles', []),
        is_judge='judges' in session.get('roles', []),
        user_id=session.get('user_id')
    )


# Import all route modules to register them with the blueprint
from . import home
from . import auth
from . import gymnasts
from . import competitions
from . import entries
from . import live
from . import scoring
from . import results
from . import admin
from . import calendar
from . import topnz
from . import profiles
