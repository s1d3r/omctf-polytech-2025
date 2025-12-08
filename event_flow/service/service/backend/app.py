from flask import Flask, render_template, abort
from routes import api_bp
from flask_cors import CORS
from waitress import serve


app = Flask(__name__)

CORS(app,
     origins=["http://10.14.9.50:5000"],
     supports_credentials=True)         


app.register_blueprint(api_bp)


if __name__ == '__main__':
     serve(app, host='0.0.0.0', port=1337)
