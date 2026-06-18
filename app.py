import os
import streamlit as st
from groq import Groq

# 1. Configuración de la aplicación web
st.set_page_config(page_title="Mi Súper Chatbot Groq", page_icon="⚡", layout="wide")
st.title("⚡ Mi Súper Chatbot de Alta Velocidad (Mensajes Ilimitados)")

# 2. Conexión segura con los secretos de Streamlit
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
elif not os.environ.get("GROQ_API_KEY"):
    st.error("Por favor, configura la variable de entorno o secreto GROQ_API_KEY.")
    st.stop()

# 3. Inicializar el historial de mensajes en la memoria web
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []

# --- NUEVA BARRA LATERAL CONFIGURADA ---
st.sidebar.header("🛠️ Configuración")

# Selector de modelos actualizado a las versiones vigentes
modelo_seleccionado = st.sidebar.selectbox(
    "Elige el cerebro de la IA:",
    options=["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
    index=0,
    help="El modelo 8b es ultra rápido; el 70b es ideal para tareas complejas o programación."
)

st.sidebar.markdown("---")

if st.sidebar.button("Toque para borrar chat"):
    st.session_state.historial_mensajes = []
    st.rerun()

# 4. Mostrar todos los mensajes anteriores en la pantalla
for mensaje in st.session_state.historial_mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario y respuesta de la IA (Con modelo dinámico y Streaming)
if pregunta_usuario := st.chat_input("Escribe tu mensaje aquí sin límites..."):
    # Mostrar y guardar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    st.session_state.historial_mensajes.append({"rol": "user", "texto": pregunta_usuario})
    
    try:
        # Iniciamos el cliente oficial de Groq
        client = Groq()
        
        # Estructuramos el historial para que la IA recuerde el contexto
        historial_completo = [
            {
                "role": "system", 
                "content": "Eres un chatbot ultra rápido, divertido y experto en tecnología creado por un programador genial llamado Wilmer. Hablas español perfectamente y respondes de forma concisa."
            }
        ]
        
        # Mapeo limpio y seguro para la API de Groq
        for msg in st.session_state.historial_mensajes:
            rol_api = "user" if msg["rol"] == "user" else "assistant"
            historial_completo.append({"role": rol_api, "content": msg["texto"]})
            
        # Llamamos al modelo seleccionado con flujo en tiempo real (Streaming)
        with st.chat_message("assistant"):
            # Generador para procesar los fragmentos de texto
            def generar_respuesta():
                stream = client.chat.completions.create(
                    model=modelo_seleccionado,  # <--- Usa el modelo elegido en la barra lateral
                    messages=historial_completo,
                    temperature=0.7,
                    stream=True,               # <--- Activamos el streaming
                )
                for chunk in stream:
                    contenido = chunk.choices[0].delta.content
                    if contenido:
                        yield contenido

            # Streamlit renderiza las palabras en pantalla en tiempo real
            respuesta_texto = st.write_stream(generar_respuesta())
            
        # Guardamos la respuesta final en el historial
        st.session_state.historial_mensajes.append({"rol": "assistant", "texto": respuesta_texto})
        
    except Exception as e:
        st.error(f"Ocurrió un problema técnico. Detalle: {e}")
