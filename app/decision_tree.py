import pickle
import os
from sklearn.tree import DecisionTreeClassifier
from .models import Task, FeedbackLog
import numpy as np
from sklearn.utils.validation import check_is_fitted

# Inicializamos el modelo
model = DecisionTreeClassifier(max_depth=5, random_state=42)
model_path = 'modelo_arbol_decision.pkl'

# Cargar el modelo desde el archivo si existe
if os.path.exists(model_path):
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    print("Modelo cargado desde archivo.")
else:
    print("No se encontró un modelo previo, se entrenará uno nuevo.")

def train_model():
    global model
    tasks = Task.query.all()
    feedback_logs = FeedbackLog.query.all()

    X = []
    y = []

    # Recopilamos los datos de feedback
    for feedback in feedback_logs:
        task = Task.query.get(feedback.task_id)
        if task and feedback.adjusted_priority is not None:  # Verifica que adjusted_priority no sea None
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
    y = np.round(y).astype(int)  # Redondear y convertir a entero

    if len(X) > 0:
        print("Valores de y después de redondear:", y)
        model.fit(X, y)
        print("Modelo reentrenado con éxito.")
        # Guardar el modelo entrenado en un archivo
        with open(model_path, 'wb') as file:
            pickle.dump(model, file)
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
