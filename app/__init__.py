from flask import Flask
from dotenv import load_dotenv
load_dotenv('.env')
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.route('/')
    def home():
        return 'Hello World!</h1>'
    return app