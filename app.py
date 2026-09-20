# =============================================================================
# SISTEMA DE GESTIÓN DE ESTACIONAMIENTO DE CAMIONES
# app.py — Versión 1.0
# Stack: Streamlit · Pandas · OpenPyXL
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import math

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────────────────────────────────────

TARIFA_HORA    = 2_000              # CLP por hora (o fracción)

# Columnas para cada hoja
COLS_ACTIVE = [
    "id", "patente", "chofer", "empresa",
    "entrada", "notas"
]
COLS_HISTORY = [
    "id", "patente", "chofer", "empresa",
    "entrada", "salida", "horas", "total_pago", "notas"
]

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS CSS PERSONALIZADOS
# ─────────────────────────────────────────────────────────────────────────────

def inject_css() -> None:
    """Inyecta CSS global para el diseño institucional de alto contraste."""
    st.markdown("""
    <style>
    /* ── Fuentes ── */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

    /* ── Variables de paleta ── */
    :root {
        --bg:         #0f1117;
        --surface:    #1a1d27;
        --border:     #2e3149;
        --text:       #e8eaf0;
        --muted:      #7b7f96;
        --green:      #00c896;
        --orange:     #ff7b35;
        --blue:       #4a9eff;
        --red:        #ff4c4c;
        --yellow:     #ffd166;
    }

    /* ── Base ── */
    html, body, .stApp {
        background-color: var(--bg) !important;
        font-family: 'IBM Plex Sans', sans-serif;
        color: var(--text);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border);
    }

    /* ── Métricas ── */
    [data-testid="metric-container"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }
    [data-testid="metric-container"] label {
        color: var(--muted) !important;
        font-size: 0.75rem;
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 2rem !important;
        font-weight: 700;
    }

    /* ── Botones primarios ── */
    .stButton > button {
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        border-radius: 8px;
        padding: 0.65rem 1.5rem;
        border: none;
        cursor: pointer;
        transition: opacity 0.15s ease, transform 0.1s ease;
        width: 100%;
    }
    .stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }
    .stButton > button:active { transform: translateY(0px); }

    /* ── Inputs y selects ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.2) !important;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface);
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        color: var(--muted) !important;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background: var(--border) !important;
        color: var(--text) !important;
    }

    /* ── Separadores ── */
    hr { border-color: var(--border) !important; }

    /* ── Alertas personalizadas ── */
    .alert-box {
        padding: 0.9rem 1.2rem;
        border-radius: 8px;
        font-size: 0.92rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .alert-success { background: rgba(0,200,150,0.12); border-left: 4px solid var(--green); }
    .alert-warning { background: rgba(255,123,53,0.12);  border-left: 4px solid var(--orange); }
    .alert-danger  { background: rgba(255,76,76,0.12);  border-left: 4px solid var(--red); }
    .alert-info    { background: rgba(74,158,255,0.12); border-left: 4px solid var(--blue); }

    /* ── Card de resumen ── */
    .summary-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .summary-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
        color: var(--muted);
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.05em;
        font-weight: 400;
    }
    .summary-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--green);
    }
    .summary-card .label {
        font-size: 0.82rem;
        color: var(--muted);
        margin-top: 0.15rem;
    }

    /* ── Badge de patente ── */
    .patente-badge {
        display: inline-block;
        background: var(--border);
        color: var(--text);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.3rem 0.75rem;
        border-radius: 6px;
        letter-spacing: 0.12em;
    }

    /* ── Checklist de ronda ── */
    .checklist-item {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .checklist-item .pat { font-family: 'IBM Plex Mono', monospace; font-weight: 600; }
    .checklist-item .info { color: var(--muted); font-size: 0.82rem; }

    /* ── Botón verde de entrada ── */
    .btn-entrada button { background: var(--green) !important; color: #0f1117 !important; }
    /* ── Botón naranja de salida ── */
    .btn-salida  button { background: var(--orange) !important; color: #0f1117 !important; }
    /* ── Botón rojo de alerta ── */
    .btn-danger  button { background: var(--red) !important;    color: #fff !important; }
    /* ── Botón azul neutro ── */
    .btn-azul    button { background: var(--blue) !important;   color: #0f1117 !important; }
    /* ── Botón gris secundario ── */
    .btn-cancel  button {
        background: transparent !important;
        color: var(--muted) !important;
        border: 1px solid var(--border) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CAPA DE DATOS — lectura / escritura / persistencia Excel
# ─────────────────────────────────────────────────────────────────────────────

def _empty_df(cols: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=cols)


def init_excel() -> None:
    """Crea el archivo Excel con las hojas necesarias si no existe."""
    path = Path(EXCEL_FILE)
    if not path.exists():
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            _empty_df(COLS_ACTIVE).to_excel(writer, sheet_name=SHEET_ACTIVE,  index=False)
            _empty_df(COLS_HISTORY).to_excel(writer, sheet_name=SHEET_HISTORY, index=False)


def load_df(sheet: str) -> pd.DataFrame:
    """Lee una hoja del Excel. Devuelve DataFrame vacío si hay error."""
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, engine="openpyxl")
        return df
    except FileNotFoundError:
        init_excel()
        return _empty_df(COLS_ACTIVE if sheet == SHEET_ACTIVE else COLS_HISTORY)
    except Exception as e:
        st.error(f"⚠️ No se pudo leer el archivo Excel: {e}")
        return _empty_df(COLS_ACTIVE if sheet == SHEET_ACTIVE else COLS_HISTORY)


def save_df(df: pd.DataFrame, sheet: str) -> bool:
    """
    Guarda un DataFrame en la hoja indicada, preservando la otra hoja.
    Retorna True si tuvo éxito, False si el archivo está bloqueado u ocurre un error.
    """
    try:
        # Leer la otra hoja para no borrarla al reescribir
        other_sheet = SHEET_HISTORY if sheet == SHEET_ACTIVE else SHEET_ACTIVE
        other_df    = load_df(other_sheet)

        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name=sheet, index=False)
            other_df.to_excel(writer, sheet_name=other_sheet, index=False)
        return True
    except PermissionError:
        st.error("🔒 El archivo Excel está abierto en otro programa. Ciérralo e intenta de nuevo.")
        return False
    except Exception as e:
        st.error(f"⚠️ Error al guardar: {e}")
        return False


def next_id(df: pd.DataFrame) -> int:
    """Genera el próximo ID autoincremental."""
    if df.empty or "id" not in df.columns:
        return 1
    return int(df["id"].max()) + 1


# ─────────────────────────────────────────────────────────────────────────────
# LÓGICA DE NEGOCIO
# ─────────────────────────────────────────────────────────────────────────────

def calcular_pago(entrada_str: str) -> tuple[float, float]:
    """
    Calcula horas transcurridas y total a pagar.
    Retorna (horas_float, total_clp).
    La tarifa aplica por fracción de hora iniciada.
    """
    entrada_dt = pd.to_datetime(entrada_str)
    ahora      = datetime.now()
    delta_min  = (ahora - entrada_dt).total_seconds() / 60
    horas      = delta_min / 60
    fracciones = math.ceil(horas)          # Se cobra fracción iniciada
    total      = fracciones * TARIFA_HORA
    return round(horas, 2), total


def registrar_entrada(patente: str, chofer: str, empresa: str, notas: str) -> bool:
    """Agrega un camión a la hoja de activos."""
    df = load_df(SHEET_ACTIVE)

    # Validar que la patente no esté ya dentro
    if not df.empty and patente.upper() in df["patente"].str.upper().values:
        st.error(f"⚠️ La patente **{patente.upper()}** ya tiene una entrada activa.")
        return False

    nueva_fila = {
        "id":      next_id(df),
        "patente": patente.upper().strip(),
        "chofer":  chofer.strip(),
        "empresa": empresa.strip(),
        "entrada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "notas":   notas.strip(),
    }
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    return save_df(df, SHEET_ACTIVE)


def registrar_salida(patente: str) -> tuple[bool, dict]:
    """
    Mueve un camión de activos al historial y registra el pago.
    Retorna (éxito, resumen_dict).
    """
    df_active  = load_df(SHEET_ACTIVE)
    df_history = load_df(SHEET_HISTORY)

    mask = df_active["patente"].str.upper() == patente.upper()
    if not mask.any():
        return False, {}

    fila       = df_active[mask].iloc[0].to_dict()
    horas, total = calcular_pago(fila["entrada"])
    ahora      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    registro_hist = {
        "id":         fila["id"],
        "patente":    fila["patente"],
        "chofer":     fila["chofer"],
        "empresa":    fila["empresa"],
        "entrada":    fila["entrada"],
        "salida":     ahora,
        "horas":      horas,
        "total_pago": total,
        "notas":      fila["notas"],
    }

    # Actualizar ambos DataFrames
    df_active  = df_active[~mask].reset_index(drop=True)
    df_history = pd.concat([df_history, pd.DataFrame([registro_hist])], ignore_index=True)

    # Guardar historial primero; luego activos
    ok_hist = save_df(df_history, SHEET_HISTORY)
    ok_act  = save_df(df_active,  SHEET_ACTIVE)

    return (ok_hist and ok_act), registro_hist


def recaudacion_hoy() -> int:
    """Suma los pagos registrados en el historial del día de hoy."""
    df = load_df(SHEET_HISTORY)
    if df.empty or "salida" not in df.columns:
        return 0
    hoy = datetime.now().strftime("%Y-%m-%d")
    df["salida_dt"] = pd.to_datetime(df["salida"], errors="coerce")
    return int(df[df["salida_dt"].dt.strftime("%Y-%m-%d") == hoy]["total_pago"].sum())


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENTES UI REUTILIZABLES
# ─────────────────────────────────────────────────────────────────────────────

def html_alert(tipo: str, msg: str) -> None:
    css_class = {"success": "alert-success", "warning": "alert-warning",
                 "danger": "alert-danger", "info": "alert-info"}.get(tipo, "alert-info")
    icon = {"success": "✅", "warning": "⚠️", "danger": "🚨", "info": "ℹ️"}.get(tipo, "•")
    st.markdown(f'<div class="alert-box {css_class}">{icon} {msg}</div>', unsafe_allow_html=True)


def render_metric_cards(df_active: pd.DataFrame) -> None:
    """Muestra las 3 tarjetas de métricas en la fila superior."""
    ocupados   = len(df_active)
    disponibles = CAPACIDAD_MAX - ocupados
    recaudado  = recaudacion_hoy()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🚛 Camiones Adentro",  ocupados)
    with c2:
        st.metric("🅿️ Espacios Disponibles",
                  f"{disponibles}/{CAPACIDAD_MAX}",
                  delta=None if disponibles > 5 else "⚠️ Capacidad baja")
    with c3:
        st.metric("💰 Recaudado Hoy", f"${recaudado:,.0f}")


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE — inicialización de flags
# ─────────────────────────────────────────────────────────────────────────────

def init_session_state() -> None:
    defaults = {
        "show_form_entrada":       False,
        "show_form_salida":        False,
        "salida_patente_sel":      None,
        "salida_resumen":          None,
        "show_confirm_pago":       False,
        "show_form_no_registrado": False,
        "entrada_success_msg":     None,
        "salida_success_msg":      None,
        "nr_success_msg":          None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO 1 — FORMULARIO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

def render_form_entrada() -> None:
    """Formulario modal de registro de entrada de camión."""
    st.markdown("### 🟢 Registrar Entrada de Camión")
    st.divider()

    with st.form("form_entrada", clear_on_submit=True):
        patente = st.text_input("Patente *",       placeholder="Ej: ABCD12")
        chofer  = st.text_input("Nombre Chofer *", placeholder="Ej: Juan Pérez")
        empresa = st.text_input("Empresa",         placeholder="Ej: Transportes del Sur")
        notas   = st.text_area("Notas adicionales", placeholder="Ej: Carga peligrosa, sector B", height=80)

        col_ok, col_cancel = st.columns(2)
        with col_ok:
            st.markdown('<div class="btn-entrada">', unsafe_allow_html=True)
            submitted = st.form_submit_button("✅ Confirmar Entrada", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_cancel:
            st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
            cancelled = st.form_submit_button("Cancelar", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if not patente or not chofer:
            html_alert("warning", "Patente y Nombre de Chofer son obligatorios.")
        else:
            ok = registrar_entrada(patente, chofer, empresa, notas)
            if ok:
                st.session_state.show_form_entrada   = False
                st.session_state.entrada_success_msg = (
                    f"Entrada registrada: <b>{patente.upper()}</b> — "
                    f"{datetime.now().strftime('%H:%M:%S')}"
                )
                st.rerun()

    if cancelled:
        st.session_state.show_form_entrada = False
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULO 1 — FORMULARIO DE SALIDA
# ─────────────────────────────────────────────────────────────────────────────

def render_form_salida(df_active: pd.DataFrame) -> None:
    """Formulario de selección y confirmación de salida."""
    st.markdown("### 🟠 Registrar Salida de Camión")
    st.divider()

    if df_active.empty:
        html_alert("info", "No hay camiones actualmente en el estacionamiento.")
        if st.button("← Volver"):
            st.session_state.show_form_salida = False
            st.rerun()
        return

    patentes = df_active["patente"].tolist()

    # ── Buscador / selector de patente ──
    def formato_opcion(row):
    hora = pd.to_datetime(row["entrada"]).strftime("%H:%M")
    return f"{row['patente']}  ·  {row['chofer']}  ·  Ingreso: {hora}"

opciones_display = ["— Selecciona —"] + [formato_opcion(r) for _, r in df_active.iterrows()]
opciones_patente = ["— Selecciona —"] + patentes

sel_idx = st.selectbox(
    "Buscar Patente:",
    options=range(len(opciones_display)),
    format_func=lambda i: opciones_display[i],
    key="sel_patente_salida"
)

patente_sel = None if sel_idx == 0 else opciones_patente[sel_idx]

   if patente_sel is None:
        st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
        if st.button("Cancelar", use_container_width=True):
            st.session_state.show_form_salida = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Mostrar resumen del camión ──
    fila = df_active[df_active["patente"] == patente_sel].iloc[0]
    horas, total = calcular_pago(fila["entrada"])

    st.markdown(f"""
    <div class="summary-card">
        <h3>Resumen de Estadía</h3>
        <p>
            <span class="patente-badge">{fila['patente']}</span>
            &nbsp;&nbsp;
            <span style="color:var(--muted)">Chofer: <b style="color:var(--text)">{fila['chofer']}</b>
            · Empresa: <b style="color:var(--text)">{fila['empresa'] or '—'}</b></span>
        </p>
        <p style="color:var(--muted); font-size:0.85rem; margin-top:0.5rem">
            Entrada: <b style="color:var(--text)">{fila['entrada']}</b>
        </p>
        <hr style="margin:0.75rem 0">
        <div style="display:flex; gap:2rem; align-items:center">
            <div>
                <div class="label">Tiempo transcurrido</div>
                <div style="font-size:1.4rem; font-weight:700; color:var(--blue)">{horas:.1f} hrs</div>
            </div>
            <div>
                <div class="label">Total a Pagar</div>
                <div class="value">${total:,.0f}</div>
                <div class="label">(fracción iniciada · ${TARIFA_HORA:,.0f}/hr)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_ok, col_cancel = st.columns(2)
    with col_ok:
        st.markdown('<div class="btn-salida">', unsafe_allow_html=True)
        if st.button("💳 Confirmar Pago y Salida", use_container_width=True):
            ok, resumen = registrar_salida(patente_sel)
            if ok:
                st.session_state.show_form_salida   = False
                st.session_state.salida_success_msg = (
                    f"Salida confirmada: <b>{patente_sel}</b> — "
                    f"Total cobrado: <b>${resumen['total_pago']:,.0f}</b>"
                )
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cancel:
        st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
        if st.button("Cancelar", use_container_width=True):
            st.session_state.show_form_salida = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — DASHBOARD + OPERACIONES
# ─────────────────────────────────────────────────────────────────────────────

def tab_dashboard(df_active: pd.DataFrame) -> None:
    # ── Mensajes de éxito persistentes ──
    if st.session_state.entrada_success_msg:
        html_alert("success", st.session_state.entrada_success_msg)
        st.session_state.entrada_success_msg = None

    if st.session_state.salida_success_msg:
        html_alert("success", st.session_state.salida_success_msg)
        st.session_state.salida_success_msg = None

    # ── Métricas ──
    render_metric_cards(df_active)
    st.divider()

    # ── Formularios (modo de pantalla completa dentro de la tab) ──
    if st.session_state.show_form_entrada:
        render_form_entrada()
        return

    if st.session_state.show_form_salida:
        render_form_salida(df_active)
        return

    # ── Botones principales de operación ──
    st.markdown("#### Operaciones")
    col_in, col_out = st.columns(2)

    with col_in:
        st.markdown('<div class="btn-entrada">', unsafe_allow_html=True)
        if st.button("🟢  REGISTRAR ENTRADA", use_container_width=True, key="btn_entrada_main"):
            st.session_state.show_form_entrada = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_out:
        st.markdown('<div class="btn-salida">', unsafe_allow_html=True)
        if st.button("🟠  REGISTRAR SALIDA", use_container_width=True, key="btn_salida_main"):
            st.session_state.show_form_salida = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # ── Vista rápida de activos ──
    st.markdown("#### Camiones Actualmente Adentro")
    if df_active.empty:
        html_alert("info", "El estacionamiento está vacío en este momento.")
    else:
        # Mostrar tabla simplificada con tiempo transcurrido
        df_display = df_active[["patente", "chofer", "empresa", "entrada"]].copy()
        df_display["tiempo"] = df_display["entrada"].apply(
            lambda e: f"{calcular_pago(e)[0]:.1f} hrs"
        )
        df_display.columns = ["Patente", "Chofer", "Empresa", "Entrada", "Tiempo"]
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — MONITOREO EN TIEMPO REAL
# ─────────────────────────────────────────────────────────────────────────────

def tab_monitoreo(df_active: pd.DataFrame) -> None:
    st.markdown("#### 🔍 Monitor de Camiones Activos")

    # ── Buscador por patente ──
    filtro = st.text_input(
        "Buscar por Patente:",
        placeholder="Escribe para filtrar...",
        key="filtro_monitoreo"
    )

    df_filtered = df_active.copy()
    if filtro:
        df_filtered = df_filtered[
            df_filtered["patente"].str.upper().str.contains(filtro.upper(), na=False)
        ]

    if df_filtered.empty:
        html_alert("info", "No se encontraron camiones con ese criterio." if filtro
                   else "No hay camiones en el estacionamiento.")
    else:
        # Enriquecer con columnas calculadas
        df_filtered = df_filtered.copy()
        df_filtered["horas"] = df_filtered["entrada"].apply(
            lambda e: round(calcular_pago(e)[0], 2)
        )
        df_filtered["acumulado ($)"] = df_filtered["entrada"].apply(
            lambda e: calcular_pago(e)[1]
        )
        df_filtered = df_filtered[[
            "id", "patente", "chofer", "empresa", "entrada", "horas", "acumulado ($)", "notas"
        ]]
        df_filtered.columns = [
            "ID", "Patente", "Chofer", "Empresa", "Entrada", "Horas", "Acumulado ($)", "Notas"
        ]
        st.data_editor(
            df_filtered,
            use_container_width=True,
            hide_index=True,
            disabled=True,          # Solo lectura
            num_rows="fixed",
        )

    st.divider()
    st.markdown("#### 📋 Historial de Hoy")

    df_hist = load_df(SHEET_HISTORY)
    if not df_hist.empty and "salida" in df_hist.columns:
        hoy = datetime.now().strftime("%Y-%m-%d")
        df_hist["salida_dt"] = pd.to_datetime(df_hist["salida"], errors="coerce")
        df_hoy = df_hist[df_hist["salida_dt"].dt.strftime("%Y-%m-%d") == hoy].copy()
        df_hoy = df_hoy.drop(columns=["salida_dt"], errors="ignore")
        if df_hoy.empty:
            html_alert("info", "No hay salidas registradas hoy.")
        else:
            st.dataframe(df_hoy, use_container_width=True, hide_index=True)
    else:
        html_alert("info", "No hay historial disponible.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — MODO RONDA (optimizado para móvil)
# ─────────────────────────────────────────────────────────────────────────────

def tab_ronda(df_active: pd.DataFrame) -> None:
    st.markdown("#### 📋 Lista de Verificación — Ronda de Guardia")
    html_alert("info", f"Según el sistema, hay <b>{len(df_active)} camiones</b> dentro del recinto.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Checklist de camiones esperados ──
    if df_active.empty:
        html_alert("warning", "No hay camiones registrados en el sistema.")
    else:
        for _, row in df_active.iterrows():
            horas, _ = calcular_pago(row["entrada"])
            st.markdown(f"""
            <div class="checklist-item">
                <div>
                    <span class="pat">{row['patente']}</span>
                    <div class="info">{row['chofer']} · {row['empresa'] or 'Sin empresa'}</div>
                    <div class="info">Entrada: {row['entrada']} · {horas:.1f} hrs</div>
                </div>
                <span style="font-size:1.4rem">✅</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Alerta de camión no registrado ──
    st.markdown("#### 🚨 Detección de Anomalías")

    if st.session_state.nr_success_msg:
        html_alert("success", st.session_state.nr_success_msg)
        st.session_state.nr_success_msg = None

    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
    if st.button("🚨  Detectar Camión No Registrado", use_container_width=True, key="btn_nr"):
        st.session_state.show_form_no_registrado = True
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Formulario de ingreso rápido ──
    if st.session_state.show_form_no_registrado:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### Ingreso Rápido — Camión No Registrado")
        html_alert("warning", "Este camión ingresó sin control. Se registrará con la hora actual.")

        with st.form("form_no_registrado", clear_on_submit=True):
            pat_nr    = st.text_input("Patente *", placeholder="Ej: XY1234")
            chofer_nr = st.text_input("Chofer (si se conoce)", placeholder="Desconocido")
            emp_nr    = st.text_input("Empresa (si se conoce)", placeholder="—")
            nota_nr   = st.text_area("Descripción del incidente",
                                     placeholder="Ej: Ingresó por portón lateral, sin control.",
                                     height=80)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                ok_nr = st.form_submit_button("🚨 Registrar Anomalía", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
                cancel_nr = st.form_submit_button("Cancelar", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if ok_nr:
            if not pat_nr:
                html_alert("danger", "La patente es obligatoria.")
            else:
                nota_completa = f"⚠️ ANOMALÍA · {nota_nr}"
                resultado = registrar_entrada(
                    pat_nr,
                    chofer_nr or "Desconocido",
                    emp_nr or "—",
                    nota_completa
                )
                if resultado:
                    st.session_state.show_form_no_registrado = False
                    st.session_state.nr_success_msg = (
                        f"Anomalía registrada: <b>{pat_nr.upper()}</b>. "
                        "El sistema ha sido actualizado."
                    )
                    st.rerun()

        if cancel_nr:
            st.session_state.show_form_no_registrado = False
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Información del sistema
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar(df_active: pd.DataFrame) -> None:
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 1rem 0 0.5rem'>
            <div style='font-size:2.5rem'>🚛</div>
            <div style='font-family:"IBM Plex Mono",monospace; font-size:0.85rem;
                        color:var(--muted); letter-spacing:0.08em'>PARKING CONTROL</div>
            <div style='font-size:1.1rem; font-weight:700; margin-top:0.25rem'>Sistema v1.0</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        ocupados  = len(df_active)
        pct       = (ocupados / CAPACIDAD_MAX) * 100
        color     = "#00c896" if pct < 70 else "#ffd166" if pct < 90 else "#ff4c4c"

        st.markdown(f"""
        <div style='margin-bottom:1rem'>
            <div style='color:var(--muted);font-size:0.75rem;letter-spacing:0.07em;
                        font-family:"IBM Plex Mono",monospace;text-transform:uppercase'>
                OCUPACIÓN
            </div>
            <div style='font-size:1.6rem;font-weight:700;color:{color}'>
                {pct:.0f}%
            </div>
            <div style='background:var(--border);border-radius:4px;height:8px;margin-top:0.4rem'>
                <div style='background:{color};height:8px;border-radius:4px;
                            width:{pct:.0f}%'></div>
            </div>
            <div style='color:var(--muted);font-size:0.8rem;margin-top:0.35rem'>
                {ocupados} / {CAPACIDAD_MAX} espacios
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        st.markdown(f"""
        <div style='color:var(--muted);font-size:0.78rem;line-height:1.7'>
            📁 <b>Archivo:</b> {EXCEL_FILE}<br>
            💲 <b>Tarifa:</b> ${TARIFA_HORA:,.0f}/hr (fracción)<br>
            🕐 <b>Ahora:</b> {datetime.now().strftime('%H:%M:%S')}<br>
            📅 <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        if st.button("🔄  Actualizar Datos", use_container_width=True):
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── Configuración de página ──
    st.set_page_config(
        page_title="Parking Control · Camiones",
        page_icon="🚛",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_css()
    init_session_state()
    init_excel()

    # ── Carga de datos principal (una sola vez por ciclo) ──
    df_active = load_df(SHEET_ACTIVE)

    # ── Sidebar ──
    render_sidebar(df_active)

    # ── Header ──
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
        <span style='font-family:"IBM Plex Mono",monospace;font-size:0.75rem;
                     color:var(--muted);letter-spacing:0.1em;text-transform:uppercase'>
            SISTEMA DE GESTIÓN
        </span>
        <h1 style='margin:0.1rem 0 0;font-size:1.75rem;font-weight:700'>
            Estacionamiento de Camiones
        </h1>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs principales ──
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard & Operaciones",
        "🖥️  Monitor en Tiempo Real",
        "📱 Modo Ronda (Guardia)",
    ])

    with tab1:
        tab_dashboard(df_active)

    with tab2:
        tab_monitoreo(df_active)

    with tab3:
        tab_ronda(df_active)


if __name__ == "__main__":
    main()
#   