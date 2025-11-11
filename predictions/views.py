from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Sum
from rest_framework.permissions import AllowAny 

# Importamos la "Plantilla" (la Clase) directamente
from .apps import PredictionsConfig

try:
    # (¡Asegúrate que este sea el nombre correcto de tu modelo!)
    from ventas.models import DetalleVenta
except ImportError:
    DetalleVenta = None

class PredictDemandView(APIView):
    # Hacemos la URL pública para probar fácil
    permission_classes = [AllowAny]
    
    def get(self, request, producto_id, format=None):
        
        # --- A. OBTENER EL MODELO "CEREBRO" (LA FORMA DIRECTA) ---
        
        # Leemos la variable "global" de la Plantilla
        model = PredictionsConfig.demand_model
        
        if model is None:
            return Response({"error": "Modelo no cargado. Revisa la consola del servidor."}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- B. RECOLECTAR LAS "PISTAS" (FEATURES) ---
        
        hoy = datetime.now()
        mes_actual = hoy.month
        semana_actual = hoy.isocalendar().week
        
        # Buscamos ventas en los últimos 7 días
        hace_7_dias = hoy - timedelta(days=7)
        
        # (¡Asegúrate que 'DetalleVenta' sea el nombre correcto!)
        ventas_pasadas = DetalleVenta.objects.filter(
            producto_id=producto_id,
            venta__fecha__gte=hace_7_dias
        ).aggregate(
            total_vendido=Sum('cantidad') 
        )

        ventas_semana_anterior = ventas_pasadas.get('total_vendido', 0)
        if ventas_semana_anterior is None:
            ventas_semana_anterior = 0

        # --- C. PREPARAR DATOS PARA EL MODELO ---
        data_para_predecir = {
            'producto_id': [producto_id],
            'mes': [mes_actual],
            'semana_del_anio': [semana_actual],
            'ventas_semana_anterior': [ventas_semana_anterior]
        }
        
        columnas_ordenadas = ['producto_id', 'mes', 'semana_del_anio', 'ventas_semana_anterior']
        df_predict = pd.DataFrame(data_para_predecir, columns=columnas_ordenadas)

        # --- D. ¡HACER LA PREDICCIÓN! ---
        prediccion_array = model.predict(df_predict)
        prediccion_valor = prediccion_array[0]
        prediccion_final = round(prediccion_valor)

        # --- E. DEVOLVER LA RESPUESTA (JSON) ---
        return Response({
            "producto_id": producto_id,
            "prediccion_proxima_semana (unidades)": prediccion_final,
            "datos_usados_para_predecir": {
                "mes_actual": mes_actual,
                "semana_actual": semana_actual,
                "ventas_reales_ultimos_7_dias": ventas_semana_anterior
            }
        }, status=status.HTTP_200_OK)
    

# ===================================================================
# --- VISTA 2: RECOMENDACIÓN DE PRODUCTOS (¡LA NUEVA!) ---
try:
    # (¡Asegúrate que este sea el nombre correcto de tu modelo!)
    from products.models import Producto
except ImportError:
    Producto = None
class RecommendProductView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, producto_id, format=None):
        
        # --- A. OBTENER EL MODELO "CEREBRO" 2 ---
        model = PredictionsConfig.recommendation_model
        
        if model is None:
            return Response({"error": "Modelo de Recomendación no cargado."}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if Producto is None:
            return Response({"error": "No se pudo importar el modelo 'Producto'"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- B. RECOLECTAR "PISTAS" ---
        # ¿Qué productos podemos recomendar? ¡Todos menos el actual!
        # Usamos .values_list('id', flat=True) para obtener solo los IDs
        try:
            otros_productos_ids = list(Producto.objects.exclude(id=producto_id).values_list('id', flat=True))
        except Exception as e:
            return Response({"error": f"Error al buscar productos: {e}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not otros_productos_ids:
            return Response({"error": "No se encontraron otros productos para recomendar."}, 
                            status=status.HTTP_404_NOT_FOUND)

        # --- C. PREPARAR DATOS PARA EL MODELO ---
        # El modelo fue entrenado con ['producto_A', 'producto_B']
        # producto_A = El que estás viendo (producto_id)
        # producto_B = Todos los demás productos
        
        data_para_predecir = {
            'producto_A': [producto_id] * len(otros_productos_ids),
            'producto_B': otros_productos_ids
        }
        df_predict = pd.DataFrame(data_para_predecir)

        # --- D. ¡HACER LA PREDICCIÓN! ---
        # ¡Esta es la parte clave!
        # No usamos .predict() (que da 0 o 1)
        # Usamos .predict_proba() que da la PROBABILIDAD (de 0.0 a 1.0)
        
        # Devuelve algo como: [[0.9, 0.1], [0.7, 0.3], [0.2, 0.8]]
        # (Probabilidad de 0, Probabilidad de 1)
        probabilidades = model.predict_proba(df_predict)
        
        # Queremos solo la probabilidad de "1" (compraron_juntos)
        probabilidad_de_compra_juntos = probabilidades[:, 1]

        # --- E. ORDENAR Y RESPONDER ---
        # Creamos un "diccionario" de (ID_Producto: Probabilidad)
        resultados = zip(otros_productos_ids, probabilidad_de_compra_juntos)
        
        # Ordenamos por probabilidad (de mayor a menor)
        resultados_ordenados = sorted(resultados, key=lambda x: x[1], reverse=True)
        
        # ¡Devolvemos los 3 MEJORES!
        top_3_recomendaciones_tuplas = resultados_ordenados[:3]
        
        # Vamos a devolver un JSON bonito
        top_3_final = []
        for prod_id, prob in top_3_recomendaciones_tuplas:
            top_3_final.append({
                "producto_id_recomendado": prod_id,
                "probabilidad": f"{prob * 100:.2f}%" # (ej. "81.23%")
            })

        return Response({
            "producto_consultado": producto_id,
            "recomendaciones": top_3_final
        }, status=status.HTTP_200_OK)