import os
import streamlit as st
from groq import Groq

# 1. Configuración de la aplicación web
st.set_page_config(page_title="Mi Súper Chatbot Groq", page_icon="⚡", layout="wide")
st.title("⚡ Mi Súper Chatbot de Alta Velocidad (Mensajes Ilimitados)")

# 2. Conexión segura con los secretos de Streamlit
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# 3. Inicializar el historial de mensajes en la memoria web
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []

# Barra lateral simple
if st.sidebar.button("Toque para borrar chat"):
    st.session_state.historial_mensajes = []
    st.rerun()

# 4. Mostrar todos los mensajes anteriores en la pantalla
for mensaje in st.session_state.historial_mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario y respuesta de la IA (Llama 3 de Meta)
if pregunta_usuario := st.chat_input("Escribe tu mensaje aquí sin límites..."):
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    st.session_state.historial_mensajes.append({"rol": "user", "texto": pregunta_usuario})
    
    try:
        # Iniciamos el cliente oficial de Groq
        client = Groq()
        
        # Estructuramos el historial para que la IA recuerde el contexto
        historial_completo = [
            {"role": "system", "content": "Eres un chatbot ultra rápido, divertido y experto en tecnología creado por un programador genial llamado Wilmer. Hablas español perfectamente."}
        ]
        
        for msg in st.session_state.historial_mensajes:
            historial_completo.append({"role": msg["rol"], "content": msg["texto"]})
            
        # Llamamos al modelo ultra rápido Llama 3 (8b es el más veloz)
        with st.spinner("⚡ Pensando a la velocidad de la luz..."):
            respuesta_api = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=historial_completo,
            )
            
        respuesta_texto = respuesta_api.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(respuesta_texto)
        st.session_state.historial_mensajes.append({"rol": "assistant", "texto": respuesta_texto})
        
    except Exception as e:
        st.error(f"Ocurrió un problema técnico. Detalle: {e}")
