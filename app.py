import streamlit as st
import base64
import os
import json
import time                                                        

st.set_page_config(
    page_title="Genesis",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="assets/logogenesis.png"
)
     
if "app_inicializada" not in st.session_state:
    st.session_state.app_inicializada = False

if not st.session_state.app_inicializada:
    placeholder_loading = st.empty()
    with placeholder_loading.container():
        st.markdown("""
            <style>
            /* Forzamos que cubra toda la pantalla de forma absoluta */
            .loading-wrapper {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background-color: #0b0d12;
                display: flex; flex-direction: column; justify-content: center; align-items: center;
                z-index: 999999;
            }
            
            /* Contenedor del Spinner Arcoíris */
            .spinner-rainbow-container {
                position: relative;
                width: 65px;
                height: 65px;
                margin-bottom: 24px;
            }
            
            /* Efecto de degradado cónico arcoíris premium */
            .spinner-genesis {
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background: conic-gradient(from 0deg, #ff007f, #7f00ff, #00ffff, #00ff7f, #ffff00, #ff007f);
                -webkit-mask: radial-gradient(farthest-side, transparent 82%, #000 83%);
                mask: radial-gradient(farthest-side, transparent 82%, #000 83%);
                animation: spin 0.8s linear infinite, rainbow-shift 4s linear infinite;
            }
            
            .loading-text {
                color: #ffffff;
                font-family: system-ui, -apple-system, sans-serif;
                font-size: 1.15rem;
                font-weight: 400;
                letter-spacing: 0.03em;
                text-align: center;
                animation: pulse 2s ease-in-out infinite;
            }
            
            .loading-subtext {
                color: #64748b;
                font-family: system-ui, -apple-system, sans-serif;
                font-size: 0.88rem;
                margin-top: 8px;
                letter-spacing: 0.01em;
                text-align: center;
            }

            /* Rotación física del spinner */
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Ciclo dinámico de color arcoíris */
            @keyframes rainbow-shift {
                0% { filter: hue-rotate(0deg); }
                100% { filter: hue-rotate(360deg); }
            }
            
            /* Suave latido para el texto principal */
            @keyframes pulse {
                0%, 100% { opacity: 0.6; }
                50% { opacity: 0.95; }
            }

            /* Ocultar el layout nativo de Streamlit temporalmente */
            [data-testid="stSidebar"], [data-testid="stHeader"], .stAppHeader {
                display: none !important;
            }
            </style>
            <div class="loading-wrapper">
                <div class="spinner-rainbow-container">
                    <div class="spinner-genesis"></div>
                </div>
                <div class="loading-text">Genesis is now loading...</div>
                <div class="loading-subtext">We're preparing everything for you...</div>
            </div>
        """, unsafe_allow_html=True)
    
                                                                        
                           
                                                                               
                                                                        
    from slpages import new_chat
    
                                                                                    
                                                                               
    new_chat.cargar_modelo_semantico()
    
                                                                                        
    time.sleep(0.5)
    
    st.session_state.app_inicializada = True
    placeholder_loading.empty()                                           
    st.rerun()

                                                            
                                                            
                                                            
def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return ""

img_base64 = get_base64_img("assets/minimalist_logo.png")

if not os.path.exists("history"):
    os.makedirs("history")

def listar_chats():
    chats = []
    for archivo in os.listdir("history"):
        if archivo.endswith(".json"):
            try:
                with open(os.path.join("history", archivo), encoding="utf-8") as f:
                    data = json.load(f)
                chats.append({
                    "id": archivo.replace(".json", ""),
                    "titulo": data.get("titulo", "New Chat"),
                    "fecha": data.get("fecha", "")
                })
            except:
                pass
    return chats

