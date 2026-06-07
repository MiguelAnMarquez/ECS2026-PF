import streamlit as st
import os
import json
import uuid
import time
import bcrypt
from datetime import datetime, timedelta

from utils.user_storage import _cargar_usuarios
from utils.user_storage import _guardar_usuarios
from utils.user_storage import _guardar_sesiones
from utils.user_storage import _cargar_sesiones
from utils.user_storage import _ensure_history_dir

HISTORY_DIR = "history"
USERS_REGISTRY_FILE = os.path.join(HISTORY_DIR, "users", "users_registry.json")
SESSIONS_FILE = os.path.join(HISTORY_DIR, "sessions", "sessions.json")
SESSION_TIMEOUT_MINUTES = 2

def _hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(rounds=12)
    ).decode()

def _verify_password(password, stored_hash):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash.encode("utf-8")
    )

def _generar_id_usuario():
    contador = 1
    while True:
        user_id = f"usr_{contador:05d}"
        if not _usuario_id_existe(user_id):
            return user_id
        contador += 1

def _generar_session_token():
    return str(uuid.uuid4())

def _usuario_id_existe(user_id):
    _ensure_history_dir()
    try:
        with open(USERS_REGISTRY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return user_id in data.get("users", {})
    except:
        return False

def _username_existe(username):
    _ensure_history_dir()
    try:
        with open(USERS_REGISTRY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for user_id, user_data in data.get("users", {}).items():
            if user_data.get("username") == username:
                return True
        return False
    except:
        return False

def registrar_usuario(username, password, display_name):
    if not username or not password or not display_name:
        return False, "All fields are required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if _username_existe(username):
        return False, "Username already taken"
    
    user_id = _generar_id_usuario()
    password_hash = _hash_password(password)
    
    data = _cargar_usuarios()
    data["user_count"] += 1
    data["users"][user_id] = {
        "id": user_id,
        "username": username,
        "display_name": display_name,
        "password_hash": password_hash,
        "role": "Free User",
        "avatar_base64": "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    _guardar_usuarios(data) 
    os.makedirs(
        os.path.join(HISTORY_DIR, "chats", user_id),
        exist_ok=True
    )
    return True, "User Registered Successfully!"

def validar_login(username, password):
    if not username or not password:
        return False, None, None, "Username and password required"
    
    data = _cargar_usuarios()
    
    for user_id, user_data in data.get("users", {}).items():
        if user_data.get("username") == username:
            if _verify_password(password,user_data.get("password_hash")):
                session_token = _generar_session_token()
                session_data = _cargar_sesiones()
                session_data["sessions"][session_token] = {
                    "user_id": user_id,
                    "token": session_token,
                    "created_at": datetime.now().isoformat(),
                    "expires_at": (datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)).isoformat(),
                }
                _guardar_sesiones(session_data)
                os.makedirs(
                    os.path.join(HISTORY_DIR, "chats", user_id),
                    exist_ok=True
                )
                return True, user_id, session_token, "Login successful"
            else:
                return False, None, None, "Invalid password"
    
    return False, None, None, "User not found"

def validar_session(session_token):

    if not session_token:
        return False, None

    session_data = _cargar_sesiones()
    sessions = session_data.get("sessions", {})
    if session_token not in sessions:
        return False, None

    session = sessions[session_token]
    expires_at = datetime.fromisoformat(
        session.get("expires_at")
    )

    if datetime.now() > expires_at:
        return False, None

    session["expires_at"] = (
        datetime.now() +
        timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ).isoformat()

    _guardar_sesiones(session_data)

    return True, session.get("user_id")

def obtener_usuario_por_id(user_id):
    data = _cargar_usuarios()
    return data.get("users", {}).get(user_id)

def obtener_usuario_por_username(username):
    data = _cargar_usuarios()
    for user_id, user_data in data.get("users", {}).items():
        if user_data.get("username") == username:
            return user_data
    return None

def obtener_chat_dir(user_id):
    path = os.path.join(
        HISTORY_DIR,
        "chats",
        user_id
    )

    os.makedirs(path, exist_ok=True)

    return path

def actualizar_usuario(user_id, updates):
    data = _cargar_usuarios()
    
    if user_id not in data.get("users", {}):
        return False, "User not found"
    
    user = data["users"][user_id]
    
    if "username" in updates and updates["username"] != user.get("username"):
        if _username_existe(updates["username"]):
            return False, "Username already taken"
    
    allowed_fields = ["display_name","username","avatar_base64","custom_prompt"]
    for field in allowed_fields:
        if field in updates:
            user[field] = updates[field]
    
    if "password" in updates:
        user["password_hash"] = _hash_password(updates["password"])
    
    user["updated_at"] = datetime.now().isoformat()
    _guardar_usuarios(data)
    return True, "User updated successfully"

def restaurar_usuario_desde_session(session_token):

    valido, user_id = validar_session(session_token)

    if not valido:
        return False

    user_data = obtener_usuario_por_id(user_id)

    if not user_data:
        return False

    st.session_state.autenticado = True
    st.session_state.user_id = user_id
    st.session_state.username = user_data.get("username", "")
    st.session_state.display_name = user_data.get("display_name", "")
    st.session_state.role = user_data.get("role", "Free User")
    st.session_state.custom_prompt = (user_data.get("custom_prompt", ""))
    st.session_state.user_avatar_base64 = user_data.get("avatar_base64", "")
    st.session_state.session_token = session_token

    return True

def guardar_token_sesion(cookie_manager, session_token):
    cookie_manager.set(
        "genesis_session",
        session_token,
        expires_at=datetime.now() + timedelta(days=30)
    )

def obtener_token_sesion(cookie_manager):

    return cookie_manager.get(
        "genesis_session"
    )

def render_login(cookie_manager=None):
    import base64
    
    logo_path = "assets/logogenesis.png"
    logo_html = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="width: 120px; height: auto; margin: 0px;">'
    
    st.markdown(f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], 
        [data-testid="stAppViewMain"], 
        .stMainBlockContainer, 
        .block-container,
        [data-testid="stMainSpaceElement"],
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stAppViewBlockContainer"] {{
            padding: 0px !important;
            margin: 0px !important;
            width: 100% !important;
            background-color: #0b0d12 !important;
        }}
        [data-testid="stSidebar"], 
        [data-testid="stHeader"], 
        .stAppHeader, 
        [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
            visibility: hidden !important;
            width: 0px !important;
        }}
        [data-testid="stVerticalBlock"] {{
            margin: 0px !important;
            padding: 0px !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) {{
            background: rgba(23, 23, 27, 0.6) !important;
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 48px 40px !important;
            border-radius: 20px;
            width: auto !important;
            max-width: 420px !important;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.7);
            position: relative !important;
            top: auto !important;
            left: auto !important;
            transform: none !important;
            z-index: 99999;
            gap: 0px !important;
            min-height: unset !important;
            margin: 80px auto !important;
        }}
        .custom-login-header {{
            text-align: center;
            color: #ffffff;
            margin-bottom: 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .custom-login-header p {{
            color: #a0a0a8;
            margin: 8px 0 8px 0;
            font-size: 0.95rem;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [role="tablist"] {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
            margin-bottom: 24px !important;
            background-color: transparent !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [role="tab"] {{
            color: #8a8a93 !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [role="tab"][aria-selected="true"] {{
            color: #FF9800 !important;
            background-color: transparent !important;
            border-bottom: 2px solid #FF9800 !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [role="tab"]:hover {{
            color: #ffffff !important;
            background-color: transparent !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [data-testid="stTextInputRootElement"] {{
            padding-right: 0px !important;
            background-color: transparent !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) input {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            padding: 12px 14px !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) input:focus {{
            border-color: #FF9800 !important;
            box-shadow: 0 0 0 2px rgba(255, 152, 0, 0.1) !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [data-testid="stTextInput"] > div {{
            position: relative !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [data-testid="stTextInput"] button {{
            background: transparent !important;
            border: none !important;
            color: #8a8a93 !important;
            cursor: pointer !important;
            position: absolute !important;
            right: 10px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            margin: 0px !important;
            padding: 0px !important;
            height: auto !important;
            width: auto !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [data-testid="stTextInput"] button:hover {{
            color: #FF9800 !important;
            background: transparent !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) button:not([data-testid="stTextInput"] button) {{
            background: #FF9800 !important;
            color: #0b0d12 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            width: 100% !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) button:not([data-testid="stTextInput"] button):hover,
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) button:not([data-testid="stTextInput"] button):focus,
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) button:not([data-testid="stTextInput"] button):active {{
            background: #E88D00 !important;
            color: #0b0d12 !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) label {{
            color: #e2e8f0 !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) h3 {{
            color: #ffffff !important;
            font-size: 1.1rem !important;
            margin: 5px 0px 20px 0px !important;
            padding: 0px !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [data-testid="stAlert"] {{
            border-radius: 8px !important;
            border: 1px solid rgba(255, 152, 0, 0.2) !important;
        }}
        [data-testid="stVerticalBlock"]:has(div.custom-login-header) [role="tabpanel"] {{
            padding-top: 1rem !important;
            background-color: transparent !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="custom-login-header">{logo_html}<p>LLM / RAG Based AI Chatbot</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown("### Welcome Back")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if username and password:
                success, user_id, session_token, message = validar_login(username, password)
                if success:

                    if cookie_manager:
                        guardar_token_sesion(
                            cookie_manager,
                            session_token
                        )

                    user_data = obtener_usuario_por_id(user_id)

                    st.session_state.show_loading_screen = True

                    st.session_state.session_token = session_token
                    st.session_state.autenticado = True
                    st.session_state.user_id = user_id
                    st.session_state.username = user_data.get("username", username)
                    st.session_state.display_name = user_data.get("display_name", username)
                    st.session_state.role = user_data.get("role", "Free User")
                    st.session_state.user_avatar_base64 = user_data.get("avatar_base64", "")

                    time.sleep(0.5)
                else:
                    st.error(message)
            else:
                st.error("Please enter username and password")
    
    with tab2:
        st.markdown("### Create Account")
        reg_username = st.text_input("Choose Username", key="reg_username")
        reg_display_name = st.text_input("Display Name", key="reg_display_name")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        
        if st.button("Register", use_container_width=True, type="primary"):
            if not all([reg_username, reg_display_name, reg_password, reg_password_confirm]):
                st.error("All fields are required")
            elif reg_password != reg_password_confirm:
                st.error("Passwords do not match")
            else:
                success, message = registrar_usuario(reg_username, reg_password, reg_display_name)
                if success:
                    st.success(message)
                    st.info("Please go to Login tab to sign in")
                else:
                    st.error(message)