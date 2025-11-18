import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math

# --- 1. OLDAL KONFIGURÁCIÓ ---
st.set_page_config(page_title="Urológiai Nomogram", layout="wide")

# --- PRÉMIUM DARK CSS DIZÁJN ---
st.markdown("""
    <style>
    /* SÖTÉT HÁTTÉR */
    .stApp {
        background-color: #2C3E50; /* Sötétkék/Szürke háttér */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* FŐ CÍMSOROK (Fehérre állítva a sötét háttér miatt) */
    h1 {
        color: #ECF0F1 !important;
        font-weight: 800;
        letter-spacing: -0.5px;
        padding-top: 10px;
    }
    
    h3 {
        color: #BDC3C7 !important;
        font-weight: 400;
        font-size: 1.2rem;
        padding-bottom: 20px;
    }
    
    /* KÁRTYA DOBOZOK (Fehér szigetek a sötét tengerben) */
    .ios-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.3); /* Erősebb árnyék */
        margin-bottom: 25px;
    }

    /* Beviteli mezők címkéi (A kártyán belül sötétek) */
    .stNumberInput > label {
        color: #2C3E50 !important;
        font-weight: 600;
    }
    
    /* Gomb stílus */
    .stButton > button {
        background: linear-gradient(135deg, #3498DB 0%, #2980B9 100%);
        color: white;
        border-radius: 10px;
        border: none;
        height: 50px;
        font-weight: 600;
        font-size: 16px;
        width: 100%;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, #5DADE2 0%, #3498DB 100%);
    }

    /* Eredmény Widgetek */
    .metric-container {
        background-color: #F8F9FA;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #E9ECEF;
    }
    
    .metric-label {
        color: #7F8C8D;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    
    .metric-value {
        color: #2C3E50;
        font-size: 1.4rem;
        font-weight: 800;
    }

    /* Fülek (Tabs) Dizájn */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
        padding-bottom: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(255, 255, 255, 0.1); /* Áttetsző fehér */
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.2);
        color: #ECF0F1; /* Világos szöveg inaktív állapotban */
        font-weight: 600;
        padding: 0 25px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3498DB; /* Aktív kék */
        color: #FFFFFF;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Expander */
    div[data-testid="stExpander"] {
        background-color: #34495E;
        color: white;
        border: none;
        border-radius: 10px;
    }
    div[data-testid="stExpander"] p {
        color: #ECF0F1;
    }
    div[data-testid="stExpander"] summary {
        color: #ECF0F1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- FEJLÉC ---
st.title("Urológiai Diagnosztika")
st.markdown("### Unified Nomogram App")

with st.expander("Jogi Nyilatkozat"):
    st.info("""
    Ez az alkalmazás kizárólag tájékoztató jellegű. A számítások szakirodalmi adatokon alapulnak (Liverpool, Miskolc, Toguri), 
    de nem helyettesítik a szakorvosi diagnózist. A döntéshozatal a kezelőorvos felelőssége.
    """)

# --- SEGÉDFÜGGVÉNYEK ---
def create_clean_plot(title, xlabel, ylabel, x_max, y_max):
    fig, ax = plt.subplots(figsize=(8, 5))
    # Tiszta stílus
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Keretek
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#95A5A6')
    ax.spines['bottom'].set_color('#95A5A6')
    
    # Címkék
    ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color='#2C3E50', loc='left')
    ax.set_xlabel(xlabel, fontsize=10, color='#7F8C8D')
    ax.set_ylabel(ylabel, fontsize=10, color='#7F8C8D')
    
    # Tengelyek
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.tick_params(axis='both', colors='#7F8C8D')
    
    # Rács
    ax.grid(True, axis='y', linestyle=':', linewidth=0.5, color='#BDC3C7')
    
    return fig, ax

def plot_patient_point(ax, x, y):
    ax.scatter(x, y, color='#E74C3C', s=120, zorder=10, marker='o', edgecolors='white', linewidth=2, label='Mért érték')
    ax.legend(loc='upper left', frameon=False, labelcolor='#7F8C8D', fontsize=9)

def result_card(label, value, color):
    st.markdown(f"""
    <div class="metric-container" style="border-left: 5px solid {color};">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 1. LIVERPOOL NOMOGRAM
# ==========================================
def liverpool_nomogram():
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown("#### Férfiak (50 év alatt)")
    st.caption("Referencia: Haylen et al.")
    st.markdown("---")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        vol = st.number_input("Ürített térfogat (ml)", min_value=0.0, value=400.0, step=10.0, key="l_v")
    with c2:
        qmax = st.number_input("Qmax (ml/s)", min_value=0.0, value=25.0, step=1.0, key="l_qm")
    with c3:
        qave = st.number_input("Qave (ml/s)", min_value=0.0, value=15.0, step=1.0, key="l_qa")

    if vol > 0:
        # Számítás
        def get_liverpool_band(val, limits):
            # Színek: Piros, Narancs, Sárga, Zöld, Kék
            if val < limits[0]: return "< 5. percentilis (Kóros)", "#E74C3C"
            if val < limits[1]: return "5-10. percentilis (Alacsony)", "#E67E22"
            if val < limits[2]: return "10-25. percentilis (Mérsékelt)", "#F1C40F"
            if val < limits[6]: return "25-95. percentilis (Normál)", "#27AE60"
            return "> 95. percentilis (Magas)", "#2980B9"

        qmax_limits = [0.75, 0.95, 1.20, 1.50, 1.80, 2.10, 2.35]
        qave_limits = [0.45, 0.55, 0.70, 0.875, 1.05, 1.20, 1.30]

        res_qmax = qmax / math.sqrt(vol)
        res_qave = qave / math.sqrt(vol)

        txt_max, col_max = get_liverpool_band(res_qmax, qmax_limits)
        txt_ave, col_ave = get_liverpool_band(res_qave, qave_limits)

        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1: result_card("Qmax Eredmény", txt_max, col_max)
        with r2: result_card("Qave Eredmény", txt_ave, col_ave)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Grafikonok
    if vol > 0:
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        st.subheader("Grafikus nézet")
        g1, g2 = st.columns(2)
        
        x_vals = np.linspace(50, 600, 100)
        colors = ['#E74C3C', '#E67E22', '#F1C40F', '#27AE60', '#27AE60', '#27AE60', '#2980B9']

        with g1:
            fig1, ax1 = create_clean_plot("Liverpool Qmax", "Térfogat (ml)", "Qmax (ml/s)", 600, 40)
            percentiles = [5, 10, 25, 50, 75, 90, 95]
            for i, (p, factor) in enumerate(zip(percentiles, qmax_limits)):
                y_vals = factor * np.sqrt(x_vals)
                ax1.plot(x_vals, y_vals, color=colors[i], linewidth=1.5, alpha=0.7)
                if p in [5, 50, 95]: ax1.text(605, factor * np.sqrt(600), f'{p}%', fontsize=8, color=colors[i])
            plot_patient_point(ax1, vol, qmax)
            st.pyplot(fig1)

        with g2:
            fig2, ax2 = create_clean_plot("Liverpool Qave", "Térfogat (ml)", "Qave (ml/s)", 600, 25)
            for i, (p, factor) in enumerate(zip(percentiles, qave_limits)):
                y_vals = factor * np.sqrt(x_vals)
                ax2.plot(x_vals, y_vals, color=colors[i], linewidth=1.5, alpha=0.7)
                if p in [5, 50, 95]: ax2.text(605, factor * np.sqrt(600), f'{p}%', fontsize=8, color=colors[i])
            plot_patient_point(ax2, vol, qave)
            st.pyplot(fig2)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. MISKOLC NOMOGRAM
# ==========================================
def miskolc_nomogram():
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown("#### Fiú Gyermekek")
    st.caption("Referencia: Szabó & Fegyverneki (1995)")
    st.markdown("---")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        vol = st.number_input("Ürített térfogat (ml)", min_value=0.0, value=150.0, step=10.0, key="m_v")
        bsa_opts = {1: "< 0.92 m² (Kicsi)", 2: "0.92 - 1.42 m² (Közepes)", 3: "> 1.42 m² (Nagy)"}
        bsa_sel = st.selectbox("Testfelszín (BSA)", options=[1, 2, 3], format_func=lambda x: bsa_opts[x])
    with c2:
        qmax = st.number_input("Qmax (ml/s)", min_value=0.0, value=18.0, step=1.0, key="m_qm")
    with c3:
        qave = st.number_input("Qave (ml/s)", min_value=0.0, value=10.0, step=1.0, key="m_qa")

    if vol > 0:
        ln_v = math.log(vol + 1)
        params = {
            1: {'max': (5.7244, -13.6033, 3.8131, 6.5131), 'ave': (3.4010, -7.4933, 4.9999, -7.8369)},
            2: {'max': (5.2440, -14.1997, 4.9923, 3.4560), 'ave': (3.1713, -8.5399, 4.0800, -2.6337)},
            3: {'max': (5.4150, -16.1122, 8.5447, -7.4559), 'ave': (4.3957, -14.5260, 6.8810, -11.0350)}
        }
        p_curr = params[bsa_sel]

        def calc_miskolc_percentile(val, A5, B5, A95, B95):
            L5 = A5 * ln_v + B5
            L95 = A95 * ln_v + B95
            mean = (L95 + L5) / 2
            sd = (L95 - L5) / 3.29
            z = (val - mean) / sd
            
            if z < -1.645: return "< 5. percentilis (Kóros)", "#E74C3C"
            if z < -1.28: return "5-10. percentilis (Alacsony)", "#E67E22"
            if z < -0.675: return "10-25. percentilis (Mérsékelt)", "#F1C40F"
            if z < 1.645: return "25-95. percentilis (Normál)", "#27AE60"
            return "> 95. percentilis (Magas)", "#2980B9"

        txt_max, col_max = calc_miskolc_percentile(qmax, *p_curr['max'])
        txt_ave, col_ave = calc_miskolc_percentile(qave, *p_curr['ave'])

        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1: result_card("Qmax Eredmény", txt_max, col_max)
        with r2: result_card("Qave Eredmény", txt_ave, col_ave)

    st.markdown('</div>', unsafe_allow_html=True)

    # Grafikonok
    if vol > 0:
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        st.subheader("Grafikus nézet")
        mg1, mg2 = st.columns(2)
        x_vals = np.linspace(20, 600, 100)
        ln_x = np.log(x_vals + 1)
        colors = ['#E74C3C', '#E67E22', '#F1C40F', '#27AE60', '#27AE60', '#27AE60', '#2980B9']

        def plot_miskolc_curves(ax, title, A5, B5, A95, B95, patient_y, y_limit):
            ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color='#2C3E50', loc='left')
            ax.set_ylim(0, y_limit)
            z_scores = [-1.645, -1.28, -0.675, 0, 0.675, 1.28, 1.645]
            labels = [5, 10, 25, 50, 75, 90, 95]
            mean_A = (A95 + A5) / 2
            mean_B = (B95 + B5) / 2
            sd_A = (A95 - A5) / 3.29
            sd_B = (B95 - B5) / 3.29

            for i, (z, lab) in enumerate(zip(z_scores, labels)):
                A_z = mean_A + z * sd_A
                B_z = mean_B + z * sd_B
                y_vals = A_z * ln_x + B_z
                ax.plot(x_vals, y_vals, linewidth=1.5, alpha=0.7, color=colors[i])
                if lab in [5, 50, 95]: ax.text(605, y_vals[-1], f'{lab}%', fontsize=8, color=colors[i])
            plot_patient_point(ax, vol, patient_y)

        with mg1:
            figm1, axm1 = create_clean_plot("Miskolc Qmax", "Térfogat (ml)", "Qmax (ml/s)", 600, 50)
            plot_miskolc_curves(axm1, "Qmax Nomogram", *p_curr['max'], qmax, 50)
            st.pyplot(figm1)

        with mg2:
            figm2, axm2 = create_clean_plot("Miskolc Qave", "Térfogat (ml)", "Qave (ml/s)", 600, 30)
            plot_miskolc_curves(axm2, "Qave Nomogram", *p_curr['ave'], qave, 30)
            st.pyplot(figm2)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. TOGURI NOMOGRAM (NINCS GRAFIKON)
