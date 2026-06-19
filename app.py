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
    st.error("Por favor, configura tu GROQ_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 3. Inicializar variables en st.session_state
if "historial_mensajes" not in st.session_state:
    st.session_state.historial_mensajes = []
if "codigo_corregido" not in st.session_state:
    st.session_state.codigo_corregido = ""
if "manual_readme" not in st.session_state:
    st.session_state.manual_readme = ""

# --- FUNCIÓN GLOBAL DE STREAMING ---
def ejecutar_stream_groq(modelo, mensajes, temperatura):
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
                contenido = chunk.choices.delta.content
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

modelo_seleccionado = st.sidebar.selectbox(
    "Elige el cerebro de la IA:",
    options=["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
    index=0
)

rol_seleccionado = st.sidebar.selectbox(
    "Elige la personalidad de la IA:",
    options=["Asistente de Wilmer", "Programador Experto 💻", "Traductor Pro 🌐", "Profesor Divertido 🎓"],
    index=0
)

mensajes_a_recordar = st.sidebar.slider("Cantidad de mensajes a recordar:", 2, 20, 6, 2)
temperatura_seleccionada = st.sidebar.slider("Creatividad (Temperatura):", 0.0, 1.0, 0.7, 0.1)

st.sidebar.markdown("---")

# Panel de Estadísticas
st.sidebar.subheader("📊 Estadísticas de la Sesión")
total_palabras = sum(len(msg["texto"].split()) for msg in st.session_state.historial_mensajes)
st.sidebar.metric(label="Palabras procesadas:", value=f"{total_palabras}")
st.sidebar.metric(label="Mensajes enviados:", value=f"{len(st.session_state.historial_mensajes)}")

st.sidebar.markdown("---")

# Subidor de archivos
st.sidebar.subheader("📂 Analizar Documento o Código")
archivo_subido = st.sidebar.file_uploader(
    "Sube un archivo de texto o código:", type=["txt", "py", "js", "html", "css", "md", "json"]
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

# Herramientas de Automatización de Archivos
if contenido_archivo:
    col_fix, col_doc = st.sidebar.columns(2)
    
    with col_fix:
        if st.button("🛠️ Reparar Bugs"):
            st.session_state.historial_mensajes.append({"rol": "user", "texto": f"Repara los errores de mi archivo: `{archivo_subido.name}`"})
            prompt_fixer = (
                f"Eres un experto en ingeniería de software. Detecta bugs y corrígelos. Devuelve únicamente el código completo "
                f"perfectamente reparado dentro de un único bloque de código markdown sin texto adicional alrededor.\n\n"
                f"Contenido:\n```\n{contenido_archivo}\n```"
            )
            with st.chat_message("assistant"):
                respuesta_texto = ejecutar_stream_groq("llama-3.3-70b-versatile", [{"role": "user", "content": prompt_fixer}], 0.1)
            if respuesta_texto:
                if "```" in respuesta_texto:
                    partes = respuesta_texto.split("```")
                    codigo_limpio = partes if len(partes) >= 3 else partes
                    for lang in ["python\n", "javascript\n", "html\n", "css\n", "json\n"]:
                        codigo_limpio = codigo_limpio.replace(lang, "")
                    st.session_state.codigo_corregido = codigo_limpio
                else:
                    st.session_state.codigo_corregido = respuesta_texto
                st.session_state.historial_mensajes.append({"rol": "assistant", "texto": "¡Código analizado y corregido con éxito!"})

    with col_doc:
        if st.button("📝 Crear README"):
            st.session_state.historial_mensajes.append({"rol": "user", "texto": f"Genera la documentación para mi archivo: `{archivo_subido.name}`"})
            prompt_readme = (
                f"Eres un documentador técnico profesional. Analiza el siguiente código y genera un manual de usuario "
                f"profesional en formato Markdown (README.md). Debe incluir: Nombre del proyecto, Descripción clara, "
                f"Funciones explicadas y Guía de uso rápido. Entrega exclusivamente el formato del manual:\n\n"
                f"Código:\n```\n{contenido_archivo}\n```"
            )
            with st.chat_message("assistant"):
                respuesta_readme = ejecutar_stream_groq("llama-3.3-70b-versatile", [{"role": "user", "content": prompt_readme}], 0.5)
            if respuesta_readme:
                st.session_state.manual_readme = respuesta_readme
                st.session_state.historial_mensajes.append({"rol": "assistant", "texto": "¡Documentación profesional generada!"})

st.sidebar.markdown("---")

# Descargas Dinámicas
if st.session_state.codigo_corregido:
    st.sidebar.download_button(
        label="🚀 Descargar archivo REPARADO", data=st.session_state.codigo_corregido, file_name=nombre_archivo, mime="text/plain"
    )

if st.session_state.manual_readme:
    st.sidebar.download_button(
        label="📝 Descargar Manual README.md", data=st.session_state.manual_readme, file_name="README.md", mime="text/plain"
    )

# Utilidades de Historial
if st.session_state.historial_mensajes:
    chat_en_texto = "=== HISTORIAL BOT DE WILMER ===\n\n"
    for msg in st.session_state.historial_mensajes:
        rol = "Usuario" if msg["rol"] == "user" else "Asistente"
        chat_en_texto += f"[{rol}]: {msg['texto']}\n" + "-"*40 + "\n"
    st.sidebar.download_button(label="💾 Descargar chat (.txt)", data=chat_en_texto, file_name="historial_chat_wilmer.txt", mime="text/plain")

if st.sidebar.button("Toque para borrar chat"):
    st.session_state.historial_mensajes = []
    st.session_state.codigo_corregido = ""
    st.session_state.manual_readme = ""
    st.rerun()

# 4. Mostrar mensajes anteriores
for mensaje in st.session_state.historial_mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario estándar (ESTRUCTURA 100% LINEAL Y PLANA)
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
        historial_completo.append({"role": rol_api, "content": msg["texto"]})
        
    # INYECCIÓN PLANA ABSOLUTA (Línea 228 Corregida): Eliminamos el bloque 'if' para evitar caídas
