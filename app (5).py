import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import json
import openpyxl

# =============================================================================
# PALETA CORPORATIVA v2.0
# =============================================================================
COLOR_NAVY       = "#0B2545"
COLOR_BLUE       = "#1E5AA8"
COLOR_GREEN      = "#2E8B57"
COLOR_RED        = "#D9534F"
COLOR_GRAY       = "#6C757D"
COLOR_BG         = "#FFFFFF"
COLOR_BG_SOFT    = "#F8F9FA"
COLOR_BORDER     = "#E9ECEF"
COLOR_TEXT       = "#212529"
COLOR_TEXT_MUTED = "#6C757D"
COLOR_TINT       = "#E8F4FD"
COLOR_WARNING    = "#F59E0B"

_BADGE = {
    "success": ("#D4EDDA", "#155724"),
    "warning": ("#FFF3CD", "#856404"),
    "danger":  ("#F8D7DA", "#721C24"),
    "neutral": ("#E2E3E5", "#383D41"),
    "info":    ("#D1ECF1", "#0C5460"),
}

PAISES_MAP = {
    'colombia': '🇨🇴 Colombia',
    'panama': '🇵🇦 Panamá',
    'panamá': '🇵🇦 Panamá',
    'costa rica': '🇨🇷 Costa Rica',
}

CARTERAS_MAP = {
    'vivi': 'Vivienda', 'vivienda': 'Vivienda',
    'cons': 'Consumo', 'consumo': 'Consumo',
    'com': 'Comercial', 'comercial': 'Comercial',
    'micro': 'Microcrédito',
}

