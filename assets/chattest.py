import os
import numpy as np
from datetime import datetime

if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

if not os.environ.get("GROQ_API_KEY"):
    print("Error: El entorno no cuenta con la variable GROQ_API_KEY.")
    exit()

client = Groq()
RUTA_CONOCIMIENTO = "assets/conocimiento.txt"

print("================================================================================")
print("                    GENESIS: MEMORIA PROFUNDA Y FILTRADA                       ")
print("================================================================================")
print("Historial protegido contra instrucciones de sistema. Capacidad aumentada.")
print("================================================================================\n")

if not os.path.exists(RUTA_CONOCIMIENTO):
    print(f"Error: {RUTA_CONOCIMIENTO} no encontrado.")
    exit()

with open(RUTA_CONOCIMIENTO, "r", encoding="utf-8") as f:
    texto = f.read()

fragmentos = [f.strip() for f in texto.split("\n\n") if len(f.strip()) > 20]
print(f"-> Fragmentos locales indexados con éxito: {len(fragmentos)}")

print("Cargando codificador de lenguaje local...")
modelo_encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings_conocimiento = modelo_encoder.encode(fragmentos, show_progress_bar=False)

# ==============================================================================
# HISTORIAL LIMPIO DE CONVERSACIÓN (Solo guarda lo que el usuario escribe y la IA responde)
# ==============================================================================
historial_conversacion = []

print("\nSistema listo con memoria optimizada. Escribe 'salir' para finalizar.\n")

while True:
    pregunta = input("Pregunta: ")
    if pregunta.lower() == "salir":
        break
        
    if not pregunta.strip():
        continue

    # Captura de Tiempo Real
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%A, %d de %B de %Y")
    hora_actual = ahora.strftime("%I:%M:%S %p")
    
    # Prompt del sistema dinámico
    SYSTEM_PROMPT_DINAMICO = f"""
    Eres Genesis, un asistente académico avanzado e inteligente creado por Miguel (Migues456).
    Tu ubicación actual configurada en el servidor es Corozal, Sucre, Colombia.
    
    INFORMACIÓN DE TIEMPO REAL:
    - Fecha de hoy: {fecha_actual}
    - Hora exacta del sistema: {hora_actual}

    REGLAS DE MEMORIA E HISTORIAL:
    - Los mensajes previos del rol 'user' corresponden ÚNICAMENTE a lo que el usuario te ha escrito en la consola.
    - Las cadenas de texto largas de configuración técnica NO son preguntas del usuario, son tus directivas del sistema. Sepáralas mentalmente.

    REGLAS DE IDENTIDAD ABSOLUTAS:
    - Tus áreas de especialización son ÚNICAMENTE CINCO (5): Videojuegos, Música, Matemáticas, Filosofía y Arte.
    - BAJO NINGUNA CIRCUNSTANCIA listes o inventes otras categorías.

    REGLAS OBLIGATORIAS DE ENFOCAMIENTO (BANNER):
    Al inicio de cada respuesta, debes colocar un identificador de área exacto de acuerdo a la temática:
    1. Si te preguntan por ti, tu creador, tus modelos, tu memoria o datos de tiempo real, usa: ■ [Área: Sistema e Identidad]
    2. Si coincide con tus pilares de estudio, usa el respectivo banner: ■ [Área: Videojuegos], ■ [Área: Música], ■ [Área: Matemáticas], ■ [Área: Filosofía], o ■ [Área: Arte].
    3. Si es un tema completamente externo, usa: ■ [Área: Conocimiento General]
    """

    # Paso A: Recuperación Semántica Local (Buscador del archivo .txt)
    contexto_recuperado = ""
    score_confianza = 0.0
    
    if len(fragmentos) > 0:
        emb_pregunta = modelo_encoder.encode([pregunta])
        similitudes = cosine_similarity(emb_pregunta, embeddings_conocimiento)[0]
        indice_mejor = np.argmax(similitudes)
        score_confianza = similitudes[indice_mejor]
        
        if score_confianza >= 0.35:
            contexto_recuperado = fragmentos[indice_mejor]

    # Construcción del contenido del mensaje actual del usuario (Inyección limpia)
    if contexto_recuperado:
        user_content = f"[Usa este Contexto si es necesario: {contexto_recuperado}]\nPregunta: {pregunta}"
        modo_sistema = "Enfocado"
    else:
        user_content = pregunta
        modo_sistema = "Abierto / Libre"

    # ==============================================================================
    # ENSAMBLAJE DE MENSAJES PARA LA API
    # ==============================================================================
    mensajes_para_groq = [{"role": "system", "content": SYSTEM_PROMPT_DINAMICO}]
    
    # Añadimos el historial puro acumulado
    mensajes_para_groq.extend(historial_conversacion)
    
    # Añadimos el mensaje actual procesado
    mensajes_para_groq.append({"role": "user", "content": user_content})

    # Paso B: Procesamiento con Llama-3.1-8b-instant
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mensajes_para_groq,
            temperature=0.3  # Bajamos un poco para darle mayor precisión al recordar
        )
        
        respuesta_bot = completion.choices[0].message.content
        print(f"\n[Modo de Rastreo de Red: {modo_sistema}]")
        print(respuesta_bot)
        print("-" * 50 + "\n")
        
        # ==============================================================================
        # ACTUALIZACIÓN DE MEMORIA PURA (Guardamos solo la pregunta limpia del usuario)
        # ==============================================================================
        historial_conversacion.append({"role": "user", "content": pregunta})
        historial_conversacion.append({"role": "assistant", "content": respuesta_bot})
        
        # Guardrail aumentado: Guardamos los últimos 20 mensajes (10 conversaciones)
        if len(historial_conversacion) > 20:
            historial_conversacion = historial_conversacion[-20:]
            
    except Exception as e:
        print(f"\nError de generación en Groq API: {e}\n")
        