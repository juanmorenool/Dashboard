import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import json
import openpyxl

# =============================================================================
# PALETA CORPORATIVA BANCA — Sin emojis, sin colores chillones
# =============================================================================
NAVY    = "#0B2545"
BLUE    = "#1E5AA8"
GREEN   = "#1A6B3E"
RED     = "#B83232"
GRAY    = "#6C757D"
LTGRAY  = "#ADB5BD"
BG      = "#F8F9FA"
WHITE   = "#FFFFFF"
BORDER  = "#DEE2E6"
TEXT    = "#1A1D23"
MUTED   = "#5A6270"
TINT    = "#EDF2F7"

# Estados corporativos (sin emojis)
ESTADO_OK      = ("#E8F5E9", "#1A6B3E", "CUMPLE")
ESTADO_WARN    = ("#FFF8E1", "#B8860B", "REVISAR")
ESTADO_FAIL    = ("#FFEBEE", "#B83232", "NO CUMPLE")
ESTADO_NEUTRAL = ("#F5F5F5", "#5A6270", "N/A")

PAISES_MAP = {
    'colombia': 'Colombia',
    'panama': 'Panamá',
    'panamá': 'Panamá',
    'costa rica': 'Costa Rica',
}

CARTERAS_MAP = {
    'vivi': 'Vivienda', 'vivienda': 'Vivienda',
    'cons': 'Consumo', 'consumo': 'Consumo',
    'com': 'Comercial', 'comercial': 'Comercial',
    'micro': 'Microcrédito',
}

