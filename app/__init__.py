from flask import Flask
from dotenv import load_dotenv
load_dotenv('.env')
from config import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    @app.route('/')
    def home():
        return 'Hello World!</h1>'
    return app