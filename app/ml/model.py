import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.validation import check_is_fitted

model_path = 'modelo_clasificacion_tareas.pkl'

if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("Modelo cargado desde archivo.")
else:
    print("No se encontró un modelo previo, y no hay archivo CSV para entrenar.")

def train_model(db):
    from app.models import Task, FeedbackLog  # Importa aquí para evitar el ciclo
    tasks = Task.query.all()
    feedback_logs = FeedbackLog.query.all()

    X, y = [], []
    for feedback in feedback_logs:
        task = Task.query.get(feedback.task_id)
        if task and feedback.adjusted_priority is not None:
            X.append([task.urgency, task.importance, task.external_priority])
            y.append(feedback.adjusted_priority)

    for task in tasks:
        if task.priority is not None and not any(log.task_id == task.id for log in feedback_logs):
            X.append([task.urgency, task.importance, task.external_priority])
            y.append(task.priority)

    X = np.array(X)
    y = np.array(y)
    y = np.round(y).astype(int)

    if len(X) > 0:
        model.fit(X, y)
        joblib.dump(model, model_path)
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
