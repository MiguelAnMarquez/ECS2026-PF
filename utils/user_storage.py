import json 
import os
from datetime import datetime, timedelta

HISTORY_DIR = "history"
USERS_REGISTRY_FILE = os.path.join(HISTORY_DIR, "users", "users_registry.json")
SESSIONS_FILE = os.path.join(HISTORY_DIR, "sessions", "sessions.json")
SESSION_TIMEOUT_MINUTES = 2


def _ensure_history_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)

    for subdir in ["users", "chats", "sessions"]:
        os.makedirs(
            os.path.join(HISTORY_DIR, subdir),
            exist_ok=True
        )
        subdir_path = os.path.join(HISTORY_DIR, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)

def _cargar_usuarios():
    _ensure_history_dir()
    if not os.path.exists(USERS_REGISTRY_FILE):
        with open(USERS_REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump({"user_count": 0, "users": {}}, f, ensure_ascii=False, indent=4)
    try:
        with open(USERS_REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"user_count": 0, "users": {}}

def _guardar_usuarios(data):
    _ensure_history_dir()
    with open(USERS_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def _cargar_sesiones():
    _ensure_history_dir()
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"sessions": {}},
                f,
                ensure_ascii=False,
                indent=4
            )
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        ahora = datetime.now()
        sesiones_validas = {}

        for token, session in data.get("sessions", {}).items():
            try:
                expires_at = datetime.fromisoformat(
                    session["expires_at"]
                )

                if ahora <= expires_at:
                    sesiones_validas[token] = session
            except Exception:
                continue

        data["sessions"] = sesiones_validas
        _guardar_sesiones(data)

        return data

    except Exception:
        return {"sessions": {}}

def _guardar_sesiones(data):
    _ensure_history_dir()
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def limpiar_sesiones_expiradas():
    session_data = _cargar_sesiones()

    ahora = datetime.now()

    sesiones_validas = {}

    for token, session in session_data.get("sessions", {}).items():

        try:
            expires_at = datetime.fromisoformat(
                session["expires_at"]
            )

            if ahora <= expires_at:
                sesiones_validas[token] = session

        except Exception:
            continue

    session_data["sessions"] = sesiones_validas

    _guardar_sesiones(session_data)

def refrescar_session(session_token):
    session_data = _cargar_sesiones()

    session = session_data["sessions"].get(session_token)

    if not session:
        return False

    session["expires_at"] = (
        datetime.now() +
        timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ).isoformat()

    _guardar_sesiones(session_data)

    return True