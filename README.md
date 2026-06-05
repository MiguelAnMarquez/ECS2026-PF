# 🌌 Genesis — AI Chat Assistant

Genesis es un chatbot asistente avanzado, inteligente y altamente personalizado, diseñado para ofrecer una experiencia de usuario interactiva y fluida. Integra un sistema de recuperación de información (RAG) basado en embeddings locales, detección automática de operaciones matemáticas, y una interfaz de usuario minimalista y estilizada construida sobre Streamlit.

El modelo está configurado bajo la identidad de **Genesis**, un entorno virtual adaptado con un motor semántico que prioriza cinco áreas de especialización académica: Videojuegos, Música, Matemáticas, Filosofía y Arte.

---

## ✨ Características Principales

* **🧠 Arquitectura RAG Local (Retrieval-Augmented Generation):** Escanea y fragmenta dinámicamente un archivo de conocimiento interno (`assets/knowledge.txt`). Mediante la métrica de *Similitud de Coseno*, inyecta contexto relevante en tiempo real si supera el umbral del 35%.
* **⚡ Respuestas de Ultra-Baja Latencia:** Potenciado por la API de **Groq** utilizando el modelo `llama-3.1-8b-instant`.
* **🌐 Reconocimiento de Idioma en Espejo:** Identifica de forma inmediata el idioma del usuario y genera el 100% de la respuesta y sus componentes en ese mismo idioma.
* **🧮 Motor de Resolución Matemática Integrado:** Detecta si la entrada del usuario es una operación aritmética pura, resolviéndola al instante a nivel de código sin consumir tokens de la API.
* **🎨 Interfaz de Usuario Premium (UI/UX):** * Fondos con gradientes dinámicos y animaciones fluidas (*Rainbow Glow*).
  * Renderizado de banners superiores automatizados según el área temática identificada (`■ [Área: ...]`).
  * Indicador visual flotante (Badge) que muestra el porcentaje de match semántico con sistema de Tooltips informativos.
  * Panel de gestión de identidad integrado (Permite cambiar nombre de pantalla y subir un Avatar personalizado en tiempo real).
* **💾 Historial de Chats Local:** Guarda y gestiona de forma persistente (en formato JSON) los hilos de conversación basados en el primer mensaje del usuario.

---

## 📂 Estructura del Proyecto

```text
├── app.py                # Código principal de la aplicación Streamlit
├── requirements.txt      # Dependencias del proyecto para el entorno de producción
├── assets/               # Recursos estáticos de la aplicación
│   ├── logogenesis.png   # Logo principal de la pantalla de bienvenida
│   ├── chatprofile.png   # Avatar por defecto del asistente
│   ├── startup.mp3       # Efecto de sonido al inicializar el sistema
│   └── knowledge.txt     # Base de conocimiento local para el sistema RAG
└── history/              # Directorio local autogenerado para el historial de chats (JSON)