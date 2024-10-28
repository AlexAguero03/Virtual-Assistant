from sklearn.tree import DecisionTreeClassifier
from .models import Task, FeedbackLog
from . import db
import numpy as np
from sklearn.utils.validation import check_is_fitted

# Inicializamos el modelo
model = DecisionTreeClassifier(max_depth=5, random_state=42)

def train_model():
    """
    Entrena el modelo de Árbol de Decisión utilizando los datos de retroalimentación.
    """
    # Recopilar los datos de Task y FeedbackLog
    tasks = Task.query.all()
    feedback_logs = FeedbackLog.query.all()

    # Crear listas para los datos y las etiquetas
    X = []
    y = []

    # Agregar datos de tareas con retroalimentación ajustada
    for feedback in feedback_logs:
        task = Task.query.get(feedback.task_id)
        if task:
            X.append([task.urgency, task.importance, task.external_priority])
            y.append(feedback.adjusted_priority)

    # Agregar datos de tareas sin retroalimentación (con prioridad original)
    for task in tasks:
        if not any(log.task_id == task.id for log in feedback_logs):
            X.append([task.urgency, task.importance, task.external_priority])
            y.append(task.priority)

    # Convertir a formato numpy
    X = np.array(X)
    y = np.array(y)

    # Reentrenar el modelo si tenemos datos suficientes
    if len(X) > 0:
        model.fit(X, y)
        print("Modelo reentrenado con éxito.")
    else:
        print("No hay suficientes datos para reentrenar el modelo.")

def classify_task(features):
    """
    Clasifica una tarea basada en sus características.
    Parámetros:
        features (list): Lista con características [urgency, importance, external_priority]
    Retorna:
        int: 0 (baja prioridad) o 1 (alta prioridad)
    """
    try:
        # Verificamos si el modelo ha sido entrenado
        check_is_fitted(model)
    except:
        # Si no está entrenado, devolvemos una prioridad por defecto (por ejemplo, baja prioridad)
        print("El modelo no está entrenado. Entrene el modelo antes de clasificar.")
        return 0  # Prioridad baja como valor predeterminado

    # Hacemos la predicción
    prediction = model.predict([features])
    return int(prediction[0])
