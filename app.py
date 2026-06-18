import os
import subprocess
import sys

# TRUCO DE EMERGENCIA: Obliga al servidor a instalar la librería si no existe
try:
    from google import genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])
    from google import genai

import streamlit as st

# 1. Configuración de la aplicación web
st.set_page_config(page_title="Mi Propio Chatbot", page_icon="🤖")
st.title("🤖 ¡Bienvenido a mi App de IA!")

# 2. Conexión segura con los secretos de Streamlit
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# 3. Inicializar el chat con memoria
if "historial" not in st.session_state:
    client = genai.Client()
    st.session_state.chat = client.chats.create(
        model="gemini-2.5-flash",
        config={'system_instruction': 'Eres un chatbot amigable creado por un programador genial.'}
    )
    st.session_state.historial = []

# 4. Mostrar el historial en pantalla
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario y respuesta de la IA
if pregunta_usuario := st.chat_input("Escribe un mensaje aquí..."):
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    st.session_state.historial.append({"rol": "user", "texto": pregunta_usuario})
    
    respuesta = st.session_state.chat.send_message(pregunta_usuario)
    
    with st.chat_message("assistant"):
        st.markdown(respuesta.text)
    st.session_state.historial.append({"rol": "assistant", "texto": respuesta.text})
