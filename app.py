import os
import time
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

# 3. Inicializar el historial y el contenedor de código corregido
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []
if "codigo_corregido" not in st.session_state:
    st.session_state.codigo_corregido = ""

# --- FUNCIÓN GLOBAL DE STREAMING REPARADA ---
def ejecutar_stream_groq(modelo, mensajes, temperatura):
    """Maneja la llamada oficial a Groq usando la sintaxis moderna de streaming de forma estable"""
    try:
        client = Groq()
        contenedor_texto = st.empty()
        respuesta_texto = ""
        
        stream = client.chat.completions.create(
            model=modelo,
            messages=mensajes,
            temperature=temperatura,
            stream=True,
        )
        
        tiempo_inicio = time.time()
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                contenido = chunk.choices[0].delta.content
                if contenido:
                    respuesta_texto += contenido
                    contenedor_texto.markdown(respuesta_texto)
        
        tiempo_total = time.time() - tiempo_inicio
        num_palabras = len(respuesta_texto.split())
        if tiempo_total > 0 and respuesta_texto:
            velocidad = num_palabras / tiempo_total
            st.caption(f"⏱️ Generadas `{num_palabras}` palabras en `{tiempo_total:.2f}` segundos (`{velocidad:.1f}` palabras/seg).")
            
        return respuesta_texto
    except Exception as e:
        st.error(f"Error de comunicación con Groq: {e}")
        return ""

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

# Control deslizante para ajustar la temperatura (Creatividad) de la IA
temperatura_seleccionada = st.sidebar.slider(
    "Creatividad de la IA (Temperatura):",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="0.0 = Súper lógica y precisa (código). 1.0 = Muy creativa e innovadora."
)

st.sidebar.markdown("---")

# Panel de Estadísticas en tiempo real
st.sidebar.subheader("📊 Estadísticas de la Sesión")
total_palabras = sum(len(msg["texto"].split()) for msg in st.session_state.historial_mensajes)
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
nombre_archivo = "archivo_corregido.py"
if archivo_subido is not None:
    try:
        contenido_archivo = archivo_subido.read().decode("utf-8")
        nombre_archivo = f"reparado_{archivo_subido.name}"
        st.sidebar.success(f"¡'{archivo_subido.name}' cargado!")
    except Exception:
        st.sidebar.error("Asegúrate de que sea texto plano o código.")

# Botón inteligente Auto-Bug Fixer
if contenido_archivo:
    if st.sidebar.button("🛠️ Buscar y reparar Bugs"):
        st.session_state.historial_mensajes.append({"role": "user", "text": f"Analiza y repara los errores de mi archivo: `{archivo_subido.name}`"})
        
        prompt_fixer = (
            f"Eres un experto en ciberseguridad e Ingeniero Senior. Analiza el siguiente archivo, "
            f"detecta bugs, vulnerabilidades o errores de lógica y corrígelos. Devuelve únicamente el código completo "
            f"perfectamente reparado dentro de un único bloque de código markdown y da una explicación muy breve.\n\n"
            f"Archivo: {archivo_subido.name}\n"
            f"Contenido:\n```\n{contenido_archivo}\n```"
        )
        
        with st.chat_message("assistant"):
            respuesta_texto = ejecutar_stream_groq("llama-3.3-70b-versatile", [{"role": "user", "content": prompt_fixer}], 0.1)
            
        if respuesta_texto:
            st.session_state.historial_mensajes.append({"rol": "assistant", "texto": respuesta_texto})
            
            if "```" in respuesta_texto:
                partes = respuesta_texto.split("```")
                codigo_limpio = partes[1] if len(partes) >= 3 else partes[0]
                for lang in ["python\n", "javascript\n", "html\n", "css\n", "json\n"]:
                    codigo_limpio = codigo_limpio.replace(lang, "")
                st.session_state.codigo_corregido = codigo_limpio
            else:
                st.session_state.codigo_corregido = respuesta_texto
            st.rerun()

# Botón para descargar exclusivamente el código reparado
if st.session_state.codigo_corregido:
    st.sidebar.download_button(
        label="🚀 Descargar archivo REPARADO",
        data=st.session_state.codigo_corregido,
        file_name=nombre_archivo,
        mime="text/plain",
        help="Descarga el script corregido directamente a tu máquina."
    )

st.sidebar.markdown("---")

# Botón para descargar historial de chat plano
if st.session_state.historial_mensajes:
    chat_en_texto = "=== HISTORIAL BOT DE WILMER ===\n\n"
    for msg in st.session_state.historial_mensajes:
        rol = "Usuario" if msg["rol"] == "user" else "Asistente"
        chat_en_texto += f"[{rol}]: {msg['texto']}\n" + "-"*40 + "\n"
        
    st.sidebar.download_button(
        label="💾 Descargar chat (.txt)",
        data=chat_en_texto,
        file_name="historial_chat_wilmer.txt",
        mime="text/plain"
    )

if st.sidebar.button("Toque para borrar chat"):
    st.session_state.historial_mensajes = []
    st.session_state.codigo_corregido = ""
    st.rerun()

# 4. Mostrar todos los mensajes anteriores en la pantalla
for mensaje in st.session_state.historial_mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario estándar
if pregunta_usuario := st.chat_input("Escribe tu mensaje aquí sin límites..."):
    st.session_state.historial_mensajes.append({"rol": "user", "texto": pregunta_usuario})
    
    with st.chat_message("user"):
        st.markdown(pregunta_usuario)
    
    prompt_sistema = "Eres un chatbot ultra rápido, divertido y experto en tecnología creado por un programador genial llamado Wilmer. Hablas español perfectamente y respondes de forma concisa."
    if rol_seleccionado == "Programador Experto 💻":
        prompt_sistema = "Eres un Ingeniero de Software Senior. Das respuestas técnicas impecables, optimizadas y explicas el código con ejemplos claros."
    elif rol_seleccionado == "Traductor Pro 🌐":
        prompt_sistema = "Eres un traductor experto bilingüe. Tu objetivo es traducir textos a cualquier idioma de forma clara."
    elif rol_seleccionado == "Profesor Divertido 🎓":
        prompt_sistema = "Eres un profesor carismático y alegre. Explicas conceptos difíciles usando analogías simples."

    historial_completo = [{"role": "system", "content": prompt_sistema}]
    historial_recortado = st.session_state.historial_mensajes[-mensajes_a_recordar:]
    
    for msg in historial_recortado:
        rol_api = "user" if msg["rol"] == "user" else "assistant"
        if msg == historial_recortado[-1] and msg["rol"] == "user" and contenido_archivo:
            texto_unificado = f"Archivo adjunto: {archivo_subido.name}\n```\n{contenido_archivo}\n```\nPetición: {msg['texto']}"
            historial_completo.append({"role": "user", "content": texto_unificado})
        else:
            historial_completo.append({"role": rol_api, "content": msg["texto"]})
            
    with st.chat_message("assistant"):
