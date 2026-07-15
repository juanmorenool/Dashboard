import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats


# =============================================================================
# PALETA Y THEMING (tonos banca: azul marino / azul / gris)
# =============================================================================

COLOR_NAVY = "#0B2545"          # Header, títulos
COLOR_BASE = "#1B4B8F"          # Escenario Base
COLOR_ACCENT = "#2E6FBA"        # Acentos interactivos
COLOR_ADVERSO = "#C0392B"       # Escenario Adverso
COLOR_OPTIMISTA = "#2E7D5B"     # Escenario Optimista
COLOR_WARNING = "#C9862B"       # Estados marginales
COLOR_NEUTRAL = "#5F6B7A"       # Series neutras (ponderado, normal teórica)
COLOR_BG = "#F5F6F8"            # Fondo de página
COLOR_BORDER = "#E3E6EA"        # Bordes de tarjetas/tablas
COLOR_TEXT = "#1F2937"          # Texto principal
COLOR_TEXT_MUTED = "#6B7280"    # Texto secundario
COLOR_TINT = "#EAF1FB"          # Fondo tenue de acento

_BADGE_PALETTE = {
    "success": ("#EAF6EF", "#1E5C41"),
    "warning": ("#FCF3E6", "#8A5A17"),
    "danger": ("#FBEAEA", "#8A2626"),
    "neutral": ("#EEF0F2", "#4B5563"),
}


def inject_theme_css():
    """CSS global para que el dashboard tenga una identidad visual consistente."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, .stMarkdown, .stDataFrame, .stButton,
    .stSelectbox, .stTextInput, .stNumberInput, .stTabs {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    /* Oculta el chrome por defecto de Streamlit para look más "producto" */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    .block-container {{
        padding-top: 1.6rem;
        padding-bottom: 2.5rem;
    }}

    .stApp {{
        background-color: {COLOR_BG};
    }}
    section[data-testid="stSidebar"] {{
        background-color: #ffffff;
        border-right: 1px solid {COLOR_BORDER};
    }}
    h1 {{
        color: {COLOR_NAVY} !important;
        font-weight: 700 !important;
    }}
    h2 {{
        color: {COLOR_NAVY} !important;
        font-weight: 600 !important;
        font-size: 20px !important;
    }}
    h3 {{
        color: {COLOR_NAVY} !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border-left: 3px solid {COLOR_ACCENT};
        padding-left: 10px;
        margin-top: 0.4rem !important;
    }}
    p, span, div, label {{
        color: {COLOR_TEXT};
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        border-bottom: 1px solid {COLOR_BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 8px 18px;
        color: {COLOR_TEXT_MUTED};
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_TINT} !important;
        color: {COLOR_NAVY} !important;
        font-weight: 600;
    }}
    div[data-testid="stMetric"] {{
        background-color: #ffffff;
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 12px 16px;
    }}
    div[data-testid="stExpander"] {{
        background-color: #ffffff;
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {COLOR_BORDER} !important;
        border-radius: 10px !important;
    }}
    .stButton > button {{
        border-radius: 6px;
        border: 1px solid {COLOR_BORDER};
        color: {COLOR_TEXT};
        font-weight: 500;
    }}
    .stButton > button:hover {{
        border-color: {COLOR_ACCENT};
        color: {COLOR_ACCENT};
    }}
    div[data-testid="stDataFrame"] {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
    }}
    /* Sidebar sticky */
    section[data-testid="stSidebar"] {{
        position: sticky;
        top: 0;
        height: 100vh;
        overflow-y: auto;
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Banner de encabezado con identidad de marca (reemplaza st.title)."""
    st.markdown(f"""
    <div style="background-color:{COLOR_NAVY}; padding:20px 28px; border-radius:10px; margin-bottom:22px;">
        <p style="color:#ffffff; font-size:22px; font-weight:600; margin:0;">Dashboard SARIMAX &mdash; Forward Looking</p>
        <p style="color:#AFC4E3; font-size:14px; margin:6px 0 0;">Calibraci&oacute;n IFRS 9 &middot; proyecci&oacute;n de PD por escenario</p>
    </div>
    """, unsafe_allow_html=True)


def metric_card(label, value, color=None):
    """Tarjeta KPI de fondo blanco, para reemplazar texto plano/markdown."""
    color = color or COLOR_TEXT
    st.markdown(f"""
    <div style="background:#ffffff;border:1px solid {COLOR_BORDER};border-radius:8px;
                padding:12px 16px;margin-bottom:8px;">
        <p style="font-size:12px;color:{COLOR_TEXT_MUTED};margin:0 0 4px;">{label}</p>
        <p style="font-size:22px;font-weight:600;color:{color};margin:0;">{value}</p>
    </div>
    """, unsafe_allow_html=True)


def badge(text, kind="neutral"):
    """Devuelve el HTML de un badge/pill coloreado (reemplaza emojis 🟢🟡🔴)."""
    bg, fg = _BADGE_PALETTE.get(kind, _BADGE_PALETTE["neutral"])
    return (f'<span style="background:{bg};color:{fg};font-size:12px;'
            f'padding:3px 10px;border-radius:12px;font-weight:500;">{text}</span>')


def aplicar_tema_plotly(fig):
    """Aplica un tema visual consistente a cualquier figura Plotly del dashboard."""
    fig.update_layout(
        font=dict(family="Inter, Arial, sans-serif", size=13, color=COLOR_TEXT),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=45, l=10, r=10, b=10),
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLOR_BORDER, zeroline=False, linecolor=COLOR_BORDER)
    fig.update_yaxes(showgrid=True, gridcolor=COLOR_BORDER, zeroline=False, linecolor=COLOR_BORDER)
    if fig.layout.title and fig.layout.title.text:
        fig.update_layout(title=dict(font=dict(size=15, color=COLOR_NAVY)))
    return fig


def section_divider():
    """Divisor de sección con estilo propio, en vez del divider gris default."""
    st.markdown(
        f"<hr style='border:none;border-top:1px solid {COLOR_BORDER};margin:1.6rem 0;'>",
        unsafe_allow_html=True
    )


