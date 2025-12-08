from . import profile_bp
from flask import render_template


@profile_bp.route('/profile')
def profile():
    return render_template('profile.html')