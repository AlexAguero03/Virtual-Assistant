import joblib

def cargar_modelo():
    return joblib.load('modelo_clasificacion_tareas.pkl')