# =============================================================================
# CSS GLOBAL
# =============================================================================
def inject_theme_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp, .stMarkdown, .stDataFrame, .stButton,
    .stSelectbox, .stTextInput, .stNumberInput, .stTabs {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{
        padding-top: 0.5rem; padding-bottom: 2rem; max-width: 1400px;
    }}
    .stApp {{ background-color: {COLOR_BG}; }}
    section[data-testid="stSidebar"] {{
        background-color: #ffffff; border-right: 1px solid {COLOR_BORDER};
        width: 280px !important;
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1rem; padding-bottom: 1rem;
    }}
    h1 {{ color: {COLOR_NAVY} !important; font-weight: 700 !important; font-size: 24px !important; }}
    h2 {{ color: {COLOR_NAVY} !important; font-weight: 600 !important; font-size: 18px !important; margin-top: 0.3rem !important; }}
    h3 {{ color: {COLOR_NAVY} !important; font-weight: 600 !important; font-size: 15px !important;
         border-left: 3px solid {COLOR_BLUE}; padding-left: 10px; margin-top: 0.4rem !important; }}
    p, span, div, label {{ color: {COLOR_TEXT}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {COLOR_BORDER}; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent; border-radius: 8px 8px 0 0;
        padding: 8px 18px; color: {COLOR_TEXT_MUTED}; font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_TINT} !important; color: {COLOR_NAVY} !important; font-weight: 600;
    }}
    div[data-testid="stMetric"] {{
        background-color: #ffffff; border: 1px solid {COLOR_BORDER}; border-radius: 8px; padding: 12px 16px;
    }}
    div[data-testid="stExpander"] {{
        background-color: #ffffff; border: 1px solid {COLOR_BORDER}; border-radius: 8px;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {COLOR_BORDER} !important; border-radius: 10px !important;
    }}
    .stButton > button {{
        border-radius: 6px; border: 1px solid {COLOR_BORDER}; color: {COLOR_TEXT}; font-weight: 500;
    }}
    .stButton > button:hover {{
        border-color: {COLOR_BLUE}; color: {COLOR_BLUE};
    }}
    div[data-testid="stDataFrame"] {{ border: 1px solid {COLOR_BORDER}; border-radius: 8px; }}
    section[data-testid="stSidebar"] {{
        position: sticky; top: 0; height: 100vh; overflow-y: auto;
    }}
    .bottom-nav {{
        position: fixed; bottom: 0; left: 280px; right: 0;
        background: rgba(255,255,255,0.97); backdrop-filter: blur(10px);
        border-top: 1px solid {COLOR_BORDER}; padding: 12px 24px;
        z-index: 9999; display: flex; align-items: center; justify-content: center; gap: 24px;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.04);
    }}
    .bottom-nav-btn {{
        background: {COLOR_NAVY}; color: white; border: none; border-radius: 8px;
        padding: 10px 24px; font-weight: 600; font-size: 14px; cursor: pointer;
        transition: all 0.2s ease;
    }}
    .bottom-nav-btn:hover {{ background: {COLOR_BLUE}; transform: translateY(-1px); }}
    .bottom-nav-btn:disabled {{
        background: {COLOR_BORDER}; color: {COLOR_TEXT_MUTED}; cursor: not-allowed; transform: none;
    }}
    .bottom-nav-info {{ font-size: 13px; color: {COLOR_TEXT_MUTED}; font-weight: 500; text-align: center; }}
    .bottom-nav-model {{ font-size: 15px; color: {COLOR_NAVY}; font-weight: 700; }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# COMPONENTES VISUALES
# =============================================================================
def badge(text, kind="neutral"):
    bg, fg = _BADGE.get(kind, _BADGE["neutral"])
    return (f'<span style="background:{bg};color:{fg};font-size:12px;'
            f'padding:3px 10px;border-radius:12px;font-weight:500;">{text}</span>')


def metric_card(label, value, color=None):
    color = color or COLOR_TEXT
    return f"""
    <div style="background:#ffffff;border:1px solid {COLOR_BORDER};border-radius:8px;
                padding:14px 16px;margin-bottom:8px;">
        <p style="font-size:11px;color:{COLOR_TEXT_MUTED};margin:0 0 4px;text-transform:uppercase;letter-spacing:0.5px;">{label}</p>
        <p style="font-size:20px;font-weight:600;color:{color};margin:0;">{value}</p>
    </div>
    """


def kpi_card(title, value, subtitle="", color=COLOR_NAVY):
    sub = f'<p style="font-size:12px;color:{COLOR_TEXT_MUTED};margin:4px 0 0;">{subtitle}</p>' if subtitle else ''
    return f"""
    <div style="background:#ffffff;border:1px solid {COLOR_BORDER};border-radius:10px;padding:16px;text-align:center;">
        <p style="font-size:11px;color:{COLOR_TEXT_MUTED};margin:0 0 6px;text-transform:uppercase;letter-spacing:0.5px;">{title}</p>
        <p style="font-size:22px;font-weight:700;color:{color};margin:0;">{value}</p>
        {sub}
    </div>
    """


def section_divider():
    return f"<hr style='border:none;border-top:1px solid {COLOR_BORDER};margin:1.2rem 0;'>"


# =============================================================================
# PARSER
# =============================================================================
def convertir_fecha(serie):
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


def leer_meta_embebida(file, prefix="sarimax_meta"):
    try:
        file.seek(0)
        wb = openpyxl.load_workbook(file, read_only=True)
        props = wb.custom_doc_props
        n_prop_name = f"{prefix}_n"
        if n_prop_name not in props.names:
            return None
        n_partes = int(props[n_prop_name].value)
        partes = [props[f"{prefix}_{idx:02d}"].value for idx in range(1, n_partes + 1)]
        return json.loads("".join(partes))
    except Exception:
        return None
    finally:
        file.seek(0)


def parsear_excel(file):
    xls = pd.ExcelFile(file)
    modelos = {}
    for sheet_name in xls.sheet_names:
        try:
            df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        except Exception:
            continue
        if len(df_raw) < 2:
            continue
        headers = [str(v).strip() if pd.notna(v) else "" for v in df_raw.iloc[1].values]
        col_map = {}
        for idx, name in enumerate(headers):
            if name:
                col_map.setdefault(name, []).append(idx)
        modelo = {"nombre": sheet_name}

        # Sección 1
        exog_cols, exog_names = [], set()
        for idx, name in enumerate(headers):
            nu = name.upper()
            if nu in ['FECHA', 'BASE', 'ADVERSO', 'OPTIMISTA'] or nu.startswith('FWL'):
                continue
            if nu.endswith(('_BASE', '_ADVERSO', '_OPTIMISTA')):
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

        # Sección 2: FWL 12m
        fwl_cols = [c for c in ['FWL_BASE', 'FWL_ADVERSO', 'FWL_OPTIMISTA'] if c in col_map]
        if fwl_cols and 'fecha' in col_map:
            idx_fwl = [col_map['fecha'][0]] + [col_map[c][0] for c in fwl_cols]
            df_fwl = df_raw.iloc[2:, idx_fwl].copy()
            df_fwl.columns = ['fecha'] + fwl_cols
            df_fwl = df_fwl.dropna(how='all').reset_index(drop=True)
            df_fwl['fecha'] = convertir_fecha(df_fwl['fecha'])
            df_fwl = df_fwl.dropna(subset=['FWL_BASE']).reset_index(drop=True)
            modelo['fwl_12m'] = df_fwl
        else:
            modelo['fwl_12m'] = None

        # Sección 3: FWL anual
        if 'Año' in col_map and 'Escenario' in col_map and 'Factor FWL' in col_map:
            idx_anual = [col_map['Año'][0], col_map['Escenario'][0], col_map['Factor FWL'][0]]
            df_anual = df_raw.iloc[2:, idx_anual].copy()
            df_anual.columns = ['Año', 'Escenario', 'Factor FWL']
            df_anual = df_anual.dropna(how='all').reset_index(drop=True)
            modelo['fwl_anual'] = df_anual
        else:
            modelo['fwl_anual'] = None

        # Sección 4: Residuos
        if 'Obs' in col_map and 'Residuo' in col_map:
            idx_res = [col_map['Obs'][0], col_map['Residuo'][0]]
            df_res = df_raw.iloc[2:, idx_res].copy()
            df_res.columns = ['Obs', 'Residuo']
            df_res = df_res.dropna(how='all').reset_index(drop=True)
            modelo['residuos_ind'] = df_res
        else:
            modelo['residuos_ind'] = None

        # Sección 5: Resumen residuos
        if 'Estadistico' in col_map and 'Valor' in col_map:
            idx_est = col_map['Estadistico'][0]
            idx_val = col_map['Valor'][0]
            df_resumen = df_raw.iloc[2:, [idx_est, idx_val]].copy()
            df_resumen.columns = ['Estadistico', 'Valor']
            df_resumen = df_resumen.dropna(how='all').reset_index(drop=True)
            modelo['resumen_residuos'] = df_resumen
        else:
            modelo['resumen_residuos'] = None

        # Sección 6: Coeficientes
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

        # Sección 7: Pruebas
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

        modelo['observaciones'] = len(modelo['fecha_endogena'].dropna(how='all')) if modelo['fecha_endogena'] is not None and not modelo['fecha_endogena'].empty else 0
        modelos[sheet_name] = modelo
    return modelos


# =============================================================================
# UTILIDADES
# =============================================================================
def contar_pruebas_aprobadas(pruebas_df):
    if pruebas_df is None or pruebas_df.empty:
        return 0, 3
    aprobadas = 0
    for _, row in pruebas_df.iterrows():
        prueba = str(row.get('Prueba', '')).lower()
        p_val = row.get('P_value', None)
        if p_val is None or pd.isna(p_val):
            continue
        try:
            p_val = float(p_val)
        except:
            continue
        if 'ljung' in prueba or 'box' in prueba:
            if p_val > 0.05: aprobadas += 1
        elif 'jarque' in prueba or 'bera' in prueba:
            if p_val > 0.05: aprobadas += 1
        elif 'hetero' in prueba or 'arch' in prueba:
            if p_val > 0.05: aprobadas += 1
    return aprobadas, 3


def clasificar_variable(var_name):
    var_lower = str(var_name).lower()
    if var_lower.startswith('ar.'): return 'AR'
    elif var_lower.startswith('ma.'): return 'MA'
    elif var_lower == 'intercept': return 'Exógena'
    elif var_lower.startswith('var_'): return 'Exógena'
    elif var_lower == 'sigma2': return 'Varianza'
    return 'Otro'


def generar_campana_normal(residuos, media, std):
    if std == 0 or len(residuos) == 0:
        return [], []
    x = np.linspace(min(residuos), max(residuos), 100)
    y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - media) / std) ** 2)
    return x, y


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
            try: p_val = float(p_val)
            except: p_val = None
        if p_val is None:
            resultados.append((exog, None, "Desconocido"))
        elif p_val < 0.05:
            resultados.append((exog, p_val, "Significativa"))
        elif p_val < 0.10:
            resultados.append((exog, p_val, "Marginal"))
        else:
            resultados.append((exog, p_val, "No significativa"))
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
    base_col, adv_col, opt_col = base_col[0], adv_col[0], opt_col[0]
    df = fwl_df.copy()
    df['FWL_Ponderado'] = (
        df[base_col].astype(float) * pesos['base'] +
        df[adv_col].astype(float) * pesos['adverso'] +
        df[opt_col].astype(float) * pesos['optimista']
    )
    return df


