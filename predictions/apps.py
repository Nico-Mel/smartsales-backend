import os
import sys
import joblib
from django.apps import AppConfig
from django.conf import settings

class PredictionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictions'
    
    # Aquí guardamos el modelo en la "Plantilla" (la clase)
    demand_model = None 
    recommendation_model = None 

    def ready(self):
        
        # --- ¡¡LA LÓGICA CORRECTA Y SIMPLE!! ---
        
        # Verificamos si el comando que escribimos es 'runserver'
        # sys.argv es la lista de palabras: ['manage.py', 'runserver']
        
        if 'runserver' in sys.argv:
            # ¡SÍ! ¡Es 'runserver'! ¡Carguemos el modelo!
            MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'demand_model.pkl')
            print(f"Iniciando carga de modelo ML (comando 'runserver')...")
            
            try:
                # Guardamos en la Plantilla (la Clase)
                PredictionsConfig.demand_model = joblib.load(MODEL_PATH)
                print(f"✅ [Servidor] Modelo de demanda cargado exitosamente.")
            except FileNotFoundError:
                print(f"⚠️ [Servidor] WARNING: No se encontró 'demand_model.pkl'. La API de predicción fallará.")
            except Exception as e:
                print(f"❌ [Servidor] ERROR al cargar 'demand_model.pkl': {e}")
        
            # --- CEREBRO 2: RECOMENDACIÓN (¡EL NUEVO!) ---
            MODEL_PATH_RECO = os.path.join(settings.BASE_DIR, 'ml_models', 'recommendation_model.pkl')
            try:
                PredictionsConfig.recommendation_model = joblib.load(MODEL_PATH_RECO)
                print(f"✅ [Servidor] Modelo de RECOMENDACIÓN cargado exitosamente.")
            except FileNotFoundError:
                print(f"⚠️ [Servidor] WARNING: No se encontró 'recommendation_model.pkl'.")
            except Exception as e:
                print(f"❌ [Servidor] ERROR al cargar 'recommendation_model.pkl': {e}")
        
        else:
            print(f"... (Carga de modelos ML omitida para el comando: {' '.join(sys.argv)}) ...")