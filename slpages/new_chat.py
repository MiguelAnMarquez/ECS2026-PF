import streamlit as st 
import json 
import os 
import re 
import base64 
import random 
import numpy as np 
from datetime import datetime 
from sentence_transformers import SentenceTransformer 
from sklearn .metrics .pairwise import cosine_similarity 
from groq import Groq 


if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

client =Groq ()
RUTA_CONOCIMIENTO ="assets/knowledge.txt"

@st .cache_resource 
def cargar_modelo_semantico ():
    modelo =SentenceTransformer ('paraphrase-multilingual-MiniLM-L12-v2')
    if os .path .exists (RUTA_CONOCIMIENTO ):
        with open (RUTA_CONOCIMIENTO ,"r",encoding ="utf-8")as f :
            texto =f .read ()
        fragmentos =[f .strip ()for f in texto .split ("\n\n")if len (f .strip ())>20 ]
        if fragmentos :
            embeddings =modelo .encode (fragmentos ,show_progress_bar =False )
            return modelo ,fragmentos ,embeddings 
    return modelo ,[],[]

modelo_encoder ,fragmentos ,embeddings_conocimiento =cargar_modelo_semantico ()




def cargar_chat (chat_id ):
    path =f"history/{chat_id}.json"
    if os .path .exists (path ):
        with open (path ,"r",encoding ="utf-8")as f :
            return json .load (f ).get ("mensajes",[])
    return []

def guardar_chat (chat_id ,mensajes ):
    if chat_id is None :
        chat_id ="chat_"+datetime .now ().strftime ("%Y%m%d_%H%M%S")
        st .session_state .chat_seleccionado_id =chat_id 

    titulo =mensajes [0 ]["content"]
    if len (titulo )>40 :
        titulo =titulo [:40 ]+"..."

    data ={
    "titulo":titulo ,
    "fecha":datetime .now ().strftime ("%Y-%m-%d %H:%M:%S"),
    "mensajes":mensajes 
    }

    if not os .path .exists ("history"):
        os .makedirs ("history")

    with open (f"history/{chat_id}.json","w",encoding ="utf-8")as f :
        json .dump (data ,f ,ensure_ascii =False ,indent =4 )

def get_image_base64 (path ):
    if os .path .exists (path ):
        with open (path ,"rb")as image_file :
            return base64 .b64encode (image_file .read ()).decode ()
    return ""

def es_operacion (texto ):
    return re .match (r'^[0-9+\-*/(). ]+$',texto .strip ())

def resolver (texto ):
    try :
        return str (eval (texto ))
    except :
        return "Math error"




def extraer_y_renderizar_banner (texto_completo ,similitud_pct =None ):
    patron =r'^■\s*\[Área:\s*([^\]]+)\]\s*\n*'
    match =re .match (patron ,texto_completo .strip ())

    badge_similitud =""
    if similitud_pct is not None :
        badge_similitud =f"""
        <span class="badge-similarity tooltip-container">
            Match: {similitud_pct}%
            <span class="tooltip-text">
                <strong>Similitud de Coseno ({similitud_pct}%)</strong><br><br>
                Métrica de coincidencia semántica contra la base de conocimiento local (RAG).<br><br>
                • <strong>&gt; 35%:</strong> Se detectó coincidencia y se inyectó contexto para robustecer la respuesta.<br>
                • <strong>&lt; 35%:</strong> No superó el umbral. Se usó el conocimiento general del modelo.
            </span>
        </span>
        """

    if match :
        area_nombre =match .group (1 ).strip ()
        texto_limpio =re .sub (patron ,'',texto_completo .strip (),count =1 )

        es_pilar =any (p in area_nombre .lower ()for p in ["videojuegos","video games","música","music","matemáticas","mathematics","filosofía","philosophy","arte","art"])
        clase_color ="badge-pilar"if es_pilar else "badge-general"

        html_banner =f"""
        <div class="chat-bubble-top-container">
            <span class="badge-label {clase_color}">■ {area_nombre}</span>
            {badge_similitud}
        </div>
        """
        return texto_limpio ,html_banner 

    return texto_completo ,f'<div class="chat-bubble-top-container-empty">{badge_similitud}</div>'if badge_similitud else ""




