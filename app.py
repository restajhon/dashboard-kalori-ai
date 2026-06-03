import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import json
from google import genai # Library Gemini AI

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Kalori AI Workspace", page_icon="🍏", layout="wide", initial_sidebar_state="expanded")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
import gspread
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KaloriKu") # Pastikan nama file Sheets Anda sesuai
worksheet = sheet_file.sheet1 

# --- GAYA DESAIN CUSTOM (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    [data-testid="stSidebar"] .block-container { padding-top: 1.5rem !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        border-radius: 16px; padding: 24px; height: 100%; transition: all 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-5px); border: 1px solid rgba(16, 185, 129, 0.5); box-shadow: 0 12px 40px 0 rgba(16, 185, 129, 0.15); }
    .card-title { font-size: 14px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; color: #888; letter-spacing: 1px;}
    .card-value { font-size: 36px; font-weight: 900; margin-bottom: 5px; line-height: 1.1;}
    .card-subtext { font-size: 13px; color: #888; font-weight: 500;}
    h1, h2, h3, h4 { font-weight: 800 !important; letter-spacing: -0.5px; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, 0.2); }
    </style>
""", unsafe_allow_html=True)

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
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>🍏 Kalori AI</h2>", unsafe_allow_html=True)
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
    st.markdown("### 🎯 Target Harian")
    target_kalori = st.number_input("Kalori (kcal)", value=2000, step=100)
    
    # Ambil data untuk progress bar harian
    data_semua = worksheet.get_all_records()
    df = pd.DataFrame(data_semua) if len(data_semua) > 0 else pd.DataFrame()
    kalori_hari_ini = 0
    if not df.empty:
        df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
        df['Kalori'] = pd.to_numeric(df['Kalori'])
        kalori_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Kalori'].sum()
        
    persen_kalori = min((kalori_hari_ini / target_kalori), 1.0)
    st.progress(persen_kalori)
    st.caption(f"{kalori_hari_ini:,.0f} / {target_kalori:,.0f} kcal terpenuhi")

# ==========================================
# HALAMAN 1: DASHBOARD
# ==========================================
if menu_pilihan == "Dashboard":
    buat_banner("Hello, Health Enthusiast! 👋", "Pantau asupan nutrisi dan capai target kalori harianmu bersama AI.")
    
    protein_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Protein'].sum() if not df.empty else 0
    karbo_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Karbohidrat'].sum() if not df.empty else 0
    lemak_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Lemak'].sum() if not df.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1: buat_kartu("🔥", "KALORI MASUK", f"{kalori_hari_ini:,.0f}", "#10b981", "Kcal konsumsi hari ini")
    with k2: buat_kartu("🥩", "PROTEIN", f"{protein_hari_ini:,.0f}g", "#3b82f6", "Total hari ini")
    with k3: buat_kartu("🍚", "KARBOHIDRAT", f"{karbo_hari_ini:,.0f}g", "#f59e0b", "Total hari ini")
    with k4: buat_kartu("🥑", "LEMAK", f"{lemak_hari_ini:,.0f}g", "#ec4899", "Total hari ini")
    
    st.write("")
    g1, g2 = st.columns([6, 4])
    with g1:
        st.markdown("#### 📊 Weekly Calorie Trend")
        if not df.empty:
            tujuh_hari_lalu = datetime.today().date() - timedelta(days=7)
            df_trend = df[df['Tanggal'] >= tujuh_hari_lalu].groupby('Tanggal')['Kalori'].sum().reset_index()
            fig_line = px.line(df_trend, x='Tanggal', y='Kalori', markers=True, color_discrete_sequence=["#10b981"])
            fig_line.update_traces(line_shape='spline', line=dict(width=4), marker=dict(size=8))
            fig_line.add_hline(y=target_kalori, line_dash="dash", line_color="gray", annotation_text="Target")
            fig_line.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_line, use_container_width=True)
        else: st.info("Belum ada data.")
            
    with g2:
        st.markdown("#### 🥗 Macros Breakdown (Hari Ini)")
        if kalori_hari_ini > 0:
            df_macros = pd.DataFrame({"Makro": ["Protein", "Karbohidrat", "Lemak"], "Gram": [protein_hari_ini, karbo_hari_ini, lemak_hari_ini]})
            fig_pie = px.pie(df_macros, values='Gram', names='Makro', hole=0.6, color_discrete_sequence=["#3b82f6", "#f59e0b", "#ec4899"])
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)
        else: st.info("Belum ada asupan hari ini.")

# ==========================================
# HALAMAN 2: ANALITIK
# ==========================================
elif menu_pilihan == "Analitik":
    buat_banner("📈 Deep Analytics", "Riwayat asupan makanan Anda.", "linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%)")
    if not df.empty:
        st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data.")

# ==========================================
# HALAMAN 3: INPUT MAKANAN (POWERED BY GEMINI)
# ==========================================
elif menu_pilihan == "Input Makanan":
    buat_banner("✨ Jurnal Pintar AI", "Cukup ketik apa yang Anda makan, biarkan Gemini AI menghitung nutrisinya!", "linear-gradient(90deg, #8b5cf6 0%, #a855f7 100%)")
    
    with st.container(border=True):
        with st.form("form_ai", clear_on_submit=True):
            waktu_makan = st.selectbox("Waktu Makan", ["Sarapan", "Makan Siang", "Makan Malam", "Cemilan"])
            makanan_input = st.text_input("Apa yang Anda makan? (Sertakan porsinya)", placeholder="Contoh: 1 mangkok bubur ayam dan sate usus")
            
            st.write("")
            submit_ai = st.form_submit_button("🧠 Hitung & Simpan ke Jurnal", use_container_width=True)
            
            if submit_ai:
                if makanan_input:
                    with st.spinner("Gemini sedang menganalisis nutrisi makanan Anda..."):
                        try:
                            # Memanggil Gemini API
                            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                            
                            prompt = f"""
                            Anda adalah ahli gizi. Berikan estimasi total nutrisi untuk porsi makanan ini: '{makanan_input}'.
                            PENTING: Balas HANYA dengan format JSON persis seperti ini (tanpa backtick, tanpa teks pembuka/penutup):
                            {{"kalori": 0, "protein": 0, "karbohidrat": 0, "lemak": 0}}
                            """
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=prompt,
                            )
                            
                            # Membersihkan dan membaca format JSON dari AI
                            teks_bersih = response.text.replace('```json', '').replace('
```', '').strip()
                            data_nutrisi = json.loads(teks_bersih)
                            
                            kalori = int(data_nutrisi.get("kalori", 0))
                            protein = int(data_nutrisi.get("protein", 0))
                            karbo = int(data_nutrisi.get("karbohidrat", 0))
                            lemak = int(data_nutrisi.get("lemak", 0))
                            
                            # Simpan ke Google Sheets
                            tanggal_teks = datetime.today().strftime("%Y-%m-%d")
                            worksheet.append_row([tanggal_teks, waktu_makan, makanan_input, kalori, protein, karbo, lemak])
                            
                            st.success(f"✅ Berhasil dicatat: **{makanan_input}**")
                            st.info(f"📊 **Estimasi AI:** {kalori} Kcal | Protein: {protein}g | Karbo: {karbo}g | Lemak: {lemak}g")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"Gagal menganalisis. Pastikan API Key valid atau coba kata yang lebih jelas. Error: {e}")
                else:
                    st.warning("Mohon ketik nama makanan terlebih dahulu!")