# ==========================================
def toguri_nomogram():
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown("#### Toguri - Obstrukció Szűrés (Fiúk)")
    st.warning("Ez a nomogram kifejezetten az alacsony áramlás (obstrukció) szűrésére készült.")
    st.markdown("---")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        vol = st.number_input("Ürített térfogat (ml)", min_value=0.0, value=140.0, step=10.0, key="t_v")
        bsa_opts = {0: "< 1.1 m² (Kicsi)", 1: "≥ 1.1 m² (Nagy)"}
        bsa_sel = st.selectbox("Testfelszín (BSA)", options=[0, 1], format_func=lambda x: bsa_opts[x])
    with c2:
        qmax = st.number_input("Qmax (ml/s)", min_value=0.0, value=12.0, step=1.0, key="t_qm")
    with c3:
        qave = st.number_input("Qave (ml/s)", min_value=0.0, value=8.0, step=1.0, key="t_qa")

    if vol > 0:
        # Toguri Adatok
        limits_max_small = [(62.5, 4.0, 4.5, 5.0, 5.5, 6.0), (112.5, 7.3, 9.0, 10.0, 8.5, 10.0), (162.5, 10.0, 12.5, 11.5, 13.0, 14.0), (9999, 11.0, 14.0, 13.5, 13.0, 15.0)]
        limits_max_large = [(62.5, 5.5, 8.0, 6.0, 7.0, 8.0), (112.5, 11.0, 13.0, 13.5, 13.0, 14.0), (162.5, 14.0, 16.0, 15.0, 17.0, 18.0), (9999, 16.0, 19.0, 17.0, 19.0, 20.0)]
        limits_ave_small = [(62.5, 3.4, 3.8, 4.5, 4.9, 5.0), (112.5, 4.9, 5.6, 6.0, 6.6, 6.9), (162.5, 7.9, 8.3, 8.9, 9.3, 9.6), (9999, 7.4, 7.9, 9.4, 9.7, 10.0)]
        limits_ave_large = [(62.5, 6.0, 6.3, 6.6, 6.8, 7.4), (112.5, 8.2, 8.8, 9.1, 9.4, 10.1), (162.5, 10.1, 11.4, 11.7, 12.0, 12.0), (9999, 11.1, 11.5, 11.7, 12.4, 13.2)]

        curr_max = limits_max_large if bsa_sel == 1 else limits_max_small
        curr_ave = limits_ave_large if bsa_sel == 1 else limits_ave_small

        def evaluate_toguri(val, v_in, table):
            row = next(r for r in table if v_in < r[0])
            thresholds = sorted(row[1:]) 
            if val < thresholds[0]: return "< 5. percentilis (Kóros)", "#E74C3C"
            if val < thresholds[1]: return "5-10. percentilis (Nagyon Alacsony)", "#E67E22"
            if val < thresholds[2]: return "10-15. percentilis (Alacsony)", "#F1C40F"
            if val < thresholds[3]: return "15-20. percentilis (Alacsony)", "#F1C40F"
            if val < thresholds[4]: return "20-25. percentilis (Mérsékelt)", "#34C759"
            return "> 25. percentilis (Normál)", "#2980B9"

        txt_max, col_max = evaluate_toguri(qmax, vol, curr_max)
        txt_ave, col_ave = evaluate_toguri(qave, vol, curr_ave)

        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1: result_card("Qmax Diagnózis", txt_max, col_max)
        with r2: result_card("Qave Diagnózis", txt_ave, col_ave)

    st.markdown('</div>', unsafe_allow_html=True)

# --- MENÜRENDSZER ---
tabs = st.tabs(["Liverpool", "Miskolc", "Toguri"])

with tabs[0]:
    liverpool_nomogram()
with tabs[1]:
    miskolc_nomogram()
with tabs[2]:
    toguri_nomogram()

# --- LÁBLÉC ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #BDC3C7; font-size: 0.8rem; margin-top: 20px; margin-bottom: 20px;">
    © 2025 <b>Gémesi Marcell</b> | Minden jog fenntartva.<br>
    Klinikai döntéstámogató segédeszköz.
</div>
""", unsafe_allow_html=True)
