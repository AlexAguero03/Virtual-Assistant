from .models import Task

def get_high_priority_tasks():
    """
    Filtra tareas de alta prioridad y urgencia.
    """
    high_priority_tasks = Task.query.filter(Task.priority == 1, Task.urgency >= 4).all()
    tasks_list = [{
        "id": task.id,
        "title": task.title,
        "urgency": task.urgency,
        "importance": task.importance,
        "external_priority": task.external_priority,
        "priority": task.priority
    } for task in high_priority_tasks]
    return tasks_list
