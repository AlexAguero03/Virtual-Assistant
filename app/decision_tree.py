from sklearn.tree import DecisionTreeClassifier
from . import db
import numpy as np
from sklearn.utils.validation import check_is_fitted
from .models import Task, FeedbackLog

# Inicializamos el modelo
model = DecisionTreeClassifier(max_depth=5, random_state=42)

def train_model():
    """
    Entrena el modelo de Árbol de Decisión utilizando los datos de retroalimentación.
    """
    tasks = Task.query.all()
    feedback_logs = FeedbackLog.query.all()

    X = []
    y = []

    for feedback in feedback_logs:
        task = Task.query.get(feedback.task_id)
        if task:
            X.append([task.urgency, task.importance, task.external_priority])
            y.append(feedback.adjusted_priority)

    for task in tasks:
        if not any(log.task_id == task.id for log in feedback_logs):
            X.append([task.urgency, task.importance, task.external_priority])
            y.append(task.priority)

    X = np.array(X)
    y = np.array(y)

    if len(X) > 0:
        model.fit(X, y)
        print("Modelo reentrenado con éxito.")
    else:
        print("No hay suficientes datos para reentrenar el modelo.")

def classify_task(features):
    try:
        check_is_fitted(model)
    except:
        print("El modelo no está entrenado. Entrene el modelo antes de clasificar.")
        return 0

    prediction = model.predict([features])
    return int(prediction[0])