def resumen_fwl(fwl_df):
    if fwl_df is None or fwl_df.empty or 'FWL_Ponderado' not in fwl_df.columns:
        return {}
    vals = fwl_df['FWL_Ponderado'].dropna().astype(float)
    if len(vals) == 0:
        return {}
    return {'promedio': vals.mean(), 'maximo': vals.max(), 'minimo': vals.min(), 'volatilidad': vals.std()}


# =============================================================================
# METADATA
# =============================================================================
def extraer_kpis_meta(meta):
    if not meta:
        return {}
    return {
        'pais': PAISES_MAP.get(str(meta.get('pais', '')).lower().strip(), meta.get('pais', 'N/A')),
        'cartera': CARTERAS_MAP.get(str(meta.get('cartera', '')).lower().strip(), meta.get('cartera', 'N/A')),
        'tipo_endogena': meta.get('motor_tipo_endogena', 'N/A'),
        'modo_endogena': meta.get('generador_modo_endogena', 'N/A'),
        'ventana_mm': meta.get('generador_ventana_mm', 'N/A'),
        'vif_max': meta.get('motor_vif_max', 'N/A'),
        'fwl_min': meta.get('motor_fwl_factor_min', '?'),
        'fwl_max': meta.get('motor_fwl_factor_max', '?'),
        'max_exog': meta.get('motor_max_exog_por_modelo', 'N/A'),
        'top_exportar': meta.get('motor_top_exportar', 'N/A'),
    }


# =============================================================================
# PLOTS
# =============================================================================
def aplicar_tema_plotly(fig):
    fig.update_layout(
        font=dict(family="Inter, Arial, sans-serif", size=13, color=COLOR_TEXT),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=45, l=10, r=10, b=10),
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLOR_BORDER, zeroline=False, linecolor=COLOR_BORDER)
    fig.update_yaxes(showgrid=True, gridcolor=COLOR_BORDER, zeroline=False, linecolor=COLOR_BORDER)
    if fig.layout.title and fig.layout.title.text:
        fig.update_layout(title=dict(font=dict(size=15, color=COLOR_NAVY)))
    return fig


def fig_predicciones(df_end, endogena_cols, exog_df, exog_sel, modelo_nombre):
    fig = go.Figure()
    fecha_col = 'fecha' if 'fecha' in df_end.columns else df_end.columns[0]
    for col in endogena_cols:
        if col not in df_end.columns:
            continue
        col_str = str(col).upper()
        if col_str == 'BASE':
            fig.add_trace(go.Scatter(x=df_end[fecha_col], y=df_end[col], mode='lines', name='Base', line=dict(color=COLOR_BLUE, width=2)))
        elif col_str in ['ADVERSO', 'ADVERSA']:
            fig.add_trace(go.Scatter(x=df_end[fecha_col], y=df_end[col], mode='lines', name='Adverso', line=dict(color=COLOR_RED, width=2, dash='dash')))
        elif col_str == 'OPTIMISTA':
            fig.add_trace(go.Scatter(x=df_end[fecha_col], y=df_end[col], mode='lines', name='Optimista', line=dict(color=COLOR_GREEN, width=2, dash='dot')))
    if exog_df is not None and exog_sel:
        for ex in exog_sel:
            for suffix in ['_BASE', '_ADVERSO', '_OPTIMISTA']:
                col_name = ex + suffix
                if col_name in exog_df.columns:
                    x_vals = exog_df[fecha_col] if fecha_col in exog_df.columns else exog_df.index
                    fig.add_trace(go.Scatter(x=x_vals, y=exog_df[col_name], mode='lines', name=f'{ex}{suffix}', line=dict(width=1.5), yaxis='y2'))
        fig.update_layout(yaxis2=dict(title='Exógenas', overlaying='y', side='right'))
    fig.update_layout(title=f"Predicciones — {modelo_nombre}", xaxis_title="Fecha", yaxis_title="Valor",
                      legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.05), hovermode='x unified')
    return aplicar_tema_plotly(fig)


