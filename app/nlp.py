import re
from datetime import datetime, timedelta
import dateparser
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions

# Configuración de IBM Watson NLU
API_KEY = '7OEn5GkcdE2865B92U07vGg7fgtZ4f9wp0ivDpuWvGA0'  # Reemplaza con tu clave de API de Watson NLU
URL = 'https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/7c16e4d1-82e6-4b02-8fb3-cefc6fd6664e'

# Autenticación y configuración de Watson NLU
authenticator = IAMAuthenticator(API_KEY)
nlu = NaturalLanguageUnderstandingV1(
    version='2021-08-01',
    authenticator=authenticator
)
nlu.set_service_url(URL)
nlu.set_disable_ssl_verification(True)

def analizar_texto_watson(texto_usuario):
    """Envía el texto a Watson NLU y recibe el análisis."""
    response = nlu.analyze(
        text=texto_usuario,
        features=Features(
            entities=EntitiesOptions(sentiment=True, limit=5),
            keywords=KeywordsOptions(sentiment=True, limit=5)
        )
    ).get_result()
    
    print("Respuesta completa de Watson NLU:", response)  # Depuración completa de la respuesta

    # Extraer entidades y palabras clave
    entidades = [ent['text'] for ent in response.get('entities', [])]
    palabras_clave = [kw['text'] for kw in response.get('keywords', [])]
    return entidades, palabras_clave

def interpret_command(command_text):
    """Interpreta el comando utilizando Watson NLU para analizar el texto."""
    print("Comando recibido para interpretación:", command_text)
    
    # Llamada a Watson NLU para extraer entidades y palabras clave
    entidades, palabras_clave = analizar_texto_watson(command_text)
    print("Entidades detectadas:", entidades)
    print("Palabras clave detectadas:", palabras_clave)

    # Inicialización de la acción y estructura de datos para la tarea
    action = None
    task_data = {}

    # Ajustar lógica para acciones en función de palabras clave específicas
    if any(kw in palabras_clave for kw in ["agregar", "crear", "reunión", "enviar", "informe"]):
        action = "add_task"
        print("Acción detectada: add_task")
    elif any(kw in palabras_clave for kw in ["listar", "mostrar", "tareas pendientes", "consultar", "ver"]):
        action = "list_tasks"
        print("Acción detectada: list_tasks")
    
    # Extraer información adicional (fecha, hora) con regex y entidades de Watson
    time_phrases = re.findall(r'\b(hoy|mañana|próximo lunes|próximo miércoles|\d{1,2} (am|pm)|\d{1,2}:\d{2} (am|pm))\b', command_text, re.IGNORECASE)
    time_text = ' '.join([phrase[0] for phrase in time_phrases])
    print("Texto extraído manualmente para fecha y hora:", time_text)

    # Ajustar fechas relativas como "próximo miércoles"
    if "próximo miércoles" in time_text:
        today = datetime.today()
        days_until_wednesday = (2 - today.weekday() + 7) % 7
        next_wednesday = today + timedelta(days=days_until_wednesday)
        time_text = next_wednesday.strftime("%Y-%m-%d") + " " + time_text.replace("próximo miércoles", "").strip()
        print("Texto ajustado para fecha relativa:", time_text)

    # Analizar con dateparser
    if time_text:
        date_time = dateparser.parse(time_text, settings={'PREFER_DATES_FROM': 'future'}, languages=['es'])
        if date_time:
            task_data["deadline"] = date_time
            print("Fecha límite detectada:", task_data["deadline"])
        else:
            print("No se pudo analizar la fecha y hora.")
    else:
        print("No se detectó ninguna frase de tiempo.")
    
    # Asignar título de la tarea si es una acción de "add_task"
    if action == "add_task":
        task_data["title"] = command_text
        print("Título de la tarea detectado:", task_data["title"])

    print("Interpretación final:", {"action": action, "task_data": task_data})
    return {"action": action, "task_data": task_data}