def consultar_llm (prompt ):
    if es_operacion (prompt ):
        st .session_state ["ultima_similitud"]=0 
        return resolver (prompt )

    ahora =datetime .now ()
    fecha_actual =ahora .strftime ("%A, %d de %B de %Y")
    hora_actual =ahora .strftime ("%I:%M:%S %p")

    nombre_usuario =st .session_state .get ("user_name","Usuario Desconocido")
    rol_usuario =st .session_state .get ("user_tag","Free User")

    SYSTEM_PROMPT_DINAMICO =f"""
    Eres Genesis, un chatbot asistente, avanzado e inteligente creado por Migues456.
    Tu ubicación actual configurada en el servidor es Corozal, Sucre, Colombia.
    
    INFORMACIÓN DE LA IDENTIDAD DEL USUARIO CON EL QUE HABLAS:
    - Nombre del Usuario: {nombre_usuario}
    - Rol/Suscripción del Usuario: {rol_usuario}
    
    INFORMACIÓN DE TIEMPO REAL:
    - Fecha de hoy: {fecha_actual}
    - Hora exacta del sistema: {hora_actual}

    MANUAL DE NAVEGACIÓN Y SOPORTE DE LA INTERFAZ (Tu deber absoluto es guiar al usuario a usar la app si te pregunta algo sobre ella):
    - Cambiar Nombre de Perfil / Nombre de usuario / Avatar: Explica detalladamente que debe mirar la barra lateral izquierda, ir hacia abajo del todo y hacer clic en el ícono de engranaje (Settings). Esto abrirá un panel central ("Edit Profile Identity Settings") donde podrá escribir su nuevo nombre de pantalla y cargar un archivo de imagen para su avatar.
    - Comenzar un Nuevo Chat: Explica que la app limpia los componentes visuales regresando a la pantalla inicial ("Blank Slate") para abrir hilos de conversación independientes sin mezclar contextos.
    - Historial de Conversaciones: Explica que cada sesión se almacena de forma local dentro del directorio 'history/' en formato JSON con un título inteligente basado en el primer mensaje, y puede darles clic desde la barra lateral izquierda para reanudarlos.
    - Rol/Rango del usuario: Muestra el tipo de cuenta asignada al usuario (actualmente configurada como: {rol_usuario}).

    REGLAS DE IDENTIDAD Y MULTILINGÜISMO ABSOLUTAS:
    - RECONOCIMIENTO DE IDIOMA EN ESPEJO: Debes identificar de forma inmediata el idioma exacto en el que el usuario te está hablando (español, inglés, francés, etc.) y generar TODA tu respuesta en ese mismo idioma. Es mandatorio.
    - El nombre de tu interlocutor es {nombre_usuario}. ¡TÚ NO TE LLAMAS ASÍ! Tú eres Genesis.
    - Si el usuario te pregunta por su nombre, rol, o quién es él, respóndele utilizando los datos provistos en la sección 'INFORMACIÓN DE LA IDENTIDAD DEL USUARIO'.
    - Tus áreas de especialización académica son ÚNICAMENTE CINCO (5): Videojuegos, Música, Matemáticas, Filosofía y Arte. Sin embargo, TIENES PLENO PERMISO Y ES OBLIGATORIO que asistas al usuario en la navegación y control de la interfaz web utilizando el 'MANUAL DE NAVEGACIÓN Y SOPORTE DE LA INTERFAZ'.
    - Si te preguntan por materias externas (ej: medicina, leyes, cocina), aclara de forma breve que recurres al conocimiento general pero responde amablemente.

    REGLAS OBLIGATORIAS DE ENFOCAMIENTO (BANNER):
    Al inicio de cada respuesta, debes colocar un identificador de área exacto adaptado obligatoriamente al idioma de la respuesta (ej. si respondes en inglés usa "System and Identity", si es en español usa "Sistema e Identidad"):
    1. Si te preguntan por ti, tu creador, tus modelos, tu memoria, navegación por la plataforma, cómo cambiar el nombre de usuario/perfil, configuraciones o tiempo real, usa exactamente al inicio de la respuesta: ■ [Área: Sistema e Identidad]
    2. Si coincide con tus pilares de estudio, usa el respectivo banner: ■ [Área: Videojuegos], ■ [Área: Música], ■ [Área: Matemáticas], ■ [Área: Filosofía], o ■ [Área: Arte].
    3. Si es un tema completamente externo, usa exactamente al inicio de la respuesta: ■ [Área: Conocimiento General]
    """

    contexto_recuperado =""
    similitud_final =0.0 
    if len (fragmentos )>0 :
        emb_pregunta =modelo_encoder .encode ([prompt ])
        similitudes =cosine_similarity (emb_pregunta ,embeddings_conocimiento )[0 ]
        indice_mejor =np .argmax (similitudes )
        similitul_max =similitudes [indice_mejor ]
        similitud_final =float (similitul_max )if similitul_max >0 else 0.0 

        if similitud_final >=0.35 :
            contexto_recuperado =fragmentos [indice_mejor ]

    st .session_state ["ultima_similitud"]=int (similitud_final *100 )

    if contexto_recuperado :
        user_content =f"[Contexto de respaldo detectado en base local: {contexto_recuperado}]\nPregunta del usuario: {prompt}"
    else :
        user_content =prompt 

    mensajes_para_groq =[{"role":"system","content":SYSTEM_PROMPT_DINAMICO }]
    historial_activo =st .session_state .mensajes_chat_actual 
    memoria_reducida =historial_activo [-14 :]if len (historial_activo )>14 else historial_activo 

    for msg in memoria_reducida :
        mensajes_para_groq .append ({
        "role":msg ["role"],
        "content":msg ["content"]
        })

    if len (mensajes_para_groq )>1 and mensajes_para_groq [-1 ]["role"]=="user":
        mensajes_para_groq [-1 ]={"role":"user","content":user_content }
    else :
        mensajes_para_groq .append ({"role":"user","content":user_content })

    try :
        completion =client .chat .completions .create (
        model ="llama-3.1-8b-instant",
        messages =mensajes_para_groq ,
        temperature =0.3 
        )
        return completion .choices [0 ].message .content 
    except Exception as e :
        return f"■ [Área: Sistema e Identidad]\nError de comunicación con Groq: {e}"




