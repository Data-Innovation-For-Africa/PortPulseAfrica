"""
Africa Maritime Ports Intelligence Dashboard
============================================
Upload any Daily_Ports_Data.csv → African data is auto-extracted → Dashboard updates instantly.
"""

import io
import os
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PortPulseAfrica — Maritime Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
AFRICAN_COUNTRIES = [
    # ── 54 African Union Member States ───────────────────────────────────────
    # North Africa (7)
    "Algeria", "Egypt", "Libya", "Morocco", "Tunisia", "Sudan", "Mauritania",
    # West Africa (15)
    "Benin", "Burkina Faso", "Cabo Verde", "Côte d'Ivoire", "The Gambia",
    "Ghana", "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Niger",
    "Nigeria", "Senegal", "Sierra Leone", "Togo",
    # East Africa (17)
    "Burundi", "Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya",
    "Madagascar", "Mauritius", "Mozambique", "Rwanda", "Seychelles",
    "Somalia", "South Sudan", "Tanzania", "Uganda",
    # Central Africa (8)
    "Cameroon", "Central African Republic", "Chad",
    "Democratic Republic of the Congo", "Equatorial Guinea", "Gabon",
    "Republic of Congo", "São Tomé and Príncipe",
    # Southern Africa (9)
    "Angola", "Botswana", "Eswatini", "Lesotho", "Malawi",
    "Namibia", "South Africa", "Zambia", "Zimbabwe",
    # ── French territories with maritime data (bonus coverage) ───────────────
    "Mayotte", "Réunion",
]

COUNTRY_COORDS = {
    "Algeria": (28.03, 1.66), "Angola": (-11.20, 17.87),
    "Benin": (9.31, 2.32), "Botswana": (-22.33, 24.68),
    "Burkina Faso": (12.36, -1.53), "Burundi": (-3.37, 29.92),
    "Cabo Verde": (16.00, -24.01), "Cameroon": (3.85, 11.50),
    "Central African Republic": (6.61, 20.94), "Chad": (15.45, 18.73),
    "Comoros": (-11.65, 43.33), "Côte d'Ivoire": (7.54, -5.55),
    "Democratic Republic of the Congo": (-4.04, 21.76),
    "Djibouti": (11.83, 42.59), "Egypt": (26.82, 30.80),
    "Equatorial Guinea": (1.65, 10.27), "Eritrea": (15.18, 39.78),
    "Eswatini": (-26.52, 31.46), "Ethiopia": (9.14, 40.49),
    "Gabon": (-0.80, 11.61), "Ghana": (7.95, -1.02),
    "Guinea": (9.95, -11.49), "Guinea-Bissau": (11.80, -15.18),
    "Kenya": (-0.02, 37.91), "Lesotho": (-29.61, 28.23),
    "Liberia": (6.43, -9.43), "Libya": (26.34, 17.23),
    "Madagascar": (-18.77, 46.87), "Malawi": (-13.25, 34.30),
    "Mali": (17.57, -3.99), "Mauritania": (21.01, -10.94),
    "Mauritius": (-20.35, 57.55), "Mayotte": (-12.83, 45.17),
    "Morocco": (31.79, -7.09), "Mozambique": (-18.67, 35.53),
    "Namibia": (-22.96, 18.49), "Niger": (17.61, 8.08),
    "Nigeria": (9.08, 8.68), "Republic of Congo": (-0.23, 15.83),
    "Réunion": (-21.12, 55.54), "Rwanda": (-1.94, 29.87),
    "São Tomé and Príncipe": (0.19, 6.61), "Senegal": (14.50, -14.45),
    "Seychelles": (-4.68, 55.49), "Sierra Leone": (8.46, -11.78),
    "Somalia": (5.15, 46.20), "South Africa": (-30.56, 22.94),
    "South Sudan": (6.88, 31.31), "Sudan": (12.86, 30.22),
    "Tanzania": (-6.37, 34.89), "The Gambia": (13.44, -15.31),
    "Togo": (8.62, 0.82), "Tunisia": (33.89, 9.54),
    "Uganda": (1.37, 32.29), "Zambia": (-13.13, 27.85),
    "Zimbabwe": (-19.02, 29.15),
}

PORT_COORDS = {
    "Durban": (-29.87, 31.04), "Cape Town": (-33.91, 18.42),
    "Port Elizabeth": (-33.96, 25.62), "Richard's Bay": (-28.78, 32.09),
    "Alexandria": (31.20, 29.89), "El Dekheila": (31.12, 29.81),
    "El Sokhna": (29.95, 32.55), "Port Said": (31.26, 32.30),
    "Suez": (29.97, 32.55), "Damietta": (31.42, 31.80),
    "Casablanca": (33.59, -7.62), "Tangier-Mediterranean": (35.86, -5.46),
    "Jorf Lasfar": (33.12, -8.63), "Agadir": (30.43, -9.62),
    "Nador": (35.28, -2.94),
    "Lagos-Apapa-Tin Can Island": (6.44, 3.36), "Onne": (4.71, 7.15),
    "Warri": (5.52, 5.76), "Bonny Island": (4.44, 7.16),
    "Abidjan": (5.30, -4.01), "San Pedro": (4.75, -6.62),
    "Tema": (5.64, -0.01), "Takoradi": (4.88, -1.75),
    "Mombasa": (-4.04, 39.67), "Djibouti": (11.59, 43.15),
    "Berbera": (10.44, 45.01), "Mogadishu": (2.04, 45.34),
    "Dar es Salaam": (-6.82, 39.29), "Zanzibar": (-6.16, 39.19),
    "Maputo": (-25.97, 32.58), "Beira": (-19.84, 34.84),
    "Nacala": (-14.54, 40.68), "Luanda": (-8.84, 13.23),
    "Lobito": (-12.34, 13.54), "Walvis Bay": (-22.96, 14.51),
    "Toamasina": (-18.15, 49.40), "Mahajanga": (-15.72, 46.32),
    "Tunis-La Goulette": (36.82, 10.31), "Sfax": (34.74, 10.76),
    "Rades": (36.77, 10.27), "Tripoli": (32.90, 13.18),
    "Misratah": (32.38, 15.06), "Benghazi": (32.11, 20.07),
    "Annaba": (36.90, 7.77), "Algiers": (36.78, 3.05),
    "Oran": (35.71, -0.63), "Arzew": (35.84, 0.31),
    "Dakar": (14.69, -17.44), "Banjul": (13.45, -16.58),
    "Conakry": (9.53, -13.68), "Freetown": (8.49, -13.23),
    "Monrovia": (6.30, -10.80), "Abidjan": (5.30, -4.01),
    "Lomé": (6.13, 1.22), "Cotonou": (6.37, 2.43),
    "Douala": (3.87, 9.74), "Kribi": (2.94, 9.91),
    "Libreville": (0.39, 9.45), "Port-Gentil": (-0.72, 8.79),
    "Malabo": (3.75, 8.78), "Pointe-Noire": (-4.79, 11.86),
    "Matadi": (-5.83, 13.46), "Mombasa": (-4.04, 39.67),
    "Nacala": (-14.54, 40.68), "Port Sudan": (19.61, 37.22),
    "Massawa": (15.61, 39.47), "Assab": (13.00, 42.73),
    "Banjul": (13.45, -16.58), "Victoria": (-4.62, 55.45),
    "Port Louis": (-20.16, 57.50), "Toamasina": (-18.15, 49.40),
}

