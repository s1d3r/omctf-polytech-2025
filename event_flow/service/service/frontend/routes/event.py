from . import event_bp
from flask import render_template, abort

@event_bp.route('/event/<id>')
def event(id):
    return render_template('event.html')