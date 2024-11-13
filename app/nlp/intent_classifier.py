# intent_classifier.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Ejemplos de entrenamiento
examples = [
    ("Agregar una tarea para mañana", "add_task"),
    ("Quiero agregar una nueva tarea", "add_task"),
    ("Mostrar todas las tareas", "list_tasks"),
    ("Listar las tareas pendientes", "list_tasks"),
    # Añade más ejemplos para mejorar la precisión
]

# Separar frases y etiquetas
texts, labels = zip(*examples)

# Vectorizar el texto y entrenar el clasificador
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
classifier = LogisticRegression().fit(X, labels)

# Función para predecir intención
def predict_intent(command_text):
    command_vec = vectorizer.transform([command_text])
    action = classifier.predict(command_vec)[0]
    return action
