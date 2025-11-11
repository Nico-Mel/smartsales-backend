import os
import django
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import joblib
from datetime import timedelta
from itertools import combinations, permutations
from sklearn.model_selection import train_test_split
import sys

# --- 0. CONFIGURACIÓN ---
# Imprimir más filas para que podamos ver las fechas
pd.set_option('display.max_rows', 50) 
print("Iniciando script de entrenamiento (v3)...")

# --- 1. CONECTAR CON DJANGO ---
try:
    # Asegúrate que 'smartsales.settings' sea el nombre correcto de tu proyecto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsales.settings') 
    django.setup()
    from ventas.models import DetalleVenta
    print("Conexión con Django exitosa.")
except Exception as e:
    print(f"Error fatal conectando con Django: {e}")
    sys.exit(1)


# --- 2. OBTENER DATOS (Data Fetching) ---
print("Obteniendo datos de ventas de la base de datos...")
try:
    # Usamos 'venta__fecha' para acceder a la fecha a través de la ForeignKey
    qs = DetalleVenta.objects.all().values('producto_id', 'cantidad', 'venta__fecha')
    df_raw = pd.DataFrame.from_records(qs)

    if df_raw.empty:
        print("\n¡ERROR! No se encontraron datos de ventas.")
        print("Asegúrate de haber corrido 'seed_ml' primero.")
        sys.exit(1)

    print(f"Se encontraron {len(df_raw)} registros de detalles de venta.")

except Exception as e:
    print(f"Error al leer la base de datos: {e}")
    sys.exit(1)

# --- 3. PREPARAR DATOS (Data Transformation) ---
print("Transformando datos para el modelo...")
df_raw['fecha'] = pd.to_datetime(df_raw['venta__fecha'])

# Agrupar por SEMANA ('W') por cada producto
df_weekly = df_raw.set_index('fecha').groupby('producto_id').resample('W')['cantidad'].sum().reset_index()

# **Feature Engineering**
df_weekly['mes'] = df_weekly['fecha'].dt.month
df_weekly['semana_del_anio'] = df_weekly['fecha'].dt.isocalendar().week
# shift(1) crea la columna 'ventas_semana_anterior'
df_weekly['ventas_semana_anterior'] = df_weekly.groupby('producto_id')['cantidad'].shift(1)
# El target es la cantidad de la semana actual
df_weekly['target_ventas_actuales'] = df_weekly['cantidad']

# Rellenar los NaN (la primera semana de cada producto) con 0
df_final = df_weekly.fillna(0)

if df_final.empty:
    print("\n¡ERROR! El DataFrame final está vacío.")
    sys.exit(1)

print("\n--- Datos Transformados (con .fillna(0)) ---")
print("Revisa estas fechas. ¡DEBERÍAN ESTAR REPARTIDAS EN EL TIEMPO!")
# Imprime las primeras 50 filas para que puedas ver las fechas
print(df_final) 
print("----------------------------------------------\n")

# --- 4. ENTRENAR EL MODELO (Model Training) ---
print("Entrenando el modelo RandomForestRegressor...")

# Estas son las "pistas" que le damos al modelo
features = ['producto_id', 'mes', 'semana_del_anio', 'ventas_semana_anterior']
# Esto es lo que queremos que aprenda a predecir
target = 'target_ventas_actuales'

X = df_final[features]
y = df_final[target]

if X.empty or y.empty:
    print("\n¡ERROR! Las variables X o y están vacías antes de 'fit'.")
    sys.exit(1)

# Inicializar el modelo
demand_model = RandomForestRegressor(n_estimators=100, random_state=42)
# Entrenar el modelo
demand_model.fit(X, y)
print("¡Modelo entrenado exitosamente!")

# --- 5. GUARDAR EL MODELO (Save Model) ---
model_dir = 'ml_models'
os.makedirs(model_dir, exist_ok=True) # Crea la carpeta si no existe
model_path = os.path.join(model_dir, 'demand_model.pkl')

# Sobrescribe el modelo anterior
joblib.dump(demand_model, model_path)

print(f"¡Modelo (SOBRE)ESCRITO exitosamente en {model_path}!")


# ===================================================================
# --- PARTE 2: MODELO DE RECOMENDACIÓN (Clasificación) ---
# ===================================================================
print("\n--- INICIANDO MODELO 2: RECOMENDACIÓN ---")

