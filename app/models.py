from .extensions import db  # Importar db desde extensions
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    urgency = db.Column(db.Integer, nullable=True)
    importance = db.Column(db.Integer, nullable=True)
    external_priority = db.Column(db.Integer, nullable=True)
    priority = db.Column(db.Integer, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)  # Campo para la fecha límite

class FeedbackLog(db.Model):
    __tablename__ = 'feedback_log'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    original_priority = db.Column(db.Integer, nullable=False)
    adjusted_priority = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    task = db.relationship('Task', backref='feedback')

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    urgency = db.Column(db.Integer, nullable=False)
    importance = db.Column(db.Integer, nullable=False)
    external_priority = db.Column(db.Integer, nullable=False)
    adjusted_priority = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
