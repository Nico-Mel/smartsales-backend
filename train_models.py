import os
import django
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import joblib
from datetime import timedelta
from itertools import combinations, permutations
import sys

# --- 0. CONFIGURACIÓN ---
pd.set_option('display.max_rows', 50) 
print("Iniciando script de entrenamiento (v5 - ¡LOS TRES MODELOS!)...")

# --- 1. CONECTAR CON DJANGO ---
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsales.settings') 
    django.setup()
    from ventas.models import DetalleVenta
    print("Conexión con Django exitosa.")
except Exception as e:
    print(f"Error fatal conectando con Django: {e}")
    sys.exit(1)

# --- Crear carpeta si no existe ---
model_dir = 'ml_models'
os.makedirs(model_dir, exist_ok=True)

# --- PARTE 1: MODELO DE VENTAS POR CATEGORÍA (Regresión) ---
print("\n--- INICIANDO MODELO 1: VENTAS POR CATEGORÍA (Mensual) ---")
try:
    # DATASET 
    # 3 columnas: categoría, cantidad y fecha
    print("M1: Leyendo datos de la Base de Datos...")
    qs_demand = DetalleVenta.objects.all().values(
        'producto__subcategoria_id', 
        'cantidad',
        'venta__fecha' 
    )
    # Convertimos los datos de Django a una "tabla" de Pandas
    df_raw_demand = pd.DataFrame.from_records(qs_demand)
    df_raw_demand = df_raw_demand.rename(columns={'producto__subcategoria_id': 'subcategoria_id'})

    if df_raw_demand.empty:
        print("¡ADVERTENCIA (M1)! No se encontraron datos.")
    else:
        # DATASET
        print("M1: Transformando datos (Agrupando por CATEGORÍA y MES)...")
        df_raw_demand['fecha'] = pd.to_datetime(df_raw_demand['venta__fecha'])
        # Agrupamos la "tabla" por ID de Categoría y por Mes ('M')
        df_monthly = df_raw_demand.set_index('fecha').groupby('subcategoria_id').resample('M')['cantidad'].sum().reset_index()

        # "Ingeniería de Pistas": Creamos las columnas que usará el modelo
        df_monthly['mes'] = df_monthly['fecha'].dt.month
        df_monthly['ventas_mes_anterior'] = df_monthly.groupby('subcategoria_id')['cantidad'].shift(1) # Pista 1
        df_monthly['target_ventas_actuales'] = df_monthly['cantidad'] # La Respuesta
        
        # Rellenamos los vacíos (el primer mes de historia) con 0
        # ¡Este es el "dataset" final que usamos para entrenar!
        df_final_demand = df_monthly.fillna(0)
        
        features_demand = ['subcategoria_id', 'mes', 'ventas_mes_anterior'] # Las Pistas
        target_demand = 'target_ventas_actuales' # La Respuesta
        X_demand = df_final_demand[features_demand]
        y_demand = df_final_demand[target_demand]

        if not X_demand.empty:
            model_1 = RandomForestRegressor(n_estimators=100, random_state=42)
            model_1.fit(X_demand, y_demand) # ¡Entrenamos!
            model_path = os.path.join(model_dir, 'sales_category_model.pkl') # <-- Nombre Cerebro 1
            joblib.dump(model_1, model_path)
            print(f"¡Modelo 1 (Ventas Categoría) guardado en {model_path}!")
        else:
            print("¡ADVERTENCIA (M1)! No hay datos finales para entrenar.")
except Exception as e:
    print(f"❌ ERROR al procesar Modelo 1: {e}")

# MODELO DE DEMANDA POR PRODUCTO (Regresión) 

