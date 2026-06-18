import os
import streamlit as st
from groq import Groq

# 1. Configuración de la aplicación web
st.set_page_config(page_title="Mi Súper Chatbot Groq", page_icon="⚡", layout="wide")

# --- DISEÑO VISUAL CON ST.HTML ---
st.html("""
    <style>
    /* Fondo principal de la app */
    .stApp {
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
    }
    
    /* Estilo del título principal */
    h1 {
        color: #00ff66 !important;
        font-family: 'Courier New', Courier, monospace !important;
        text-shadow: 0 0 10px rgba(0, 255, 102, 0.5) !important;
    }
    
    /* Personalización de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 2px solid #00ff66 !important;
    }
    
    /* Textos dentro de la barra lateral */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #00ff66 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    </style>
""")

st.title("⚡ Mi Súper Chatbot de Alta Velocidad")

# 2. Conexión segura con los secretos de Streamlit
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
elif not os.environ.get("GROQ_API_KEY"):
    st.error("Por favor, configura la variable de entorno o secreto GROQ_API_KEY.")
    st.stop()

# 3. Inicializar el historial de mensajes en la memoria web
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []

# --- BARRA LATERAL CONFIGURADA ---
st.sidebar.header("🛠️ CONFIGURACIÓN")

# Selector de modelos
modelo_seleccionado = st.sidebar.selectbox(
    "Elige el cerebro de la IA:",
    options=["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
    index=0,
    help="El modelo 8b es ultra rápido; el 70b es ideal para tareas complejas."
)

# Selector de Personalidad/Rol
rol_seleccionado = st.sidebar.selectbox(
    "Elige la personalidad de la IA:",
    options=["Asistente de Wilmer", "Programador Experto 💻", "Traductor Pro 🌐", "Profesor Divertido 🎓"],
    index=0,
    help="Cambia el rol y el comportamiento de la IA."
)

# Control deslizante para limitar la memoria del chat
mensajes_a_recordar = st.sidebar.slider(
    "Cantidad de mensajes a recordar:",
    min_value=2,
    max_value=20,
    value=6,
    step=2,
    help="Cuántos mensajes del historial verá la IA. Un número menor ahorra tokens y acelera el chat."
)

st.sidebar.markdown("---")

# Panel de Estadísticas en tiempo real
st.sidebar.subheader("📊 Estadísticas de la Sesión")

# Calculamos el total de palabras acumuladas en el chat
total_palabras = 0
for msg in st.session_state.historial_mensajes:
    total_palabras += len(msg["texto"].split())

# Mostramos la métrica de forma visual e intuitiva
st.sidebar.metric(label="Palabras procesadas:", value=f"{total_palabras}")
st.sidebar.metric(label="Mensajes enviados:", value=f"{len(st.session_state.historial_mensajes)}")

st.sidebar.markdown("---")

# Subidor de archivos en la barra lateral
st.sidebar.subheader("📂 Analizar Documento o Código")
archivo_subido = st.sidebar.file_uploader(
    "Sube un archivo de texto o código:", 
    type=["txt", "py", "js", "html", "css", "md", "json"],
    help="Sube tu código o notas para que la IA los analice."
)

contenido_archivo = ""
if archivo_subido is not None:
    try:
        contenido_archivo = archivo_subido.read().decode("utf-8")
        st.sidebar.success(f"¡'{archivo_subido.name}' cargado con éxito!")
    except Exception as e:
        st.sidebar.error("No se pudo leer el archivo. Asegúrate de que sea texto plano.")

st.sidebar.markdown("---")

# Función para formatear el historial y hacerlo un texto descargable
def formatear_historial_txt():
    texto_final = "=== HISTORIAL DE CHAT - BOT DE WILMER ===\n\n"
    for msg in st.session_state.historial_mensajes:
        rol = "Usuario" if msg["rol"] == "user" else "Asistente"
        texto_final += f"[{rol}]: {msg['texto']}\n"
        texto_final += "-" * 40 + "\n"
    return texto_final

# Botón de descarga inteligente
if st.session_state.historial_mensajes:
    chat_en_texto = formatear_historial_txt()
    st.sidebar.download_button(
        label="💾 Descargar conversación (.txt)",
        data=chat_en_texto,
        file_name="historial_chat_wilmer.txt",
        mime="text/plain"
    )

if st.sidebar.button("Toque para borrar chat"):
    st.session_state.historial_mensajes = []
    st.rerun()

# 4. Mostrar todos los mensajes anteriores en la pantalla
for mensaje in st.session_state.historial_mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario y respuesta de la IA (Con Roles Dinámicos y Archivos adjuntos)
if pregunta_usuario := st.chat_input("Escribe tu mensaje aquí sin límites..."):
    
    # Si hay un archivo subido, modificamos la pregunta del usuario para incluirlo discretamente
    pregunta_final_api = pregunta_usuario
    if contenido_archivo:
        pregunta_final_api = (
            f"El usuario ha adjuntado un archivo llamado '{archivo_subido.name}' con el siguiente contenido:\n"
            f"```\n{contenido_archivo}\n```\n"
            f"Teniendo en cuenta ese archivo, responde a la siguiente petición del usuario: {pregunta_usuario}"
        )

    # Mostrar inmediatamente en pantalla el mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    
    # Guardamos en la memoria interna
    st.session_state.historial_mensajes.append({"rol": "user", "texto": pregunta_usuario})
    
    try:
        # Iniciamos el cliente oficial de Groq
        client = Groq()
        
        # Diccionario para definir el System Prompt según el rol elegido
        prompt_sistema = "Eres un chatbot ultra rápido, divertido y experto en tecnología creado por un programador genial llamado Wilmer. Hablas español perfectamente y respondes de forma concisa."
        
        if rol_seleccionado == "Programador Experto 💻":
            prompt_sistema = "Eres un Ingeniero de Software Senior. Das respuestas técnicas impecables, optimizadas y explicas el código de programación con ejemplos claros en bloques de código."
        elif rol_seleccionado == "Traductor Pro 🌐":
            prompt_sistema = "Eres un traductor experto bilingüe. Tu objetivo es traducir textos a cualquier idioma, corregir gramática y explicar modismos locales de forma clara."
        elif rol_seleccionado == "Profesor Divertido 🎓":
            prompt_sistema = "Eres un profesor carismático y alegre. Explicas conceptos difíciles (ciencia, historia, matemáticas) usando analogías simples, chistes y un tono muy motivador."

        # Mensaje del sistema inicial configurado dinámicamente
        historial_completo = [{"role": "system", "content": prompt_sistema}]
        
        # Recortamos el historial usando el valor del slider (los últimos X mensajes)
        historial_recortado = st.session_state.historial_mensajes[-mensajes_a_recordar:]
        
        # Mapeo limpio y seguro para la API de Groq
        for msg in historial_recortado[:-1]: 
            rol_api = "user" if msg["rol"] == "user" else "assistant"
            historial_completo.append({"role": rol_api, "content": msg["texto"]})
            
        # Reemplazamos el último mensaje por la versión que contiene el archivo adjunto
        historial_completo.append({"role": "user", "content": pregunta_final_api})
            
        # Llamamos al modelo seleccionado con flujo en tiempo real
        with st.chat_message("assistant"):
            def generar_respuesta():
                stream = client.chat.completions.create(
                    model=modelo_seleccionado,
                    messages=historial_completo,
                    temperature=0.7,
                    stream=True,
                )
                for chunk in stream:
                    try:
                        if chunk.choices and len(chunk.choices) > 0:
                            contenido = chunk.choices.delta.content
                            if contenido:
                                yield contenido
                    except Exception:
                        continue

            # Streamlit renderiza las palabras en pantalla en tiempo real
            respuesta_texto = st.write_stream(generar_respuesta())
            
        # Guardamos la respuesta final en el historial completo (Sin hacer rerun para evitar congelamientos)
        st.session_state.historial_mensajes.append({"rol": "assistant", "texto": respuesta_texto})
        
    except Exception as e:
        st.error(f"Ocurrió un problema técnico. Detalle: {e}")