def inject_css (is_blank_slate =False ):
    scrollbar_lock ="""
    [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important;
    }
    """if is_blank_slate else ""

    custom_avatar_url =st .session_state .get ("user_avatar_base64","")
    avatar_bg_style =f"background-image: url('{custom_avatar_url}') !important; background-size: cover !important; background-position: center !important; color: transparent !important;"if custom_avatar_url else ""

    st .markdown (f"""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />
    
    <style>
    [data-testid="stBlockContainer"] {{
        position: relative !important; 
        z-index: 1 !important;
        padding-bottom: 0rem !important;
    }}
    {scrollbar_lock}
    
    [data-testid="stMain"] {{position: relative !important;}}
    [data-testid="stMain"]::before {{content: ""; position: absolute; top: 310px; left: 50%; width: 1100px; height: 1100px; transform: translate(-50%, -50%); background: radial-gradient(circle, rgba(255, 0, 128, 0.14) 0%, rgba(123, 0, 255, 0.08) 25%, rgba(0, 191, 255, 0.04) 55%, transparent 70%); filter: blur(65px); animation: pulseRainbowGlow 12s ease-in-out infinite; pointer-events: none; z-index: 0; will-change: transform, filter;}}
    @keyframes pulseRainbowGlow {{ 0%, 100% {{transform: translate(-50%, -50%) scale(1); filter: blur(65px) hue-rotate(0deg);}} 50% {{transform: translate(-50%, -50%) scale(1.05); filter: blur(75px) hue-rotate(180deg);}} }}
    div[data-testid="stHorizontalBlock"]:has(.landing-marker) > div[data-testid="stColumn"]:nth-child(2) {{animation: continuousWorkspaceHover 6s ease-in-out infinite !important; will-change: transform;}}
    @keyframes continuousWorkspaceHover {{ 0%, 100% {{transform: translateY(0px);}} 50% {{transform: translateY(-10px);}} }}
    .logo-container {{display: flex; justify-content: center; align-items: center; margin-top: -35px; margin-bottom: -15px; height: 180px !important; overflow: visible !important;}}
    .logo-wrapper {{position: relative; display: inline-block; width: 300px; height: 180px; transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); will-change: transform;}}
    .logo-wrapper:hover {{transform: scale(1.04);}}
    .genesis-logo {{position: absolute !important; top: 50% !important; left: 50% !important; width: 200px; height: 180px !important; object-fit: contain; animation: logoBreatheGlint 7s ease-in-out infinite; will-change: transform, filter;}}
    @keyframes logoBreatheGlint {{ 0%, 100% {{transform: translate(-50%, -50%) scale(1); filter: drop-shadow(0 0px 0px rgba(255,255,255,0));}} 50% {{transform: translate(-50%, -50%) scale(1.02); filter: drop-shadow(0 0px 15px rgba(255,255,255,0.06));}} }}
    @keyframes fadeIn {{ from {{opacity: 0; transform: translateY(10px);}} to {{opacity: 1; transform: translateY(0px);}} }}

    [data-testid="stSidebarNav"] {{ padding-bottom: 95px !important; }}
    [data-testid="stSidebarUserContent"] {{ padding-bottom: 95px !important; }}
    
    .custom-sidebar-fixed-bottom {{
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 18.72rem !important;
        max-width: 18.72rem !important;
        background-color: #111113 !important;
        border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 16px 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 12px !important;
        z-index: 99999 !important;
        box-sizing: border-box !important;
    }}
    
    .profile-info-group {{
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        min-width: 0 !important;
        flex-grow: 1 !important;
    }}
    .profile-avatar-wrapper {{
        width: 38px !important;
        height: 38px !important;
        border-radius: 50% !important;
        overflow: hidden !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #ff9800;
        flex-shrink: 0 !important;
    }}
    .profile-avatar-wrapper img {{
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
    }}
    .profile-details {{
        display: flex !important;
        flex-direction: column !important;
        min-width: 0 !important;
    }}
    .profile-name {{
        color: #ffffff !important;
        font-size: 0.90rem !important;
        font-weight: 500 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    .profile-tag {{
        color: #8a8a93 !important;
        font-size: 0.76rem !important;
        margin-top: 1px !important;
        white-space: nowrap !important;
    }}
    
    .custom-cog-icon-trigger {{
        color: #8a8a93 !important;
        font-size: 20px !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        user-select: none !important;
        transition: color 0.15s ease, transform 0.4s ease !important;
        text-decoration: none !important;
        padding: 4px !important;
    }}
    .custom-cog-icon-trigger:hover {{
        color: #ffffff !important;
        transform: rotate(45deg);
    }}

    .stChatInputTextArea, 
    div[data-testid="stChatInput"] textarea,
    div[data-baseweb="base-input"] textarea {{
        padding: 14px 18px !important;
        font-size: 1.05rem !important;
        line-height: 1.5 !important;
        min-height: 54px !important;
    }}

    [data-testid="stAppViewBlockContainer"] {{
        overflow: visible !important;
    }}

    [data-testid="stChatMessage"] {{
        animation: fadeIn .25s ease;
        background-color: transparent !important;
        border: none !important;
        padding: 10px 0px !important;
    }}
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        flex-direction: row-reverse !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageAvatarUser"] {{
        {avatar_bg_style}
        border-radius: 50% !important;
    }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {{
        background-color: #212124 !important;
        padding: 14px 20px !important;
        border-radius: 18px 18px 4px 18px !important;
        max-width: 75% !important;
        margin-right: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }}
    
    [data-testid="stChatMessage"]:not(:has([data-testid="stChatMessageAvatarUser"])) [data-testid="stChatMessageContent"] {{
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        padding: 0px !important; 
        border-radius: 18px 18px 18px 4px !important; 
        max-width: 75% !important; 
        margin-left: 12px !important; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        gap: 0px !important;
    }}
    [data-testid="stChatMessage"]:not(:has([data-testid="stChatMessageAvatarUser"])) [data-testid="stChatMessageContent"] div[data-testid="stVerticalBlock"] {{
        gap: 0px !important;
    }}
    [data-testid="stChatMessageContent"] {{
        color: #e2e8f0 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }}

    .chat-bubble-top-container {{
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 12px 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        user-select: none !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0px !important;
    }}
    .chat-bubble-top-container-empty {{
        display: flex !important;
        justify-content: flex-end !important;
        padding: 6px 20px 0px 20px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0px !important;
    }}
    .badge-label {{
        font-size: 0.70rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}
    .badge-pilar {{ color: #4caf50 !important; }}
    .badge-general {{ color: #ff9800 !important; }}

    .badge-similarity {{
        font-size: 0.68rem !important;
        font-weight: 500 !important;
        color: #8a8a93 !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        padding: 2px 8px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
    }}

    .tooltip-container {{
        position: relative !important;
        cursor: help !important;
    }}

    .tooltip-container .tooltip-text {{
        visibility: hidden;
        width: 280px;
        background-color: #1a1a1e !important;
        color: #e2e8f0 !important;
        text-align: left;
        border-radius: 8px;
        padding: 14px;
        position: absolute;
        z-index: 999999 !important;
        bottom: -999%; 
        right: 0;
        opacity: 0;
        transition: opacity 0.2s ease, transform 0.2s ease;
        transform: translateY(-10px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important;
        font-family: inherit !important;
        font-size: 0.78rem !important;
        line-height: 1.4 !important;
        white-space: normal !important;
        text-transform: none !important;
        letter-spacing: normal !important;
    }}

    .tooltip-container .tooltip-text::after {{
        content: "";
        position: absolute;
        bottom: 100%;
        right: 20px;
        border-width: 6px;
        border-style: solid;
        border-color: transparent transparent #1a1a1e transparent;
    }}

    .tooltip-container:hover .tooltip-text {{
        visibility: visible;
        opacity: 1;
        transform: translateY(0px);
    }}

    .chat-bubble-body-text {{
        padding: 24px 22px 24px 22px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    .chat-bubble-body-text p:first-child {{ margin-top: 0px !important; }}
    .chat-bubble-body-text p:last-child {{ margin-bottom: 0px !important; }}
    </style>
    """,unsafe_allow_html =True )

