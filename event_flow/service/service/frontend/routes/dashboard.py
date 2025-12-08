from . import dashboard_bp
from flask import render_template,session


@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')