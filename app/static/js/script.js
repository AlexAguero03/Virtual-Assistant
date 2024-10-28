// Cargar las tareas al inicio
document.addEventListener("DOMContentLoaded", loadTasks);

function loadTasks() {
    fetch('/tasks')
        .then(response => response.json())
        .then(data => {
            const taskList = document.getElementById('tasks');
            taskList.innerHTML = '';
            data.forEach(task => {
                const listItem = document.createElement('li');
                const deadline = task.deadline ? new Date(task.deadline).toLocaleString() : "Sin fecha límite";
                listItem.innerHTML = `
                    <span>${task.title} (Urgencia: ${task.urgency}, Importancia: ${task.importance}, Fecha límite: ${deadline})</span>
                    <div class="actions">
                        <button onclick="deleteTask(${task.id})">Eliminar</button>
                    </div>
                `;
                taskList.appendChild(listItem);
            });
        });
}


// Enviar tarea como comando al backend para su interpretación
document.getElementById('taskForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const description = document.getElementById('taskDescription').value;

    fetch('/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command: description })
    })
    .then(response => {
        if (!response.ok) {
            console.error("Error en la solicitud:", response.statusText);
            return response.json().then(errorData => {
                console.error("Detalles del error:", errorData);
            });
        }
        document.getElementById('taskDescription').value = '';  // Limpiar el campo de entrada
        loadTasks();
    })
    .catch(error => console.error("Error al enviar comando:", error));  // Manejo de errores
});

function deleteTask(id) {
    fetch(`/tasks/${id}`, { method: 'DELETE' })
        .then(() => loadTasks())
        .catch(error => console.error("Error al eliminar tarea:", error));  // Manejo de errores
}

function sendCommand() {
    const command = document.getElementById('commandInput').value;
    fetch('/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
    })
    .then(response => {
        if (!response.ok) {
            console.error("Error en la solicitud:", response.statusText);
            return response.json().then(errorData => {
                console.error("Detalles del error:", errorData);
            });
        }
        loadTasks();
    })
    .catch(error => console.error("Error al enviar comando:", error));  // Manejo de errores
}
