# routes.py
from flask import Blueprint, render_template, request, jsonify
from .models import Task, FeedbackLog, UserPreferences  # Modelos de la base de datos
from .decision_tree import classify_task, train_model  # Clasificador de prioridad
from .nlp import interpret_command  # Interprete NLP para comandos
from . import db  # Base de datos
from flask import request, jsonify
from .models import Task  # Asegúrate de que este import está configurado
from datetime import datetime

main = Blueprint('main', __name__)

# Umbral para reentrenamiento automático
FEEDBACK_THRESHOLD = 5

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title')
    urgency = data.get('urgency')
    importance = data.get('importance')
    external_priority = data.get('external_priority', 0)  # Default to 0 if not provided
    
    # Clasificar la prioridad de la tarea
    priority = classify_task([urgency, importance, external_priority])

    # Crear una nueva tarea con la prioridad clasificada
    new_task = Task(
        title=title,
        urgency=urgency,
        importance=importance,
        external_priority=external_priority,
        priority=priority
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Tarea añadida correctamente", "task_id": new_task.id, "priority": priority})

"""
@main.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    tasks_list = [{
        "id": task.id,
        "title": task.title,
        "urgency": task.urgency,
        "importance": task.importance,
        "external_priority": task.external_priority,
        "priority": task.priority,
        "deadline": task.deadline
    } for task in tasks]
    return jsonify(tasks_list) 
"""

@main.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    tasks_list = []
    for task in tasks:
        # Imprimir la fecha límite en el backend para depuración
        print("Fecha en el backend:", task.deadline)
        
        tasks_list.append({
            "id": task.id,
            "title": task.title,
            "urgency": task.urgency,
            "importance": task.importance,
            "external_priority": task.external_priority,
            "priority": task.priority,
            # Convertir la fecha a ISO format para enviar al frontend
            "deadline": task.deadline.isoformat() if task.deadline else None
        })
        
    return jsonify(tasks_list)

@main.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = Task.query.get_or_404(task_id)

    # Actualizar los datos de la tarea
    task.title = data.get('title', task.title)
    task.urgency = data.get('urgency', task.urgency)
    task.importance = data.get('importance', task.importance)
    task.external_priority = data.get('external_priority', task.external_priority)

    # Reclasificar la prioridad con los nuevos valores
    task.priority = classify_task([task.urgency, task.importance, task.external_priority])
    db.session.commit()

    return jsonify({"message": "Tarea actualizada correctamente"})

@main.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Tarea eliminada correctamente"})

@main.route('/tasks/<int:task_id>/feedback', methods=['POST'])
def give_feedback(task_id):
    data = request.get_json()
    task = Task.query.get_or_404(task_id)
    adjusted_priority = data.get('priority')

    if adjusted_priority is not None:
        # Guardar retroalimentación en FeedbackLog
        feedback = FeedbackLog(
            task_id=task.id,
            original_priority=task.priority,
            adjusted_priority=adjusted_priority
        )
        db.session.add(feedback)
        
        # Actualizar la prioridad de la tarea con la retroalimentación ajustada
        task.priority = adjusted_priority
        db.session.commit()

        # Guardar preferencia de usuario basada en retroalimentación
        preference = UserPreferences(
            urgency=task.urgency,
            importance=task.importance,
            external_priority=task.external_priority,
            adjusted_priority=adjusted_priority
        )
        db.session.add(preference)
        db.session.commit()

        # Reentrenamiento automático si se ha alcanzado el umbral de retroalimentación
        feedback_count = FeedbackLog.query.count()
        if feedback_count >= FEEDBACK_THRESHOLD:
            train_model()
            print("Modelo reentrenado automáticamente después de recibir suficiente retroalimentación.")
        
        return jsonify({"message": "Retroalimentación recibida correctamente", "task_id": task.id})
    else:
        return jsonify({"message": "No se proporcionó prioridad ajustada"}), 400


@main.route('/command', methods=['POST'])
def process_command():
    data = request.json
    command_text = data.get("command")
    date_str = data.get("date")      # Recibir fecha
    time_str = data.get("time")      # Recibir hora

    interpreted = interpret_command(command_text)
    
    action = interpreted["action"]
    task_data = interpreted["task_data"]

    # Si se proporcionan fecha y hora, combina ambas en un datetime
    if date_str and time_str:
        # Convierte `date_str` y `time_str` a un objeto datetime
        task_data["deadline"] = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    
    # Ejecuta la acción según lo interpretado
    if action == "add_task":
        return add_task_with_data(task_data)
    elif action == "list_tasks":
        return get_tasks()
    elif action == "update_task" and "id" in task_data:
        return update_task(task_data["id"])
    elif action == "delete_task" and "id" in task_data:
        return delete_task(task_data["id"])
    else:
        return jsonify({"message": "Comando no reconocido"}), 400
    
@main.route('/test_classification', methods=['POST'])
def test_classification():
    data = request.get_json()
    urgency = data.get('urgency', 1)
    importance = data.get('importance', 1)
    external_priority = data.get('external_priority', 0)
    # Agrupa las características en un arreglo
    features = [urgency, importance, external_priority]
    
    # Clasifica la tarea usando el modelo
    priority = classify_task(features)
    
    return jsonify({
        "message": "Clasificación completada",
        "priority": priority
    })

def add_task_with_data(task_data):
    title = task_data.get('title')
    urgency = task_data.get('urgency', 1)
    importance = task_data.get('importance', 1)
    external_priority = task_data.get('external_priority', 0)
    deadline = task_data.get('deadline')
    print("Fecha límite detectada en 'add_task_with_data':", deadline)


    # Clasificar la tarea utilizando el árbol de decisión
    priority = classify_task([urgency, importance, external_priority])

    # Crear la tarea con los datos proporcionados
    new_task = Task(
        title=title,
        urgency=urgency,
        importance=importance,
        external_priority=external_priority,
        priority=priority,
        deadline=deadline
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Tarea añadida correctamente", "task_id": new_task.id, "priority": priority})