# =============================================================================
# CSS GLOBAL — Corporativo, limpio, sin emojis
# =============================================================================
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp, .stMarkdown, .stDataFrame, .stButton,
    .stSelectbox, .stTextInput, .stNumberInput, .stTabs {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ padding-top: 0.5rem; padding-bottom: 2rem; max-width: 1400px; }}
    .stApp {{ background-color: {BG}; }}

    /* Sidebar compacto */
    section[data-testid="stSidebar"] {{
        background-color: {WHITE}; border-right: 1px solid {BORDER};
        min-width: 260px !important; max-width: 260px !important;
    }}
    section[data-testid="stSidebar"] .block-container {{ padding: 16px; }}

    h1 {{ color: {NAVY} !important; font-weight: 700 !important; font-size: 22px !important; }}
    h2 {{ color: {NAVY} !important; font-weight: 600 !important; font-size: 16px !important; margin-top: 0.2rem !important; }}
    h3 {{ color: {NAVY} !important; font-weight: 600 !important; font-size: 14px !important;
         border-left: 3px solid {BLUE}; padding-left: 10px; margin-top: 0.3rem !important; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 2px; border-bottom: 1px solid {BORDER}; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent; border-radius: 6px 6px 0 0;
        padding: 8px 16px; color: {MUTED}; font-weight: 500; font-size: 13px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {TINT} !important; color: {NAVY} !important; font-weight: 600;
    }}

    /* Dataframes */
    div[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 6px; }}

    /* Sidebar sticky */
    section[data-testid="stSidebar"] {{ position: sticky; top: 0; height: 100vh; overflow-y: auto; }}

    /* Bottom nav */
    .bottom-bar {{
        position: fixed; bottom: 0; left: 260px; right: 0;
        background: {WHITE}; border-top: 1px solid {BORDER};
        padding: 0; z-index: 9999;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 -2px 12px rgba(0,0,0,0.04);
    }}
    .bottom-bar-inner {{
        display: flex; align-items: center; gap: 0;
        max-width: 600px; width: 100%;
    }}
    .nav-btn {{
        background: none; border: none; color: {BLUE}; font-weight: 600; font-size: 13px;
        padding: 14px 24px; cursor: pointer; letter-spacing: 0.3px;
        border-right: 1px solid {BORDER}; flex: 1; text-align: center;
        transition: background 0.15s;
    }}
    .nav-btn:hover {{ background: {TINT}; }}
    .nav-btn:disabled {{ color: {LTGRAY}; cursor: not-allowed; background: none; }}
    .nav-center {{
        padding: 10px 32px; text-align: center; flex: 2;
        border-right: 1px solid {BORDER};
    }}
    .nav-center-top {{ font-size: 12px; color: {MUTED}; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}
    .nav-center-bot {{ font-size: 14px; color: {NAVY}; font-weight: 700; margin-top: 2px; }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# COMPONENTES HTML CORPORATIVOS
# =============================================================================
def pill(text, color_bg, color_fg):
    return f'<span style="background:{color_bg};color:{color_fg};font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600;text-transform:uppercase;letter-spacing:0.4px;">{text}</span>'


def tag_ok():    return pill("CUMPLE", ESTADO_OK[0], ESTADO_OK[1])
def tag_warn():  return pill("REVISAR", ESTADO_WARN[0], ESTADO_WARN[1])
def tag_fail():  return pill("NO CUMPLE", ESTADO_FAIL[0], ESTADO_FAIL[1])
def tag_neutral(): return pill("N/A", ESTADO_NEUTRAL[0], ESTADO_NEUTRAL[1])


def card_kpi(title, value, subtitle="", accent=NAVY):
    sub = f'<p style="font-size:12px;color:{MUTED};margin:4px 0 0;line-height:1.3;">{subtitle}</p>' if subtitle else ''
    return f"""
    <div style="background:{WHITE};border:1px solid {BORDER};border-radius:8px;padding:14px 16px;height:100%;box-sizing:border-box;">
        <p style="font-size:10px;color:{LTGRAY};margin:0 0 6px;text-transform:uppercase;letter-spacing:0.6px;font-weight:600;">{title}</p>
        <p style="font-size:18px;font-weight:700;color:{accent};margin:0;line-height:1.2;">{value}</p>
        {sub}
    </div>
    """


def card_metric(label, value, color=TEXT):
    return f"""
    <div style="background:{WHITE};border:1px solid {BORDER};border-radius:6px;padding:12px 14px;">
        <p style="font-size:10px;color:{LTGRAY};margin:0 0 4px;text-transform:uppercase;letter-spacing:0.6px;font-weight:600;">{label}</p>
        <p style="font-size:20px;font-weight:700;color:{color};margin:0;">{value}</p>
    </div>
    """


def divider():
    return f"<div style='height:1px;background:{BORDER};margin:16px 0;'></div>"


def section_title(text):
    return f"<p style='font-size:13px;font-weight:700;color:{NAVY};margin:0 0 12px;text-transform:uppercase;letter-spacing:0.5px;'>{text}</p>"

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

        if 'Año' in col_map and 'Escenario' in col_map and 'Factor FWL' in col_map:
            idx_anual = [col_map['Año'][0], col_map['Escenario'][0], col_map['Factor FWL'][0]]
            df_anual = df_raw.iloc[2:, idx_anual].copy()
            df_anual.columns = ['Año', 'Escenario', 'Factor FWL']
            df_anual = df_anual.dropna(how='all').reset_index(drop=True)
            modelo['fwl_anual'] = df_anual
        else:
            modelo['fwl_anual'] = None

        if 'Obs' in col_map and 'Residuo' in col_map:
            idx_res = [col_map['Obs'][0], col_map['Residuo'][0]]
            df_res = df_raw.iloc[2:, idx_res].copy()
            df_res.columns = ['Obs', 'Residuo']
            df_res = df_res.dropna(how='all').reset_index(drop=True)
            modelo['residuos_ind'] = df_res
        else:
            modelo['residuos_ind'] = None

        if 'Estadistico' in col_map and 'Valor' in col_map:
            idx_est = col_map['Estadistico'][0]
            idx_val = col_map['Valor'][0]
            df_resumen = df_raw.iloc[2:, [idx_est, idx_val]].copy()
            df_resumen.columns = ['Estadistico', 'Valor']
            df_resumen = df_resumen.dropna(how='all').reset_index(drop=True)
            modelo['resumen_residuos'] = df_resumen
        else:
            modelo['resumen_residuos'] = None

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
        try: p_val = float(p_val)
        except: continue
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
            resultados.append((exog, None, "Sin datos"))
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
        font=dict(family="Inter, Arial, sans-serif", size=12, color=TEXT),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=40, l=10, r=10, b=10),
    )
    fig.update_xaxes(showgrid=True, gridcolor=BORDER, zeroline=False, linecolor=BORDER)
    fig.update_yaxes(showgrid=True, gridcolor=BORDER, zeroline=False, linecolor=BORDER)
    if fig.layout.title and fig.layout.title.text:
        fig.update_layout(title=dict(font=dict(size=14, color=NAVY)))
    return fig