def fig_fwl_12m(df_fwl):
    fig = go.Figure()
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
            fig.add_trace(go.Scatter(x=df_fwl[fecha_col], y=df_fwl[col], mode='lines', name='Base', line=dict(color=COLOR_BLUE, width=2)))
        elif 'FWL_ADVERSO' in col_str or 'FWL_ADVERSA' in col_str:
            fig.add_trace(go.Scatter(x=df_fwl[fecha_col], y=df_fwl[col], mode='lines', name='Adverso', line=dict(color=COLOR_RED, width=2, dash='dash')))
        elif 'FWL_OPTIMISTA' in col_str:
            fig.add_trace(go.Scatter(x=df_fwl[fecha_col], y=df_fwl[col], mode='lines', name='Optimista', line=dict(color=COLOR_GREEN, width=2, dash='dot')))
    fig.update_layout(title="Factor FWL a 12 Meses", xaxis_title="Fecha", yaxis_title="FWL",
                      legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.05), hovermode='x unified')
    return aplicar_tema_plotly(fig)


def fig_fwl_ponderado(df_pond):
    fecha_col = None
    for c in df_pond.columns:
        if 'fecha' in str(c).lower():
            fecha_col = c
            break
    if fecha_col is None:
        fecha_col = df_pond.columns[0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_pond[fecha_col], y=df_pond['FWL_Ponderado'], mode='lines', name='FWL Ponderado',
                              fill='tozeroy', line=dict(color=COLOR_BLUE, width=2), fillcolor='rgba(30,90,168,0.12)'))
    fig.update_layout(title="Factor FWL Ponderado", xaxis_title="Fecha", yaxis_title="FWL Ponderado")
    return aplicar_tema_plotly(fig)


def fig_histograma_residuos(vals, media, std):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=vals, nbinsx=20, marker_color=COLOR_BLUE, opacity=0.75, name='Residuos'))
    x_norm, y_norm = generar_campana_normal(vals, media, std)
    if len(x_norm) > 0:
        bin_width = (vals.max() - vals.min()) / 20 if vals.max() != vals.min() else 1
        y_norm_scaled = y_norm * len(vals) * bin_width
        fig.add_trace(go.Scatter(x=x_norm, y=y_norm_scaled, mode='lines', name='Normal teórica', line=dict(color=COLOR_RED, width=2)))
    fig.update_layout(xaxis_title="Residuos", yaxis_title="Frecuencia")
    return aplicar_tema_plotly(fig)


def fig_barras_coeficientes(df_coef):
    df = df_coef.copy()
    df['abs'] = df['Coeficiente'].abs()
    df = df.sort_values('abs', ascending=True)
    colors = [COLOR_GREEN if c >= 0 else COLOR_RED for c in df['Coeficiente']]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df['Lag'], x=df['Coeficiente'], orientation='h', marker_color=colors,
                          text=df['Coeficiente'].round(4), textposition='outside'))
    fig.update_layout(title="Coeficientes del Modelo", xaxis_title="Valor", yaxis_title="Variable", showlegend=False)
    return aplicar_tema_plotly(fig)


# =============================================================================
# DIAGNÓSTICOS
# =============================================================================
def evaluar_prueba(prueba, p_val):
    if pd.isna(p_val):
        return "N/A", "neutral"
    try:
        p_val = float(p_val)
    except:
        return "N/A", "neutral"
    prueba_lower = str(prueba).lower()
    if 'jarque' in prueba_lower or 'bera' in prueba_lower:
        if p_val < 0.05: return "No cumple", "danger"
        elif p_val < 0.10: return "Revisar", "warning"
        else: return "Correcto", "success"
    if p_val > 0.05: return "Correcto", "success"
    elif p_val > 0.01: return "Revisar", "warning"
    else: return "No cumple", "danger"


def limpiar_nombre_prueba(nombre):
    nombre_lower = str(nombre).lower()
    if 'arch' in nombre_lower: return "Heterocedasticidad"
    if 'ljung' in nombre_lower or 'box' in nombre_lower: return "Ljung-Box"
    if 'jarque' in nombre_lower or 'bera' in nombre_lower: return "Jarque-Bera"
    return str(nombre)


