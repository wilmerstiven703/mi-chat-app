import os
import streamlit as st
from google import genai
from google.genai import types
import PIL.Image

# 1. Configuración de la aplicación web
st.set_page_config(page_title="Mi Súper Chatbot IA", page_icon="🚀", layout="wide")
st.title("🚀 Mi Súper Chatbot con Visión Artificial")

# 2. Conexión segura con los secretos de Streamlit
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# 3. Inicializar el historial de mensajes en la memoria web
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []

# BARRA LATERAL: Opción para subir imágenes
st.sidebar.header("📸 Superpoder de Visión")
imagen_subida = st.sidebar.file_uploader("Sube una foto para que el bot la analice:", type=["jpg", "jpeg", "png"])

if imagen_subida is not None:
    imagen_pil = PIL.Image.open(imagen_subida)
    st.sidebar.image(imagen_pil, caption="Imagen cargada con éxito", use_container_width=True)

# Button para limpiar el chat si se llena mucho
if st.sidebar.button("🧹 Limpiar conversación"):
    st.session_state.historial_mensajes = []
    st.rerun()

# 4. Mostrar todos los mensajes anteriores en la pantalla
for mensaje in st.session_state.historial_mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario y respuesta de la IA
if pregunta_usuario := st.chat_input("Escribe tu mensaje o pregunta sobre la foto aquí..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    st.session_state.historial_mensajes.append({"rol": "user", "texto": pregunta_usuario})
    
    try:
        client = genai.Client()
        
        # Recopilamos los elementos a enviar (Texto + Imagen opcional)
        elementos_a_enviar = []
        
        # Si el usuario subió una imagen en la barra lateral, se la adjuntamos a la IA
        if imagen_subida is not None:
            elementos_a_enviar.append(imagen_pil)
            
        elementos_a_enviar.append(pregunta_usuario)
        
        # Enviamos la petición a Gemini 2.5 Flash
        respuesta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=elementos_a_enviar,
            config=types.GenerateContentConfig(
                system_instruction="Eres el mejor chatbot del mundo. Eres amigable, inteligente, hablas español y puedes ver imágenes detalladamente si el usuario las sube."
            )
        )
        
        # Mostrar respuesta de la IA
        with st.chat_message("assistant"):
            st.markdown(respuesta.text)
        st.session_state.historial_mensajes.append({"rol": "assistant", "texto": respuesta.text})
        
    except Exception as e:
        st.error(f"Ocurrió un problema de conexión con Google. Detalle: {e}")
