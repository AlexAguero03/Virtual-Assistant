from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

        # Entrenar el modelo dentro del contexto de la aplicación
        from .decision_tree import train_model
        train_model()

    # Registrar el blueprint de rutas
    from .routes import main
    app.register_blueprint(main)

    return app