# =============================================================================
# NAV FIJO (FLECHAS) QUE SÍ FUNCIONA EN STREAMLIT COMMUNITY CLOUD
# =============================================================================
# `position: sticky` no funciona porque los contenedores padre de Streamlit
# tienen su propio `overflow`, que rompe el contexto de sticky.
# `position: fixed` a secas tampoco funciona porque no sabemos de antemano
# las coordenadas (left/width) del panel derecho: dependen del ancho del
# sidebar, que el usuario puede colapsar.
#
# La solución: usamos st.container(key=...) para tener una clase CSS estable
# (.st-key-<key>) y un pequeño script que, desde el iframe del componente,
# accede a window.parent.document (permitido: mismo origen) para MEDIR en
# tiempo real dónde está el panel de contenido y fijar el nav con esas
# coordenadas exactas. También insertamos un "spacer" para que el contenido
# no salte al volverse `fixed`.

_STICKY_NAV_KEY = "sarimax_sticky_nav"


def render_nav_fijo(modelo_actual, current_idx, total, disabled_prev, disabled_next):
    """
    Renderiza las flechas de navegación en un contenedor que queda
    verdaderamente fijo (fixed) en pantalla al hacer scroll.
    Solo los botones son visibles (sin fondo ancho).
    Devuelve (prev_clicked, next_clicked).
    """
    nav = st.container(key=_STICKY_NAV_KEY)
    with nav:
        cols_nav = st.columns([1, 1, 8, 2])
        with cols_nav[0]:
            prev_clicked = st.button(
                "← Anterior", disabled=disabled_prev, key="btn_prev",
                use_container_width=True
            )
        with cols_nav[1]:
            next_clicked = st.button(
                "Siguiente →", disabled=disabled_next, key="btn_next",
                use_container_width=True
            )
        with cols_nav[2]:
            st.markdown(f"**{modelo_actual}** ({current_idx + 1}/{total})")
        with cols_nav[3]:
            pass

    # Script que fija el contenedor con estilo mínimo (solo botones visibles)
    components.html(f"""
    <script>
    (function() {{
        const doc = window.parent.document;

        function aplicarFijado() {{
            const nav = doc.querySelector(".st-key-{_STICKY_NAV_KEY}");
            if (!nav) return false;

            const header = doc.querySelector('header[data-testid="stHeader"]');
            const headerH = header ? header.offsetHeight : 0;

            // Encontrar el wrapper del contenedor para hacerlo fixed
            // El contenedor de Streamlit tiene estructura: .st-key-xxx > div > div
            let wrapper = nav.closest('.element-container');
            if (!wrapper) wrapper = nav.parentElement;

            const yaFijado = wrapper.dataset.stickyFijado === "1";

            if (!yaFijado) {{
                // Guardar altura original para el spacer
                const altoOriginal = nav.offsetHeight;
                wrapper.dataset.altoOriginal = altoOriginal;

                // Crear spacer antes de modificar el wrapper
                let spacer = wrapper.previousElementSibling;
                if (!spacer || !spacer.classList.contains('sticky-nav-spacer')) {{
                    spacer = doc.createElement("div");
                    spacer.className = "sticky-nav-spacer";
                    spacer.style.height = altoOriginal + "px";
                    wrapper.parentNode.insertBefore(spacer, wrapper);
                }}
            }}

            // Aplicar estilo fixed al wrapper (no al nav interno)
            wrapper.style.position = "fixed";
            wrapper.style.top = headerH + "px";
            wrapper.style.left = "0";
            wrapper.style.width = "100%";
            wrapper.style.zIndex = "999999";
            wrapper.style.background = "transparent";
            wrapper.style.padding = "0";
            wrapper.style.border = "none";
            wrapper.style.boxShadow = "none";
            wrapper.style.boxSizing = "border-box";
            wrapper.style.pointerEvents = "none";  /* Dejar pasar clicks al contenido debajo */

            // El nav interno SÍ recibe clicks - estilo minimalista
            nav.style.pointerEvents = "auto";
            nav.style.background = "rgba(255, 255, 255, 0.0)";  /* TOTALMENTE transparente */
            nav.style.backdropFilter = "none";
            nav.style.padding = "4px 0";
            nav.style.borderBottom = "none";
            nav.style.maxWidth = "500px";  /* Solo el ancho de los botones */
            nav.style.margin = "0";        /* Alinear a la izquierda */
            nav.style.borderRadius = "0";

            // Ocultar el fondo del contenedor de columnas de Streamlit
            const colContainer = nav.querySelector('[data-testid="stHorizontalBlock"]');
            if (colContainer) {{
                colContainer.style.background = "transparent";
                colContainer.style.boxShadow = "none";
            }}

            wrapper.dataset.stickyFijado = "1";
            return true;
        }}

        let intentos = 0;
        const timer = setInterval(function() {{
            const ok = aplicarFijado();
            intentos++;
            if (intentos > 15) clearInterval(timer);
        }}, 150);

        window.addEventListener("resize", aplicarFijado);
    }})();
    </script>
    """, height=0)

    return prev_clicked, next_clicked

# =============================================================================
# CONFIGURACIÓN INICIAL DE SESSION STATE
# =============================================================================

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "modelos_data" not in st.session_state:
    st.session_state.modelos_data = {}
if "modelo_seleccionado" not in st.session_state:
    st.session_state.modelo_seleccionado = None
if "ordenar_por_pruebas" not in st.session_state:
    st.session_state.ordenar_por_pruebas = False
if "mostrar_significancia" not in st.session_state:
    st.session_state.mostrar_significancia = False
if "mostrar_flechas" not in st.session_state:
    st.session_state.mostrar_flechas = False
if "criterio_ordenamiento" not in st.session_state:
    st.session_state.criterio_ordenamiento = "Nombre (A-Z)"

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def convertir_fecha(serie):
    """Convierte una serie de fechas, manejando seriales de Excel o fechas reales."""
    if serie is None or len(serie) == 0:
        return serie
    if pd.api.types.is_datetime64_any_dtype(serie):
        return serie
    try:
        numeric = pd.to_numeric(serie, errors='coerce')
        if numeric.notna().sum() > 0 and numeric.dropna().min() > 30000:
            result = pd.to_datetime(numeric, unit='D', origin='1899-12-30', errors='coerce')
            if result.notna().sum() > 0:
                return result
    except:
        pass
    return pd.to_datetime(serie, errors='coerce')


