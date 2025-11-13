import json
from decouple import config
import google.generativeai as genai
from django.utils import timezone # Para saber la fecha de "hoy"

# reports/nlp_utils.py
# ... (importaciones) ...

# ----------------- PROMPT DE REPORTES (CORREGIDO) -----------------
PROMPT_PLANTILLA = """
Eres un asistente experto en analizar peticiones de reportes de ventas.
Tu única tarea es analizar la solicitud del usuario y extraer los parámetros 
relevantes en un objeto JSON.

FECHA ACTUAL (Contexto): {fecha_hoy}

Reglas:
1. Siempre devuelve la salida como un objeto JSON válido.
2. Si un parámetro no se menciona, usa una cadena vacía "" o 0 para números.
3. Formato: Si no se especifica el formato, usa "pdf" por defecto.
4. Fechas:
   - Si se mencionan fechas (ej: "de enero", "mes pasado", "ayer", "de 2024"), 
     calcula y devuelve 'fecha_inicio' y 'fecha_fin' en formato "YYYY-MM-DD".
   - Si no se mencionan fechas, usa "" para las fechas.
5. Reporte: 
   - Debes identificar cuál de los 4 reportes se está pidiendo.
   - Si no puedes identificar un reporte claro, usa "".

Parámetros JSON (¡DEBES USAR ESTOS NOMBRES EXACTOS!):
- reporte_a_generar: (string, uno de: "ventas_producto", "ventas_sucursal", "ventas_vendedor", "ingresos_metodo_pago")
- formato: (string, uno de: "pdf", "excel", "csv")
- fecha_inicio: (string, "YYYY-MM-DD" o "")
- fecha_fin: (string, "YYYY-MM-DD" o "")

EJEMPLOS:
Solicitud: "Quiero un reporte de ventas por producto de septiembre, en PDF."
JSON:
{{
  "reporte_a_generar": "ventas_producto",
  "formato": "pdf",
  "fecha_inicio": "2025-09-01",
  "fecha_fin": "2025-09-30"
}}

Solicitud: "dame el excel de ingresos por método de pago del mes pasado"
JSON:
{{
  "reporte_a_generar": "ingresos_metodo_pago",
  "formato": "excel",
  "fecha_inicio": "2025-10-01",
  "fecha_fin": "2025-10-31"
}}

Solicitud: "reporte de vendedores"
JSON:
{{
  "reporte_a_generar": "ventas_vendedor",
  "formato": "pdf",
  "fecha_inicio": "",
  "fecha_fin": ""
}}

Solicitud: "{texto_usuario}"
Devuelve SOLAMENTE el objeto JSON.
"""
# ----------------------------------------------------

def parse_natural_query(texto_usuario: str) -> dict:
    
    api_key = config('API_GEMINI', default=config('GOOGLE_API_KEY', default=''))
    if not api_key:
        print("ERROR: Clave API_GEMINI no configurada.")
        return {"error": "API Key no configurada"}
    
    try:
        genai.configure(api_key=api_key)
        # ¡Usamos 'gemini-pro' que sí existe en la API v1beta!
        model = genai.GenerativeModel('gemini-2.5-flash')
        fecha_hoy_str = timezone.now().strftime('%Y-%m-%d')
        prompt_final = PROMPT_PLANTILLA.format(
            texto_usuario=texto_usuario,
            fecha_hoy=fecha_hoy_str  # <-- Esta es la variable que causaba el KeyError
        )

        response = model.generate_content(prompt_final)
        raw_text = response.text.strip()
        
        # (Limpieza de JSON...)
        if raw_text.startswith("```json"):
            raw_text = raw_text.lstrip("```json").rstrip("```").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.lstrip("```").rstrip("```").strip()

        parsed_json = json.loads(raw_text)
        return parsed_json

    except json.JSONDecodeError as e:
        print(f"Error JSON Decode: No se pudo parsear. Texto crudo: '{raw_text}'")
        return {"error": "Respuesta de IA no es un JSON válido"} 

    except Exception as e:
        print(f"Error FATAL en Gemini API: {type(e).__name__}: {e}")
        return {"error": f"Error de API: {e}"}
    
def analyze_data_with_gemini(datos_json: str, prompt_analista: str) -> dict:
    """
    Toma un string JSON de datos y un prompt, y le pide a Gemini que los analice.
    """
    
    api_key = config('API_GEMINI', default=config('GOOGLE_API_KEY', default=''))
    if not api_key:
        print("ERROR: Clave API_GEMINI no configurada.")
        return {"error": "API Key no configurada"}

    try:
        genai.configure(api_key=api_key)
        # Usamos el modelo que SÍ te funciona
        model = genai.GenerativeModel('gemini-2.5-flash') 

        # ¡Este es el prompt del Analista!
        # Combina el prompt de instrucciones con los datos.
        prompt_final = f"""
        {prompt_analista}

        Aquí están los datos en formato JSON:
        {datos_json}
        """

        response = model.generate_content(prompt_final)
        
        # Para el análisis, solo devolvemos el texto crudo.
        return {"analisis": response.text.strip()}

    except Exception as e:
        print(f"Error FATAL en Gemini API (Analisis): {type(e).__name__}: {e}")
        return {"error": f"Error de API: {e}"}