import os
import streamlit as st
from google import genai
from google.genai import types

# 1. Configuración de la aplicación web
st.set_page_config(page_title="Mi Propio Chatbot", page_icon="🤖")
st.title("🤖 ¡Bienvenido a mi App de IA!")

# 2. Conexión segura con los secretos de Streamlit
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# 3. Inicializar el historial de mensajes plano en la memoria web
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []

# 4. Mostrar todos los mensajes anteriores en la pantalla
for mensaje in st.session_state.historial_mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario y respuesta de la IA
if pregunta_usuario := st.chat_input("Escribe un mensaje aquí..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    st.session_state.historial_mensajes.append({"rol": "user", "texto": pregunta_usuario})
    
    try:
        # Creamos un cliente limpio para cada mensaje (así nunca se cierra la conexión)
        client = genai.Client()
        
        # Estructuramos el historial para que Gemini entienda el contexto anterior
        historial_api = []
        for msg in st.session_state.historial_mensajes[:-1]:
            rol_api = "user" if msg["rol"] == "user" else "model"
            historial_api.append(types.Content(role=rol_api, parts=[types.Part.from_text(text=msg["texto"])]))
        
        # Enviamos la petición con la instrucción del sistema y el historial completo
        respuesta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=historial_api + [pregunta_usuario],
            config=types.GenerateContentConfig(
                system_instruction="Eres un chatbot amigable, experto en tecnología y creado por un programador genial llamado Wilmer."
            )
        )
        
        # Mostrar respuesta de la IA
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
        st.session_state.historial_mensajes.append({"rol": "assistant", "texto": respuesta.text})
        
    except Exception as e:
        st.error(f"Ocurrió un problema de conexión con Google. Inténtalo de nuevo. Detalle: {e}")