def obtener_codigo_aleatorio ():
    return str (random .randint (1000 ,9999 ))

def render_profile_sidebar ():
    if st .session_state .user_avatar_base64 :
        avatar_html =f'<img src="{st.session_state.user_avatar_base64}" class="user-avatar-marker" alt="Avatar">'
    else :
        inicial =st .session_state .user_name [0 ].upper ()if st .session_state .user_name else "U"
        avatar_html =f'<span style="color: white; font-weight: bold; font-size: 1.05rem;">{inicial}</span>'

    @st .dialog ("Edit Profile Identity Settings")
    def open_profile_modal ():
        nuevo_nombre =st .text_input ("Profile Display Name",value =st .session_state .user_name )
        st .write (f"**Assigned System Role:** `{st.session_state.user_tag}`")
        archivo_imagen =st .file_uploader ("Upload Profile Avatar Graphic",type =["png","jpg","jpeg"])

        if st .button ("Save Changes",use_container_width =True ):
            st .session_state .user_name =nuevo_nombre if nuevo_nombre .strip ()else f"Guest-{obtener_codigo_aleatorio()}"
            if archivo_imagen :
                encoded =base64 .b64encode (archivo_imagen .read ()).decode ()
                st .session_state .user_avatar_base64 =f"data:{archivo_imagen.type};base64,{encoded}"
            st .rerun ()

    query_params =st .query_params 
    if "edit_profile"in query_params :
        st .query_params .clear ()
        open_profile_modal ()

    with st .sidebar :
        st .markdown (f"""
            <div class="custom-sidebar-fixed-bottom">
                <div class="profile-info-group">
                    <div class="profile-avatar-wrapper">
                        {avatar_html}
                    </div>
                    <div class="profile-details">
                        <span class="profile-name">{st.session_state.user_name}</span>
                        <span class="profile-tag">{st.session_state.user_tag}</span>
                    </div>
                </div>
                <a href="?edit_profile=1" target="_self" class="material-symbols-rounded custom-cog-icon-trigger">
                    settings
                </a>
            </div>
        """,unsafe_allow_html =True )




