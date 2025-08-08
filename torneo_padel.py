import streamlit as st
import json
import os
from itertools import combinations
import hashlib
from streamlit_cookies_manager import EncryptedCookieManager
import pandas as pd
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(
    page_title="Torneo de Pádel",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para título compacto y tema claro
st.markdown("""
<style>
/* --- Estilos generales para fondo y texto --- */
body, .main, .block-container {
    background-color: #f8fafc;
    color: #222222;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* --- Títulos compactos (con poco margen vertical) --- */
h1, h2, h3 {
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
}

/* --- Botones grandes y accesibles sin fondo azul --- */
div.stButton > button {
    width: 100%;
    padding: 1rem;
    font-size: 1.15rem;
    border-radius: 0.6rem;
    background-color: transparent;
    color: #111827;
    border: 2px solid transparent;
    transition: background-color 0.3s ease, border-color 0.3s ease;
    margin-bottom: 0.5rem;
    text-align: left;
    user-select: none;
}
div.stButton > button:hover {
    background-color: #e0e7ff;
    border-color: #3b82f6;
    color: #1e3a8a;
    font-weight: 700;
}

/* --- Inputs y selects grandes y claros --- */
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
    height: 3rem;
    font-size: 1.1rem;
    padding: 0.6rem 1rem;
    border-radius: 0.5rem;
    border: 1.5px solid #d1d5db;
    background-color: white;
    color: #222222;
    box-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
    transition: border-color 0.3s ease;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    border-color: #3b82f6;
    outline: none;
}

/* --- Cards para parejas --- */
.pareja-card {
    background: #ffffff;
    padding: 1rem 1.2rem;
    border-radius: 12px;
    margin: 0.6rem 0;
    border-left: 6px solid #3b82f6;
    box-shadow: 0 2px 8px rgb(59 130 246 / 0.2);
    color: #222222;
    user-select: none;
}
.pareja-card h4 {
    margin: 0;
    font-size: 1.3rem;
    font-weight: 700;
}
.pareja-card p {
    margin: 0.4rem 0 0 0;
    font-size: 1rem;
    color: #555555;
}

/* --- Cards para partidos --- */
.partido-card {
    background: #fefefe;
    padding: 1.4rem 1.6rem;
    border-radius: 14px;
    margin: 1.2rem 0;
    border: 2px solid #e0e7ff;
    box-shadow: 0 3px 9px rgb(99 102 241 / 0.15);
    color: #222222;
}
.partido-header {
    color: #3b82f6;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* --- Tabla de clasificación --- */
.clasificacion-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 0.6rem;
    background: transparent;
    font-size: 1rem;
}
.clasificacion-table th,
.clasificacion-table td {
    text-align: center;
    padding: 0.8rem 1rem;
    background: #ffffff;
    color: #222222;
    border-radius: 12px;
    box-shadow: 0 1px 4px rgb(0 0 0 / 0.08);
    user-select: none;
}
.clasificacion-table th {
    background: #3b82f6;
    color: #f9fafb;
    font-weight: 700;
}
.clasificacion-table tr td:first-child {
    font-weight: 700;
    font-size: 1.1rem;
}
.clasificacion-table tr:nth-child(even) td {
    background: #f3f4f6;
}
.clasificacion-table tr:hover td {
    background-color: #dbeafe;
}

/* --- Radio buttons grandes y modernos --- */
.stRadio > div {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.stRadio label {
    padding: 1rem 1.6rem;
    border-radius: 0.8rem;
    background-color: #e0e7ff;
    color: #1e3a8a;
    font-weight: 600;
    font-size: 1.1rem;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.3s ease, color 0.3s ease;
}
.stRadio input[type="radio"]:checked + label {
    background-color: #3b82f6;
    color: white;
}

/* --- Sidebar luminoso y compacto --- */
.sidebar .sidebar-content {
    background: #f9fafb;
    padding-top: 1rem;
}

/* Usuario y botones en sidebar */
.sidebar > div > div {
    font-weight: 600;
    font-size: 1.1rem;
    color: #111827;
    margin-bottom: 1rem;
}

/* Alertas más suaves */
.stAlert {
    border-radius: 0.6rem;
    font-size: 1.1rem;
    background-color: #bfdbfe !important;
    color: #1e40af !important;
}

/* Métricas */
.metric-container {
    background: #e0e7ff;
    padding: 1.2rem;
    border-radius: 12px;
    text-align: center;
    margin: 0.6rem 0;
    color: #1e3a8a;
    font-weight: 700;
    user-select: none;
}
</style>
""", unsafe_allow_html=True)

# Configuración de cookies cifradas
cookies = EncryptedCookieManager(
    prefix="padel_app_",
    password="tu_clave_secreta_muy_larga_y_segura_123456789"
)

if not cookies.ready():
    st.stop()

# Archivos de datos
USUARIOS_FILE = "usuarios.json"
TORNEO_FILE = "torneo_parejas.json"

# Funciones de utilidad
def load_json(filename, default_content=None):
    if default_content is None:
        default_content = {}
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            save_json(filename, default_content)
            return default_content
    except Exception as e:
        st.error(f"Error cargando {filename}: {e}")
        return default_content

def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error guardando {filename}: {e}")

# Funciones de autenticación
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def initialize_users():
    users = load_json(USUARIOS_FILE, {})
    if "admin" not in users:
        users["admin"] = hash_password("IMSusana50")  # Contraseña por defecto actualizada
        save_json(USUARIOS_FILE, users)
    return users

def login_user(username, password):
    users = load_json(USUARIOS_FILE, {})
    if username in users and verify_password(password, users[username]):
        cookies["authenticated"] = "true"
        cookies["username"] = username
        cookies.save()
        return True
    return False

def is_authenticated():
    return cookies.get("authenticated") == "true"

def get_current_user():
    return cookies.get("username")

def logout_user():
    cookies["authenticated"] = ""
    cookies["username"] = ""
    cookies.save()

# Funciones torneo (igual que antes)
def initialize_tournament():
    return load_json(TORNEO_FILE, {"parejas": [], "partidos": []})

def add_pareja(jugador1, jugador2):
    torneo = initialize_tournament()
    jugadores_existentes = []
    for pareja in torneo["parejas"]:
        jugadores_existentes.extend(pareja["jugadores"])
    if jugador1 in jugadores_existentes or jugador2 in jugadores_existentes:
        return False, "Uno de los jugadores ya está en otra pareja"
    nueva_pareja = {
        "id": len(torneo["parejas"]) + 1,
        "jugadores": [jugador1, jugador2],
        "victorias": 0,
        "derrotas": 0
    }
    torneo["parejas"].append(nueva_pareja)
    save_json(TORNEO_FILE, torneo)
    return True, "Pareja añadida correctamente"

def remove_pareja(pareja_id):
    torneo = initialize_tournament()
    torneo["parejas"] = [p for p in torneo["parejas"] if p["id"] != pareja_id]
    torneo["partidos"] = [p for p in torneo["partidos"] if p["pareja1_id"] != pareja_id and p["pareja2_id"] != pareja_id]
    save_json(TORNEO_FILE, torneo)

def generate_jornada():
    torneo = initialize_tournament()
    parejas = torneo["parejas"]
    if len(parejas) < 2:
        return False, "Se necesitan al menos 2 parejas para generar una jornada"
    enfrentamientos_hechos = set()
    for partido in torneo["partidos"]:
        pareja1_id = partido["pareja1_id"]
        pareja2_id = partido["pareja2_id"]
        enfrentamientos_hechos.add((min(pareja1_id, pareja2_id), max(pareja1_id, pareja2_id)))
    nuevos_partidos = []
    for pareja1, pareja2 in combinations(parejas, 2):
        enfrentamiento = (min(pareja1["id"], pareja2["id"]), max(pareja1["id"], pareja2["id"]))
        if enfrentamiento not in enfrentamientos_hechos:
            nuevo_partido = {
                "id": len(torneo["partidos"]) + len(nuevos_partidos) + 1,
                "pareja1_id": pareja1["id"],
                "pareja2_id": pareja2["id"],
                "ganador_id": None,
                "fecha": datetime.now().isoformat()
            }
            nuevos_partidos.append(nuevo_partido)
    if not nuevos_partidos:
        return False, "No hay nuevos enfrentamientos por generar"
    torneo["partidos"].extend(nuevos_partidos)
    save_json(TORNEO_FILE, torneo)
    return True, f"Se generaron {len(nuevos_partidos)} nuevos partidos"

def update_resultado(partido_id, ganador_id):
    torneo = initialize_tournament()
    for partido in torneo["partidos"]:
        if partido["id"] == partido_id:
            if partido["ganador_id"]:
                for pareja in torneo["parejas"]:
                    if pareja["id"] == partido["ganador_id"]:
                        pareja["victorias"] -= 1
                    elif pareja["id"] in [partido["pareja1_id"], partido["pareja2_id"]]:
                        pareja["derrotas"] -= 1
            partido["ganador_id"] = ganador_id
            for pareja in torneo["parejas"]:
                if pareja["id"] == ganador_id:
                    pareja["victorias"] += 1
                elif pareja["id"] in [partido["pareja1_id"], partido["pareja2_id"]]:
                    pareja["derrotas"] += 1
            break
    save_json(TORNEO_FILE, torneo)

def get_clasificacion():
    torneo = initialize_tournament()
    parejas = torneo["parejas"].copy()
    parejas.sort(key=lambda x: (-x["victorias"], x["derrotas"]))
    return parejas

def reset_tournament():
    save_json(TORNEO_FILE, {"parejas": [], "partidos": []})

# Interfaz principal
def main():
    initialize_users()

    with st.sidebar:
        # Título compacto en sidebar
        st.markdown("<h1 style='font-size:2rem; margin:0.2rem 0; line-height:1.2;'>🎾 Pádel</h1>", unsafe_allow_html=True)

        st.markdown("### Navegación")
        pages = {
            "📊 Dashboard": "Dashboard",
            "👥 Parejas": "Parejas",
            "🏆 Partidos": "Partidos",
            "📈 Clasificación": "Clasificación",
            "⚙️ Configuración": "Configuración"
        }
        if is_authenticated():
            st.success(f"👋 {get_current_user()}")
            for label, page_key in pages.items():
                if st.button(label, key=page_key):
                    st.session_state.page = page_key
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            st.info("🔒 No autenticado")


    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    if not is_authenticated():
        show_login()
    else:
        show_main_app(st.session_state.page)

def show_login():
    st.markdown("<h1 style='font-size:2rem; margin:0.2rem 0; line-height:1.2;'>🎾 Pádel</h1>", unsafe_allow_html=True)
    st.markdown("### 🔐 Iniciar Sesión")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese su contraseña")
            login_button = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
            if login_button:
                if username and password:
                    if login_user(username, password):
                        st.success("✅ ¡Login exitoso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                else:
                    st.error("⚠️ Por favor, complete todos los campos")
        st.markdown("---")
        st.info("🔑 **Usuario por defecto:**\n\n**Usuario:** admin\n\n**Contraseña:** IMSusana50")

def show_main_app(page):
    st.title("🎾 Pádel 50")
    if page == "Dashboard":
        show_dashboard()
    elif page == "Parejas":
        show_parejas_management()
    elif page == "Partidos":
        show_partidos_management()
    elif page == "Clasificación":
        show_clasificacion()
    elif page == "Configuración":
        show_configuration()


def show_dashboard():
    """Muestra el dashboard principal con estadísticas"""
    st.header("📊 Dashboard")

    torneo = initialize_tournament()

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-container">
            <h3>👥</h3>
            <h2>""" + str(len(torneo["parejas"])) + """</h2>
            <p>Parejas</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-container">
            <h3>🏆</h3>
            <h2>""" + str(len(torneo["partidos"])) + """</h2>
            <p>Partidos</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        partidos_jugados = len([p for p in torneo["partidos"] if p["ganador_id"]])
        st.markdown("""
        <div class="metric-container">
            <h3>✅</h3>
            <h2>""" + str(partidos_jugados) + """</h2>
            <p>Completados</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        partidos_pendientes = len([p for p in torneo["partidos"] if not p["ganador_id"]])
        st.markdown("""
        <div class="metric-container">
            <h3>⏳</h3>
            <h2>""" + str(partidos_pendientes) + """</h2>
            <p>Pendientes</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Próximos partidos
    if torneo["partidos"]:
        st.subheader("⏳ Próximos Partidos")
        partidos_pendientes = [p for p in torneo["partidos"] if not p["ganador_id"]][:3]

        if partidos_pendientes:
            for partido in partidos_pendientes:
                pareja1 = next(p for p in torneo["parejas"] if p["id"] == partido["pareja1_id"])
                pareja2 = next(p for p in torneo["parejas"] if p["id"] == partido["pareja2_id"])

                st.markdown(f"""
                <div class="partido-card">
                    <div class="partido-header">Partido #{partido["id"]}</div>
                    <p><strong>{" & ".join(pareja1["jugadores"])}</strong> vs <strong>{" & ".join(pareja2["jugadores"])}</strong></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🎉 ¡Todos los partidos han sido completados!")

    # Clasificación resumida
    if torneo["parejas"]:
        st.subheader("🏆 Top 3 Clasificación")
        clasificacion = get_clasificacion()[:3]

        for i, pareja in enumerate(clasificacion):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "🏅"
            st.markdown(f"""
            <div class="pareja-card">
                <h4>{medal} {" & ".join(pareja["jugadores"])}</h4>
                <p>Victorias: {pareja["victorias"]} | Derrotas: {pareja["derrotas"]}</p>
            </div>
            """, unsafe_allow_html=True)


def show_parejas_management():
    """Gestión de parejas"""
    st.header("👥 Parejas")

    # Formulario para añadir pareja
    st.subheader("➕ Añadir Nueva Pareja")

    with st.form("add_pareja_form"):
        col1, col2 = st.columns(2)
        with col1:
            jugador1 = st.text_input("🏃 Jugador 1", placeholder="Nombre del jugador 1")
        with col2:
            jugador2 = st.text_input("🏃 Jugador 2", placeholder="Nombre del jugador 2")

        add_button = st.form_submit_button("➕ Añadir Pareja", use_container_width=True)

        if add_button:
            if jugador1.strip() and jugador2.strip():
                if jugador1.strip() != jugador2.strip():
                    success, message = add_pareja(jugador1.strip(), jugador2.strip())
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Los jugadores deben ser diferentes")
            else:
                st.error("❌ Por favor, complete ambos nombres")

    st.markdown("---")

    # Lista de parejas existentes
    torneo = initialize_tournament()

    if torneo["parejas"]:
        st.subheader(f"📝 Parejas Registradas ({len(torneo['parejas'])})")

        for pareja in torneo["parejas"]:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"""
                <div class="pareja-card">
                    <h4>👥 {" & ".join(pareja["jugadores"])}</h4>
                    <p>Victorias: {pareja["victorias"]} | Derrotas: {pareja["derrotas"]}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button(f"🗑️", key=f"delete_{pareja['id']}", help="Eliminar pareja"):
                    remove_pareja(pareja["id"])
                    st.rerun()
    else:
        st.info("📝 No hay parejas registradas. ¡Añade la primera pareja para comenzar!")


def show_partidos_management():
    """Gestión de partidos"""
    st.header("🏆 Partidos")

    torneo = initialize_tournament()

    # Botón para generar jornada
    if len(torneo["parejas"]) >= 2:
        if st.button("🎯 Generar Nueva Jornada", use_container_width=True):
            success, message = generate_jornada()
            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.warning(f"⚠️ {message}")
    else:
        st.info("👥 Se necesitan al menos 2 parejas para generar partidos")

    st.markdown("---")

    if torneo["partidos"]:
        st.subheader(f"📋 Partidos ({len(torneo['partidos'])})")

        # Filtros
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            mostrar_completados = st.checkbox("✅ Mostrar completados", value=True)
        with filter_col2:
            mostrar_pendientes = st.checkbox("⏳ Mostrar pendientes", value=True)

        partidos_filtrados = torneo["partidos"]
        if not mostrar_completados:
            partidos_filtrados = [p for p in partidos_filtrados if not p["ganador_id"]]
        if not mostrar_pendientes:
            partidos_filtrados = [p for p in partidos_filtrados if p["ganador_id"]]

        for partido in partidos_filtrados:
            pareja1 = next(p for p in torneo["parejas"] if p["id"] == partido["pareja1_id"])
            pareja2 = next(p for p in torneo["parejas"] if p["id"] == partido["pareja2_id"])

            st.markdown(f"""
            <div class="partido-card">
                <div class="partido-header">🏆 Partido #{partido["id"]}</div>
            </div>
            """, unsafe_allow_html=True)

            # Información de las parejas
            col1, col2, col3 = st.columns([2, 1, 2])

            with col1:
                st.markdown(f"**👥 {' & '.join(pareja1['jugadores'])}**")
                st.caption(f"Victorias: {pareja1['victorias']}")

            with col2:
                st.markdown("<div style='text-align: center; font-size: 2rem;'>⚔️</div>", unsafe_allow_html=True)

            with col3:
                st.markdown(f"**👥 {' & '.join(pareja2['jugadores'])}**")
                st.caption(f"Victorias: {pareja2['victorias']}")

            # Selector de ganador
            ganador_actual = partido["ganador_id"]
            opciones = [
                (None, "Sin resultado"),
                (pareja1["id"], f"🏆 {' & '.join(pareja1['jugadores'])}"),
                (pareja2["id"], f"🏆 {' & '.join(pareja2['jugadores'])}")
            ]

            index_actual = 0
            for i, (id_pareja, _) in enumerate(opciones):
                if id_pareja == ganador_actual:
                    index_actual = i
                    break

            ganador_seleccionado = st.radio(
                "Seleccionar ganador:",
                options=[opcion[1] for opcion in opciones],
                index=index_actual,
                key=f"ganador_{partido['id']}",
                horizontal=True
            )

            # Actualizar resultado
            ganador_id_seleccionado = None
            for id_pareja, texto in opciones:
                if texto == ganador_seleccionado:
                    ganador_id_seleccionado = id_pareja
                    break

            if ganador_id_seleccionado != ganador_actual:
                if st.button(f"💾 Guardar Resultado", key=f"save_{partido['id']}", use_container_width=True):
                    update_resultado(partido["id"], ganador_id_seleccionado)
                    st.success("✅ Resultado guardado")
                    st.rerun()

            st.markdown("---")
    else:
        st.info("🏆 No hay partidos generados. Genera una jornada para comenzar.")


def show_clasificacion():
    """Muestra la clasificación actual"""
    st.header("📈 Clasificación")

    clasificacion = get_clasificacion()

    if clasificacion:
        # Crear tabla de clasificación
        data = []
        for i, pareja in enumerate(clasificacion):
            posicion = i + 1
            nombre_pareja = " & ".join(pareja["jugadores"])
            victorias = pareja["victorias"]
            derrotas = pareja["derrotas"]
            partidos_jugados = victorias + derrotas
            porcentaje_victoria = (victorias / partidos_jugados * 100) if partidos_jugados > 0 else 0

            data.append({
                "Pos": posicion,
                "Pareja": nombre_pareja,
                "PJ": partidos_jugados,
                "V": victorias,
                "D": derrotas,
                "% Victoria": f"{porcentaje_victoria:.1f}%"
            })

        df = pd.DataFrame(data)

        # Mostrar como tabla HTML personalizada
        st.markdown("### 🏆 Tabla de Clasificación")

        table_html = '<table class="clasificacion-table"><thead><tr>'
        for col in df.columns:
            table_html += f'<th>{col}</th>'
        table_html += '</tr></thead><tbody>'

        for _, row in df.iterrows():
            table_html += '<tr>'
            for col in df.columns:
                if col == "Pos" and row[col] <= 3:
                    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                    table_html += f'<td>{medals.get(row[col], "")} {row[col]}</td>'
                else:
                    table_html += f'<td>{row[col]}</td>'
            table_html += '</tr>'

        table_html += '</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)

        # Estadísticas adicionales
        st.markdown("---")
        st.subheader("📊 Estadísticas del Torneo")

        total_partidos = sum(p["victorias"] + p["derrotas"] for p in clasificacion) // 2
        total_parejas = len(clasificacion)
        partidos_posibles = total_parejas * (total_parejas - 1) // 2 if total_parejas > 1 else 0
        progreso = (total_partidos / partidos_posibles * 100) if partidos_posibles > 0 else 0

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🎯 Partidos Jugados", total_partidos, delta=None)

        with col2:
            st.metric("📊 Partidos Posibles", partidos_posibles, delta=None)

        with col3:
            st.metric("⚡ Progreso", f"{progreso:.1f}%", delta=None)

        # Barra de progreso
        st.progress(progreso / 100)

    else:
        st.info("📊 No hay datos de clasificación. Registra parejas y juega algunos partidos para ver la clasificación.")


def show_configuration():
    """Configuración del sistema (solo admin)"""
    st.header("⚙️ Configuración")

    current_user = get_current_user()

    if current_user != "admin":
        st.error("🔒 Solo el administrador puede acceder a esta sección")
        return

    st.success("🔑 Acceso de administrador confirmado")

    # Gestión de usuarios
    st.subheader("👥 Gestión de Usuarios")

    users = load_json(USUARIOS_FILE, {})

    # Crear nuevo usuario
    with st.expander("➕ Crear Nuevo Usuario"):
        with st.form("create_user_form"):
            new_username = st.text_input("👤 Nombre de usuario", placeholder="Ingrese nombre de usuario")
            new_password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese contraseña")
            create_button = st.form_submit_button("➕ Crear Usuario", use_container_width=True)

            if create_button:
                if new_username and new_password:
                    if new_username not in users:
                        users[new_username] = hash_password(new_password)
                        save_json(USUARIOS_FILE, users)
                        st.success(f"✅ Usuario '{new_username}' creado correctamente")
                        st.rerun()
                    else:
                        st.error("❌ El usuario ya existe")
                else:
                    st.error("❌ Complete todos los campos")

    # Lista de usuarios existentes
    st.write("**Usuarios Registrados:**")
    for username in users.keys():
        col1, col2 = st.columns([3, 1])
        with col1:
            if username == "admin":
                st.write(f"👑 {username} (Administrador)")
            else:
                st.write(f"👤 {username}")

        with col2:
            if username != "admin":  # No permitir eliminar admin
                if st.button(f"🗑️", key=f"delete_user_{username}", help="Eliminar usuario"):
                    del users[username]
                    save_json(USUARIOS_FILE, users)
                    st.success(f"✅ Usuario '{username}' eliminado")
                    st.rerun()

    st.markdown("---")

    # Gestión del torneo
    st.subheader("🏆 Gestión del Torneo")

    torneo = initialize_tournament()

    # Estadísticas del torneo
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Total Parejas", len(torneo["parejas"]))
    with col2:
        st.metric("🏆 Total Partidos", len(torneo["partidos"]))

    # Botón para reiniciar torneo
    st.warning("⚠️ **Zona de Peligro**")

    if st.button("🔄 Reiniciar Torneo Completo", use_container_width=True, type="secondary"):
        if "confirm_reset" not in st.session_state:
            st.session_state.confirm_reset = True
            st.rerun()

    if st.session_state.get("confirm_reset", False):
        st.error("⚠️ **¿Estás seguro? Esta acción eliminará todas las parejas y partidos.**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sí, Reiniciar", use_container_width=True):
                reset_tournament()
                st.session_state.confirm_reset = False
                st.success("✅ Torneo reiniciado correctamente")
                st.rerun()

        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()

    st.markdown("---")

    # Información del sistema
    st.subheader("ℹ️ Información del Sistema")
    st.info(f"""
    **📱 Aplicación:** Torneo de Pádel v1.0

    **👤 Usuario Actual:** {current_user}

    **📁 Archivos de Datos:**
    - Usuarios: `{USUARIOS_FILE}`
    - Torneo: `{TORNEO_FILE}`

    **🔧 Desarrollado con:** Streamlit + Python
    """)


if __name__ == "__main__":
    main()
