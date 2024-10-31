// Cargar las tareas al inicio
document.addEventListener("DOMContentLoaded", loadTasks);

function loadTasks() {
    fetch('/tasks')
        .then(response => response.json())
        .then(data => {
            const taskList = document.getElementById('tasks');
            taskList.innerHTML = '';
            data.forEach(task => {
                // Ajustar la fecha límite a la zona horaria específica (GMT-6)
                const deadline = task.deadline 
                    ? new Date(task.deadline).toLocaleString("es-MX", { 
                        timeZone: "America/Mexico_City", 
                        hour12: true 
                    }) 
                    : "Sin fecha límite";
                    console.log(deadline)
                
                const listItem = document.createElement('li');
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
    const date = document.getElementById('taskDate').value;  // Captura la fecha
    const time = document.getElementById('taskTime').value;  // Captura la hora

    fetch('/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            command: description, 
            date: date,   // Envía la fecha
            time: time    // Envía la hora
        })
    })
    .then(response => {
        if (!response.ok) {
            console.error("Error en la solicitud:", response.statusText);
            return response.json().then(errorData => {
                console.error("Detalles del error:", errorData);
            });
        }
        document.getElementById('taskDescription').value = '';  // Limpiar el campo de entrada
        document.getElementById('taskDate').value = '';         // Limpiar fecha
        document.getElementById('taskTime').value = '';         // Limpiar hora
        loadTasks();
    })
    .catch(error => console.error("Error al enviar comando:", error));  // Manejo de errores
});

function deleteTask(id) {
    fetch(`/tasks/${id}`, { method: 'DELETE' })
        .then(() => loadTasks())
        .catch(error => console.error("Error al eliminar tarea:", error));  // Manejo de errores
}