def run ():

    if "user_name"not in st .session_state :
        st .session_state .user_name =f"Guest-{obtener_codigo_aleatorio()}"
    if "user_tag"not in st .session_state :
        st .session_state .user_tag ="Free User"
    if "user_avatar_base64"not in st .session_state :
        st .session_state .user_avatar_base64 =""
    if "chat_seleccionado_id"not in st .session_state :
        st .session_state .chat_seleccionado_id =None 
    if "ultima_similitud"not in st .session_state :
        st .session_state ["ultima_similitud"]=None 


    if "audio_reproducido"not in st .session_state :
        st .session_state .audio_reproducido =False 


    if not st .session_state .audio_reproducido and os .path .exists ("assets/startup.mp3"):
        with open ("assets/startup.mp3","rb")as f :
            audio_bytes =f .read ()

        audio_base64 =base64 .b64encode (audio_bytes ).decode ()
        st .markdown (
        f'<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>',
        unsafe_allow_html =True 
        )
        st .session_state .audio_reproducido =True 

    chat_id =st .session_state .chat_seleccionado_id 

    if "instancia_chat_id"not in st .session_state :
        st .session_state .instancia_chat_id =None 

    if st .session_state .instancia_chat_id !=chat_id :
        st .session_state .instancia_chat_id =chat_id 
        st .session_state .mensajes_chat_actual =cargar_chat (chat_id )if chat_id else []

    if "mensajes_chat_actual"not in st .session_state :
        st .session_state .mensajes_chat_actual =cargar_chat (chat_id )if chat_id else []

    mensajes =st .session_state .mensajes_chat_actual 
    logo_avatar_path ="assets/chatprofile.png"

    inject_css (is_blank_slate =(len (mensajes )==0 ))
    render_profile_sidebar ()


    if len (mensajes )==0 :
        st .markdown ("<br><br><br>",unsafe_allow_html =True )
        c1 ,c2 ,c3 =st .columns ([1 ,4 ,1 ])
        with c2 :
            st .markdown ('<div class="landing-marker"></div>',unsafe_allow_html =True )
            logo_data =get_image_base64 ("assets/logogenesis.png")
            if logo_data :
                st .markdown (f"""
                    <div class="logo-container">
                        <div class="logo-wrapper">
                            <img src="data:image/png;base64,{logo_data}" class="genesis-logo" alt="Genesis Logo">
                        </div>
                    </div>
                """,unsafe_allow_html =True )
            else :
                st .markdown ("<div style='text-align:center; color:#ff007f;'>[Asset missing at assets/logogenesis.png]</div>",unsafe_allow_html =True )
                st .markdown ("<br><br>",unsafe_allow_html =True )

            st .markdown ('<h1 style="text-align:center; font-size:3.5rem; font-weight:300; color:white; margin:0px; padding-bottom:5px;">What can I help you with?</h1>',unsafe_allow_html =True )
            st .markdown ('<p style="text-align:center; color:#9aa0a6; font-size:1.1rem; margin-bottom:25px;">Ask Genesis about anything!</p>',unsafe_allow_html =True )

            prompt =st .chat_input ("Ask Genesis anything...",key ="blank_slate_chat_input")

        if prompt :
            mensajes .append ({"role":"user","content":prompt })
            respuesta =consultar_llm (prompt )
            mensajes .append ({"role":"assistant","content":respuesta })
            guardar_chat (st .session_state .chat_seleccionado_id ,mensajes )
            st .rerun ()


    else :
        for index ,msg in enumerate (mensajes ):
            avatar_to_use =logo_avatar_path if msg ["role"]=="assistant"else None 
            with st .chat_message (msg ["role"],avatar =avatar_to_use ):
                if msg ["role"]=="assistant":
                    pct =st .session_state ["ultima_similitud"]if index ==len (mensajes )-1 else None 
                    texto_limpio ,html_banner =extraer_y_renderizar_banner (msg ["content"],similitud_pct =pct )

                    if html_banner :
                        st .markdown (html_banner ,unsafe_allow_html =True )
                    st .markdown (f'<div class="chat-bubble-body-text">{texto_limpio}</div>',unsafe_allow_html =True )
                else :
                    st .markdown (msg ["content"])

        prompt =st .chat_input ("Ask Genesis anything...",key ="active_chat_input")
        if prompt :
            mensajes .append ({"role":"user","content":prompt })
            with st .chat_message ("user",avatar =None ):
                st .markdown (prompt )

            with st .chat_message ("assistant",avatar =logo_avatar_path ):
                respuesta =consultar_llm (prompt )
                pct =st .session_state ["ultima_similitud"]

                texto_limpio ,html_banner =extraer_y_renderizar_banner (respuesta ,similitud_pct =pct )
                if html_banner :
                    st .markdown (html_banner ,unsafe_allow_html =True )

                placeholder =st .empty ()
                texto =""

                for char in texto_limpio :
                    texto +=char 
                    placeholder .markdown (f'<div class="chat-bubble-body-text">{texto}</div>',unsafe_allow_html =True )

            mensajes .append ({"role":"assistant","content":respuesta })
            guardar_chat (chat_id ,mensajes )
            st .rerun ()

if __name__ =="__main__":
    run ()