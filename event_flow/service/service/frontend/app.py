from flask import Flask, render_template, abort
from errors import error_bp, register_error_handlers
from routes import auth_bp, dashboard_bp, profile_bp, event_bp
from waitress import serve

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(event_bp)
app.register_blueprint(error_bp)


register_error_handlers(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