def clasificar_variable(var_name):
    """Clasifica una variable en AR, MA, Exógena, o Varianza."""
    var_lower = str(var_name).lower()
    if var_lower.startswith('ar.'):
        return 'AR'
    elif var_lower.startswith('ma.'):
        return 'MA'
    elif var_lower == 'intercept':
        return 'Exógena'
    elif var_lower.startswith('var_'):
        return 'Exógena'
    elif var_lower == 'sigma2':
        return 'Varianza'
    else:
        return 'Otro'


def parsear_excel(file):
    """
    Parser robusto para el formato fijo de Excel SARIMAX.
    Cada hoja tiene secciones en columnas fijas.
    """
    xls = pd.ExcelFile(file)
    modelos = {}

    for sheet_name in xls.sheet_names:
        try:
            df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        except Exception as e:
            st.warning(f"Error leyendo hoja '{sheet_name}': {e}")
            continue

        if len(df_raw) < 2:
            continue

        headers = [str(v).strip() if pd.notna(v) else "" for v in df_raw.iloc[1].values]

        col_map = {}
        for idx, name in enumerate(headers):
            if name:
                col_map.setdefault(name, []).append(idx)

        modelo = {"nombre": sheet_name}

        # SECCIÓN 1: Fecha + Endógena + Exógenas + FWL
        fecha_idx = col_map.get('fecha', [0])[0]
        base_idx = col_map.get('BASE', [1])[0]
        adv_idx = col_map.get('ADVERSO', [2])[0]
        opt_idx = col_map.get('OPTIMISTA', [3])[0]

        exog_cols = []
        exog_names = set()
        for idx, name in enumerate(headers):
            name_upper = name.upper()
            if name_upper in ['FECHA', 'BASE', 'ADVERSO', 'OPTIMISTA']:
                continue
            if name_upper.startswith('FWL'):
                continue
            if name_upper.endswith(('_BASE', '_ADVERSO', '_OPTIMISTA')):
                exog_cols.append(name)
                base_name = name
                for suffix in ['_BASE', '_ADVERSO', '_OPTIMISTA']:
                    if base_name.upper().endswith(suffix):
                        base_name = base_name[:-len(suffix)]
                        break
                exog_names.add(base_name)

        endogena_cols = ['BASE', 'ADVERSO', 'OPTIMISTA']

        cols_seccion1 = ['fecha'] + endogena_cols + exog_cols
        if 'FWL_BASE' in col_map:
            cols_seccion1.extend(['FWL_BASE', 'FWL_ADVERSO', 'FWL_OPTIMISTA'])

        cols_seccion1 = [c for c in cols_seccion1 if c in col_map]
        idx_seccion1 = [col_map[c][0] for c in cols_seccion1]

        df_seccion1 = df_raw.iloc[2:, idx_seccion1].copy()
        df_seccion1.columns = cols_seccion1
        df_seccion1 = df_seccion1.dropna(how='all').reset_index(drop=True)

        if 'fecha' in df_seccion1.columns:
            df_seccion1['fecha'] = convertir_fecha(df_seccion1['fecha'])

        modelo['fecha_endogena'] = df_seccion1
        modelo['endogenas_cols'] = endogena_cols
        modelo['exogenas_cols'] = exog_cols
        modelo['exogenas_nombres'] = sorted(list(exog_names))
        if exog_cols:
            modelo['exogenas'] = df_seccion1[['fecha'] + exog_cols] if 'fecha' in df_seccion1.columns else df_seccion1[exog_cols]
        else:
            modelo['exogenas'] = None

        # SECCIÓN 2: FWL 12 meses
        fwl_cols = []
        for c in ['FWL_BASE', 'FWL_ADVERSO', 'FWL_OPTIMISTA']:
            if c in col_map:
                fwl_cols.append(c)
        if fwl_cols and 'fecha' in col_map:
            idx_fwl = [col_map['fecha'][0]] + [col_map[c][0] for c in fwl_cols]
            df_fwl = df_raw.iloc[2:, idx_fwl].copy()
            df_fwl.columns = ['fecha'] + fwl_cols
            df_fwl = df_fwl.dropna(how='all').reset_index(drop=True)
            df_fwl['fecha'] = convertir_fecha(df_fwl['fecha'])
            # Eliminar filas donde FWL_BASE es NaN (período sin FWL)
            df_fwl = df_fwl.dropna(subset=['FWL_BASE']).reset_index(drop=True)
            modelo['fwl_12m'] = df_fwl
        else:
            modelo['fwl_12m'] = None

        # SECCIÓN 3: Factor FWL por Año
        if 'Año' in col_map and 'Escenario' in col_map and 'Factor FWL' in col_map:
            idx_anual = [col_map['Año'][0], col_map['Escenario'][0], col_map['Factor FWL'][0]]
            df_anual = df_raw.iloc[2:, idx_anual].copy()
            df_anual.columns = ['Año', 'Escenario', 'Factor FWL']
            df_anual = df_anual.dropna(how='all').reset_index(drop=True)
            modelo['fwl_anual'] = df_anual
        else:
            modelo['fwl_anual'] = None

        # SECCIÓN 4: Residuos individuales
        if 'Obs' in col_map and 'Residuo' in col_map:
            idx_res = [col_map['Obs'][0], col_map['Residuo'][0]]
            df_res = df_raw.iloc[2:, idx_res].copy()
            df_res.columns = ['Obs', 'Residuo']
            df_res = df_res.dropna(how='all').reset_index(drop=True)
            modelo['residuos_ind'] = df_res
        else:
            modelo['residuos_ind'] = None

        # SECCIÓN 5: Resumen Distribución Residuos
        if 'Estadistico' in col_map and 'Valor' in col_map:
            idx_est = col_map['Estadistico'][0]
            idx_val = col_map['Valor'][0]
            df_resumen = df_raw.iloc[2:, [idx_est, idx_val]].copy()
            df_resumen.columns = ['Estadistico', 'Valor']
            df_resumen = df_resumen.dropna(how='all').reset_index(drop=True)
            modelo['resumen_residuos'] = df_resumen
        else:
            modelo['resumen_residuos'] = None

        # SECCIÓN 6: Coeficientes del Modelo
        if 'Variable' in col_map and 'Coeficiente' in col_map and 'P_value' in col_map:
            idx_var = col_map['Variable'][0]
            idx_coef = col_map['Coeficiente'][0]
            idx_pval = col_map['P_value'][0]
            df_coef = df_raw.iloc[2:, [idx_var, idx_coef, idx_pval]].copy()
            df_coef.columns = ['Variable', 'Coeficiente', 'P_value']
            df_coef = df_coef.dropna(how='all').reset_index(drop=True)
            modelo['coeficientes'] = df_coef
        else:
            modelo['coeficientes'] = None

        # SECCIÓN 7: Pruebas Estadísticas
        if 'Prueba' in col_map and 'Estadistico' in col_map and 'P_value' in col_map:
            idx_prueba = col_map['Prueba'][0]
            idx_est = col_map['Estadistico'][-1]
            idx_pval = col_map['P_value'][-1]
            df_pruebas = df_raw.iloc[2:, [idx_prueba, idx_est, idx_pval]].copy()
            df_pruebas.columns = ['Prueba', 'Estadistico', 'P_value']
            df_pruebas = df_pruebas.dropna(how='all').reset_index(drop=True)
            modelo['pruebas'] = df_pruebas
        else:
            modelo['pruebas'] = None

        if modelo['fecha_endogena'] is not None and not modelo['fecha_endogena'].empty:
            modelo['observaciones'] = len(modelo['fecha_endogena'].dropna(how='all'))
        else:
            modelo['observaciones'] = 0

        modelos[sheet_name] = modelo

    return modelos


