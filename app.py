import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu 

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Kalori AI Workspace", page_icon="🍏", layout="wide", initial_sidebar_state="expanded")

# --- GAYA DESAIN CUSTOM (CSS) SUPER PREMIUM ---
st.markdown("""
    <style>
    /* Memaksimalkan lebar layar dan membuang ruang kosong */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    
    /* Menarik Sidebar ke atas */
    [data-testid="stSidebar"] .block-container { padding-top: 1.5rem !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* Efek Glassmorphism Modern untuk Kartu */
    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(16, 185, 129, 0.5); /* Glow hijau segar */
        box-shadow: 0 12px 40px 0 rgba(16, 185, 129, 0.15);
    }
    
    /* Tipografi */
    .card-title { font-size: 14px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; color: #888; letter-spacing: 1px;}
    .card-value { font-size: 36px; font-weight: 900; margin-bottom: 5px; line-height: 1.1;}
    .card-subtext { font-size: 13px; color: #888; font-weight: 500;}
    h1, h2, h3, h4 { font-weight: 800 !important; letter-spacing: -0.5px; }
    
    /* Merapikan Form */
    [data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, 0.2); }
    </style>
""", unsafe_allow_html=True)

# --- FUNGSI UI KOMPONEN ---
def buat_kartu(icon, judul, nilai, warna_nilai, teks_bawah):
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-title">{icon} {judul}</div>
        <div class="card-value" style="color: {warna_nilai};">{nilai}</div>
        <div class="card-subtext">{teks_bawah}</div>
    </div>
    """, unsafe_allow_html=True)

def buat_banner(judul, subjudul, gradient="linear-gradient(90deg, #064e3b 0%, #10b981 100%)"):
    st.markdown(f"""
    <div style='background: {gradient}; padding: 30px 40px; border-radius: 16px; color: white; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
        <h1 style='color: white; margin-top: 0; font-size: 38px; font-weight: 900;'>{judul}</h1>
        <p style='margin-bottom: 0; font-size: 16px; opacity: 0.9; font-weight: 500;'>{subjudul}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# SIDEBAR (NAVIGASI TANPA DROPDOWN)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>🍏 Kalori AI</h2>", unsafe_allow_html=True)
    
    # Navigasi Modern (Bukan Dropdown)
    menu_pilihan = option_menu(
        menu_title=None,  
        options=["Dashboard", "Analitik", "Input Makanan"], 
        icons=["grid-1x2-fill", "activity", "egg-fried"], 
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"8px 0px", "font-weight": "600", "border-radius": "10px"},
            "nav-link-selected": {"background-color": "#10b981", "color": "white", "box-shadow": "0 4px 12px rgba(16,185,129,0.3)"},
        }
    )
    
    st.divider()
    
    # Widget Filter & Ringkasan Cepat di Sidebar
    st.markdown("### 🎯 Target Harian")
    target_kalori = st.number_input("Kalori (kcal)", value=2000, step=100)
    st.progress(0.65) # Dummy progress
    st.caption("1,300 / 2,000 kcal terpenuhi")

# ==========================================
# HALAMAN 1: DASHBOARD
# ==========================================
if menu_pilihan == "Dashboard":
    buat_banner("Hello, Health Enthusiast! 👋", "Pantau asupan nutrisi dan capai target kalori harianmu bersama AI.")
    
    # ROW 1: KARTU METRIK UTAMA
    k1, k2, k3, k4 = st.columns(4)
    with k1: buat_kartu("🔥", "KALORI MASUK", "1,300", "#10b981", "Kcal konsumsi hari ini")
    with k2: buat_kartu("🥩", "PROTEIN", "85g", "#3b82f6", "Dari target 120g")
    with k3: buat_kartu("🍚", "KARBOHIDRAT", "150g", "#f59e0b", "Dari target 200g")
    with k4: buat_kartu("🥑", "LEMAK", "40g", "#ec4899", "Dari target 60g")
    
    st.write("")
    
    # ROW 2: GRAFIK FULL WIDTH
    g1, g2 = st.columns([6, 4])
    with g1:
        st.markdown("#### 📊 Weekly Calorie Trend")
        # Dummy data untuk contoh tampilan
        df_trend = pd.DataFrame({
            "Hari": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
            "Kalori": [1900, 2100, 1950, 2050, 1800, 2200, 1300]
        })
        fig_line = px.line(df_trend, x='Hari', y='Kalori', markers=True, color_discrete_sequence=["#10b981"])
        fig_line.update_traces(line_shape='spline', line=dict(width=4), marker=dict(size=8))
        fig_line.add_hline(y=2000, line_dash="dash", line_color="gray", annotation_text="Target")
        fig_line.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_line, use_container_width=True)
            
    with g2:
        st.markdown("#### 🥗 Macros Breakdown")
        df_macros = pd.DataFrame({"Makro": ["Protein", "Karbohidrat", "Lemak"], "Gram": [85, 150, 40]})
        fig_pie = px.pie(df_macros, values='Gram', names='Makro', hole=0.6, color_discrete_sequence=["#3b82f6", "#f59e0b", "#ec4899"])
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# HALAMAN 2: ANALITIK
# ==========================================
elif menu_pilihan == "Analitik":
    buat_banner("📈 Deep Analytics", "Analisis pola makan dan kebiasaan nutrisi Anda.", "linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%)")
    
    st.info("Fitur analitik lanjutan akan ditampilkan di sini. (Grafik rata-rata bulanan, korelasi kalori vs berat badan, dll).")
    
    # Contoh Layout Kosong yang rapi
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("<div style='height: 300px; display: flex; align-items: center; justify-content: center; color: gray;'>[ Area Grafik Distribusi Waktu Makan ]</div>", unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown("<div style='height: 300px; display: flex; align-items: center; justify-content: center; color: gray;'>[ Area Grafik Top Kalori ]</div>", unsafe_allow_html=True)

# ==========================================
# HALAMAN 3: INPUT MAKANAN
# ==========================================
elif menu_pilihan == "Input Makanan":
    st.markdown("<h2 style='margin-bottom: 20px;'>🍳 Catat Jurnal Makanan</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("Masukkan detail makanan yang baru saja Anda konsumsi.")
        with st.form("form_kalori"):
            col1, col2 = st.columns(2)
            with col1:
                waktu_makan = st.selectbox("Waktu Makan", ["Sarapan", "Makan Siang", "Makan Malam", "Cemilan"])
                nama_makanan = st.text_input("Nama Makanan / Minuman")
            with col2:
                kalori = st.number_input("Total Kalori (kcal)", min_value=0, step=50)
                porsi = st.number_input("Jumlah Porsi", min_value=1.0, step=0.5)
                
            st.markdown("#### Estimasi Makronutrien (Opsional)")
            m1, m2, m3 = st.columns(3)
            with m1: protein = st.number_input("Protein (g)", min_value=0)
            with m2: karbo = st.number_input("Karbohidrat (g)", min_value=0)
            with m3: lemak = st.number_input("Lemak (g)", min_value=0)
            
            st.write("")
            submit = st.form_submit_button("Simpan ke Jurnal", use_container_width=True)
            
            if submit:
                st.success(f"✅ {nama_makanan} berhasil dicatat! (+{kalori} kcal)")