def render_diagnosticos_ejecutivo(pruebas_df):
    if pruebas_df is None or pruebas_df.empty:
        st.info("No hay datos de pruebas estadísticas.")
        return
    df = pruebas_df.copy()
    df['Prueba'] = df['Prueba'].apply(limpiar_nombre_prueba)
    resultados = []
    for _, row in df.iterrows():
        prueba = row['Prueba']
        p_val = row['P_value']
        estado, tipo = evaluar_prueba(prueba, p_val)
        resultados.append({
            'Diagnóstico': prueba, 'Estado': estado, 'tipo': tipo,
            'P-valor': p_val, 'Estadístico': row.get('Estadistico', '—'),
        })
    df_res = pd.DataFrame(resultados)
    st.markdown("#### Resumen Ejecutivo")
    cols = st.columns(len(df_res))
    for i, (_, row) in enumerate(df_res.iterrows()):
        with cols[i]:
            color = COLOR_GREEN if row['tipo'] == 'success' else (COLOR_RED if row['tipo'] == 'danger' else COLOR_WARNING)
            emoji = "🟢" if row['tipo'] == 'success' else ("🔴" if row['tipo'] == 'danger' else "🟡")
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid {COLOR_BORDER};border-radius:10px;padding:18px;text-align:center;">
                <p style="font-size:28px;margin:0 0 8px;">{emoji}</p>
                <p style="font-size:13px;font-weight:600;color:{COLOR_NAVY};margin:0;">{row['Diagnóstico']}</p>
                <p style="font-size:12px;color:{color};font-weight:600;margin:6px 0 0;">{row['Estado']}</p>
            </div>
            """, unsafe_allow_html=True)
    with st.expander("🔍 Ver detalle técnico"):
        df_display = df_res[['Diagnóstico', 'Estadístico', 'P-valor', 'Estado']].copy()
        def color_estado(val):
            if val == "Correcto": return f"color: {COLOR_GREEN}; font-weight: 600;"
            elif val == "No cumple": return f"color: {COLOR_RED}; font-weight: 600;"
            elif val == "Revisar": return f"color: {COLOR_WARNING}; font-weight: 600;"
            return ""
        styler = df_display.style
        if hasattr(styler, "map"):
            styler = styler.map(color_estado, subset=['Estado'])
        else:
            styler = styler.applymap(color_estado, subset=['Estado'])
        st.dataframe(styler, use_container_width=True, hide_index=True)


def render_metricas_diagnostico(pruebas_df):
    if pruebas_df is None or pruebas_df.empty:
        return
    lb_p = jb_p = het_p = None
    for _, row in pruebas_df.iterrows():
        prueba = str(row.get('Prueba', '')).lower()
        p_val = row.get('P_value', None)
        if pd.isna(p_val):
            continue
        try: p_val = float(p_val)
        except: continue
        if 'ljung' in prueba or 'box' in prueba: lb_p = p_val
        elif 'jarque' in prueba or 'bera' in prueba: jb_p = p_val
        elif 'hetero' in prueba or 'arch' in prueba: het_p = p_val
    c1, c2, c3 = st.columns(3)
    with c1:
        val = f"{lb_p:.4f}" if lb_p is not None else "N/A"
        color = COLOR_GREEN if lb_p is not None and lb_p > 0.05 else COLOR_RED
        st.markdown(metric_card("Ljung-Box P-valor", val, color), unsafe_allow_html=True)
    with c2:
        val = f"{jb_p:.4f}" if jb_p is not None else "N/A"
        color = COLOR_RED if jb_p is not None and jb_p < 0.05 else COLOR_GREEN
        st.markdown(metric_card("Jarque-Bera P-valor", val, color), unsafe_allow_html=True)
    with c3:
        val = f"{het_p:.4f}" if het_p is not None else "N/A"
        color = COLOR_GREEN if het_p is not None and het_p > 0.05 else COLOR_RED
        st.markdown(metric_card("Heterocedasticidad P-valor", val, color), unsafe_allow_html=True)


# =============================================================================
# CARDS / UI COMPONENTS
# =============================================================================
def render_header_ejecutivo(modelo_nombre, meta_kpis, n_modelos, fecha_gen="—"):
    pais = meta_kpis.get('pais', '—')
    cartera = meta_kpis.get('cartera', '—')
    cols = st.columns([3, 1, 1, 1, 1])
    with cols[0]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;">
            <div>
                <p style="font-size:11px;color:{COLOR_TEXT_MUTED};margin:0;text-transform:uppercase;letter-spacing:0.5px;">Modelo seleccionado</p>
                <p style="font-size:22px;font-weight:700;color:{COLOR_NAVY};margin:0;">{modelo_nombre}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]: st.markdown(kpi_card("País", pais, color=COLOR_NAVY), unsafe_allow_html=True)
    with cols[2]: st.markdown(kpi_card("Cartera", cartera, color=COLOR_BLUE), unsafe_allow_html=True)
    with cols[3]: st.markdown(kpi_card("Modelos", str(n_modelos), color=COLOR_GREEN), unsafe_allow_html=True)
    with cols[4]: st.markdown(kpi_card("Generado", fecha_gen, color=COLOR_GRAY), unsafe_allow_html=True)
    st.markdown(f"<div style='border-bottom:2px solid {COLOR_BORDER};margin:12px 0;'></div>", unsafe_allow_html=True)


def render_chips_exogenas(exogenas, seleccionadas, key_prefix):
    cols = st.columns(min(len(exogenas), 6))
    for i, ex in enumerate(exogenas):
        with cols[i % len(cols)]:
            activo = ex in seleccionadas
            bg = COLOR_BLUE if activo else COLOR_BG_SOFT
            fg = "#ffffff" if activo else COLOR_TEXT
            border = "none" if activo else f"1px solid {COLOR_BORDER}"
            if st.button(f"{'✓ ' if activo else ''}{ex}", key=f"{key_prefix}_chip_{ex}", use_container_width=True):
                if activo:
                    seleccionadas.remove(ex)
                else:
                    seleccionadas.append(ex)
                st.rerun()


def render_tarjetas_meta(meta_kpis):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(metric_card("País", meta_kpis.get('pais', '—'), COLOR_NAVY), unsafe_allow_html=True)
        st.markdown(metric_card("Cartera", meta_kpis.get('cartera', '—'), COLOR_BLUE), unsafe_allow_html=True)
        st.markdown(metric_card("Modo endógena", meta_kpis.get('modo_endogena', '—'), COLOR_GRAY), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Ventana MM", meta_kpis.get('ventana_mm', '—'), COLOR_GRAY), unsafe_allow_html=True)
        fwl_range = f"{meta_kpis.get('fwl_min', '?')} – {meta_kpis.get('fwl_max', '?')}"
        st.markdown(metric_card("Rango FWL", fwl_range, COLOR_GREEN), unsafe_allow_html=True)
        st.markdown(metric_card("Top exportados", meta_kpis.get('top_exportar', '—'), COLOR_GRAY), unsafe_allow_html=True)


def render_kpis_fwl(resumen):
    if not resumen:
        return
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(metric_card("Promedio", f"{resumen.get('promedio', 0):.4f}", COLOR_BLUE), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("Máximo", f"{resumen.get('maximo', 0):.4f}", COLOR_GREEN), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("Mínimo", f"{resumen.get('minimo', 0):.4f}", COLOR_RED), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("Volatilidad (σ)", f"{resumen.get('volatilidad', 0):.4f}", COLOR_GRAY), unsafe_allow_html=True)


# =============================================================================
# SESSION STATE
# =============================================================================
for key, default in [
    ("uploaded_file", None), ("modelos_data", {}), ("meta_contexto", None),
    ("modelo_seleccionado", None), ("criterio_ordenamiento", "Pruebas aprobadas ↓"),
    ("exog_sel", {}), ("pred_filtro", "Todas"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =============================================================================
# APP PRINCIPAL
# =============================================================================
st.set_page_config(page_title="Dashboard SARIMAX v2.0", layout="wide")
inject_theme_css()

col_left, col_right = st.columns([1, 4])

# =========================================================================
# SIDEBAR
# =========================================================================
with col_left:
    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{COLOR_NAVY};margin:0 0 10px;'>📂 Cargar modelo</p>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Archivo Excel (.xlsx)", type=["xlsx"], label_visibility="collapsed")
    if uploaded is not None:
        st.session_state.uploaded_file = uploaded
        if not st.session_state.modelos_data or uploaded.name != getattr(st.session_state, 'last_file_name', None):
            with st.spinner("Parseando modelos..."):
                st.session_state.modelos_data = parsear_excel(uploaded)
                st.session_state.meta_contexto = leer_meta_embebida(uploaded)
                st.session_state.last_file_name = uploaded.name
            st.success(f"✅ {uploaded.name} ({uploaded.size/1024:.1f} KB)")
            if st.session_state.modelo_seleccionado is None or st.session_state.modelo_seleccionado not in st.session_state.modelos_data:
                st.session_state.modelo_seleccionado = list(st.session_state.modelos_data.keys())[0]

    if st.session_state.uploaded_file is not None:
        if st.button("🗑️ Eliminar", key="btn_eliminar", use_container_width=True):
            for k in ["uploaded_file", "modelos_data", "meta_contexto", "modelo_seleccionado", "last_file_name"]:
                st.session_state[k] = None if k not in ["modelos_data", "exog_sel"] else ({}, {})
            st.rerun()

    if st.session_state.modelos_data:
        st.markdown(section_divider(), unsafe_allow_html=True)

        meta = st.session_state.meta_contexto
        if meta:
            meta_kpis = extraer_kpis_meta(meta)
            st.markdown(f"<p style='font-size:12px;font-weight:600;color:{COLOR_NAVY};margin:0 0 8px;'>📋 Contexto</p>", unsafe_allow_html=True)
            render_tarjetas_meta(meta_kpis)
        else:
            st.caption("Sin metadata embebida.")

        st.markdown(section_divider(), unsafe_allow_html=True)

        criterio = st.radio("Ordenar por:", ["Nombre (A-Z)", "Pruebas aprobadas ↓", "Pruebas aprobadas ↑"],
                            index=1, key="criterio_orden")
        st.session_state.criterio_ordenamiento = criterio

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

        opciones = [f"{m}  ({pruebas_dict[m][0]}/{pruebas_dict[m][1]} ✅)" for m in modelos_list]
        idx = modelos_list.index(st.session_state.modelo_seleccionado) if st.session_state.modelo_seleccionado in modelos_list else 0
        seleccion = st.selectbox("Modelo", opciones, index=idx, key="sel_modelo")
        st.session_state.modelo_seleccionado = seleccion.split("  (")[0]

        datos = st.session_state.modelos_data.get(st.session_state.modelo_seleccionado, {})
        st.markdown(f"<p style='font-size:12px;font-weight:600;color:{COLOR_NAVY};margin:12px 0 4px;'>Modelo actual</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:15px;font-weight:600;color:{COLOR_NAVY};margin:0;'>{st.session_state.modelo_seleccionado}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:12px;color:{COLOR_TEXT_MUTED};margin:4px 0 0;'>{datos.get('observaciones', 0)} observaciones</p>", unsafe_allow_html=True)

        exogenas = datos.get('exogenas_nombres', [])
        if exogenas:
            st.markdown(f"<p style='font-size:12px;font-weight:600;color:{COLOR_NAVY};margin:12px 0 8px;'>📊 Exógenas</p>", unsafe_allow_html=True)
            coefs = datos.get('coeficientes')
            sigs = obtener_significancia_exogenas(coefs, exogenas)
            sig_count = sum(1 for _, _, s in sigs if s == "Significativa")
            st.markdown(f"<p style='font-size:11px;color:{COLOR_TEXT_MUTED};margin:0 0 8px;'>{sig_count}/{len(exogenas)} significativas</p>", unsafe_allow_html=True)
            for ex, pval, status in sigs:
                color = COLOR_GREEN if status == "Significativa" else (COLOR_RED if status == "No significativa" else COLOR_WARNING)
                label = "Sig." if status == "Significativa" else ("No sig." if status == "No significativa" else "Marg.")
                p_txt = f"p={pval:.3f}" if pval is not None else "p=N/A"
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:3px 0;font-size:12px;"><span>{ex}</span><span style="color:{color};font-weight:500;">{label} ({p_txt})</span></div>', unsafe_allow_html=True)

# =========================================================================
# PANEL PRINCIPAL
# =========================================================================
with col_right:
    if not st.session_state.modelos_data:
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid {COLOR_BORDER};border-radius:12px;padding:60px 32px;text-align:center;margin-top:40px;">
            <p style="font-size:20px;font-weight:600;color:{COLOR_NAVY};margin:0 0 8px;">Bienvenido al Dashboard SARIMAX v2.0</p>
            <p style="font-size:14px;color:{COLOR_TEXT_MUTED};margin:0;">Sube un archivo Excel en el panel izquierdo para comenzar.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        datos = st.session_state.modelos_data.get(st.session_state.modelo_seleccionado, {})
        meta_kpis = extraer_kpis_meta(st.session_state.meta_contexto)

        # --- Header ejecutivo ---
        render_header_ejecutivo(
            st.session_state.modelo_seleccionado,
            meta_kpis,
            len(st.session_state.modelos_data),
            fecha_gen="—"
        )

        # --- Navegación (botones ocultos) ---
        modelos_list = [m[0] for m in sorted(
            [(n, contar_pruebas_aprobadas(d.get('pruebas'))[0]) for n, d in st.session_state.modelos_data.items()],
            key=lambda x: (-x[1], x[0]) if st.session_state.criterio_ordenamiento == "Pruebas aprobadas ↓" else (x[0] if st.session_state.criterio_ordenamiento == "Nombre (A-Z)" else (x[1], x[0]))
        )]
        current_idx = modelos_list.index(st.session_state.modelo_seleccionado)

        # Botones reales (ocultos visualmente pero funcionales)
        c_prev, c_next = st.columns(2)
        with c_prev:
            if st.button("←", disabled=current_idx==0, key="btn_prev", use_container_width=True):
                st.session_state.modelo_seleccionado = modelos_list[current_idx - 1]
                st.rerun()
        with c_next:
            if st.button("→", disabled=current_idx==len(modelos_list)-1, key="btn_next", use_container_width=True):
                st.session_state.modelo_seleccionado = modelos_list[current_idx + 1]
                st.rerun()

        # --- Tabs ---
        tab1, tab2, tab3 = st.tabs(["📈 Visualización", "🔮 Predicciones", "🩺 Diagnósticos"])

        # =====================================================================
        # TAB 1: VISUALIZACIÓN
        # =====================================================================
        with tab1:
            st.markdown("#### Exógenas activas")
            exogenas = datos.get('exogenas_nombres', [])
            modelo_key = st.session_state.modelo_seleccionado
            if modelo_key not in st.session_state.exog_sel:
                st.session_state.exog_sel[modelo_key] = []
            if exogenas:
                render_chips_exogenas(exogenas, st.session_state.exog_sel[modelo_key], modelo_key)
            else:
                st.caption("Sin exógenas en este modelo.")

            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

            df_end = datos.get('fecha_endogena')
            endogena_cols = datos.get('endogenas_cols', [])
            if df_end is not None and not df_end.empty and endogena_cols:
                fig = fig_predicciones(df_end, endogena_cols, datos.get('exogenas'), st.session_state.exog_sel.get(modelo_key, []), st.session_state.modelo_seleccionado)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de predicciones.")

            st.markdown(section_divider(), unsafe_allow_html=True)

            st.markdown("#### Factor FWL por año y escenario")
            df_fwl_anual = datos.get('fwl_anual')
            if df_fwl_anual is not None and not df_fwl_anual.empty:
                try:
                    df_pivot = df_fwl_anual.pivot(index='Año', columns='Escenario', values='Factor FWL').reset_index()
                    rename_map = {}
                    for c in df_pivot.columns:
                        c_str = str(c).lower()
                        if 'base' in c_str: rename_map[c] = 'Base'
                        elif 'adverso' in c_str or 'advers' in c_str: rename_map[c] = 'Adverso'
                        elif 'optimista' in c_str: rename_map[c] = 'Optimista'
                    df_pivot = df_pivot.rename(columns=rename_map)
                    st.dataframe(df_pivot, use_container_width=True, hide_index=True)
                except:
                    st.dataframe(df_fwl_anual, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de Factor FWL por Año.")

            st.markdown(section_divider(), unsafe_allow_html=True)

            st.markdown("#### Factor FWL a 12 meses")
            df_fwl = datos.get('fwl_12m')
            if df_fwl is not None and not df_fwl.empty:
                st.plotly_chart(fig_fwl_12m(df_fwl), use_container_width=True)
            else:
                st.info("No hay datos de FWL a 12 meses.")

            st.markdown(section_divider(), unsafe_allow_html=True)

            st.markdown("#### Factor FWL ponderado")
            c1, c2, c3 = st.columns(3)
            with c1: peso_base = st.number_input("Peso Base", 0.0, 1.0, 0.33, 0.01, key="pw_base")
            with c2: peso_adverso = st.number_input("Peso Adverso", 0.0, 1.0, 0.33, 0.01, key="pw_adv")
            with c3: peso_optimista = st.number_input("Peso Optimista", 0.0, 1.0, 0.34, 0.01, key="pw_opt")

            suma = peso_base + peso_adverso + peso_optimista
            if abs(suma - 1.0) < 0.001:
                st.markdown(badge("Válido", "success"), unsafe_allow_html=True)
            elif suma < 1.0:
                st.markdown(badge(f"{1.0-suma:.2f} disponible", "warning"), unsafe_allow_html=True)
            else:
                st.markdown(badge(f"Excede en {suma-1.0:.2f}", "danger"), unsafe_allow_html=True)

            if df_fwl is not None and not df_fwl.empty and suma <= 1.0:
                pesos = {'base': peso_base, 'adverso': peso_adverso, 'optimista': peso_optimista}
                df_pond = calcular_fwl_ponderado(df_fwl, pesos)
                if df_pond is not None:
                    render_kpis_fwl(resumen_fwl(df_pond))
                    st.plotly_chart(fig_fwl_ponderado(df_pond), use_container_width=True)
                else:
                    st.info("No se pudo calcular el FWL ponderado.")
            elif suma > 1.0:
                st.warning("Ajusta los pesos para que la suma no exceda 1.0")

        # =====================================================================
        # TAB 2: PREDICCIONES
        # =====================================================================
        with tab2:
            st.markdown("#### Datos de predicción")
            filtros = st.columns(4)
            with filtros[0]:
                if st.button("📊 Ver Base", use_container_width=True): st.session_state.pred_filtro = "Base"
            with filtros[1]:
                if st.button("📉 Ver Adverso", use_container_width=True): st.session_state.pred_filtro = "Adverso"
            with filtros[2]:
                if st.button("📈 Ver Optimista", use_container_width=True): st.session_state.pred_filtro = "Optimista"
            with filtros[3]:
                if st.button("👁️ Ver todas", use_container_width=True): st.session_state.pred_filtro = "Todas"

            df_end = datos.get('fecha_endogena')
            endogena_cols = datos.get('endogenas_cols', [])
            if df_end is not None and not df_end.empty and endogena_cols:
                fecha_col = 'fecha' if 'fecha' in df_end.columns else df_end.columns[0]
                base_col = adv_col = opt_col = None
                for col in endogena_cols:
                    col_str = str(col).upper()
                    if col_str == 'BASE': base_col = col
                    elif col_str in ['ADVERSO', 'ADVERSA']: adv_col = col
                    elif col_str == 'OPTIMISTA': opt_col = col

                df_pred = pd.DataFrame()
                df_pred['Fecha'] = pd.to_datetime(df_end[fecha_col]).dt.strftime('%Y-%m-%d')
                cols_export = ['Fecha']
                if base_col and base_col in df_end.columns and st.session_state.pred_filtro in ["Base", "Todas"]:
                    df_pred['Base'] = df_end[base_col].astype(float).round(4)
                    cols_export.append('Base')
                if adv_col and adv_col in df_end.columns and st.session_state.pred_filtro in ["Adverso", "Todas"]:
                    df_pred['Adverso'] = df_end[adv_col].astype(float).round(4)
                    cols_export.append('Adverso')
                if opt_col and opt_col in df_end.columns and st.session_state.pred_filtro in ["Optimista", "Todas"]:
                    df_pred['Optimista'] = df_end[opt_col].astype(float).round(4)
                    cols_export.append('Optimista')

                st.dataframe(df_pred[cols_export], use_container_width=True, hide_index=True, height=400)
                csv = df_pred[cols_export].to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Descargar CSV", csv, f"predicciones_{st.session_state.modelo_seleccionado}.csv", "text/csv")
            else:
                st.info("No hay datos de predicciones.")

        # =====================================================================
        # TAB 3: DIAGNÓSTICOS
        # =====================================================================
        with tab3:
            pruebas = datos.get('pruebas')
            render_metricas_diagnostico(pruebas)
            st.markdown(section_divider(), unsafe_allow_html=True)
            render_diagnosticos_ejecutivo(pruebas)
            st.markdown(section_divider(), unsafe_allow_html=True)

            st.markdown("#### Distribución de residuos")
            residuos = datos.get('residuos_ind')
            if residuos is not None and not residuos.empty:
                res_col = None
                for c in residuos.columns:
                    if 'residuo' in str(c).lower():
                        res_col = c
                        break
                if res_col:
                    vals = residuos[res_col].dropna().astype(float)
                    media, std = vals.mean(), vals.std()
                    st.plotly_chart(fig_histograma_residuos(vals, media, std), use_container_width=True)
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Media", f"{media:.4f}")
                    c2.metric("Desv. Std.", f"{std:.4f}")
                    c3.metric("Asimetría", f"{stats.skew(vals):.4f}")
                    c4.metric("Curtosis", f"{stats.kurtosis(vals):.4f}")
                    c5.metric("N", f"{len(vals)}")
            else:
                st.info("No hay datos de residuos.")

            st.markdown(section_divider(), unsafe_allow_html=True)

            st.markdown("#### Coeficientes del modelo")
            coefs = datos.get('coeficientes')
            if coefs is not None and not coefs.empty:
                df_coef = coefs.copy()
                df_coef['Tipo'] = df_coef['Variable'].apply(clasificar_variable)
                if 'P_value' in df_coef.columns:
                    def fmt_pval(x):
                        if pd.isna(x): return "N/A"
                        try:
                            xv = float(x)
                            return f"{xv:.4e}" if xv < 0.001 else f"{xv:.4f}"
                        except: return str(x)
                    df_coef['P-valor'] = df_coef['P_value'].apply(fmt_pval)
                df_coef = df_coef.rename(columns={'Variable': 'Lag'})
                df_display = df_coef[['Tipo', 'Lag', 'Coeficiente', 'P-valor']]
                st.plotly_chart(fig_barras_coeficientes(df_coef), use_container_width=True)
                def color_pval(v):
                    try: return f"color: {COLOR_GREEN}; font-weight: 600;" if float(v) < 0.05 else f"color: {COLOR_RED};"
                    except: return ""
                styler = df_display.style
                if hasattr(styler, "map"):
                    styler = styler.map(color_pval, subset=['P-valor'])
                else:
                    styler = styler.applymap(color_pval, subset=['P-valor'])
                st.dataframe(styler, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de coeficientes.")

        # --- Barra de navegación inferior ---
        st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="bottom-nav">
            <button class="bottom-nav-btn" {"disabled" if current_idx==0 else ""}
                onclick="window.parent.document.querySelector('button[key=\'btn_prev\']').click()">◀ Anterior</button>
            <div class="bottom-nav-info">
                <div>Modelo {current_idx + 1} de {len(modelos_list)}</div>
                <div class="bottom-nav-model">{st.session_state.modelo_seleccionado}</div>
            </div>
            <button class="bottom-nav-btn" {"disabled" if current_idx==len(modelos_list)-1 else ""}
                onclick="window.parent.document.querySelector('button[key=\'btn_next\']').click()">Siguiente ▶</button>
        </div>
        """, unsafe_allow_html=True)