def contar_pruebas_aprobadas(pruebas_df):
    if pruebas_df is None or pruebas_df.empty:
        return 0, 3
    aprobadas = 0
    for _, row in pruebas_df.iterrows():
        prueba = str(row.get('Prueba', '')).lower()
        p_val = row.get('P_value', None)
        if pd.isna(p_val):
            continue
        try:
            p_val = float(p_val)
        except:
            continue
        if 'ljung' in prueba or 'box' in prueba:
            if p_val > 0.05:
                aprobadas += 1
        elif 'jarque' in prueba or 'bera' in prueba:
            if p_val > 0.05:
                aprobadas += 1
        elif 'hetero' in prueba or 'arch' in prueba:
            if p_val > 0.05:
                aprobadas += 1
    return aprobadas, 3


def obtener_significancia_exogenas(coeficientes_df, exogenas_lista):
    if coeficientes_df is None or coeficientes_df.empty:
        return []
    resultados = []
    for exog in exogenas_lista:
        p_val = None
        for _, row in coeficientes_df.iterrows():
            var = str(row.get('Variable', ''))
            if exog in var:
                p_val = row.get('P_value', None)
                break
        if p_val is not None:
            try:
                p_val = float(p_val)
            except:
                p_val = None
        if p_val is None:
            resultados.append((exog, None, "Desconocido"))
        elif p_val < 0.05:
            resultados.append((exog, p_val, "Significativa (p < 0.05)"))
        elif p_val < 0.10:
            resultados.append((exog, p_val, "Marginal (0.05 ≤ p < 0.10)"))
        else:
            resultados.append((exog, p_val, "No significativa (p ≥ 0.10)"))
    return resultados


def calcular_fwl_ponderado(fwl_df, pesos):
    if fwl_df is None or fwl_df.empty:
        return None
    fecha_col = None
    for c in fwl_df.columns:
        if 'fecha' in str(c).lower():
            fecha_col = c
            break
    base_col = [c for c in fwl_df.columns if 'FWL_BASE' in str(c).upper()]
    adv_col = [c for c in fwl_df.columns if 'FWL_ADVERSO' in str(c).upper() or 'FWL_ADVERSA' in str(c).upper()]
    opt_col = [c for c in fwl_df.columns if 'FWL_OPTIMISTA' in str(c).upper()]
    if not base_col or not adv_col or not opt_col:
        return None
    base_col = base_col[0]
    adv_col = adv_col[0]
    opt_col = opt_col[0]
    df = fwl_df.copy()
    df['FWL_Ponderado'] = (
        df[base_col].astype(float) * pesos['base'] +
        df[adv_col].astype(float) * pesos['adverso'] +
        df[opt_col].astype(float) * pesos['optimista']
    )
    return df


def generar_campana_normal(residuos, media, std):
    if std == 0 or len(residuos) == 0:
        return [], []
    x = np.linspace(min(residuos), max(residuos), 100)
    y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - media) / std) ** 2)
    return x, y


# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================

st.set_page_config(page_title="Dashboard SARIMAX", layout="wide")
inject_theme_css()
render_header()

col_left, col_right = st.columns([1, 3])

