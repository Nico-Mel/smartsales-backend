import json
from decouple import config
import google.generativeai as genai 
from django.utils import timezone

# ----------------- PROMPT DE PRODUCTOS (RETAIL) -----------------
PROMPT_PLANTILLA = """
Eres un analizador de lenguaje natural experto en retail de electrodomésticos y tecnología.
Tu tarea es analizar la solicitud del usuario y extraer los parámetros relevantes
para una consulta de base de datos de PRODUCTOS.

FECHA ACTUAL (Contexto): {fecha_hoy}

CONTEXTO DE LA TIENDA (Tus datos):
Categorías: "Dispositivos Móviles", "Laptops", "Accesorios", "Audio", "Televisores", "Electrohogar"
Subcategorías: "Smartphones", "Tablets", "Notebooks", "Gaming Laptops", "Mouses", "Teclados", "Auriculares", "Parlantes Bluetooth", "Smart TV", "Licuadoras", "Microondas"
Marcas: "Samsung", "Xiaomi", "Apple", "LG", "HP", "Dell", "Razer", "Logitech", "Sony", "JBL", "Bose", "Philips", "Oster", "Mabe"

Reglas:
1. Siempre devuelve la salida como un objeto JSON válido.
2. Si un parámetro no se menciona, usa una cadena vacía "" o 0 para números.
3. Precios: Deben ser números enteros o flotantes.
4. Palabras_clave: Usar para atributos no estructurados (ej: 'rojo', 'gamer', 'grande', 'inoxidable').

Parámetros JSON (¡DEBES USAR ESTOS NOMBRES EXACTOS!):
- nombre_producto: (string, ej: 'Galaxy S23', 'Licuadora Xpert')
- marca: (string, ej: 'Samsung', 'Oster', 'Apple')
- categoria: (string, ej: 'Dispositivos Móviles', 'Electrohogar')
- subcategoria: (string, ej: 'Smartphones', 'Licuadoras')
- precio_minimo: (float/integer)
- precio_maximo: (float/integer)
- palabras_clave: (lista de strings, ej: ['rojo', 'gamer', '16GB RAM'])

EJEMPLOS:
Solicitud: "Busco un Samsung Galaxy S23 de menos de 5000bs"
JSON:
{{
  "nombre_producto": "Galaxy S23",
  "marca": "Samsung",
  "categoria": "Dispositivos Móviles",
  "subcategoria": "Smartphones",
  "precio_minimo": 0,
  "precio_maximo": 5000,
  "palabras_clave": []
}}

Solicitud: "mostrame licuadoras Oster"
JSON:
{{
  "nombre_producto": "licuadora",
  "marca": "Oster",
  "categoria": "Electrohogar",
  "subcategoria": "Licuadoras",
  "precio_minimo": 0,
  "precio_maximo": 0,
  "palabras_clave": []
}}

Solicitud: "laptops gamer razer"
JSON:
{{
  "nombre_producto": "laptop",
  "marca": "Razer",
  "categoria": "Laptops",
  "subcategoria": "Gaming Laptops",
  "precio_minimo": 0,
  "precio_maximo": 0,
  "palabras_clave": ["gamer"]
}}

Solicitud: "{texto_usuario}"
Devuelve SOLAMENTE el objeto JSON.
"""
# ----------------------------------------------------

def parse_natural_query(texto_usuario: str) -> dict:
    
    # Esta función es IDÉNTICA a la de tu app 'reports'
    
    api_key = config('API_GEMINI', default=config('GOOGLE_API_KEY', default=''))
    if not api_key:
        print("ERROR: Clave API_GEMINI no configurada.")
        return {"error": "API Key no configurada"}
    
    try:
        genai.configure(api_key=api_key)
        # Usamos el modelo que SÍ te funciona
        model = genai.GenerativeModel('gemini-2.5-flash') 

        fecha_hoy_str = timezone.now().strftime('%Y-%m-%d')
        # ¡IMPORTANTE! Usamos la plantilla de PRODUCTOS
        prompt_final = PROMPT_PLANTILLA.format(
            texto_usuario=texto_usuario,
            fecha_hoy=fecha_hoy_str
        )

        response = model.generate_content(prompt_final)
        raw_text = response.text.strip()
        
        # Limpieza de JSON
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
    
