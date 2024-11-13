import threading
from flask import Flask
from .extensions import db  # Importar db desde extensions
from .routes.main import main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

        # Pasa `db` a `train_model`
        from .ml.model import train_model
        train_model(db)

    app.register_blueprint(main_blueprint)

    TRAIN_INTERVAL_SECONDS = 60

    def timer_function():
        with app.app_context():
            print("Reentrenando el modelo de decisión...")
            train_model(db)
        threading.Timer(TRAIN_INTERVAL_SECONDS, timer_function).start()

    timer_function()

    return app