# =========================================================================
# SIDEBAR IZQUIERDO
# =========================================================================
with col_left:
    st.subheader("Cargar modelos")

    uploaded = st.file_uploader(
        "Sube un único archivo Excel. Cada hoja del archivo se interpreta como un modelo distinto.",
        type=["xlsx"]
    )

    if uploaded is not None:
        st.session_state.uploaded_file = uploaded
        if not st.session_state.modelos_data or uploaded.name != getattr(st.session_state, 'last_file_name', None):
            with st.spinner("Parseando modelos..."):
                st.session_state.modelos_data = parsear_excel(uploaded)
                st.session_state.last_file_name = uploaded.name
            st.success(f"Archivo cargado: {uploaded.name} ({uploaded.size / 1024:.1f} KB)")

            if st.session_state.modelo_seleccionado is None or st.session_state.modelo_seleccionado not in st.session_state.modelos_data:
                st.session_state.modelo_seleccionado = list(st.session_state.modelos_data.keys())[0]

    # Botón eliminar SIEMPRE visible cuando hay datos cargados
    if st.session_state.uploaded_file is not None:
        if st.button("Eliminar archivo", key="btn_eliminar"):
            st.session_state.uploaded_file = None
            st.session_state.modelos_data = {}
            st.session_state.modelo_seleccionado = None
            st.session_state.last_file_name = None
            st.rerun()

    if st.session_state.modelos_data:
        section_divider()

        # --- ORDENAMIENTO SIEMPRE ACTIVO (default: por pruebas aprobadas ↓) ---
        criterio = st.radio(
            "Ordenar modelos por:",
            ["Nombre (A-Z)", "Pruebas aprobadas ↓", "Pruebas aprobadas ↑"],
            index=1,  # Default: Pruebas aprobadas ↓
            key="criterio_orden"
        )
        st.session_state.criterio_ordenamiento = criterio
        st.session_state.ordenar_por_pruebas = True  # Siempre activo

        # Preparar lista ordenada
        modelos_con_pruebas = []
        for nombre, datos in st.session_state.modelos_data.items():
            apr, tot = contar_pruebas_aprobadas(datos.get('pruebas'))
            modelos_con_pruebas.append((nombre, apr, tot))

        if criterio == "Nombre (A-Z)":
            modelos_con_pruebas.sort(key=lambda x: x[0])
        elif criterio == "Pruebas aprobadas ↓":
            modelos_con_pruebas.sort(key=lambda x: (-x[1], x[0]))
        else:
            modelos_con_pruebas.sort(key=lambda x: (x[1], x[0]))

        modelos_list = [m[0] for m in modelos_con_pruebas]
        pruebas_dict = {m[0]: (m[1], m[2]) for m in modelos_con_pruebas}

        # Dropdown con info de pruebas
        opciones = []
        for m in modelos_list:
            apr, tot = pruebas_dict.get(m, (0, 3))
            opciones.append(f"{m}  ({apr}/{tot} ✅)")

        idx = 0
        if st.session_state.modelo_seleccionado in modelos_list:
            idx = modelos_list.index(st.session_state.modelo_seleccionado)

        seleccion = st.selectbox("Seleccionar modelo", opciones, index=idx)
        modelo_nombre = seleccion.split("  (")[0]
        st.session_state.modelo_seleccionado = modelo_nombre

        section_divider()

        # --- INFO DEL MODELO SELECCIONADO ---
        datos = st.session_state.modelos_data.get(modelo_nombre, {})

        st.markdown(f"<p style='font-size:12px;color:{COLOR_TEXT_MUTED};margin:0 0 4px;'>Modelo actual</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:16px;font-weight:600;color:{COLOR_NAVY};margin:0;'>{modelo_nombre}</p>", unsafe_allow_html=True)

        metric_card("Observaciones", datos.get('observaciones', 'N/A'))

        # --- EXÓGENAS CON SIGNIFICANCIA (SIEMPRE VISIBLE) ---
        exogenas = datos.get('exogenas_nombres', [])
        if exogenas:
            section_divider()
            st.markdown(f"<p style='font-size:13px;font-weight:600;color:{COLOR_NAVY};margin:0 0 10px;'>📊 Exógenas y significancia</p>", unsafe_allow_html=True)

            coefs = datos.get('coeficientes')
            sigs = obtener_significancia_exogenas(coefs, exogenas)
            sig_count = sum(1 for _, _, status in sigs if "Significativa" in status)

            st.markdown(
                f"<p style='font-size:12px;color:{COLOR_TEXT_MUTED};margin:0 0 12px;'>"
                f"{sig_count} de {len(exogenas)} significativas (p < 0.05)</p>",
                unsafe_allow_html=True
            )

            for ex, pval, status in sigs:
                if "No significativa" in status:
                    color_dot = COLOR_ADVERSO
                    label = "No sig."
                elif "Marginal" in status:
                    color_dot = COLOR_WARNING
                    label = "Marginal"
                elif "Significativa" in status:
                    color_dot = COLOR_OPTIMISTA
                    label = "Sig."
                else:
                    color_dot = COLOR_TEXT_MUTED
                    label = "N/A"

                p_texto = f"p = {pval:.4f}" if pval is not None else "p = N/A"

                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                            padding:6px 0;border-bottom:1px solid {COLOR_BORDER};">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="display:inline-block;width:8px;height:8px;
                                     border-radius:50%;background:{color_dot};"></span>
                        <span style="font-size:13px;color:{COLOR_TEXT};">{ex}</span>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:11px;color:{COLOR_TEXT_MUTED};">{p_texto}</span>
                        <span style="font-size:11px;color:{color_dot};font-weight:500;margin-left:6px;">{label}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        section_divider()

        # --- SWITCH FLECHAS STICKY ---
        st.session_state.flechas_sticky = st.toggle(
            "Anclar flechas al scroll",
            value=st.session_state.get("flechas_sticky", False),
            help="Las flechas de navegación se quedan fijas al desplazarte por el contenido."
        )