def fig_predicciones(df_end, endogena_cols, exog_df, exog_sel, modelo_nombre):
    fig = go.Figure()
    fecha_col = 'fecha' if 'fecha' in df_end.columns else df_end.columns[0]
    for col in endogena_cols:
        if col not in df_end.columns:
            continue
        col_str = str(col).upper()
        if col_str == 'BASE':
            fig.add_trace(go.Scatter(x=df_end[fecha_col], y=df_end[col], mode='lines', name='Base', line=dict(color=BLUE, width=2)))
        elif col_str in ['ADVERSO', 'ADVERSA']:
            fig.add_trace(go.Scatter(x=df_end[fecha_col], y=df_end[col], mode='lines', name='Adverso', line=dict(color=RED, width=2, dash='dash')))
        elif col_str == 'OPTIMISTA':
            fig.add_trace(go.Scatter(x=df_end[fecha_col], y=df_end[col], mode='lines', name='Optimista', line=dict(color=GREEN, width=2, dash='dot')))
    if exog_df is not None and exog_sel:
        for ex in exog_sel:
            for suffix in ['_BASE', '_ADVERSO', '_OPTIMISTA']:
                col_name = ex + suffix
                if col_name in exog_df.columns:
                    x_vals = exog_df[fecha_col] if fecha_col in exog_df.columns else exog_df.index
                    fig.add_trace(go.Scatter(x=x_vals, y=exog_df[col_name], mode='lines', name=f'{ex}{suffix}', line=dict(width=1.2), yaxis='y2'))
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
            fig.add_trace(go.Scatter(x=df_fwl[fecha_col], y=df_fwl[col], mode='lines', name='Base', line=dict(color=BLUE, width=2)))
        elif 'FWL_ADVERSO' in col_str or 'FWL_ADVERSA' in col_str:
            fig.add_trace(go.Scatter(x=df_fwl[fecha_col], y=df_fwl[col], mode='lines', name='Adverso', line=dict(color=RED, width=2, dash='dash')))
        elif 'FWL_OPTIMISTA' in col_str:
            fig.add_trace(go.Scatter(x=df_fwl[fecha_col], y=df_fwl[col], mode='lines', name='Optimista', line=dict(color=GREEN, width=2, dash='dot')))
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
                              fill='tozeroy', line=dict(color=BLUE, width=2), fillcolor='rgba(30,90,168,0.10)'))
    fig.update_layout(title="Factor FWL Ponderado", xaxis_title="Fecha", yaxis_title="FWL Ponderado")
    return aplicar_tema_plotly(fig)


def fig_histograma_residuos(vals, media, std):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=vals, nbinsx=20, marker_color=BLUE, opacity=0.7, name='Residuos'))
    x_norm, y_norm = generar_campana_normal(vals, media, std)
    if len(x_norm) > 0:
        bin_width = (vals.max() - vals.min()) / 20 if vals.max() != vals.min() else 1
        y_norm_scaled = y_norm * len(vals) * bin_width
        fig.add_trace(go.Scatter(x=x_norm, y=y_norm_scaled, mode='lines', name='Normal teórica', line=dict(color=RED, width=2)))
    fig.update_layout(xaxis_title="Residuos", yaxis_title="Frecuencia")
    return aplicar_tema_plotly(fig)


def fig_barras_coeficientes(df_coef):
    df = df_coef.copy()
    df['abs'] = df['Coeficiente'].abs()
    df = df.sort_values('abs', ascending=True)
    colors = [GREEN if c >= 0 else RED for c in df['Coeficiente']]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df['Variable'], x=df['Coeficiente'], orientation='h', marker_color=colors,
                          text=df['Coeficiente'].round(4), textposition='outside'))
    fig.update_layout(title="Coeficientes del Modelo", xaxis_title="Valor", yaxis_title="Variable", showlegend=False)
    return aplicar_tema_plotly(fig)


# =============================================================================
# DIAGNOSTICOS — Corporativo, sin emojis, sin expanders
# =============================================================================
def limpiar_nombre_prueba(nombre):
    nl = str(nombre).lower()
    if 'arch' in nl: return "Heterocedasticidad"
    if 'ljung' in nl or 'box' in nl: return "Ljung-Box"
    if 'jarque' in nl or 'bera' in nl: return "Jarque-Bera"
    return str(nombre)


def evaluar_prueba(prueba, p_val):
    if pd.isna(p_val):
        return "N/A", ESTADO_NEUTRAL
    try: p_val = float(p_val)
    except: return "N/A", ESTADO_NEUTRAL
    pl = str(prueba).lower()
    if 'jarque' in pl or 'bera' in pl:
        if p_val < 0.05: return "NO CUMPLE", ESTADO_FAIL
        elif p_val < 0.10: return "REVISAR", ESTADO_WARN
        else: return "CUMPLE", ESTADO_OK
    if p_val > 0.05: return "CUMPLE", ESTADO_OK
    elif p_val > 0.01: return "REVISAR", ESTADO_WARN
    else: return "NO CUMPLE", ESTADO_FAIL


