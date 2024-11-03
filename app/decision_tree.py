import joblib
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.validation import check_is_fitted
from .models import Task, FeedbackLog

# Inicializamos el modelo
model_path = 'modelo_clasificacion_tareas.pkl'
csv_path = 'conjunto_datos_tareas_dinamico.csv'

# Cargar el modelo desde el archivo si existe
if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("Modelo cargado desde archivo.")
else:
    print("No se encontró un modelo previo, y no hay archivo CSV para entrenar.")

def train_model():
    global model
    tasks = Task.query.all()
    feedback_logs = FeedbackLog.query.all()

    X = []
    y = []

    # Recopilamos los datos de feedback
    for feedback in feedback_logs:
        task = Task.query.get(feedback.task_id)
        if task and feedback.adjusted_priority is not None:
            X.append([task.urgency, task.importance, task.external_priority])
            y.append(feedback.adjusted_priority)

    # Agregar tareas sin feedback
    for task in tasks:
        if task.priority is not None and not any(log.task_id == task.id for log in feedback_logs):
            X.append([task.urgency, task.importance, task.external_priority])
            y.append(task.priority)

    X = np.array(X)
    y = np.array(y)

    # Asegurarse de que y tenga valores discretos
    y = np.round(y).astype(int)

    if len(X) > 0:
        print("Valores de y después de redondear:", y)
        model.fit(X, y)
        print("Modelo reentrenado con éxito.")
        # Guardar el modelo entrenado en un archivo
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
    print("Predicción de urgencia e importancia:", prediction)
    return int(prediction[0])