# =========================================================================
# PANEL DERECHO
# =========================================================================
with col_right:
    if not st.session_state.modelos_data:
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid {COLOR_BORDER};border-radius:10px;
                    padding:40px 32px;text-align:center;">
            <p style="font-size:18px;font-weight:600;color:{COLOR_NAVY};margin:0 0 8px;">Bienvenido</p>
            <p style="font-size:14px;color:{COLOR_TEXT_MUTED};margin:0;">
                Sube un archivo Excel en el panel izquierdo para comenzar. Cada hoja se interpretará
                como un modelo SARIMAX distinto.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.modelo_seleccionado and st.session_state.modelo_seleccionado in st.session_state.modelos_data:
        datos = st.session_state.modelos_data[st.session_state.modelo_seleccionado]

        # Flechas de navegación SIEMPRE visibles
        modelos_list = list(st.session_state.modelos_data.keys())
        if st.session_state.ordenar_por_pruebas:
            modelos_con_pruebas = []
            for nombre, d in st.session_state.modelos_data.items():
                apr, tot = contar_pruebas_aprobadas(d.get('pruebas'))
                modelos_con_pruebas.append((nombre, apr, tot))
            criterio = st.session_state.criterio_ordenamiento
            if criterio == "Nombre (A-Z)":
                modelos_con_pruebas.sort(key=lambda x: x[0])
            elif criterio == "Pruebas aprobadas ↓":
                modelos_con_pruebas.sort(key=lambda x: (-x[1], x[0]))
            else:
                modelos_con_pruebas.sort(key=lambda x: (x[1], x[0]))
            modelos_list = [m[0] for m in modelos_con_pruebas]

        current_idx = modelos_list.index(st.session_state.modelo_seleccionado)
        disabled_prev = current_idx == 0
        disabled_next = current_idx == len(modelos_list) - 1

        # Si sticky está activado, usar render_nav_fijo (con JS)
        # Si no, renderizar flechas normales
        if st.session_state.get("flechas_sticky", False):
            prev_clicked, next_clicked = render_nav_fijo(
                st.session_state.modelo_seleccionado,
                current_idx,
                len(modelos_list),
                disabled_prev,
                disabled_next,
            )
        else:
            cols_nav = st.columns([1, 1, 8, 2])
            with cols_nav[0]:
                prev_clicked = st.button(
                    "← Anterior", disabled=disabled_prev, key="btn_prev",
                    use_container_width=True
                )
            with cols_nav[1]:
                next_clicked = st.button(
                    "Siguiente →", disabled=disabled_next, key="btn_next",
                    use_container_width=True
                )
            with cols_nav[2]:
                st.markdown(f"**{st.session_state.modelo_seleccionado}** ({current_idx + 1}/{len(modelos_list)})")
            with cols_nav[3]:
                pass

        if prev_clicked:
            st.session_state.modelo_seleccionado = modelos_list[current_idx - 1]
            st.rerun()
        if next_clicked:
            st.session_state.modelo_seleccionado = modelos_list[current_idx + 1]
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["Visualización", "Predicciones", "Diagnósticos"])

        # =====================================================================
        # TAB 1: VISUALIZACIÓN
        # =====================================================================
        with tab1:
            st.header(f"Gráficas - {st.session_state.modelo_seleccionado}")

            st.subheader("Seleccionar exógenas a mostrar")
            exogenas = datos.get('exogenas_nombres', [])
            exog_seleccionadas = []
            if exogenas:
                cols_exog = st.columns(min(len(exogenas), 4))
                for i, ex in enumerate(exogenas):
                    with cols_exog[i % len(cols_exog)]:
                        if st.checkbox(ex, key=f"exog_{ex}_{st.session_state.modelo_seleccionado}"):
                            exog_seleccionadas.append(ex)

            # Gráfico de Predicciones
            df_end = datos.get('fecha_endogena')
            endogena_cols = datos.get('endogenas_cols', [])

            if df_end is not None and not df_end.empty and endogena_cols:
                fig = go.Figure()
                fecha_col = 'fecha' if 'fecha' in df_end.columns else df_end.columns[0]

                for col in endogena_cols:
                    if col not in df_end.columns:
                        continue
                    col_str = str(col).upper()
                    if col_str == 'BASE':
                        fig.add_trace(go.Scatter(
                            x=df_end[fecha_col], y=df_end[col],
                            mode='lines', name='Endógena - Base',
                            line=dict(color=COLOR_BASE, width=2)
                        ))
                    elif col_str in ['ADVERSO', 'ADVERSA']:
                        fig.add_trace(go.Scatter(
                            x=df_end[fecha_col], y=df_end[col],
                            mode='lines', name='Endógena - Adversa',
                            line=dict(color=COLOR_ADVERSO, width=2, dash='dash')
                        ))
                    elif col_str == 'OPTIMISTA':
                        fig.add_trace(go.Scatter(
                            x=df_end[fecha_col], y=df_end[col],
                            mode='lines', name='Endógena - Optimista',
                            line=dict(color=COLOR_OPTIMISTA, width=2, dash='dot')
                        ))

                df_exog = datos.get('exogenas')
                if df_exog is not None and exog_seleccionadas:
                    for ex in exog_seleccionadas:
                        for suffix in ['_BASE', '_ADVERSO', '_OPTIMISTA']:
                            col_name = ex + suffix
                            if col_name in df_exog.columns:
                                x_vals = df_exog[fecha_col] if fecha_col in df_exog.columns else df_exog.index
                                fig.add_trace(go.Scatter(
                                    x=x_vals, y=df_exog[col_name],
                                    mode='lines', name=f'{ex}{suffix}',
                                    line=dict(width=1.5),
                                    yaxis='y2'
                                ))

                    fig.update_layout(
                        yaxis2=dict(title='Exógenas', overlaying='y', side='right')
                    )

                fig.update_layout(
                    title=f"Predicciones - {st.session_state.modelo_seleccionado}",
                    xaxis_title="Fecha",
                    yaxis_title="Valor",
                    legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.05),
                    hovermode='x unified'
                )
                aplicar_tema_plotly(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de predicciones para este modelo.")

            section_divider()

            # Factor FWL por Año y Escenario
            st.subheader("Factor FWL por año y escenario")
            df_fwl_anual = datos.get('fwl_anual')
            if df_fwl_anual is not None and not df_fwl_anual.empty:
                if 'Escenario' in df_fwl_anual.columns and 'Factor FWL' in df_fwl_anual.columns:
                    try:
                        df_pivot = df_fwl_anual.pivot(index='Año', columns='Escenario', values='Factor FWL')
                        df_pivot = df_pivot.reset_index()
                        rename_map = {}
                        for c in df_pivot.columns:
                            c_str = str(c).lower()
                            if 'base' in c_str:
                                rename_map[c] = 'Base'
                            elif 'adverso' in c_str or 'advers' in c_str:
                                rename_map[c] = 'Adverso'
                            elif 'optimista' in c_str:
                                rename_map[c] = 'Optimista'
                        df_pivot = df_pivot.rename(columns=rename_map)
                        st.dataframe(df_pivot, width="stretch")
                    except:
                        st.dataframe(df_fwl_anual, width="stretch")
                else:
                    st.dataframe(df_fwl_anual, width="stretch")
            else:
                st.info("No hay datos de Factor FWL por Año para este modelo.")

            section_divider()

            # Factor FWL a 12 Meses
            st.subheader("Factor FWL a 12 meses")
            df_fwl = datos.get('fwl_12m')
            if df_fwl is not None and not df_fwl.empty:
                fig_fwl = go.Figure()
                fecha_col = None
                for c in df_fwl.columns:
                    if 'fecha' in str(c).lower():
                        fecha_col = c
                        break
                if fecha_col is None:
                    fecha_col = df_fwl.columns[0]

                for col in df_fwl.columns:
                    col_str = str(col).upper()
                    if 'FWL_BASE' in col_str:
                        fig_fwl.add_trace(go.Scatter(
                            x=df_fwl[fecha_col], y=df_fwl[col],
                            mode='lines', name='FWL Base',
                            line=dict(color=COLOR_BASE, width=2)
                        ))
                    elif 'FWL_ADVERSO' in col_str or 'FWL_ADVERSA' in col_str:
                        fig_fwl.add_trace(go.Scatter(
                            x=df_fwl[fecha_col], y=df_fwl[col],
                            mode='lines', name='FWL Adverso',
                            line=dict(color=COLOR_ADVERSO, width=2, dash='dash')
                        ))
                    elif 'FWL_OPTIMISTA' in col_str:
                        fig_fwl.add_trace(go.Scatter(
                            x=df_fwl[fecha_col], y=df_fwl[col],
                            mode='lines', name='FWL Optimista',
                            line=dict(color=COLOR_OPTIMISTA, width=2, dash='dot')
                        ))

                fig_fwl.update_layout(
                    title="Factor FWL a 12 Meses",
                    xaxis_title="Fecha",
                    yaxis_title="FWL",
                    legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.05),
                    hovermode='x unified'
                )
                aplicar_tema_plotly(fig_fwl)
                st.plotly_chart(fig_fwl, use_container_width=True)
            else:
                st.info("No hay datos de FWL a 12 meses para este modelo.")

            section_divider()

            # Factor FWL Ponderado (Dinámico)
            st.subheader("Factor FWL ponderado (dinámico)")
            st.markdown(
                f"<span style='color:{COLOR_TEXT_MUTED};font-size:13px;'>"
                f"Ajusta los pesos para ver cómo cambia la gráfica en tiempo real. "
                f"La suma de pesos no puede exceder 1.0.</span>",
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                peso_base = st.number_input("Peso - Escenario Base", min_value=0.0, max_value=1.0, value=0.33, step=0.01, key="peso_base")
            with c2:
                peso_adverso = st.number_input("Peso - Escenario Adverso", min_value=0.0, max_value=1.0, value=0.33, step=0.01, key="peso_adverso")
            with c3:
                peso_optimista = st.number_input("Peso - Escenario Optimista", min_value=0.0, max_value=1.0, value=0.34, step=0.01, key="peso_optimista")

            suma_pesos = peso_base + peso_adverso + peso_optimista

            if abs(suma_pesos - 1.0) < 0.001:
                st.markdown(badge("Válido", "success"), unsafe_allow_html=True)
            elif suma_pesos < 1.0:
                disponible = 1.0 - suma_pesos
                st.markdown(badge(f"{disponible:.2f} disponible", "warning"), unsafe_allow_html=True)
            else:
                excede = suma_pesos - 1.0
                st.markdown(badge(f"Excede en {excede:.2f}", "danger"), unsafe_allow_html=True)

            leyenda_pesos = f"""
            <div style="display:flex; gap:20px; margin-top:10px; font-size:14px;">
                <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{COLOR_BASE};margin-right:6px;"></span><b>Base:</b> {peso_base:.2f} ({peso_base*100:.0f}%)</span>
                <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{COLOR_ADVERSO};margin-right:6px;"></span><b>Adverso:</b> {peso_adverso:.2f} ({peso_adverso*100:.0f}%)</span>
                <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{COLOR_OPTIMISTA};margin-right:6px;"></span><b>Optimista:</b> {peso_optimista:.2f} ({peso_optimista*100:.0f}%)</span>
            </div>
            """
            st.markdown(leyenda_pesos, unsafe_allow_html=True)

            if df_fwl is not None and not df_fwl.empty and suma_pesos <= 1.0:
                pesos = {'base': peso_base, 'adverso': peso_adverso, 'optimista': peso_optimista}
                df_pond = calcular_fwl_ponderado(df_fwl, pesos)
                if df_pond is not None:
                    fecha_col = None
                    for c in df_pond.columns:
                        if 'fecha' in str(c).lower():
                            fecha_col = c
                            break
                    if fecha_col is None:
                        fecha_col = df_pond.columns[0]

                    fig_pond = go.Figure()
                    fig_pond.add_trace(go.Scatter(
                        x=df_pond[fecha_col],
                        y=df_pond['FWL_Ponderado'],
                        mode='lines',
                        name='FWL Ponderado',
                        fill='tozeroy',
                        line=dict(color=COLOR_ACCENT, width=2),
                        fillcolor='rgba(46, 111, 186, 0.15)'
                    ))
                    fig_pond.update_layout(
                        title="Factor FWL Ponderado (Dinámico)",
                        xaxis_title="Fecha",
                        yaxis_title="FWL Ponderado"
                    )
                    aplicar_tema_plotly(fig_pond)
                    st.plotly_chart(fig_pond, use_container_width=True)
                else:
                    st.info("No se pudo calcular el FWL ponderado.")
            elif suma_pesos > 1.0:
                st.warning("Ajusta los pesos para que la suma no exceda 1.0")

        # =====================================================================
        # TAB 2: PREDICCIONES
        # =====================================================================
        with tab2:
            st.header(f"Predicciones - {st.session_state.modelo_seleccionado}")

            df_end = datos.get('fecha_endogena')
            endogena_cols = datos.get('endogenas_cols', [])

            if df_end is not None and not df_end.empty and endogena_cols:
                fecha_col = 'fecha' if 'fecha' in df_end.columns else df_end.columns[0]

                base_col = None
                adv_col = None
                opt_col = None

                for col in endogena_cols:
                    col_str = str(col).upper()
                    if col_str == 'BASE':
                        base_col = col
                    elif col_str in ['ADVERSO', 'ADVERSA']:
                        adv_col = col
                    elif col_str == 'OPTIMISTA':
                        opt_col = col

                df_pred = pd.DataFrame()
                df_pred['Fecha'] = pd.to_datetime(df_end[fecha_col]).dt.strftime('%Y-%m-%d 00:00:00')
                if base_col and base_col in df_end.columns:
                    df_pred['Base'] = df_end[base_col].astype(float).round(4)
                if adv_col and adv_col in df_end.columns:
                    df_pred['Adverso'] = df_end[adv_col].astype(float).round(4)
                if opt_col and opt_col in df_end.columns:
                    df_pred['Optimista'] = df_end[opt_col].astype(float).round(4)

                st.dataframe(df_pred, width="stretch", height=400)

                csv = df_pred.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"predicciones_{st.session_state.modelo_seleccionado}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No hay datos de predicciones para este modelo.")

        # =====================================================================
        # TAB 3: DIAGNÓSTICOS
        # =====================================================================
        with tab3:
            st.header("Diagnósticos")

            # Indicadores del Modelo
            pruebas = datos.get('pruebas')
            if pruebas is not None and not pruebas.empty:
                lb_p = None
                jb_p = None
                het_p = None

                for _, row in pruebas.iterrows():
                    prueba = str(row.get('Prueba', '')).lower()
                    p_val = row.get('P_value', None)
                    if pd.isna(p_val):
                        continue
                    try:
                        p_val = float(p_val)
                    except:
                        continue

                    if 'ljung' in prueba or 'box' in prueba:
                        lb_p = p_val
                    elif 'jarque' in prueba or 'bera' in prueba:
                        jb_p = p_val
                    elif 'hetero' in prueba or 'arch' in prueba:
                        het_p = p_val

                col_m1, col_m2, col_m3 = st.columns(3)

                with col_m1:
                    val = f"{lb_p:.4f}" if lb_p is not None else "N/A"
                    color = COLOR_OPTIMISTA if lb_p is not None and lb_p > 0.05 else COLOR_ADVERSO
                    metric_card("Ljung-Box P-valor", val, color)

                with col_m2:
                    val = f"{jb_p:.4f}" if jb_p is not None else "N/A"
                    color = COLOR_ADVERSO if jb_p is not None and jb_p < 0.05 else COLOR_OPTIMISTA
                    metric_card("Jarque-Bera P-valor", val, color)

                with col_m3:
                    val = f"{het_p:.4f}" if het_p is not None else "N/A"
                    color = COLOR_OPTIMISTA if het_p is not None and het_p > 0.05 else COLOR_ADVERSO
                    metric_card("Heterocedasticidad P-valor", val, color)
            else:
                st.info("No hay datos de pruebas estadísticas.")

            section_divider()

            # Distribución de Residuos
            st.subheader("Distribución de residuos")
            residuos = datos.get('residuos_ind')
            if residuos is not None and not residuos.empty:
                n_obs = len(residuos.dropna())
                st.markdown(f"Distribución de Residuos (n={n_obs})")

                res_col = None
                for c in residuos.columns:
                    if 'residuo' in str(c).lower():
                        res_col = c
                        break

                if res_col:
                    vals = residuos[res_col].dropna().astype(float)
                    media = vals.mean()
                    std = vals.std()

                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=vals, nbinsx=20,
                        marker_color=COLOR_BASE, opacity=0.75,
                        name='Residuos'
                    ))

                    x_norm, y_norm = generar_campana_normal(vals, media, std)
                    if len(x_norm) > 0:
                        bin_width = (vals.max() - vals.min()) / 20 if vals.max() != vals.min() else 1
                        y_norm_scaled = y_norm * len(vals) * bin_width
                        fig_hist.add_trace(go.Scatter(
                            x=x_norm, y=y_norm_scaled,
                            mode='lines', name='Normal teórica',
                            line=dict(color=COLOR_ADVERSO, width=2)
                        ))

                    fig_hist.update_layout(
                        xaxis_title="Residuos",
                        yaxis_title="Frecuencia"
                    )
                    aplicar_tema_plotly(fig_hist)
                    st.plotly_chart(fig_hist, use_container_width=True)

                    skew = stats.skew(vals)
                    kurt = stats.kurtosis(vals)

                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Media", f"{media:.4f}")
                    c2.metric("Desv. Std.", f"{std:.4f}")
                    c3.metric("Asimetría", f"{skew:.4f}")
                    c4.metric("Curtosis", f"{kurt:.4f}")
                    c5.metric("N Observaciones", f"{n_obs}")
            else:
                st.info("No hay datos de residuos para este modelo.")

            section_divider()

            # Coeficientes del Modelo
            st.subheader("Coeficientes del modelo")
            coefs = datos.get('coeficientes')
            if coefs is not None and not coefs.empty:
                df_coef = coefs.copy()

                # Clasificar variables
                df_coef['Tipo'] = df_coef['Variable'].apply(clasificar_variable)

                # Formatear P-valor
                if 'P_value' in df_coef.columns:
                    def fmt_pval(x):
                        if pd.isna(x):
                            return "N/A"
                        try:
                            xv = float(x)
                            if xv < 0.001:
                                return f"{xv:.4e}"
                            else:
                                return f"{xv:.4f}"
                        except:
                            return str(x)
                    df_coef['P-valor'] = df_coef['P_value'].apply(fmt_pval)

                # Renombrar Variable a Lag (como en el original)
                df_coef = df_coef.rename(columns={'Variable': 'Lag'})

                # Reordenar columnas: Tipo, Lag, Coeficiente, P-valor
                cols_display = ['Tipo', 'Lag', 'Coeficiente', 'P-valor']
                df_mostrar = df_coef[cols_display]

                def _color_pval(val):
                    try:
                        v = float(val)
                    except (TypeError, ValueError):
                        return ""
                    if v < 0.05:
                        return f"color: {COLOR_OPTIMISTA}; font-weight: 600;"
                    return f"color: {COLOR_ADVERSO};"

                _styler = df_mostrar.style
                if hasattr(_styler, "map"):
                    _styler = _styler.map(_color_pval, subset=['P-valor'])
                else:
                    _styler = _styler.applymap(_color_pval, subset=['P-valor'])
                st.dataframe(_styler, width="stretch")
            else:
                st.info("No hay datos de coeficientes para este modelo.")

            section_divider()

            # Pruebas Estadísticas
            st.subheader("Pruebas estadísticas")

            if pruebas is not None and not pruebas.empty:
                df_test = pruebas.copy()

                def evaluar_significancia(row):
                    prueba = str(row.get('Prueba', '')).lower()
                    p_val = row.get('P_value', None)
                    if pd.isna(p_val):
                        return "N/A"
                    try:
                        p_val = float(p_val)
                    except:
                        return "N/A"

                    if 'jarque' in prueba or 'bera' in prueba:
                        return "Falla" if p_val < 0.05 else "Pasa"
                    else:
                        return "Pasa" if p_val > 0.05 else "Falla"

                df_test['Significancia'] = df_test.apply(evaluar_significancia, axis=1)

                def _color_significancia(val):
                    if val == "Pasa":
                        return f"color: {COLOR_OPTIMISTA}; font-weight: 600;"
                    elif val == "Falla":
                        return f"color: {COLOR_ADVERSO}; font-weight: 600;"
                    return f"color: {COLOR_TEXT_MUTED};"

                _styler_test = df_test.style
                if hasattr(_styler_test, "map"):
                    _styler_test = _styler_test.map(_color_significancia, subset=['Significancia'])
                else:
                    _styler_test = _styler_test.applymap(_color_significancia, subset=['Significancia'])
                st.dataframe(_styler_test, width="stretch")
            else:
                st.info("No hay datos de pruebas estadísticas.")
    else:
        st.info("Selecciona un modelo del panel izquierdo para ver los resultados.")
