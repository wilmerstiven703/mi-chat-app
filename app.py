import os
import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import io

# 1. Configuración de la aplicación web
st.set_page_config(page_title="Mi Súper Chatbot IA", page_icon="🚀", layout="wide")
st.title("🚀 Mi Súper Chatbot Multimodal (Texto, Visión e Imágenes)")

# 2. Conexión segura con los secretos de Streamlit
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# 3. Inicializar el historial de mensajes en la memoria web
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []

# BARRA LATERAL: Superpoderes
st.sidebar.header("📸 Superpoder de Visión")
imagen_subida = st.sidebar.file_uploader("Sube una foto para que el bot la analice:", type=["jpg", "jpeg", "png", "webp", "bmp", "gif"])

if imagen_subida is not None:
    imagen_pil = PIL.Image.open(imagen_subida)
    st.sidebar.image(imagen_pil, caption="Imagen cargada con éxito", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("🎨 Superpoder de Dibujo")
st.sidebar.info("Para que dibuje, empieza tu mensaje con la palabra **'dibuja'**.")

if st.sidebar.button("🧹 Limpiar conversación"):
    st.session_state.historial_mensajes = []
    st.rerun()

# 4. Mostrar todos los mensajes anteriores en la pantalla
for mensaje in st.session_state.historial_mensajes:
    with st.chat_message(mensaje["rol"]):
        if mensaje.get("es_imagen"):
            st.image(mensaje["texto"], caption="Imagen generada por IA", width=400)
        else:
            st.markdown(mensaje["texto"])

# 5. Entrada del usuario y respuesta de la IA
if pregunta_usuario := st.chat_input("Escribe tu mensaje o pregunta aquí..."):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    st.session_state.historial_mensajes.append({"rol": "user", "texto": pregunta_usuario})
    
    try:
        client = genai.Client()
        texto_minuscula = pregunta_usuario.lower()
        
        # ¿EL USUARIO QUIERE QUE DIBUJE?
        if texto_minuscula.startswith("dibuja") or "crea una imagen" in texto_minuscula:
            with st.spinner("🤖 Intentando conectar con el motor de dibujo..."):
                try:
                    # Intenta llamar al motor de dibujo Imagen 3
                    resultado_dibujo = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=pregunta_usuario,
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            output_mime_type="image/jpeg",
                            aspect_ratio="1:1"
                        )
                    )
                    bytes_imagen = resultado_dibujo.generated_images.image.image_bytes
                    imagen_creada = PIL.Image.open(io.BytesIO(bytes_imagen))
                    
                    with st.chat_message("assistant"):
                        st.image(imagen_creada, caption="¡Aquí tienes tu dibujo!", width=400)
                    st.session_state.historial_mensajes.append({"rol": "assistant", "texto": imagen_creada, "es_imagen": True})
                
                except Exception as error_api:
                    # SI LA LLAVE GRATUITA NO TIENE PERMISO DE DIBUJO, LA IA RESPONDE CON TEXTO AMIGABLEMENTE
                    respuesta_alternativa = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"El usuario te pidió dibujar esto: '{pregunta_usuario}'. Explícale amigablemente que tu creador Wilmer te programó la función de dibujo, pero que la API Key actual es de la versión gratuita de Google AI Studio y no tiene los permisos premium activados para generar imágenes. Dile qué podrías escribirle en texto en su lugar.",
                        config=types.GenerateContentConfig(
                            system_instruction="Eres un chatbot amigable creado por Wilmer."
                        )
                    )
                    with st.chat_message("assistant"):
                        st.markdown(respuesta_alternativa.text)
                    st.session_state.historial_mensajes.append({"rol": "assistant", "texto": respuesta_alternativa.text})
        
        # SI ES UNA CONVERSACIÓN NORMAL O ANÁLISIS DE FOTO
        else:
            elementos_a_enviar = []
            if imagen_subida is not None:
                elementos_a_enviar.append(imagen_pil)
            elementos_a_enviar.append(pregunta_usuario)
            
            respuesta = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=elementos_a_enviar,
                config=types.GenerateContentConfig(
                    system_instruction="Eres el mejor chatbot del mundo. Hablas español, eres divertido y puedes ver imágenes detalladamente. Tu creador es un gran programador llamado Wilmer."
                )
            )
            
            with st.chat_message("assistant"):
                st.markdown(respuesta.text)
            st.session_state.historial_mensajes.append({"rol": "assistant", "texto": respuesta.text})
            
    except Exception as e:
        st.error(f"Ocurrió un problema general. Detalle: {e}")
