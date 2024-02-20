from flask import Flask
from dotenv import load_dotenv
load_dotenv('.env')
from config import Config
from flask_migrate import Migrate
from app.extensions import db
from app.models.camera import Camera
from app.models.object_detection import ObjectDetection


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route('/')
    def home():
        return 'Hello World!</h1>'
    return app