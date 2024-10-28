from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Importa Flask-Migrate
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
migrate = Migrate()  # Inicializa el objeto Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)  # Inicializa Flask-Migrate con la app y db

    # Crear tablas solo si no existen
    with app.app_context():
        db.create_all()  # Crea las tablas antes de entrenar el modelo
    
    from .routes import main
    app.register_blueprint(main)
    
    return app