def render_diagnosticos_corporativo(pruebas_df):
    """Tabla ejecutiva + detalle técnico en la misma vista, sin expanders."""
    if pruebas_df is None or pruebas_df.empty:
        st.info("No hay datos de pruebas estadísticas.")
        return

    df = pruebas_df.copy()
    df['Prueba'] = df['Prueba'].apply(limpiar_nombre_prueba)

    # --- RESUMEN EJECUTIVO: tarjetas horizontales ---
    st.markdown(section_title("Resumen de Diagnósticos"), unsafe_allow_html=True)
    filas = []
    for _, row in df.iterrows():
        prueba = row['Prueba']
        p_val = row['P_value']
        estado, (bg, fg, label) = evaluar_prueba(prueba, p_val)
        filas.append({
            'Diagnóstico': prueba,
            'Estado': label,
            'Color': fg,
            'Bg': bg,
            'P-valor': p_val,
            'Estadístico': row.get('Estadistico', '—'),
        })

    cols = st.columns(len(filas))
    for i, f in enumerate(filas):
        with cols[i]:
            st.markdown(f"""
            <div style="background:{f['Bg']};border:1px solid {BORDER};border-radius:6px;padding:16px;text-align:center;">
                <p style="font-size:10px;color:{LTGRAY};margin:0 0 6px;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">{f['Diagnóstico']}</p>
                <p style="font-size:16px;font-weight:700;color:{f['Color']};margin:0;">{f['Estado']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # --- DETALLE TÉCNICO: tabla limpia, visible siempre ---
    st.markdown(section_title("Detalle Técnico"), unsafe_allow_html=True)
    df_tec = pd.DataFrame(filas)[['Diagnóstico', 'Estadístico', 'P-valor', 'Estado']]

    def fmt_p(v):
        try:
            if pd.isna(v): return "—"
            vf = float(v)
            return f"{vf:.4f}" if vf >= 0.001 else f"{vf:.2e}"
        except: return str(v)

    df_tec['P-valor'] = df_tec['P-valor'].apply(fmt_p)
    df_tec['Estadístico'] = df_tec['Estadístico'].apply(fmt_p)

    def color_estado(val):
        if val == "CUMPLE": return f"color: {GREEN}; font-weight: 700;"
        elif val == "NO CUMPLE": return f"color: {RED}; font-weight: 700;"
        elif val == "REVISAR": return f"color: #B8860B; font-weight: 700;"
        return ""

    styler = df_tec.style
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
        if pd.isna(p_val): continue
        try: p_val = float(p_val)
        except: continue
        if 'ljung' in prueba or 'box' in prueba: lb_p = p_val
        elif 'jarque' in prueba or 'bera' in prueba: jb_p = p_val
        elif 'hetero' in prueba or 'arch' in prueba: het_p = p_val

    c1, c2, c3 = st.columns(3)
    with c1:
        val = f"{lb_p:.4f}" if lb_p is not None else "—"
        color = GREEN if lb_p is not None and lb_p > 0.05 else RED
        st.markdown(card_metric("Ljung-Box (p-valor)", val, color), unsafe_allow_html=True)
    with c2:
        val = f"{jb_p:.4f}" if jb_p is not None else "—"
        color = RED if jb_p is not None and jb_p < 0.05 else GREEN
        st.markdown(card_metric("Jarque-Bera (p-valor)", val, color), unsafe_allow_html=True)
    with c3:
        val = f"{het_p:.4f}" if het_p is not None else "—"
        color = GREEN if het_p is not None and het_p > 0.05 else RED
        st.markdown(card_metric("Heterocedasticidad (p-valor)", val, color), unsafe_allow_html=True)


def construir_opciones_modelos():
    """Construye la lista de modelos ordenada segun el criterio activo y el
    diccionario de pruebas aprobadas. Es la UNICA fuente de orden: tanto el
    selectbox del sidebar como las flechas de navegacion la usan, para que
    nunca queden desincronizados."""
    criterio = st.session_state.get("criterio_ordenamiento", "Pruebas aprobadas ↓")
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
    return modelos_list, pruebas_dict


def label_modelo(nombre, pruebas_dict):
    apr, tot = pruebas_dict.get(nombre, (0, 3))
    return f"{nombre}  ({apr}/{tot})"


# =============================================================================
# SESSION STATE
# =============================================================================
for key, default in [
    ("uploaded_file", None), ("modelos_data", {}), ("meta_contexto", None),
    ("modelo_seleccionado", None), ("criterio_ordenamiento", "Pruebas aprobadas ↓"),
    ("exog_sel", {}), ("pred_filtro", "Todas"), ("nav_sticky", True),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =============================================================================
# APP
# =============================================================================
st.set_page_config(page_title="Dashboard SARIMAX", layout="wide")
inject_css()

col_left, col_right = st.columns([1, 4])

# =========================================================================
# SIDEBAR
# =========================================================================
with col_left:
    st.markdown(f"<p style='font-size:12px;font-weight:700;color:{NAVY};margin:0 0 10px;letter-spacing:0.5px;'>CARGAR MODELO</p>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Archivo Excel (.xlsx)", type=["xlsx"], label_visibility="collapsed")
    if uploaded is not None:
        st.session_state.uploaded_file = uploaded
        if not st.session_state.modelos_data or uploaded.name != getattr(st.session_state, 'last_file_name', None):
            with st.spinner("Parseando modelos..."):
                st.session_state.modelos_data = parsear_excel(uploaded)
                st.session_state.meta_contexto = leer_meta_embebida(uploaded)
                st.session_state.last_file_name = uploaded.name
            st.success(f"Archivo cargado: {uploaded.name}")
            if st.session_state.modelo_seleccionado is None or st.session_state.modelo_seleccionado not in st.session_state.modelos_data:
                st.session_state.modelo_seleccionado = list(st.session_state.modelos_data.keys())[0]

    if st.session_state.uploaded_file is not None:
        if st.button("Eliminar archivo", key="btn_eliminar", use_container_width=True):
            st.session_state.uploaded_file = None
            st.session_state.modelos_data = {}
            st.session_state.meta_contexto = None
            st.session_state.modelo_seleccionado = None
            st.session_state.last_file_name = None
            st.session_state.exog_sel = {}
            st.rerun()

    if st.session_state.modelos_data:
        st.markdown(divider(), unsafe_allow_html=True)

        meta = st.session_state.meta_contexto
        if meta:
            meta_kpis = extraer_kpis_meta(meta)
            st.markdown(section_title("Contexto de la corrida"), unsafe_allow_html=True)

            # Tarjetas metadata en grid 2x3, sin texto cortado
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(card_kpi("Pais", meta_kpis.get('pais', '—')), unsafe_allow_html=True)
            with c2:
                st.markdown(card_kpi("Ventana media movil", meta_kpis.get('ventana_mm', '—')), unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(card_kpi("Cartera", meta_kpis.get('cartera', '—'), accent=BLUE), unsafe_allow_html=True)
            with c2:
                fwl_range = f"{meta_kpis.get('fwl_min', '?')} – {meta_kpis.get('fwl_max', '?')}"
                st.markdown(card_kpi("Rango FWL", fwl_range, accent=GREEN), unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(card_kpi("Modo endogena", meta_kpis.get('modo_endogena', '—')), unsafe_allow_html=True)
            with c2:
                st.markdown(card_kpi("Top exportados", meta_kpis.get('top_exportar', '—')), unsafe_allow_html=True)
        else:
            st.caption("Sin metadata embebida.")

        st.markdown(divider(), unsafe_allow_html=True)

        criterio = st.radio("Ordenar por:", ["Nombre (A-Z)", "Pruebas aprobadas ↓", "Pruebas aprobadas ↑"],
                            index=1, key="criterio_orden")
        st.session_state.criterio_ordenamiento = criterio

        modelos_list, pruebas_dict = construir_opciones_modelos()

        opciones = [label_modelo(m, pruebas_dict) for m in modelos_list]
        idx = modelos_list.index(st.session_state.modelo_seleccionado) if st.session_state.modelo_seleccionado in modelos_list else 0
        seleccion = st.selectbox("Modelo", opciones, index=idx, key="sel_modelo")
        st.session_state.modelo_seleccionado = seleccion.split("  (")[0]

        st.markdown(divider(), unsafe_allow_html=True)
        st.toggle("Fijar flechas de navegacion", key="nav_sticky",
                  help="Mantiene los botones Anterior/Siguiente siempre visibles, flotando sobre la pagina al hacer scroll.")

        datos = st.session_state.modelos_data.get(st.session_state.modelo_seleccionado, {})
        st.markdown(f"<p style='font-size:11px;font-weight:600;color:{NAVY};margin:12px 0 4px;'>MODELO ACTUAL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:14px;font-weight:700;color:{NAVY};margin:0;'>{st.session_state.modelo_seleccionado}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:11px;color:{MUTED};margin:4px 0 0;'>{datos.get('observaciones', 0)} observaciones</p>", unsafe_allow_html=True)

        exogenas = datos.get('exogenas_nombres', [])
        if exogenas:
            st.markdown(f"<p style='font-size:11px;font-weight:600;color:{NAVY};margin:12px 0 6px;'>EXOGENAS</p>", unsafe_allow_html=True)
            coefs = datos.get('coeficientes')
            sigs = obtener_significancia_exogenas(coefs, exogenas)
            sig_count = sum(1 for _, _, s in sigs if s == "Significativa")
            st.markdown(f"<p style='font-size:10px;color:{MUTED};margin:0 0 6px;'>{sig_count} de {len(exogenas)} significativas</p>", unsafe_allow_html=True)
            for ex, pval, status in sigs:
                color = GREEN if status == "Significativa" else (RED if status == "No significativa" else "#B8860B")
                label = "SIG" if status == "Significativa" else ("NO SIG" if status == "No significativa" else "MARG")
                p_txt = f"p={pval:.3f}" if pval is not None else "p=N/A"
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:2px 0;font-size:11px;"><span style="color:{TEXT}">{ex}</span><span style="color:{color};font-weight:600;">{label} ({p_txt})</span></div>', unsafe_allow_html=True)

# =========================================================================
# PANEL PRINCIPAL
# =========================================================================
with col_right:
    if not st.session_state.modelos_data:
        st.markdown(f"""
        <div style="background:{WHITE};border:1px solid {BORDER};border-radius:10px;padding:60px 32px;text-align:center;margin-top:40px;">
            <p style="font-size:18px;font-weight:700;color:{NAVY};margin:0 0 8px;">Dashboard SARIMAX</p>
            <p style="font-size:13px;color:{MUTED};margin:0;">Suba un archivo Excel para comenzar el analisis.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        datos = st.session_state.modelos_data.get(st.session_state.modelo_seleccionado, {})
        meta_kpis = extraer_kpis_meta(st.session_state.meta_contexto)

        # --- Header ejecutivo ---
        pais = meta_kpis.get('pais', '—')
        cartera = meta_kpis.get('cartera', '—')
        st.markdown(f"""
        <div style="display:flex;align-items:flex-end;gap:16px;margin-bottom:4px;">
            <div style="flex:1;">
                <p style="font-size:11px;color:{MUTED};margin:0;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">Modelo seleccionado</p>
                <p style="font-size:20px;font-weight:700;color:{NAVY};margin:4px 0 0;">{st.session_state.modelo_seleccionado}</p>
            </div>
            <div style="text-align:right;">
                <p style="font-size:11px;color:{MUTED};margin:0;">{pais} · {cartera}</p>
                <p style="font-size:11px;color:{LTGRAY};margin:2px 0 0;">{len(st.session_state.modelos_data)} modelos cargados</p>
            </div>
        </div>
        <div style="height:1px;background:{BORDER};margin:12px 0 16px;"></div>
        """, unsafe_allow_html=True)

        # --- Navegacion (botones reales, no JS) ---
        modelos_list, pruebas_dict_nav = construir_opciones_modelos()
        current_idx = modelos_list.index(st.session_state.modelo_seleccionado)

        tab1, tab2, tab3 = st.tabs(["Visualizacion", "Predicciones", "Diagnosticos"])

        # =====================================================================
        # TAB 1: VISUALIZACION
        # =====================================================================
        with tab1:
            st.markdown(section_title("Exogenas activas"), unsafe_allow_html=True)
            exogenas = datos.get('exogenas_nombres', [])
            modelo_key = st.session_state.modelo_seleccionado
            if modelo_key not in st.session_state.exog_sel:
                st.session_state.exog_sel[modelo_key] = []
            if exogenas:
                n_cols = min(len(exogenas), 6)
                chip_cols = st.columns(n_cols)
                for i, ex in enumerate(exogenas):
                    with chip_cols[i % n_cols]:
                        activo = ex in st.session_state.exog_sel[modelo_key]
                        label = f"[x] {ex}" if activo else f"[ ] {ex}"
                        if st.button(label, key=f"chip_{modelo_key}_{ex}", use_container_width=True):
                            if activo:
                                st.session_state.exog_sel[modelo_key].remove(ex)
                            else:
                                st.session_state.exog_sel[modelo_key].append(ex)
                            st.rerun()
            else:
                st.caption("Sin exogenas en este modelo.")

            df_end = datos.get('fecha_endogena')
            endogena_cols = datos.get('endogenas_cols', [])
            if df_end is not None and not df_end.empty and endogena_cols:
                fig = fig_predicciones(df_end, endogena_cols, datos.get('exogenas'), st.session_state.exog_sel.get(modelo_key, []), st.session_state.modelo_seleccionado)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de predicciones.")

            st.markdown(divider(), unsafe_allow_html=True)

            st.markdown(section_title("Factor FWL por ano y escenario"), unsafe_allow_html=True)
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
                st.info("No hay datos de Factor FWL por Ano.")

            st.markdown(divider(), unsafe_allow_html=True)

            st.markdown(section_title("Factor FWL a 12 meses"), unsafe_allow_html=True)
            df_fwl = datos.get('fwl_12m')
            if df_fwl is not None and not df_fwl.empty:
                st.plotly_chart(fig_fwl_12m(df_fwl), use_container_width=True)
            else:
                st.info("No hay datos de FWL a 12 meses.")

            st.markdown(divider(), unsafe_allow_html=True)

            st.markdown(section_title("Factor FWL ponderado"), unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: peso_base = st.number_input("Peso Base", 0.0, 1.0, 0.33, 0.01, key="pw_base")
            with c2: peso_adverso = st.number_input("Peso Adverso", 0.0, 1.0, 0.33, 0.01, key="pw_adv")
            with c3: peso_optimista = st.number_input("Peso Optimista", 0.0, 1.0, 0.34, 0.01, key="pw_opt")

            suma = peso_base + peso_adverso + peso_optimista
            if abs(suma - 1.0) < 0.001:
                st.markdown(pill("VALIDO", "#E8F5E9", GREEN), unsafe_allow_html=True)
            elif suma < 1.0:
                st.markdown(pill(f"{1.0-suma:.2f} DISPONIBLE", "#FFF8E1", "#B8860B"), unsafe_allow_html=True)
            else:
                st.markdown(pill(f"EXCEDE {suma-1.0:.2f}", "#FFEBEE", RED), unsafe_allow_html=True)

            if df_fwl is not None and not df_fwl.empty and suma <= 1.0:
                pesos = {'base': peso_base, 'adverso': peso_adverso, 'optimista': peso_optimista}
                df_pond = calcular_fwl_ponderado(df_fwl, pesos)
                if df_pond is not None:
                    res = resumen_fwl(df_pond)
                    if res:
                        c1, c2, c3, c4 = st.columns(4)
                        with c1: st.markdown(card_metric("Promedio", f"{res.get('promedio', 0):.4f}", BLUE), unsafe_allow_html=True)
                        with c2: st.markdown(card_metric("Maximo", f"{res.get('maximo', 0):.4f}", GREEN), unsafe_allow_html=True)
                        with c3: st.markdown(card_metric("Minimo", f"{res.get('minimo', 0):.4f}", RED), unsafe_allow_html=True)
                        with c4: st.markdown(card_metric("Volatilidad (s)", f"{res.get('volatilidad', 0):.4f}", GRAY), unsafe_allow_html=True)
                    st.plotly_chart(fig_fwl_ponderado(df_pond), use_container_width=True)
                else:
                    st.info("No se pudo calcular el FWL ponderado.")
            elif suma > 1.0:
                st.warning("Ajuste los pesos para que la suma no exceda 1.0")

        # =====================================================================
        # TAB 2: PREDICCIONES
        # =====================================================================
        with tab2:
            st.markdown(section_title("Datos de prediccion"), unsafe_allow_html=True)
            filtros = st.columns(4)
            with filtros[0]:
                if st.button("Ver Base", use_container_width=True): st.session_state.pred_filtro = "Base"
            with filtros[1]:
                if st.button("Ver Adverso", use_container_width=True): st.session_state.pred_filtro = "Adverso"
            with filtros[2]:
                if st.button("Ver Optimista", use_container_width=True): st.session_state.pred_filtro = "Optimista"
            with filtros[3]:
                if st.button("Ver todas", use_container_width=True): st.session_state.pred_filtro = "Todas"

            st.markdown(f"<p style='font-size:11px;color:{MUTED};margin:8px 0;'>Filtro activo: <b>{st.session_state.pred_filtro}</b></p>", unsafe_allow_html=True)

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
                st.download_button("Descargar CSV", csv, f"predicciones_{st.session_state.modelo_seleccionado}.csv", "text/csv")
            else:
                st.info("No hay datos de predicciones.")

        # =====================================================================
        # TAB 3: DIAGNOSTICOS
        # =====================================================================
        with tab3:
            pruebas = datos.get('pruebas')
            render_metricas_diagnostico(pruebas)
            st.markdown(divider(), unsafe_allow_html=True)
            render_diagnosticos_corporativo(pruebas)
            st.markdown(divider(), unsafe_allow_html=True)

            st.markdown(section_title("Distribucion de residuos"), unsafe_allow_html=True)
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

                    # Estadisticas en cards horizontales, no st.metric apretadas
                    st.markdown(section_title("Estadisticas descriptivas"), unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns(5)
                    with c1: st.markdown(card_metric("Media", f"{media:.4f}"), unsafe_allow_html=True)
                    with c2: st.markdown(card_metric("Desv. Std.", f"{std:.4f}"), unsafe_allow_html=True)
                    with c3: st.markdown(card_metric("Asimetria", f"{stats.skew(vals):.4f}"), unsafe_allow_html=True)
                    with c4: st.markdown(card_metric("Curtosis", f"{stats.kurtosis(vals):.4f}"), unsafe_allow_html=True)
                    with c5: st.markdown(card_metric("Observaciones", f"{len(vals)}"), unsafe_allow_html=True)
            else:
                st.info("No hay datos de residuos.")

            st.markdown(divider(), unsafe_allow_html=True)

            st.markdown(section_title("Coeficientes del modelo"), unsafe_allow_html=True)
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
                df_coef = df_coef.rename(columns={'Variable': 'Variable'})
                df_display = df_coef[['Tipo', 'Variable', 'Coeficiente', 'P-valor']]
                st.plotly_chart(fig_barras_coeficientes(df_coef), use_container_width=True)
                def color_pval(v):
                    try: return f"color: {GREEN}; font-weight: 700;" if float(v) < 0.05 else f"color: {RED};"
                    except: return ""
                styler = df_display.style
                if hasattr(styler, "map"):
                    styler = styler.map(color_pval, subset=['P-valor'])
                else:
                    styler = styler.applymap(color_pval, subset=['P-valor'])
                st.dataframe(styler, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de coeficientes.")

        # --- Bottom nav bar (flechas), sticky opcional via switch en el sidebar ---
        nav_sticky = st.session_state.get("nav_sticky", True)

        if nav_sticky:
            st.markdown(f"""
            <style>
            div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div.st-key-nav_flechas),
            .st-key-nav_flechas {{
                position: fixed !important;
                bottom: 22px;
                left: 50%;
                transform: translateX(-46%);
                z-index: 9999;
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 14px;
                box-shadow: 0 8px 28px rgba(11,37,69,0.16);
                padding: 6px 10px !important;
                width: auto !important;
                max-width: 560px;
            }}
            .block-container {{ padding-bottom: 120px !important; }}
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

        with st.container(key="nav_flechas"):
            nav_cols = st.columns([1, 2, 1])
            with nav_cols[0]:
                if st.button("← Anterior", disabled=current_idx == 0, key="btn_prev_real", use_container_width=True):
                    nuevo = modelos_list[current_idx - 1]
                    st.session_state.modelo_seleccionado = nuevo
                    st.session_state.sel_modelo = label_modelo(nuevo, pruebas_dict_nav)
                    st.rerun()
            with nav_cols[1]:
                st.markdown(f"""
                <div style="text-align:center;padding:6px 4px;">
                    <p style="font-size:10px;color:{MUTED};margin:0;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">Modelo {current_idx + 1} de {len(modelos_list)}</p>
                    <p style="font-size:13px;color:{NAVY};font-weight:700;margin:2px 0 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{st.session_state.modelo_seleccionado}</p>
                </div>
                """, unsafe_allow_html=True)
            with nav_cols[2]:
                if st.button("Siguiente →", disabled=current_idx == len(modelos_list) - 1, key="btn_next_real", use_container_width=True):
                    nuevo = modelos_list[current_idx + 1]
                    st.session_state.modelo_seleccionado = nuevo
                    st.session_state.sel_modelo = label_modelo(nuevo, pruebas_dict_nav)
                    st.rerun()
