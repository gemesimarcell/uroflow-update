import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math

# --- 1. OLDAL BEÁLLÍTÁSOK ---
st.set_page_config(page_title="Uroflowmetria kiértékelés", layout="wide")

# --- STÍLUS (CSS - Modern Design) ---
st.markdown("""
    <style>
    /* Fő háttér és betűtípus */
    .main {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Címsorok */
    h1 { color: #2c3e50; font-weight: 700; letter-spacing: -0.5px; }
    h3 { color: #7f8c8d; font-weight: 400; margin-bottom: 20px; }

    /* Kártya dobozok (fehér háttér, árnyék) */
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: 1px solid #edf2f7;
    }

    /* Gombok stílusa */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 45px;
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 4px 6px rgba(52, 152, 219, 0.2);
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(52, 152, 219, 0.3);
    }

    /* Eredmény dobozok */
    .result-box {
        padding: 15px 20px;
        background: #ffffff;
        border-radius: 10px;
        border-left: 5px solid #bdc3c7; /* Alapértelmezett szürke */
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 10px;
    }
    
    .metric-label {
        font-size: 0.85em;
        color: #95a5a6;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.4em;
        font-weight: 700;
        color: #2c3e50;
    }
    
    /* Figyelmeztetések eltüntetése a plotok körül */
    canvas { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- CÍMSOR ---
st.title("Uroflow kiértékelés")
st.markdown("")

with st.expander("Jogi Nyilatkozat (Kattints a megnyitáshoz)"):
    st.warning("""
    Ez az alkalmazás kizárólag tájékoztató jellegű segédeszköz. 
    A számítások a szakirodalomban publikált nomogramokon alapulnak (Liverpool, Miskolc, Toguri), de a klinikai döntéshozatal minden esetben a vizsgáló szakorvos felelőssége.
    A fejlesztő nem vállal felelősséget az eredmények alapján hozott döntésekért.
    """)

# --- SEGÉDFÜGGVÉNYEK ---
def create_plot(title, xlabel, ylabel, x_max, y_max):
    fig, ax = plt.subplots(figsize=(8, 5))
    # Modern rács és stílus
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color='#34495e')
    ax.set_xlabel(xlabel, fontsize=10, color='#7f8c8d')
    ax.set_ylabel(ylabel, fontsize=10, color='#7f8c8d')
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.grid(True, which='both', linestyle=':', linewidth=0.8, alpha=0.5)
    return fig, ax

def plot_patient_point(ax, x, y):
    ax.scatter(x, y, color='#e74c3c', s=100, zorder=10, marker='X', edgecolors='white', label='Páciens')
    ax.legend(loc='upper left', frameon=True)

# ==========================================
# 1. LIVERPOOL NOMOGRAM
# ==========================================
def liverpool_nomogram():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.info("Férfiak (50 év alatt) áramlása")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        vol = st.number_input("Ürített térfogat (ml)", min_value=0.0, value=400.0, step=10.0, key="l_v")
    with c2:
        qmax = st.number_input("Maximális áramlás (Qmax - ml/s)", min_value=0.0, value=25.0, step=1.0, key="l_qm")
        qave = st.number_input("Átlagos áramlás (Qave - ml/s)", min_value=0.0, value=15.0, step=1.0, key="l_qa")

    if vol > 0:
        # Percentilis logika
        def get_band_text(val, limits):
            # limits: [5p, 10p, 25p, 50p, 75p, 90p, 95p]
            if val < limits[0]: return "< 5. percentilis (Kóros)", "#e74c3c" # Piros
            if val < limits[1]: return "5-10. percentilis (Alacsony)", "#e67e22" # Narancs
            if val < limits[2]: return "10-25. percentilis (Mérsékelt)", "#f1c40f" # Sárga
            if val < limits[3]: return "25-50. percentilis (Átlagos)", "#27ae60" # Zöld
            if val < limits[4]: return "50-75. percentilis (Jó)", "#27ae60"
            if val < limits[5]: return "75-90. percentilis (Kiváló)", "#27ae60"
            if val < limits[6]: return "90-95. percentilis (Kiemelkedő)", "#2980b9" # Kék
            return "> 95. percentilis (Magas)", "#2980b9"

        qmax_limits = [0.75, 0.95, 1.20, 1.50, 1.80, 2.10, 2.35]
        qave_limits = [0.45, 0.55, 0.70, 0.875, 1.05, 1.20, 1.30]

        res_qmax_val = qmax / math.sqrt(vol)
        res_qave_val = qave / math.sqrt(vol)

        txt_max, col_max = get_band_text(res_qmax_val, qmax_limits)
        txt_ave, col_ave = get_band_text(res_qave_val, qave_limits)

        # Eredmény megjelenítés
        with c3:
            st.markdown(f"""
            <div class="result-box" style="border-left-color: {col_max};">
                <div class="metric-label">Qmax Eredmény</div>
                <div class="metric-value" style="color: {col_max};">{txt_max}</div>
            </div>
            <div class="result-box" style="border-left-color: {col_ave};">
                <div class="metric-label">Qave Eredmény</div>
                <div class="metric-value" style="color: {col_ave};">{txt_ave}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Grafikonok
    if vol > 0:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Grafikus ábrázolás")
        g1, g2 = st.columns(2)
        x_vals = np.linspace(50, 600, 100)
        # Színek a görbékhez
        curve_colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60', '#3498db', '#2980b9']
        
        with g1:
            fig1, ax1 = create_plot("Liverpool Qmax", "Térfogat (ml)", "Qmax (ml/s)", 600, 40)
            percentiles = [5, 10, 25, 50, 75, 90, 95]
            for i, (p, factor) in enumerate(zip(percentiles, qmax_limits)):
                y_vals = factor * np.sqrt(x_vals)
                ax1.plot(x_vals, y_vals, label=f'{p}. pc', color=curve_colors[i], linewidth=1.5, alpha=0.8)
                if p in [5, 50, 95]: ax1.text(605, factor * np.sqrt(600), f'{p}%', fontsize=8, color=curve_colors[i])
            plot_patient_point(ax1, vol, qmax)
            st.pyplot(fig1)

        with g2:
            fig2, ax2 = create_plot("Liverpool Qave", "Térfogat (ml)", "Qave (ml/s)", 600, 25)
            for i, (p, factor) in enumerate(zip(percentiles, qave_limits)):
                y_vals = factor * np.sqrt(x_vals)
                ax2.plot(x_vals, y_vals, label=f'{p}. pc', color=curve_colors[i], linewidth=1.5, alpha=0.8)
                if p in [5, 50, 95]: ax2.text(605, factor * np.sqrt(600), f'{p}%', fontsize=8, color=curve_colors[i])
            plot_patient_point(ax2, vol, qave)
            st.pyplot(fig2)
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 2. MISKOLC NOMOGRAM
# ==========================================
def miskolc_nomogram():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.info("Fiú gyermekek áramlása.")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        vol = st.number_input("Ürített térfogat (ml)", min_value=0.0, value=150.0, step=10.0, key="m_v")
        bsa_sel = st.selectbox("Testfelszín (BSA)", options=[1, 2, 3], 
                               format_func=lambda x: {1:"< 0.92 m² (Kicsi)", 2:"0.92 - 1.42 m² (Közepes)", 3:"> 1.42 m² (Nagy)"}[x])
    with c2:
        qmax = st.number_input("Maximális áramlás (Qmax)", min_value=0.0, value=18.0, step=1.0, key="m_qm")
        qave = st.number_input("Átlagos áramlás (Qave)", min_value=0.0, value=10.0, step=1.0, key="m_qa")

    if vol > 0:
        ln_v = math.log(vol + 1)
        # Paraméterek
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
            
            if z < -1.645: return "< 5. percentilis (Kóros)", "#e74c3c"
            if z < -1.28: return "5-10. percentilis (Alacsony)", "#e67e22"
            if z < -0.675: return "10-25. percentilis (Mérsékelt)", "#f1c40f"
            if z < 0: return "25-50. percentilis (Átlagos)", "#27ae60"
            if z < 0.675: return "50-75. percentilis (Jó)", "#27ae60"
            if z < 1.28: return "75-90. percentilis (Kiváló)", "#27ae60"
            if z < 1.645: return "90-95. percentilis (Kiemelkedő)", "#2980b9"
            return "> 95. percentilis (Magas)", "#2980b9"

        txt_max, col_max = calc_miskolc_percentile(qmax, *p_curr['max'])
        txt_ave, col_ave = calc_miskolc_percentile(qave, *p_curr['ave'])

        with c3:
            st.markdown(f"""
            <div class="result-box" style="border-left-color: {col_max};">
                <div class="metric-label">Qmax Becslés</div>
                <div class="metric-value" style="color: {col_max};">{txt_max}</div>
            </div>
            <div class="result-box" style="border-left-color: {col_ave};">
                <div class="metric-label">Qave Becslés</div>
                <div class="metric-value" style="color: {col_ave};">{txt_ave}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Grafikonok
    if vol > 0:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Grafikus ábrázolás")
        mg1, mg2 = st.columns(2)
        x_vals = np.linspace(20, 600, 100)
        ln_x = np.log(x_vals + 1)
        curve_colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60', '#3498db', '#2980b9']

        def plot_miskolc_curves(ax, title, A5, B5, A95, B95, patient_y, y_limit):
            ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color='#34495e')
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
                ax.plot(x_vals, y_vals, label=f'{lab}. pc', linewidth=1.5, alpha=0.8, color=curve_colors[i])
                if lab in [5, 50, 95]: ax.text(605, y_vals[-1], f'{lab}%', fontsize=8, color=curve_colors[i])
            plot_patient_point(ax, vol, patient_y)

        with mg1:
            figm1, axm1 = create_plot("Miskolc Qmax", "Térfogat (ml)", "ml/s", 600, 50)
            plot_miskolc_curves(axm1, "Qmax Nomogram", *p_curr['max'], qmax, 50)
            st.pyplot(figm1)

        with mg2:
            figm2, axm2 = create_plot("Miskolc Qave", "Térfogat (ml)", "ml/s", 600, 30)
            plot_miskolc_curves(axm2, "Qave Nomogram", *p_curr['ave'], qave, 30)
            st.pyplot(figm2)
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 3. TOGURI NOMOGRAM (NINCS GRAFIKON)
# ==========================================
def toguri_nomogram():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.warning("Fiú gyermekek áramlása.")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        vol = st.number_input("Ürített térfogat (ml)", min_value=0.0, value=140.0, step=10.0, key="t_v")
        bsa_sel = st.selectbox("Testfelszín (BSA)", options=[0, 1], 
                               format_func=lambda x: {0:"< 1.1 m² (Kicsi)", 1:"≥ 1.1 m² (Nagy)"}[x])
    with c2:
        qmax = st.number_input("Maximális áramlás (Qmax)", min_value=0.0, value=12.0, step=1.0, key="t_qm")
        qave = st.number_input("Átlagos áramlás (Qave)", min_value=0.0, value=8.0, step=1.0, key="t_qa")

    if vol > 0:
        # Toguri Adatok (Limits)
        limits_max_small = [(62.5, 4.0, 4.5, 5.0, 5.5, 6.0), (112.5, 7.3, 9.0, 10.0, 8.5, 10.0), (162.5, 10.0, 12.5, 11.5, 13.0, 14.0), (9999, 11.0, 14.0, 13.5, 13.0, 15.0)]
        limits_max_large = [(62.5, 5.5, 8.0, 6.0, 7.0, 8.0), (112.5, 11.0, 13.0, 13.5, 13.0, 14.0), (162.5, 14.0, 16.0, 15.0, 17.0, 18.0), (9999, 16.0, 19.0, 17.0, 19.0, 20.0)]
        limits_ave_small = [(62.5, 3.4, 3.8, 4.5, 4.9, 5.0), (112.5, 4.9, 5.6, 6.0, 6.6, 6.9), (162.5, 7.9, 8.3, 8.9, 9.3, 9.6), (9999, 7.4, 7.9, 9.4, 9.7, 10.0)]
        limits_ave_large = [(62.5, 6.0, 6.3, 6.6, 6.8, 7.4), (112.5, 8.2, 8.8, 9.1, 9.4, 10.1), (162.5, 10.1, 11.4, 11.7, 12.0, 12.0), (9999, 11.1, 11.5, 11.7, 12.4, 13.2)]

        curr_max = limits_max_large if bsa_sel == 1 else limits_max_small
        curr_ave = limits_ave_large if bsa_sel == 1 else limits_ave_small

        def evaluate_toguri(val, v_in, table):
            row = next(r for r in table if v_in < r[0])
            # row[1] = 5p, row[2]=10p, row[3]=15p, row[4]=20p, row[5]=25p
            thresholds = sorted(row[1:]) 
            if val < thresholds[0]: return "< 5. percentilis (Kóros)", "#e74c3c"
            if val < thresholds[1]: return "5-10. percentilis (Nagyon Alacsony)", "#e67e22"
            if val < thresholds[2]: return "10-15. percentilis (Alacsony)", "#f1c40f"
            if val < thresholds[3]: return "15-20. percentilis (Alacsony)", "#f1c40f"
            if val < thresholds[4]: return "20-25. percentilis (Mérsékelt)", "#f39c12"
            return "> 25. percentilis (Normál)", "#27ae60"

        txt_max, col_max = evaluate_toguri(qmax, vol, curr_max)
        txt_ave, col_ave = evaluate_toguri(qave, vol, curr_ave)

        with c3:
            st.markdown(f"""
            <div class="result-box" style="border-left-color: {col_max};">
                <div class="metric-label">Qmax Szűrés</div>
                <div class="metric-value" style="color: {col_max};">{txt_max}</div>
            </div>
            <div class="result-box" style="border-left-color: {col_ave};">
                <div class="metric-label">Qave Szűrés</div>
                <div class="metric-value" style="color: {col_ave};">{txt_ave}</div>
            </div>
            """, unsafe_allow_html=True)
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
<div style="text-align: center; color: #95a5a6; font-size: 0.85em; margin-top: 20px;">
    © 2025 <b>Gémesi Marcell</b> | Minden jog fenntartva.<br>
    A szoftver szellemi tulajdona a készítőt illeti.
</div>
""", unsafe_allow_html=True)
