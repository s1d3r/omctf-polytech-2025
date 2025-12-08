from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
profile_bp = Blueprint('profile_bp', __name__)
event_bp = Blueprint('event_bp', __name__)

from . import auth, dashboard, profile, event