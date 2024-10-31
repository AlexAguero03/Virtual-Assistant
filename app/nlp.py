import re
from datetime import datetime, timedelta, timezone
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

# Definir la zona horaria de México, por ejemplo, GMT-6
MEXICO_TIMEZONE = timezone(timedelta(hours=-6))

def set_to_mexico_timezone(dt):
    return dt.astimezone(MEXICO_TIMEZONE)

def interpretar_fecha_relativa(texto):
    """Detecta y convierte fechas relativas en fechas específicas."""
    hoy = datetime.now()
    if "mañana" in texto:
        return hoy + timedelta(days=1)
    elif "próximo lunes" in texto:
        dias_para_lunes = (7 - hoy.weekday() + 0) % 7 or 7
        return hoy + timedelta(days=dias_para_lunes)
    elif "esta tarde" in texto:
        return hoy.replace(hour=17, minute=0)
    elif "esta noche" in texto:
        return hoy.replace(hour=21, minute=0)
    # Agrega más condiciones según sea necesario
    return None

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

def interpret_command(command_text, deadline=None):
    """Interpreta el comando y usa la fecha y hora proporcionadas directamente."""
    print("Comando recibido para interpretación:", command_text)

    # Usa el deadline proporcionado directamente en lugar de intentar detectarlo
    if deadline:
        deadline = datetime.fromisoformat(deadline)
    else:
        deadline = None  # O asigna alguna fecha predeterminada si es necesario

    task_data = {
        "title": command_text,
        "deadline": deadline
    }

    # Definir la acción en base al texto (esto puede ser simplificado según tus necesidades)
    action = "add_task"
    print("Interpretación final:", {"action": action, "task_data": task_data})
    return {"action": action, "task_data": task_data}