print("\n--- INICIANDO MODELO 2: DEMANDA POR PRODUCTO (Semanal) ---")
try:
    # DATASET 

    print("M2: Leyendo datos de la Base de Datos...")
    qs_demand_prod = DetalleVenta.objects.all().values(
        'producto_id', 
        'cantidad',
        'venta__fecha' 
    )
    df_raw_demand_prod = pd.DataFrame.from_records(qs_demand_prod)

    if df_raw_demand_prod.empty:
        print("¡ADVERTENCIA (M2)! No se encontraron datos.")
    else:
        #  DATASET  "tabla"-
        print("M2: Transformando datos (Agrupando por PRODUCTO y SEMANA)...")
        df_raw_demand_prod['fecha'] = pd.to_datetime(df_raw_demand_prod['venta__fecha'])
        # Agrupamos la "tabla" por ID de Producto y por Semana ('W')
        df_weekly = df_raw_demand_prod.set_index('fecha').groupby('producto_id').resample('W')['cantidad'].sum().reset_index()

        # "Ingeniería de Pistas": columnas que usará el modelo
        df_weekly['mes'] = df_weekly['fecha'].dt.month
        df_weekly['semana_del_anio'] = df_weekly['fecha'].dt.isocalendar().week
        df_weekly['ventas_semana_anterior'] = df_weekly.groupby('producto_id')['cantidad'].shift(1) # Pista 1
        df_weekly['target_ventas_actuales'] = df_weekly['cantidad'] # La Respuesta
        
        # "dataset" final
        df_final_demand_prod = df_weekly.fillna(0)

        features_demand_prod = ['producto_id', 'mes', 'semana_del_anio', 'ventas_semana_anterior'] # Pistas
        target_demand_prod = 'target_ventas_actuales' # Respuesta
        X_demand_prod = df_final_demand_prod[features_demand_prod]
        y_demand_prod = df_final_demand_prod[target_demand_prod]

        if not X_demand_prod.empty:
            model_2 = RandomForestRegressor(n_estimators=100, random_state=42)
            model_2.fit(X_demand_prod, y_demand_prod) # ¡Entrenamos!
            model_path = os.path.join(model_dir, 'demand_product_model.pkl') # <-- Nombre Cerebro 2
            joblib.dump(model_2, model_path)
            print(f"¡Modelo 2 (Demanda Producto) guardado en {model_path}!")
        else:
            print("¡ADVERTENCIA (M2)! No hay datos finales para entrenar.")
except Exception as e:
    print(f"❌ ERROR al procesar Modelo 2: {e}")

#MODELO DE RECOMENDACIÓN (Clasificación) ---
print("\n--- INICIANDO MODELO 3: RECOMENDACIÓN ---")
try:

    print("M3: Leyendo datos de la Base de Datos...")
    qs_reco = DetalleVenta.objects.all().values('venta_id', 'producto_id')
    df_raw_reco = pd.DataFrame.from_records(qs_reco)
    if df_raw_reco.empty:
        print("¡ADVERTENCIA (M3)! No se encontraron datos.")
        df_final_reco = pd.DataFrame()
    else:

        print("M3: Transformando datos (Buscando 'Ventas Combo')...")
        # Agrupamos por Venta y creamos una lista de productos
        df_ventas = df_raw_reco.groupby('venta_id')['producto_id'].apply(list).reset_index()
        # Filtramos solo las ventas que tienen 2 o más productos
        df_combos = df_ventas[df_ventas['producto_id'].apply(len) > 1]
        print(f"Se encontraron {len(df_combos)} ventas 'combo' (con 2+ productos).")
        
        # Creamos los pares "Positivos" (ej. [Laptop, Mouse] = 1)
        all_pairs = []
        for combo_list in df_combos['producto_id']:
            for pair in permutations(combo_list, 2):
                all_pairs.append(pair)
    
        if not all_pairs:
            print("¡ADVERTENCIA (M3)! No se encontraron pares de productos.")
            df_final_reco = pd.DataFrame()
        else:
            df_positivos = pd.DataFrame(all_pairs, columns=['producto_A', 'producto_B'])
            df_positivos['compraron_juntos'] = 1
            
            # Creamos los pares "Negativos" (ej. [Laptop, Teclado] = 0)
            all_products = df_raw_reco['producto_id'].unique()
            all_possible_pairs = pd.DataFrame(permutations(all_products, 2), columns=['producto_A', 'producto_B'])
            df_merged = pd.merge(all_possible_pairs, df_positivos, on=['producto_A', 'producto_B'], how='left')
            
            # ¡Este es el "dataset" final que usamos para entrenar!
            df_final_reco = df_merged.fillna(0)

            print(f"Datos finales de recomendación listos: {len(df_final_reco)} pares totales.")

            if not df_final_reco.empty:
                features_reco = ['producto_A', 'producto_B'] # Pistas
                target_reco = 'compraron_juntos' # Respuesta (0 o 1)
                X_reco = df_final_reco[features_reco]
                y_reco = df_final_reco[target_reco]
                
                model_3 = RandomForestClassifier(n_estimators=100, random_state=42)
                model_3.fit(X_reco, y_reco) # ¡Entrenamos!
                model_path_reco = os.path.join(model_dir, 'recommendation_model.pkl') # <-- Nombre Cerebro 3
                joblib.dump(model_3, model_path_reco)
                print(f"¡Modelo 3 (Recomendación) guardado en {model_path_reco}!")
            else:
                 print("¡ADVERTENCIA (M3)! No hay datos finales para entrenar.")
except Exception as e:
    print(f"❌ ERROR al procesar Modelo 3: {e}")

print("\n--- ¡Script de entrenamiento COMPLETO! ---")