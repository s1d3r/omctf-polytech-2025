from flask import render_template
from flask import Blueprint, render_template

error_bp = Blueprint('error', __name__)


def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', status_code=404, status_text='Oops! The page you are looking for does not exist.'), 200


    @app.errorhandler(500)
    def internal_server_error():
        return render_template('error.html', status_code=500, status_text='Something went wrong on the server.'), 200

    @app.errorhandler(Exception)
    def handle_all_exceptions(e):
        if isinstance(e, HTTPException):
            code = e.code
            description = e.description
        else:
            code = 500
            description = str(e) or 'An unexpected error occurred.'

        return render_template(
            'error.html',
            status_code=code,
            status_text=description
        ), 200