# --- 3. OBTENER DATOS (Modelo 2) ---
print("Obteniendo datos de ventas (Modelo 2)...")
try:
    # Necesitamos saber QUÉ productos se compraron JUNTOS.
    # Pedimos el 'venta_id' y el 'producto_id'
    qs_reco = DetalleVenta.objects.all().values('venta_id', 'producto_id')
    df_raw_reco = pd.DataFrame.from_records(qs_reco)
    if df_raw_reco.empty:
        print("¡ADVERTENCIA! No se encontraron datos de ventas para Recomendación.")
        all_pairs = []
    else:
        print(f"Se encontraron {len(df_raw_reco)} registros de detalles.")
        # Agrupamos por 'venta_id' y creamos una lista de productos para cada venta
        df_ventas = df_raw_reco.groupby('venta_id')['producto_id'].apply(list).reset_index()
        # Filtramos solo ventas que tienen 2 o más productos (¡las "Ventas Combo"!)
        df_combos = df_ventas[df_ventas['producto_id'].apply(len) > 1]
        print(f"Se encontraron {len(df_combos)} ventas 'combo' (con 2+ productos).")
        # --- 4. PREPARAR DATOS (Modelo 2) ---
        # ¡Aquí creamos los "pares"!
        all_pairs = []
        for combo_list in df_combos['producto_id']:
            # permutations() nos da (Laptop, Mouse) y (Mouse, Laptop)
            for pair in permutations(combo_list, 2):
                all_pairs.append(pair)
    
    if not all_pairs:
        print("¡ADVERTENCIA! No se encontraron pares de productos. ¿El seeder creó 'Ventas Combo'?")
        df_final_reco = pd.DataFrame()
    else:
        # Creamos un DataFrame con los pares "Positivos" (compraron juntos)
        df_positivos = pd.DataFrame(all_pairs, columns=['producto_A', 'producto_B'])
        df_positivos['compraron_juntos'] = 1 # ¡Target = 1!
        
        # --- Creación de "Negativos" ---
        # Ahora necesitamos pares de productos que NO se compraron juntos
        all_products = df_raw_reco['producto_id'].unique()
        # Creamos todos los pares posibles de productos
        all_possible_pairs = pd.DataFrame(permutations(all_products, 2), columns=['producto_A', 'producto_B'])
        
        # Juntamos los posibles con los positivos
        df_merged = pd.merge(all_possible_pairs, df_positivos, on=['producto_A', 'producto_B'], how='left')
        
        # Los que NO estaban en positivos, ahora son 'NaN'. Los rellenamos con 0.
        df_final_reco = df_merged.fillna(0)
        # (Esto es una forma simple, hay formas más avanzadas pero esta funciona)
        print(f"Datos finales de recomendación listos: {len(df_final_reco)} pares totales.")

except Exception as e:
    print(f"Error al procesar Modelo 2: {e}")
    df_final_reco = pd.DataFrame()

# --- 5. ENTRENAR EL MODELO (Modelo 2) ---
if not df_final_reco.empty:
    print("Entrenando RandomForestClassifier (Modelo 2)...")
    
    features_reco = ['producto_A', 'producto_B']
    target_reco = 'compraron_juntos'
    
    X_reco = df_final_reco[features_reco]
    y_reco = df_final_reco[target_reco]
    
    if X_reco.empty:
         print("¡ERROR (Modelo 2)! X está vacío. Saltando entrenamiento.")
    else:
        # Usamos un Clasificador esta vez
        reco_model = RandomForestClassifier(n_estimators=100, random_state=42)
        reco_model.fit(X_reco, y_reco)
        print("¡Modelo 2 (Recomendación) entrenado exitosamente!")
        # --- 6. GUARDAR EL MODELO (Modelo 2) ---
        model_dir = 'ml_models' # Ya debería existir
        model_path_reco = os.path.join(model_dir, 'recommendation_model.pkl')
        joblib.dump(reco_model, model_path_reco)
        print(f"¡Modelo 2 (Recomendación) guardado en {model_path_reco}!")
else:
    print("¡ADVERTENCIA! No hay datos finales para entrenar el Modelo 2. Saltando.")

print("\n--- ¡Script de entrenamiento COMPLETO! ---")