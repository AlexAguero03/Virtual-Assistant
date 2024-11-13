from flask import current_app
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions
from datetime import datetime, timedelta, timezone

MEXICO_TIMEZONE = timezone(timedelta(hours=-6))

def set_to_mexico_timezone(dt):
    return dt.astimezone(MEXICO_TIMEZONE)

def interpretar_fecha_relativa(texto):
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
    return None

def get_watson_nlu():
    authenticator = IAMAuthenticator(current_app.config['WATSON_API_KEY'])
    nlu = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=authenticator
    )
    nlu.set_service_url(current_app.config['WATSON_URL'])
    nlu.set_disable_ssl_verification(True)
    return nlu

def analizar_texto_watson(texto_usuario):
    nlu = get_watson_nlu()
    response = nlu.analyze(
        text=texto_usuario,
        features=Features(
            entities=EntitiesOptions(sentiment=True, limit=5),
            keywords=KeywordsOptions(sentiment=True, limit=5)
        )
    ).get_result()
    entidades = [ent['text'] for ent in response.get('entities', [])]
    palabras_clave = [kw['text'] for kw in response.get('keywords', [])]
    return entidades, palabras_clave

def interpret_command(command_text, deadline=None):
    print("Comando recibido para interpretación:", command_text)
    deadline = datetime.fromisoformat(deadline) if deadline else None
    task_data = {
        "title": command_text,
        "deadline": deadline
    }
    action = "add_task"
    return {"action": action, "task_data": task_data}
