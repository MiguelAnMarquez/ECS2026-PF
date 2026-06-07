import streamlit as st 
import json 
import os 
from datetime import datetime 

def get_user_history_dir():

    user_id = st.session_state.get("user_id")

    if not user_id:
        raise Exception("No authenticated user.")

    path = os.path.join(
        "history",
        "chats",
        user_id
    )

    os.makedirs(path, exist_ok=True)

    return path

def validate_chat_access(chat_id):

    if not chat_id:
        return None

    chat_dir = get_user_history_dir()

    path = os.path.join(
        chat_dir,
        f"{chat_id}.json"
    )

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    except Exception:
        return None

def listar_chats():

    chats = []

    history_dir_f = get_user_history_dir()

    if os.path.exists(history_dir_f):
        for archivo in os.listdir(history_dir_f):
            if archivo.endswith(".json"):
                try:
                    with open(os.path.join(history_dir_f, archivo), encoding="utf-8") as f:
                        data = json.load(f)
                    chats.append({
                        "id": archivo.replace(".json", ""),
                        "titulo": data.get("titulo", "New Chat"),
                        "fecha": data.get("fecha", "")
                    })
                except:
                    pass
    return chats

def get_user_chat_dir():
    user_id = st.session_state.get("user_id")

    if not user_id:
        raise Exception("No authenticated user.")

    chat_dir = os.path.join(
        "history",
        "chats",
        user_id
    )

    os.makedirs(chat_dir, exist_ok=True)

    return chat_dir

def cargar_chat(chat_id):

    chat_dir = get_user_chat_dir()

    path = os.path.join(
        chat_dir,
        f"{chat_id}.json"
    )

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("mensajes", [])
    return []

def guardar_chat(chat_id, mensajes):

    if chat_id is None:
        chat_id = "chat_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        st.session_state.chat_seleccionado_id = chat_id 
        

    titulo = "New Chat"

    if mensajes:
        titulo = mensajes[0].get("content", "New Chat")

    if len(titulo) > 40:
        titulo = titulo[:40] + "..."

    data = {
        "titulo": titulo,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mensajes": mensajes 
    }

    chat_dir = get_user_chat_dir()

    path = os.path.join(
        chat_dir,
        f"{chat_id}.json"
    )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)