@st.dialog("Rename Chat")
def mostrar_modal_rename(chat_id, titulo_actual):
    st.markdown("""
        <style>
        div[data-testid="stPopoverBody"] {
            display: none !important; visibility: hidden !important; opacity: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.write("Enter a new title for this conversation:")
    with st.form("rename_form", border=False):
        nuevo_titulo = st.text_input("Title", value=titulo_actual, label_visibility="collapsed")
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            btn_save = st.form_submit_button("Save Changes", use_container_width=True, type="primary")
        with col2:
            btn_cancel = st.form_submit_button("Cancel", use_container_width=True)
            
        if btn_save:
            if nuevo_titulo.strip() and nuevo_titulo.strip() != titulo_actual:
                archivo_path = os.path.join("history", f"{chat_id}.json")
                if os.path.exists(archivo_path):
                    try:
                        with open(archivo_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        data["titulo"] = nuevo_titulo.strip()
                        with open(archivo_path, "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                    except:
                        pass
            st.session_state.force_close_popover = True
            st.rerun()
        if btn_cancel:
            st.session_state.force_close_popover = True
            st.rerun()

if "chat_seleccionado_id" not in st.session_state:
    st.session_state.chat_seleccionado_id = None

if "force_close_popover" not in st.session_state:
    st.session_state.force_close_popover = False

if st.session_state.force_close_popover:
    st.session_state.force_close_popover = False
    st.rerun()

logo_style = f"""
[data-testid="stLogoSpacer"]::before {{
    content: "" !important; width: 50px !important; height: 50px !important;
    background-image: url("data:image/png;base64,{img_base64}") !important;
    background-size: contain !important; background-repeat: no-repeat !important; background-position: center !important;
}}
""" if img_base64 else ""

st.markdown(f"""
<style>
.stApp{{background:#0b0d12;}}
[data-testid="stSidebar"]{{background:#171717; border-right:1px solid rgba(255,255,255,.05);}}
[data-testid="stSidebarContent"]{{padding:0px !important;}}
[data-testid="stSidebarUserContent"]{{padding:4px 12px 16px 12px !important;}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{{gap:0px !important;}}
section[data-testid="stSidebar"] [data-testid="stElementContainer"]{{margin-bottom:2px !important; padding-bottom:0px !important;}}
.recent-title{{display:flex !important; align-items:center !important; font-size:1rem !important; font-weight:500; color:#8e8e8e; margin:14px 12px 14px 12px !important; text-align:left; white-space:nowrap !important;}}
.recent-title::after{{content:"" !important; flex:1 !important; margin-left:12px !important; border-bottom:1px solid rgba(255,255,255,0.06) !important;}}
[data-testid="stSidebarHeader"]{{padding:16px 12px 12px 12px !important; border-bottom:1px solid rgba(255,255,255,0.06) !important; margin-bottom:4px !important; display:flex !important; justify-content:space-between !important; align-items:center !important;}}
[data-testid="stLogoSpacer"]{{display:flex !important; align-items:center !important; gap:12px !important; width:auto !important;}}
{logo_style}
[data-testid="stLogoSpacer"]::after{{content:"Genesis AI" !important; color:#ffffff !important; font-size:1.15rem !important; font-weight:500 !important; font-family:inherit !important;}}

/* Base Sidebar Navigation Controls Styling */
section[data-testid="stSidebar"] .stButton button{{width:100% !important; border:none !important; border-radius:8px !important; background:transparent !important; color:white !important; display:flex !important; justify-content:flex-start !important; align-items:center !important; text-align:left !important; padding:8px 12px !important; margin:0 !important;}}
section[data-testid="stSidebar"] .stButton button:hover{{background:#242424 !important;}}
section[data-testid="stSidebar"] .stButton button > div, section[data-testid="stSidebar"] .stButton button > div > span, section[data-testid="stSidebar"] .stButton button div[data-testid="stMarkdownContainer"]{{display:flex !important; justify-content:flex-start !important; align-items:center !important; text-align:left !important; width:100% !important; gap:12px !important;}}
section[data-testid="stSidebar"] .stButton button div[data-testid="stMarkdownContainer"] p{{text-align:left !important; margin:0 !important; width:auto !important;}}

/* Recent History Row Overlay Actions Custom Styling */
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]{{background:transparent !important; border-radius:8px !important; padding:0px 4px 0px 0px !important; transition:background 0.12s ease-in-out !important; align-items:center !important; gap:0px !important;}}
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover{{background:#242424 !important;}}
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton button, section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton button:hover{{background:transparent !important;}}
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div:nth-child(2){{opacity:0 !important; pointer-events:none !important; transition:opacity 0.15s ease-in-out !important; display:flex !important; justify-content:center !important; align-items:center !important;}}
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover > div:nth-child(2), section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:focus-within > div:nth-child(2){{opacity:1 !important; pointer-events:auto !important;}}

/* Context Menu Options Popover Minimalizer (Three Dots) */
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stPopover"]{{display:flex !important; width:100% !important; justify-content:center !important; align-items:center !important;}}
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stPopover"] button{{background:transparent !important; border:none !important; box-shadow:none !important; border-radius:6px !important; width:34px !important; height:34px !important; padding:0px !important; display:flex !important; justify-content:center !important; align-items:center !important;}}
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stPopover"] button:hover{{background:rgba(255, 255, 255, 0.08) !important;}}
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stPopover"] button > div > div:nth-child(2){{display:none !important; visibility:hidden !important; width:0px !important; height:0px !important;}}
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stPopover"] button > div > div:nth-child(1){{width:100% !important; justify-content:center !important; display:flex !important;}}

/* Global Menu Dropdown Body Context Containers */
div[data-testid="stPopoverBody"]{{background-color:#171717 !important; border:1px solid rgba(255, 255, 255, 0.05) !important; border-radius:8px !important; box-shadow:0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5) !important; min-width:max-content !important; width:max-content !important; padding:0px !important;}}
div[data-testid="stPopoverBody"] div[data-testid="stVerticalBlock"]{{gap:0px !important;}}
div[data-testid="stPopoverBody"] div[data-testid="stElementContainer"]{{margin-bottom:0px !important; padding-bottom:0px !important;}}
div[data-testid="stPopoverBody"] .stButton button{{background-color:#171717 !important; border:none !important; box-shadow:none !important; color:#e0e0e0 !important; padding:12px 20px !important; border-radius:0px !important; width:100% !important; transition:background-color 0.1s ease !important;}}
div[data-testid="stPopoverBody"] div[data-testid="stElementContainer"]:first-child button{{border-top-left-radius:8px !important; border-top-right-radius:8px !important;}}
div[data-testid="stPopoverBody"] div[data-testid="stElementContainer"]:last-child button{{border-bottom-left-radius:8px !important; border-bottom-right-radius:8px !important;}}
div[data-testid="stPopoverBody"] .stButton button:hover{{background-color:#242424 !important; color:#ffffff !important; border:none !important;}}

/* Main Dashboard Aesthetic Glow FX */
.center-glow{{position:fixed; top:50%; left:55%; width:900px; height:900px; transform:translate(-50%,-50%); background:radial-gradient(circle, rgba(29,78,216,.22) 0%, rgba(29,78,216,.08) 30%, transparent 70%); pointer-events:none; z-index:-1;}}

/* ==========================================================
   STABLE PERMANENT INHERITANCE RULES
   ========================================================= */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stPopover"] {{
    width: 100% !important;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stPopover"] button {{
    width: 100% !important;
    height: auto !important;
    background-color: unset !important;
    background: transparent !important;
    border: 0 !important;
    border-radius: 8px !important;
    color: white !important;
    display: flex !important;
    align-items: center !important;
    padding: 8px 12px !important;
    box-shadow: none !important;
    margin: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stPopover"] button:hover {{
    background: #242424 !important;
    background-color: #242424 !important;
}}

/* Target structural sub-div layout elements that force default center alignment values */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stPopover"] button > div,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stPopover"] button div[class*="-1lads1q"] {{
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stPopover"] button span[class*="-1kl7f1u"] {{
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 12px !important;
    width: 100% !important;
}}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stPopover"] button div[data-testid="stMarkdownContainer"] {{
    display: flex !important;
    visibility: visible !important;
    width: auto !important;
    height: auto !important;
    color: white !important;
    white-space: nowrap !important;
    overflow: visible !important;
    font-size: 1rem !important;
    font-weight: normal !important;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stPopover"] button svg:not([data-testimonial]) {{
    display: none !important;
    visibility: hidden !important;
}}

/* Custom formatting configuration inside popover filter selection pane */
div[data-testid="stPopoverBody"]:has(div[data-testid="stMarkdownContainer"] .search-combobox-marker) {{
    width: 270px !important;
    min-width: 270px !important;
    padding: 12px !important;
}}
div[data-testid="stPopoverBody"] .search-combobox-marker + div .stButton button {{
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
    font-size: 0.85rem !important;
    color: #cccccc !important;
}}
div[data-testid="stPopoverBody"] .search-combobox-marker + div .stButton button:hover {{
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
}}

/* ==========================================================
   HOMEPAGE EMPTY SLATE BLANK CHAT INPUT BACKGROUND REPAIR
   ========================================================= */
div[data-testid="stChatInput"],
div[data-testid="stChatInput"] > div,
div[data-baseweb="base-input"],
div[data-baseweb="textarea"] {{
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
.stChatInputTextArea, 
div[data-testid="stChatInput"] textarea,
div[data-baseweb="base-input"] textarea {{
    background-color: #171717 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}}
div[data-testid="stChatInput"] textarea:focus,
div[data-baseweb="base-input"] textarea:focus {{
    border-color: rgba(255, 0, 128, 0.35) !important;
    box-shadow: 0 0 18px rgba(255, 0, 128, 0.12), 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    outline: none !important;
}}

/* INSTANT FRONTEND CLICK INDICATOR (CSS ONLY OVERLAY) */
section[data-testid="stSidebar"] .stButton button:active::after {{
    content: "Connecting..." !important;
    position: absolute !important;
    right: 12px !important;
    font-size: 0.75rem !important;
    color: rgba(255, 255, 255, 0.4) !important;
    animation: pulse 1s infinite !important;
}}

/* Global fallback fallback spinner override if Streamlit delays building elements */
div[data-testid="stStatusWidget"] {{
    background-color: #171717 !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
}}
</style>
<div class="center-glow"></div>
""", unsafe_allow_html=True)

                                                            
                                                         
                                                            
if "sort_order_abc" not in st.session_state:
    st.session_state.sort_order_abc = False
if "search_query_filter" not in st.session_state:
    st.session_state.search_query_filter = ""

if "combobox_text_input_field" in st.session_state:
    st.session_state.search_query_filter = st.session_state["combobox_text_input_field"]

current_query = st.session_state.search_query_filter.strip()
combobox_label = f"Search: \"{current_query[:10]}...\"" if len(current_query) > 10 else f"Search: \"{current_query}\"" if current_query else "Search"

with st.sidebar:
    if st.button("New Chat", icon=":material/edit_square:", use_container_width=True):
        st.session_state.chat_seleccionado_id = None
        if "mensajes_chat_actual" in st.session_state:
            del st.session_state["mensajes_chat_actual"]
        st.rerun()

    with st.popover(combobox_label, icon=":material/search:", use_container_width=True):
        st.markdown('<div class="search-combobox-marker"></div>', unsafe_allow_html=True)
        
        st.text_input(
            "Filter recent list...", 
            value=st.session_state.search_query_filter,
            placeholder="Type text to filter...", 
            label_visibility="collapsed",
            key="combobox_text_input_field"
        )
        
        sort_btn_text = "Sort: Alphabetical (A-Z)" if st.session_state.sort_order_abc else "Sort: Newest First"
        if st.button(sort_btn_text, use_container_width=True, key="combobox_sort_order_action"):
            st.session_state.sort_order_abc = not st.session_state.sort_order_abc
            st.rerun()
            
        if current_query:
            if st.button("Clear Filters", use_container_width=True):
                st.session_state.search_query_filter = ""
                if "combobox_text_input_field" in st.session_state:
                    del st.session_state["combobox_text_input_field"]
                st.rerun()

    st.markdown('<div class="recent-title">Recent</div>', unsafe_allow_html=True)

    all_chats = listar_chats()
    filtro_texto = st.session_state.search_query_filter.strip()
    if filtro_texto:
        all_chats = [c for c in all_chats if filtro_texto.lower() in c["titulo"].lower()]

    if st.session_state.sort_order_abc:
        all_chats = sorted(all_chats, key=lambda x: x["titulo"].lower())
    else:
        all_chats = sorted(all_chats, key=lambda x: x["fecha"], reverse=True)

    if not all_chats:
        st.markdown("<p style='color: #55555a; font-size: 0.85rem; padding-left: 14px; font-style: italic;'>No conversations found</p>", unsafe_allow_html=True)
    else:
        for chat in all_chats:
            titulo = chat["titulo"]
            if len(titulo) > 18:
                titulo = titulo[:18] + "..."

            col_title, col_action = st.columns([0.84, 0.16])
            with col_title:
                if st.button(titulo, key=chat["id"], icon=":material/chat_bubble:", use_container_width=True):
                    st.session_state.chat_seleccionado_id = chat["id"]
                    st.rerun()

            with col_action:
                with st.popover("", icon=":material/more_vert:", use_container_width=True, key=f"pop_{chat['id']}"):
                    if st.button("Rename Chat", key=f"ren_btn_{chat['id']}", icon=":material/edit:", use_container_width=True):
                        mostrar_modal_rename(chat["id"], chat["titulo"])
                    
                    if st.button("Delete Chat", key=f"del_{chat['id']}", icon=":material/delete:", use_container_width=True):
                        archivo_path = os.path.join("history", f"{chat['id']}.json")
                        if os.path.exists(archivo_path):
                            os.remove(archivo_path)
                        if st.session_state.chat_seleccionado_id == chat["id"]:
                            st.session_state.chat_seleccionado_id = None
                            if "mensajes_chat_actual" in st.session_state:
                                del st.session_state["mensajes_chat_actual"]
                        st.rerun()

                                                            
                                                      
                                                            
from slpages import new_chat
new_chat.run()