CARGO_TYPES = {
    "container": "🏗️ Container",
    "dry_bulk": "⛏️ Dry Bulk",
    "general_cargo": "📦 General Cargo",
    "roro": "🚗 RoRo",
    "tanker": "🛢️ Tanker",
}

COLORS = {
    "primary": "#00D4FF",
    "secondary": "#FF6B35",
    "accent": "#7B2FBE",
    "success": "#00C896",
    "warning": "#FFB800",
    "bg_dark": "#0D1117",
    "bg_card": "#161B22",
    "text": "#E6EDF3",
    "muted": "#8B949E",
}

PALETTE = ["#00D4FF", "#FF6B35", "#7B2FBE", "#00C896", "#FFB800",
           "#FF4757", "#2ED573", "#1E90FF", "#FF6348", "#ECCC68"]

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0D1117;
    color: #E6EDF3;
  }
  .main { background-color: #0D1117; }
  .block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 1600px; }
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1117 0%, #161B22 100%);
    border-right: 1px solid #21262D;
  }
  .stSelectbox > div, .stMultiSelect > div {
    background-color: #21262D; border: 1px solid #30363D;
  }

  /* KPI Cards */
  .kpi-card {
    background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
    border: 1px solid #21262D;
    border-radius: 16px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: transform .2s, box-shadow .2s;
  }
  .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,212,255,0.15); }
  .kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
  }
  .kpi-card.blue::before  { background: linear-gradient(90deg,#00D4FF,#0080FF); }
  .kpi-card.orange::before{ background: linear-gradient(90deg,#FF6B35,#FF4757); }
  .kpi-card.purple::before{ background: linear-gradient(90deg,#7B2FBE,#A855F7); }
  .kpi-card.green::before { background: linear-gradient(90deg,#00C896,#00E5CC); }
  .kpi-card.yellow::before{ background: linear-gradient(90deg,#FFB800,#FFCF63); }

  .kpi-label  { font-size:12px; font-weight:600; color:#8B949E; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }
  .kpi-value  { font-size:32px; font-weight:800; color:#E6EDF3; line-height:1.1; }
  .kpi-delta  { font-size:12px; margin-top:6px; }
  .kpi-icon   { font-size:28px; position:absolute; right:20px; top:20px; opacity:.7; }
  .kpi-sub    { font-size:11px; color:#8B949E; margin-top:4px; }

  .delta-up   { color:#00C896; }
  .delta-down { color:#FF4757; }
  .delta-flat { color:#8B949E; }

  /* Section headers */
  .section-header {
    font-size:18px; font-weight:700; color:#E6EDF3;
    border-left: 4px solid #00D4FF; padding-left:12px;
    margin: 24px 0 16px 0;
  }

  /* Insight boxes */
  .insight-box {
    background: linear-gradient(135deg,#161B22,#1C2128);
    border:1px solid #21262D; border-radius:12px;
    padding:16px 20px; margin-bottom:10px;
  }
  .insight-title { font-size:13px; font-weight:700; color:#00D4FF; margin-bottom:6px; }
  .insight-text  { font-size:12px; color:#C9D1D9; line-height:1.6; }

  /* Upload zone */
  .upload-zone {
    background: linear-gradient(135deg,#161B22,#1C2128);
    border: 2px dashed #30363D; border-radius:16px;
    padding:32px; text-align:center; margin-bottom:20px;
  }
  .upload-title { font-size:22px; font-weight:700; color:#00D4FF; margin-bottom:8px; }
  .upload-sub   { font-size:14px; color:#8B949E; }

  /* Hero */
  .hero {
    background: linear-gradient(135deg,#0D1117 0%,#161B22 50%,#1C2128 100%);
    border: 1px solid #21262D; border-radius:20px;
    padding:32px 40px; margin-bottom:28px;
    position:relative; overflow:hidden;
  }
  .hero::after {
    content:'';
    position:absolute; top:-60px; right:-60px;
    width:200px; height:200px; border-radius:50%;
    background: radial-gradient(circle,rgba(0,212,255,0.08),transparent 70%);
  }
  .hero h1 { font-size:2rem; font-weight:800; color:#E6EDF3; margin:0 0 6px 0; }
  .hero p  { font-size:15px; color:#8B949E; margin:0; }
  .hero-badge {
    display:inline-block; background:rgba(0,212,255,0.1);
    border:1px solid rgba(0,212,255,0.3); border-radius:20px;
    padding:4px 12px; font-size:11px; font-weight:600;
    color:#00D4FF; margin-bottom:12px;
  }

  div[data-testid="stFileUploader"] { background: transparent; }
  div[data-testid="stFileUploader"] section {
    background:#161B22; border:2px dashed #30363D; border-radius:12px;
  }

  .stTabs [data-baseweb="tab-list"] { background:#161B22; border-radius:12px; padding:4px; }
  .stTabs [data-baseweb="tab"] { background:transparent; color:#8B949E; border-radius:8px; }
  .stTabs [aria-selected="true"] { background:#21262D !important; color:#00D4FF !important; font-weight:600; }

  .footer {
    text-align:center; padding:24px; margin-top:40px;
    border-top:1px solid #21262D; color:#8B949E; font-size:12px;
  }
  a { color:#00D4FF; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_and_filter(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(file_bytes), low_memory=False)
    africa = df[df["country"].isin(AFRICAN_COUNTRIES)].copy()
    africa["date"] = pd.to_datetime(africa["date"], errors="coerce")
    africa["trade_balance"] = africa["export"] - africa["import"]
    africa["total_trade"] = africa["import"] + africa["export"]
    africa["lat"] = africa["country"].map(lambda c: COUNTRY_COORDS.get(c, (0, 0))[0])
    africa["lon"] = africa["country"].map(lambda c: COUNTRY_COORDS.get(c, (0, 0))[1])
    # Assign sub-regions
    REGION_MAP = {
        # North Africa
        "Algeria": "North Africa", "Egypt": "North Africa", "Libya": "North Africa",
        "Morocco": "North Africa", "Tunisia": "North Africa", "Sudan": "North Africa",
        "Mauritania": "North Africa",
        # West Africa
        "Benin": "West Africa", "Burkina Faso": "West Africa", "Cabo Verde": "West Africa",
        "Côte d'Ivoire": "West Africa", "The Gambia": "West Africa", "Ghana": "West Africa",
        "Guinea": "West Africa", "Guinea-Bissau": "West Africa", "Liberia": "West Africa",
        "Mali": "West Africa", "Niger": "West Africa", "Nigeria": "West Africa",
        "Senegal": "West Africa", "Sierra Leone": "West Africa", "Togo": "West Africa",
        # East Africa
        "Burundi": "East Africa", "Comoros": "East Africa", "Djibouti": "East Africa",
        "Eritrea": "East Africa", "Ethiopia": "East Africa", "Kenya": "East Africa",
        "Madagascar": "East Africa", "Mauritius": "East Africa", "Mayotte": "East Africa",
        "Mozambique": "East Africa", "Réunion": "East Africa", "Rwanda": "East Africa",
        "Seychelles": "East Africa", "Somalia": "East Africa", "South Sudan": "East Africa",
        "Tanzania": "East Africa", "Uganda": "East Africa",
        # Central Africa
        "Cameroon": "Central Africa", "Central African Republic": "Central Africa",
        "Chad": "Central Africa", "Democratic Republic of the Congo": "Central Africa",
        "Equatorial Guinea": "Central Africa", "Gabon": "Central Africa",
        "Republic of Congo": "Central Africa", "São Tomé and Príncipe": "Central Africa",
        # Southern Africa
        "Angola": "Southern Africa", "Botswana": "Southern Africa",
        "Eswatini": "Southern Africa", "Lesotho": "Southern Africa",
        "Malawi": "Southern Africa", "Namibia": "Southern Africa",
        "South Africa": "Southern Africa", "Zambia": "Southern Africa",
        "Zimbabwe": "Southern Africa",
    }
    africa["region"] = africa["country"].map(REGION_MAP).fillna("Other")
    return africa


def fmt_number(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))


def plotly_layout(fig, title="", height=400, showlegend=True):
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#E6EDF3", family="Inter"), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,27,34,0.8)",
        font=dict(family="Inter", color="#C9D1D9"),
        height=height,
        showlegend=showlegend,
        legend=dict(
            bgcolor="rgba(22,27,34,0.9)", bordercolor="#30363D", borderwidth=1,
            font=dict(size=11, color="#C9D1D9"),
        ),
        margin=dict(t=50, b=30, l=10, r=10),
        xaxis=dict(gridcolor="#21262D", zerolinecolor="#30363D", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#21262D", zerolinecolor="#30363D", tickfont=dict(size=11)),
    )
    return fig


def kpi_card(label, value, icon, color_class, delta=None, sub=None):
    delta_html = ""
    if delta is not None:
        sign = "▲" if delta >= 0 else "▼"
        cls  = "delta-up" if delta >= 0 else "delta-down"
        delta_html = f'<div class="kpi-delta {cls}">{sign} {abs(delta):.1f}% vs prev period</div>'
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="kpi-card {color_class}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta_html}{sub_html}
      <div class="kpi-icon">{icon}</div>
    </div>"""


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Africa Port Data")
        wb  = writer.book
        ws  = writer.sheets["Africa Port Data"]

        # Formats
        hdr_fmt = wb.add_format({
            "bold": True, "bg_color": "#0D1117", "font_color": "#00D4FF",
            "border": 1, "border_color": "#30363D", "align": "center",
            "valign": "vcenter", "font_size": 11, "font_name": "Calibri",
        })
        num_fmt = wb.add_format({
            "num_format": "#,##0", "bg_color": "#161B22", "font_color": "#E6EDF3",
            "border": 1, "border_color": "#21262D", "font_name": "Calibri",
        })
        str_fmt = wb.add_format({
            "bg_color": "#161B22", "font_color": "#E6EDF3",
            "border": 1, "border_color": "#21262D", "font_name": "Calibri",
        })
        alt_fmt = wb.add_format({
            "bg_color": "#1C2128", "font_color": "#E6EDF3",
            "border": 1, "border_color": "#21262D", "font_name": "Calibri",
        })
        alt_num = wb.add_format({
            "num_format": "#,##0", "bg_color": "#1C2128", "font_color": "#E6EDF3",
            "border": 1, "border_color": "#21262D", "font_name": "Calibri",
        })

        # Header
        for ci, col in enumerate(df.columns):
            ws.write(0, ci, col, hdr_fmt)

        # Rows
        num_cols_idx = {ci for ci, col in enumerate(df.columns)
                        if pd.api.types.is_numeric_dtype(df[col])}
        for ri, row in enumerate(df.itertuples(index=False), start=1):
            is_alt = ri % 2 == 0
            for ci, val in enumerate(row):
                if ci in num_cols_idx:
                    ws.write(ri, ci, val, alt_num if is_alt else num_fmt)
                else:
                    ws.write(ri, ci, val, alt_fmt if is_alt else str_fmt)

        # Column widths
        for ci, col in enumerate(df.columns):
            max_w = max(len(str(col)), df[col].astype(str).str.len().max())
            ws.set_column(ci, ci, min(max_w + 2, 30))

        # Freeze top row
        ws.freeze_panes(1, 0)

        # Add summary sheet
        summary = pd.DataFrame({
            "Metric": ["Total Rows", "Countries", "Ports", "Date Range",
                       "Total Port Calls", "Total Imports (TEU/MT)", "Total Exports (TEU/MT)"],
            "Value": [
                len(df),
                df["country"].nunique() if "country" in df.columns else "N/A",
                df["portname"].nunique() if "portname" in df.columns else "N/A",
                f"{df['date'].min()} → {df['date'].max()}" if "date" in df.columns else "N/A",
                f"{df['portcalls'].sum():,}" if "portcalls" in df.columns else "N/A",
                f"{df['import'].sum():,}" if "import" in df.columns else "N/A",
                f"{df['export'].sum():,}" if "export" in df.columns else "N/A",
            ]
        })
        summary.to_excel(writer, index=False, sheet_name="Summary")
        ws2 = writer.sheets["Summary"]
        ws2.set_column(0, 0, 30)
        ws2.set_column(1, 1, 40)

    return output.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 8px 0;">
      <div style="font-size:22px; font-weight:800; color:#00D4FF; margin-bottom:4px;">⚓ PortPulseAfrica</div>
      <div style="font-size:11px; color:#8B949E; margin-bottom:20px;">Real-time Heartbeat of African Ports</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Data Upload")
    uploaded_file = st.file_uploader(
        "Drop your Daily_Ports_Data.csv here",
        type=["csv"],
        help="Upload the full ports dataset — African countries are extracted automatically.",
    )

    st.markdown("---")
    st.markdown("### 🎛️ Filters")


# ─────────────────────────────────────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">⚡ PORTPULSEAFRICA</div>
  <h1>⚓ PortPulseAfrica</h1>
  <p>Real-time insights on African maritime trade • Port calls • Imports & Exports • Cargo flows</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
#  DATA SOURCE RESOLUTION
#  Priority: 1) uploaded file  2) bundled africa_ports_data.csv  3) error
# ─────────────────────────────────────────────────────────────────────────────
BUNDLED_DATA = "africa_ports_data.csv"   # file committed alongside app.py

@st.cache_data(show_spinner=False)
def load_bundled(path: str) -> pd.DataFrame:
    """Load the pre-filtered African CSV bundled in the repo."""
    df = pd.read_csv(path, low_memory=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "trade_balance" not in df.columns:
        df["trade_balance"] = df["export"] - df["import"]
    if "total_trade" not in df.columns:
        df["total_trade"]   = df["import"] + df["export"]
    if "region" not in df.columns:
        REGION_MAP_LOCAL = {
            "Algeria":"North Africa","Egypt":"North Africa","Libya":"North Africa",
            "Morocco":"North Africa","Tunisia":"North Africa","Sudan":"North Africa",
            "Mauritania":"North Africa","Benin":"West Africa","Burkina Faso":"West Africa",
            "Cabo Verde":"West Africa","Côte d'Ivoire":"West Africa","The Gambia":"West Africa",
            "Ghana":"West Africa","Guinea":"West Africa","Guinea-Bissau":"West Africa",
            "Liberia":"West Africa","Mali":"West Africa","Niger":"West Africa",
            "Nigeria":"West Africa","Senegal":"West Africa","Sierra Leone":"West Africa",
            "Togo":"West Africa","Burundi":"East Africa","Comoros":"East Africa",
            "Djibouti":"East Africa","Eritrea":"East Africa","Ethiopia":"East Africa",
            "Kenya":"East Africa","Madagascar":"East Africa","Mauritius":"East Africa",
            "Mayotte":"East Africa","Mozambique":"East Africa","Réunion":"East Africa",
            "Rwanda":"East Africa","Seychelles":"East Africa","Somalia":"East Africa",
            "South Sudan":"East Africa","Tanzania":"East Africa","Uganda":"East Africa",
            "Cameroon":"Central Africa","Central African Republic":"Central Africa",
            "Chad":"Central Africa","Democratic Republic of the Congo":"Central Africa",
            "Equatorial Guinea":"Central Africa","Gabon":"Central Africa",
            "Republic of Congo":"Central Africa","São Tomé and Príncipe":"Central Africa",
            "Angola":"Southern Africa","Botswana":"Southern Africa","Eswatini":"Southern Africa",
            "Lesotho":"Southern Africa","Malawi":"Southern Africa","Namibia":"Southern Africa",
            "South Africa":"Southern Africa","Zambia":"Southern Africa","Zimbabwe":"Southern Africa",
        }
        df["region"] = df["country"].map(REGION_MAP_LOCAL).fillna("Other")
    if "lat" not in df.columns:
        df["lat"] = df["country"].map(lambda c: COUNTRY_COORDS.get(c, (0, 0))[0])
        df["lon"] = df["country"].map(lambda c: COUNTRY_COORDS.get(c, (0, 0))[1])
    return df


# ── Resolve data source ───────────────────────────────────────────────────────
if uploaded_file is not None:
    # User uploaded a new file → use it (could be full global CSV or africa CSV)
    with st.spinner("🔄 Loading uploaded file..."):
        file_bytes = uploaded_file.read()
        df_all = load_and_filter(file_bytes)
    data_source = f"📤 Uploaded: **{uploaded_file.name}**"

elif os.path.exists(BUNDLED_DATA):
    # Use the pre-filtered CSV bundled in the repo
    with st.spinner("⚡ Loading bundled African data..."):
        df_all = load_bundled(BUNDLED_DATA)
    data_source = f"📦 Default dataset: **{BUNDLED_DATA}**"

else:
    # Nothing available → show upload prompt
    st.markdown("""
    <div class="upload-zone">
      <div style="font-size:52px; margin-bottom:12px;">📡</div>
      <div class="upload-title">⚡ PortPulseAfrica — No Data Found</div>
      <div class="upload-sub">
        No bundled data detected.<br>
        Upload <strong>africa_ports_data.csv</strong> (pre-filtered) <b>or</b>
        <strong>Daily_Ports_Data.csv</strong> (full global dataset) via the sidebar.
      </div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, icon, clr in zip(
        [c1, c2, c3, c4, c5],
        ["Total Port Calls", "Total Imports", "Total Exports", "Countries", "Ports"],
        ["🚢", "📥", "📤", "🌍", "⚓"],
        ["blue", "orange", "purple", "green", "yellow"],
    ):
        col.markdown(kpi_card(label, "—", icon, clr, sub="Upload data to unlock"),
                     unsafe_allow_html=True)
    st.stop()

if df_all.empty:
    st.error("❌ No African country data found.")
    st.stop()

# Show data source badge
st.markdown(
    f'<div style="background:#161B22;border:1px solid #21262D;border-radius:8px;'
    f'padding:8px 16px;margin-bottom:12px;font-size:12px;color:#8B949E;">'
    f'📊 Data source: {data_source} &nbsp;·&nbsp; '
    f'<b style="color:#00D4FF;">{len(df_all):,}</b> rows &nbsp;·&nbsp; '
    f'<b style="color:#00D4FF;">{df_all["country"].nunique()}</b> countries</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR FILTERS (after data loaded)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    all_years = sorted(df_all["year"].dropna().unique().tolist())
    sel_years = st.multiselect("📅 Year", all_years, default=all_years,
                               help="Select one or more years")

    all_regions = sorted(df_all["region"].unique().tolist())
    sel_regions = st.multiselect("🌍 Region", all_regions, default=all_regions)

    all_countries = sorted(df_all["country"].unique().tolist())
    sel_countries = st.multiselect("🏳️ Country", all_countries, default=all_countries)

    all_ports = sorted(df_all["portname"].unique().tolist())
    sel_ports = st.multiselect("⚓ Port", all_ports, default=all_ports,
                               help="Filter specific ports")

    st.markdown("---")
    cargo_options = list(CARGO_TYPES.keys())
    sel_cargo = st.multiselect(
        "🚢 Cargo Type",
        cargo_options,
        default=cargo_options,
        format_func=lambda x: CARGO_TYPES[x],
    )

    st.markdown("---")
    metric_choice = st.radio(
        "📊 Primary Metric",
        ["portcalls", "import", "export", "total_trade"],
        format_func=lambda x: {
            "portcalls": "🚢 Port Calls",
            "import": "📥 Imports",
            "export": "📤 Exports",
            "total_trade": "🔄 Total Trade",
        }[x],
    )
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:11px; color:#8B949E; text-align:center;">
      <b style="color:#00D4FF;">{df_all['country'].nunique()}</b> countries •
      <b style="color:#00D4FF;">{df_all['portname'].nunique()}</b> ports<br>
      Data: {df_all['date'].min().strftime('%b %Y')} → {df_all['date'].max().strftime('%b %Y')}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
df = df_all.copy()
if sel_years:     df = df[df["year"].isin(sel_years)]
if sel_regions:   df = df[df["region"].isin(sel_regions)]
if sel_countries: df = df[df["country"].isin(sel_countries)]
if sel_ports:     df = df[df["portname"].isin(sel_ports)]

# Filter by cargo (portcalls sum of selected types)
if sel_cargo:
    pc_cols = [f"portcalls_{c}" for c in sel_cargo if f"portcalls_{c}" in df.columns]
    imp_cols = [f"import_{c}"    for c in sel_cargo if f"import_{c}"    in df.columns]
    exp_cols = [f"export_{c}"    for c in sel_cargo if f"export_{c}"    in df.columns]
    df["portcalls"] = df[pc_cols].sum(axis=1) if pc_cols else df["portcalls"]
    df["import"]    = df[imp_cols].sum(axis=1) if imp_cols else df["import"]
    df["export"]    = df[exp_cols].sum(axis=1) if exp_cols else df["export"]
    df["total_trade"] = df["import"] + df["export"]

if df.empty:
    st.warning("⚠️ No data matches your filters. Please adjust the filter settings.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  KPI CARDS
# ─────────────────────────────────────────────────────────────────────────────
total_calls  = int(df["portcalls"].sum())
total_import = int(df["import"].sum())
total_export = int(df["export"].sum())
n_countries  = df["country"].nunique()
n_ports      = df["portname"].nunique()

# Delta vs unfiltered
def pct_delta(a, b):
    return (a - b) / b * 100 if b else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.markdown(kpi_card("Total Port Calls", fmt_number(total_calls), "🚢", "blue",
                     sub=f"{n_countries} countries · {n_ports} ports"), unsafe_allow_html=True)
c2.markdown(kpi_card("Total Imports", fmt_number(total_import), "📥", "orange",
                     sub="Metric tonnes / TEU"), unsafe_allow_html=True)
c3.markdown(kpi_card("Total Exports", fmt_number(total_export), "📤", "purple",
                     sub="Metric tonnes / TEU"), unsafe_allow_html=True)
c4.markdown(kpi_card("Trade Balance",
                     ("+" if (total_export - total_import) >= 0 else "") +
                     fmt_number(total_export - total_import),
                     "⚖️", "green" if (total_export - total_import) >= 0 else "orange",
                     sub="Export − Import"), unsafe_allow_html=True)
c5.markdown(kpi_card("Active Countries", str(n_countries), "🌍", "yellow",
                     sub=f"{n_ports} distinct ports"), unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️  Map View", "📈  Trends", "🏆  Rankings", "🚢  Cargo Analysis", "📊  Deep Dive"
])


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 1 — MAP VIEW
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    col_map, col_insights = st.columns([3, 1])

    with col_map:
        st.markdown('<div class="section-header">🌍 Africa Maritime Trade Map</div>', unsafe_allow_html=True)

        map_agg = (df.groupby(["country", "ISO3", "lat", "lon", "region"])
                   .agg(portcalls=("portcalls","sum"), imports=("import","sum"),
                        exports=("export","sum"), total_trade=("total_trade","sum"),
                        n_ports=("portname","nunique"))
                   .reset_index())

        map_type = st.radio("Map Style", ["Choropleth", "Bubble"], horizontal=True)
        map_metric = st.selectbox(
            "Metric",
            ["total_trade", "portcalls", "imports", "exports"],
            format_func=lambda x: {
                "total_trade": "Total Trade", "portcalls": "Port Calls",
                "imports": "Imports", "exports": "Exports"
            }[x],
        )

        if map_type == "Choropleth":
            fig_map = px.choropleth(
                map_agg, locations="ISO3", color=map_metric,
                hover_name="country",
                hover_data={"portcalls": ":,", "imports": ":,", "exports": ":,",
                            "n_ports": True, "ISO3": False},
                color_continuous_scale=[[0,"#0D1117"],[0.2,"#003366"],
                                        [0.5,"#0066CC"],[0.8,"#00D4FF"],[1,"#FFFFFF"]],
                scope="africa",
                title=f"Africa — {map_metric.replace('_',' ').title()}",
                labels={map_metric: map_metric.replace("_"," ").title()},
            )
            fig_map.update_geos(
                bgcolor="#0D1117", landcolor="#1C2128", coastlinecolor="#30363D",
                countrycolor="#30363D", showocean=True, oceancolor="#0A0F16",
                showlakes=True, lakecolor="#0A0F16", showrivers=False,
                fitbounds="locations",
            )
            fig_map.update_coloraxes(colorbar=dict(
                bgcolor="#161B22", bordercolor="#30363D",
                tickfont=dict(color="#C9D1D9"), title=dict(font=dict(color="#C9D1D9")),
            ))
        else:
            fig_map = px.scatter_geo(
                map_agg, lat="lat", lon="lon", size=map_metric,
                color="region", hover_name="country",
                hover_data={"portcalls": ":,", "imports": ":,", "exports": ":,", "n_ports": True},
                size_max=60, scope="africa",
                color_discrete_sequence=PALETTE,
                title=f"Africa — {map_metric.replace('_',' ').title()} by Country",
            )
            fig_map.update_geos(
                bgcolor="#0D1117", landcolor="#1C2128", coastlinecolor="#30363D",
                countrycolor="#30363D", showocean=True, oceancolor="#0A0F16",
                showlakes=True, lakecolor="#0A0F16", fitbounds="locations",
            )

        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#C9D1D9"),
            height=540, margin=dict(t=50, b=0, l=0, r=0),
            title=dict(font=dict(size=15, color="#E6EDF3"), x=0.01),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_insights:
        st.markdown('<div class="section-header">🧠 Key Insights</div>', unsafe_allow_html=True)

        top5 = map_agg.nlargest(5, "total_trade")[["country", "total_trade", "portcalls"]]
        for _, row in top5.iterrows():
            st.markdown(f"""
            <div class="insight-box">
              <div class="insight-title">🏆 {row['country']}</div>
              <div class="insight-text">
                Total Trade: <b>{fmt_number(row['total_trade'])}</b><br>
                Port Calls: <b>{int(row['portcalls'])}</b>
              </div>
            </div>""", unsafe_allow_html=True)

        # Region breakdown pie
        reg = (df.groupby("region")["total_trade"].sum().reset_index()
               .sort_values("total_trade", ascending=False))
        fig_pie = go.Figure(go.Pie(
            labels=reg["region"], values=reg["total_trade"],
            hole=0.55, marker_colors=PALETTE[:len(reg)],
            textinfo="label+percent", textfont=dict(size=10),
            hovertemplate="<b>%{label}</b><br>Trade: %{value:,}<br>Share: %{percent}<extra></extra>",
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0), height=200,
            annotations=[dict(text="By<br>Region", x=0.5, y=0.5,
                              font=dict(size=11, color="#8B949E"), showarrow=False)],
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 2 — TRENDS
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📈 Temporal Trends</div>', unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)

    # Monthly trend
    with r1c1:
        monthly = (df.groupby(["year", "month"])
                   .agg(portcalls=("portcalls","sum"),
                        imports=("import","sum"), exports=("export","sum"))
                   .reset_index())
        monthly["period"] = pd.to_datetime(
            monthly[["year","month"]].assign(day=1)
        )
        monthly = monthly.sort_values("period")

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly["period"], y=monthly["imports"], name="Imports",
            line=dict(color="#FF6B35", width=2.5), fill="tozeroy",
            fillcolor="rgba(255,107,53,0.1)",
            hovertemplate="<b>Imports</b><br>%{x|%b %Y}: %{y:,}<extra></extra>",
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly["period"], y=monthly["exports"], name="Exports",
            line=dict(color="#00D4FF", width=2.5), fill="tozeroy",
            fillcolor="rgba(0,212,255,0.1)",
            hovertemplate="<b>Exports</b><br>%{x|%b %Y}: %{y:,}<extra></extra>",
        ))
        plotly_layout(fig_trend, "📅 Monthly Import vs Export Volume", 360)
        st.plotly_chart(fig_trend, use_container_width=True)

    # Annual port calls by region
    with r1c2:
        yr_reg = (df.groupby(["year", "region"])["portcalls"].sum().reset_index())
        fig_bar = px.bar(
            yr_reg, x="year", y="portcalls", color="region",
            color_discrete_sequence=PALETTE, barmode="stack",
            labels={"portcalls": "Port Calls", "year": "Year"},
        )
        plotly_layout(fig_bar, "📊 Annual Port Calls by Region", 360)
        fig_bar.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Calls: %{y:,}<extra></extra>")
        st.plotly_chart(fig_bar, use_container_width=True)

    # YoY growth
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        yoy = (df.groupby("year")
               .agg(imports=("import","sum"), exports=("export","sum"),
                    portcalls=("portcalls","sum"))
               .reset_index())
        yoy["import_growth"] = yoy["imports"].pct_change() * 100
        yoy["export_growth"] = yoy["exports"].pct_change() * 100

        fig_yoy = go.Figure()
        fig_yoy.add_trace(go.Bar(
            x=yoy["year"], y=yoy["import_growth"], name="Import Growth",
            marker_color=["#00C896" if v >= 0 else "#FF4757" for v in yoy["import_growth"].fillna(0)],
        ))
        fig_yoy.add_trace(go.Scatter(
            x=yoy["year"], y=yoy["export_growth"], name="Export Growth",
            line=dict(color="#FFB800", width=2), mode="lines+markers",
            marker=dict(size=6),
        ))
        fig_yoy.add_hline(y=0, line_dash="dash", line_color="#8B949E", line_width=1)
        plotly_layout(fig_yoy, "📈 Year-over-Year Growth (%)", 360)
        st.plotly_chart(fig_yoy, use_container_width=True)

    with r2c2:
        # Trade balance by country
        tb = (df.groupby("country")
              .agg(imports=("import","sum"), exports=("export","sum"))
              .assign(balance=lambda d: d["exports"] - d["imports"])
              .sort_values("balance")
              .reset_index())
        fig_tb = go.Figure(go.Bar(
            x=tb["balance"],
            y=tb["country"],
            orientation="h",
            marker_color=["#00C896" if v >= 0 else "#FF4757" for v in tb["balance"]],
            hovertemplate="<b>%{y}</b><br>Balance: %{x:,}<extra></extra>",
        ))
        fig_tb.add_vline(x=0, line_color="#8B949E", line_width=1, line_dash="dash")
        plotly_layout(fig_tb, "⚖️ Trade Balance by Country (Export − Import)",
                      max(300, len(tb) * 20), showlegend=False)
        fig_tb.update_layout(yaxis=dict(tickfont=dict(size=9)))
        st.plotly_chart(fig_tb, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 3 — RANKINGS
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🏆 Port & Country Rankings</div>', unsafe_allow_html=True)

    rc1, rc2 = st.columns(2)

    # Top ports by selected metric
    with rc1:
        top_n = st.slider("Number of top ports", 5, 30, 15, key="top_n")
        port_agg = (df.groupby(["portname", "country"])
                    .agg(portcalls=("portcalls","sum"), imports=("import","sum"),
                         exports=("export","sum"), total_trade=("total_trade","sum"))
                    .reset_index().nlargest(top_n, metric_choice))

        fig_ports = px.bar(
            port_agg.sort_values(metric_choice),
            x=metric_choice, y="portname", orientation="h",
            color="country", color_discrete_sequence=PALETTE,
            text=port_agg.sort_values(metric_choice)[metric_choice].apply(fmt_number),
            labels={metric_choice: metric_choice.replace("_"," ").title(), "portname": "Port"},
        )
        fig_ports.update_traces(textposition="outside", textfont=dict(size=9))
        plotly_layout(fig_ports, f"⚓ Top {top_n} Ports by {metric_choice.replace('_',' ').title()}",
                      max(400, top_n * 28))
        fig_ports.update_layout(yaxis=dict(tickfont=dict(size=9)))
        st.plotly_chart(fig_ports, use_container_width=True)

    # Country ranking
    with rc2:
        country_agg = (df.groupby("country")
                       .agg(portcalls=("portcalls","sum"), imports=("import","sum"),
                            exports=("export","sum"), total_trade=("total_trade","sum"),
                            n_ports=("portname","nunique"))
                       .reset_index().sort_values(metric_choice, ascending=False))

        fig_ctry = px.treemap(
            country_agg.head(20),
            path=["country"], values=metric_choice,
            color=metric_choice,
            color_continuous_scale=[[0,"#0D1117"],[0.4,"#003366"],[0.7,"#0066CC"],[1,"#00D4FF"]],
            hover_data={"portcalls": ":,", "imports": ":,", "exports": ":,", "n_ports": True},
        )
        fig_ctry.update_traces(textfont=dict(size=12, color="#E6EDF3"),
                               hovertemplate="<b>%{label}</b><br>%{customdata[0]:,}<extra></extra>")
        fig_ctry.update_coloraxes(colorbar=dict(
            tickfont=dict(color="#C9D1D9"), title=dict(font=dict(color="#C9D1D9")),
        ))
        fig_ctry.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#C9D1D9"),
            height=480, margin=dict(t=40, b=0, l=0, r=0),
            title=dict(text=f"🌍 Country Share — {metric_choice.replace('_',' ').title()}",
                       font=dict(size=15, color="#E6EDF3"), x=0.01),
        )
        st.plotly_chart(fig_ctry, use_container_width=True)

    # Data table
    st.markdown('<div class="section-header">📋 Rankings Table</div>', unsafe_allow_html=True)
    display_cols = ["country", "portname", "year", "portcalls", "import", "export", "total_trade", "region"]
    display_cols = [c for c in display_cols if c in df.columns]
    ranked = (df[display_cols]
              .groupby(["country", "portname", "region"])
              .agg({"portcalls": "sum", "import": "sum", "export": "sum", "total_trade": "sum"})
              .reset_index()
              .sort_values(metric_choice, ascending=False)
              .reset_index(drop=True))
    ranked.index += 1
    st.dataframe(
        ranked.head(50).style
              .background_gradient(subset=["portcalls","import","export","total_trade"],
                                   cmap="Blues")
              .format({"portcalls":"{:,.0f}","import":"{:,.0f}",
                       "export":"{:,.0f}","total_trade":"{:,.0f}"}),
        use_container_width=True, height=380,
    )


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 4 — CARGO ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🚢 Cargo Type Analysis</div>', unsafe_allow_html=True)

    ca1, ca2 = st.columns(2)

    with ca1:
        cargo_pc = {ct: df[f"portcalls_{ct}"].sum() for ct in cargo_options
                    if f"portcalls_{ct}" in df.columns}
        fig_radar = go.Figure(go.Scatterpolar(
            r=list(cargo_pc.values()),
            theta=[CARGO_TYPES[k] for k in cargo_pc.keys()],
            fill="toself",
            fillcolor="rgba(0,212,255,0.15)",
            line=dict(color="#00D4FF", width=2),
            marker=dict(size=8, color="#00D4FF"),
            name="Port Calls",
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(22,27,34,0.8)",
                angularaxis=dict(tickfont=dict(size=11, color="#C9D1D9"), gridcolor="#30363D"),
                radialaxis=dict(tickfont=dict(size=9, color="#8B949E"), gridcolor="#21262D",
                                showticklabels=True),
            ),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#C9D1D9"),
            showlegend=False, height=380,
            title=dict(text="🔄 Cargo Mix — Port Calls Radar",
                       font=dict(size=14, color="#E6EDF3"), x=0.01),
            margin=dict(t=50, b=30),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with ca2:
        # Import by cargo type stacked
        cargo_imp = {}
        cargo_exp = {}
        for ct in cargo_options:
            if f"import_{ct}" in df.columns:
                cargo_imp[CARGO_TYPES[ct]] = df[f"import_{ct}"].sum()
            if f"export_{ct}" in df.columns:
                cargo_exp[CARGO_TYPES[ct]] = df[f"export_{ct}"].sum()

        fig_cargo_bar = go.Figure()
        for i, (label, val) in enumerate(cargo_imp.items()):
            fig_cargo_bar.add_trace(go.Bar(
                name=label, x=["Imports"], y=[val],
                marker_color=PALETTE[i], showlegend=True,
                hovertemplate=f"<b>{label}</b><br>Imports: %{{y:,}}<extra></extra>",
            ))
        for i, (label, val) in enumerate(cargo_exp.items()):
            fig_cargo_bar.add_trace(go.Bar(
                name=label, x=["Exports"], y=[val],
                marker_color=PALETTE[i], showlegend=False,
                hovertemplate=f"<b>{label}</b><br>Exports: %{{y:,}}<extra></extra>",
            ))
        fig_cargo_bar.update_layout(barmode="stack")
        plotly_layout(fig_cargo_bar, "📦 Import vs Export by Cargo Type", 380)
        st.plotly_chart(fig_cargo_bar, use_container_width=True)

    # Cargo trend over time
    ca3, ca4 = st.columns(2)
    with ca3:
        yr_cargo = {}
        for ct in cargo_options:
            col = f"portcalls_{ct}"
            if col in df.columns:
                yr_cargo[CARGO_TYPES[ct]] = df.groupby("year")[col].sum()

        if yr_cargo:
            fig_ct = go.Figure()
            for i, (label, series) in enumerate(yr_cargo.items()):
                fig_ct.add_trace(go.Scatter(
                    x=series.index, y=series.values, name=label,
                    mode="lines+markers",
                    line=dict(color=PALETTE[i], width=2),
                    marker=dict(size=6),
                    hovertemplate=f"<b>{label}</b><br>Year: %{{x}}<br>Calls: %{{y:,}}<extra></extra>",
                ))
            plotly_layout(fig_ct, "📈 Port Calls per Cargo Type Over Time", 360)
            st.plotly_chart(fig_ct, use_container_width=True)

    with ca4:
        # Heatmap: country × cargo type
        heat_data = []
        for ct in cargo_options:
            col = f"portcalls_{ct}"
            if col in df.columns:
                g = df.groupby("country")[col].sum().reset_index()
                g["cargo"] = CARGO_TYPES[ct]
                g.columns = ["country", "value", "cargo"]
                heat_data.append(g)

        if heat_data:
            heat_df = pd.concat(heat_data)
            pivot   = heat_df.pivot(index="country", columns="cargo", values="value").fillna(0)
            fig_heat = px.imshow(
                pivot, color_continuous_scale="Blues",
                labels=dict(color="Port Calls"),
                aspect="auto",
            )
            fig_heat.update_traces(
                hovertemplate="<b>%{y}</b><br>%{x}<br>Calls: %{z:,}<extra></extra>"
            )
            fig_heat.update_coloraxes(colorbar=dict(
                tickfont=dict(color="#C9D1D9"), title=dict(font=dict(color="#C9D1D9")),
            ))
            fig_heat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#C9D1D9"),
                height=max(300, len(pivot) * 20),
                margin=dict(t=50, b=0, l=0, r=0),
                title=dict(text="🌡️ Heatmap: Country × Cargo Type",
                           font=dict(size=14, color="#E6EDF3"), x=0.01),
                xaxis=dict(tickfont=dict(size=9)), yaxis=dict(tickfont=dict(size=9)),
            )
            st.plotly_chart(fig_heat, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 5 — DEEP DIVE
# ═════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">🔬 Deep Dive & Data Export</div>', unsafe_allow_html=True)

    dd1, dd2 = st.columns(2)

    with dd1:
        # Scatter: import vs export colored by region
        fig_scatter = px.scatter(
            df.groupby(["country","region"])
              .agg(imports=("import","sum"), exports=("export","sum"),
                   portcalls=("portcalls","sum"), n_ports=("portname","nunique"))
              .reset_index(),
            x="imports", y="exports", color="region",
            size="portcalls", size_max=50,
            hover_name="country",
            hover_data={"portcalls":":,","imports":":,","exports":":,","n_ports":True},
            color_discrete_sequence=PALETTE,
            labels={"imports":"Total Imports","exports":"Total Exports"},
        )
        # Diagonal reference
        max_val = max(df["import"].sum(), df["export"].sum())
        fig_scatter.add_trace(go.Scatter(
            x=[0, max_val / df["country"].nunique() * 5],
            y=[0, max_val / df["country"].nunique() * 5],
            mode="lines", line=dict(color="#8B949E", dash="dash", width=1),
            showlegend=False, hoverinfo="skip",
        ))
        plotly_layout(fig_scatter, "🔵 Import vs Export per Country (bubble = port calls)", 420)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with dd2:
        # Monthly seasonality
        month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                       7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        seas = (df.groupby("month")
                .agg(portcalls=("portcalls","mean"), imports=("import","mean"),
                     exports=("export","mean"))
                .reset_index())
        seas["month_name"] = seas["month"].map(month_names)

        fig_seas = go.Figure()
        fig_seas.add_trace(go.Bar(
            x=seas["month_name"], y=seas["portcalls"],
            name="Avg Port Calls", marker_color="#00D4FF", yaxis="y",
            hovertemplate="<b>%{x}</b><br>Avg Calls: %{y:.1f}<extra></extra>",
        ))
        fig_seas.add_trace(go.Scatter(
            x=seas["month_name"], y=seas["imports"],
            name="Avg Imports", line=dict(color="#FF6B35", width=2),
            mode="lines+markers", yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Avg Imports: %{y:,.0f}<extra></extra>",
        ))
        fig_seas.update_layout(
            yaxis2=dict(overlaying="y", side="right", gridcolor="#21262D",
                        tickfont=dict(size=10, color="#FF6B35")),
        )
        plotly_layout(fig_seas, "🗓️ Seasonality — Monthly Average", 420)
        st.plotly_chart(fig_seas, use_container_width=True)

    # Raw data table + download
    st.markdown('<div class="section-header">📥 Export Filtered Data</div>', unsafe_allow_html=True)

    dcol1, dcol2, dcol3 = st.columns([2, 1, 1])
    with dcol1:
        st.markdown(f"""
        <div class="insight-box">
          <div class="insight-title">📋 Current Dataset</div>
          <div class="insight-text">
            <b>{len(df):,}</b> rows &nbsp;·&nbsp;
            <b>{df['country'].nunique()}</b> countries &nbsp;·&nbsp;
            <b>{df['portname'].nunique()}</b> ports<br>
            Period: <b>{df['date'].min().strftime('%d %b %Y') if pd.notna(df['date'].min()) else '—'}</b>
            → <b>{df['date'].max().strftime('%d %b %Y') if pd.notna(df['date'].max()) else '—'}</b>
          </div>
        </div>""", unsafe_allow_html=True)

    with dcol2:
        excel_data = to_excel_bytes(df)
        st.download_button(
            label="⬇️ Download Excel",
            data=excel_data,
            file_name=f"portpulseafrica_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with dcol3:
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name=f"portpulseafrica_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.dataframe(
        df.head(200),
        use_container_width=True,
        height=380,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  ⚓ <strong>PortPulseAfrica Intelligence Dashboard</strong> &nbsp;·&nbsp;
  Built with Streamlit & Plotly &nbsp;·&nbsp;
  Data: {df_all['date'].min().strftime('%Y')}–{df_all['date'].max().strftime('%Y')} &nbsp;·&nbsp;
  {df_all['country'].nunique()} African countries &nbsp;·&nbsp;
  {df_all['portname'].nunique()} ports &nbsp;·&nbsp;
  <a href="https://github.com" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
