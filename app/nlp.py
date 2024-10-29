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

    # Determinar la acción basada en palabras clave o entidades
    action = None
    task_data = {}

    # Verificar si las palabras clave contienen alguna acción específica
    add_task_keywords = {"agregar", "crear", "añadir", "programar", "reunión"}
    list_task_keywords = {"listar", "mostrar", "consultar", "ver"}

    # Determinar acción en base a palabras clave
    if any(word in command_text for word in add_task_keywords):
        action = "add_task"
    elif any(word in command_text for word in list_task_keywords):
        action = "list_tasks"

    # Análisis de fechas en entidades o palabras clave
    detected_date = None
    if "mañana" in entidades:
        detected_date = datetime.today() + timedelta(days=1)
    elif "hoy" in entidades:
        detected_date = datetime.today()

    # Si encontramos una hora exacta en el comando
    time_match = re.search(r'\b(\d{1,2}) (am|pm)\b', command_text, re.IGNORECASE)
    if time_match and detected_date:
        hour = int(time_match.group(1))
        if "pm" in time_match.group(2).lower() and hour != 12:
            hour += 12
        detected_date = detected_date.replace(hour=hour, minute=0, second=0)

    if detected_date:
        task_data["deadline"] = detected_date
        print("Fecha límite detectada:", task_data["deadline"])

    # Asignar título de la tarea
    if action == "add_task":
        task_data["title"] = command_text
        print("Título de la tarea detectado:", task_data["title"])

    print("Interpretación final:", {"action": action, "task_data": task_data})
    return {"action": action, "task_data": task_data}
