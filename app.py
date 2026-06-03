import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from streamlit_gsheets import GSheetsConnection

# 1. Konfigurasi Halaman (WAJIB DI PALING ATAS)
st.set_page_config(page_title="Dashboard Kalori Premium", page_icon="🍃", layout="wide")

# --- FITUR SUPER PREMIUM: CSS INJECTION (GLASSMORPHISM) ---
st.markdown("""
<style>
    /* 1. Latar Belakang Utama Aplikasi (Gradien Gelap Premium) */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }
    
    /* 2. Glassmorphism pada Sidebar Navigation */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 3. Glassmorphism pada Kotak Metrik (Grid Dashboard) */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    
    /* Efek melayang saat kursor diarahkan ke kotak metrik */
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
    }
    
    /* Warna Teks Metrik Utama */
    [data-testid="stMetricValue"] {
        color: #2ECC71 !important;
        font-weight: 800;
    }

    /* 4. Tombol Premium Melayang */
    .stButton > button {
        background: linear-gradient(135deg, #2ECC71, #27AE60);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.6);
        color: white;
    }
    
    /* Menghaluskan garis pembatas */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 2. Membaca API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 3. Mengambil Data dari Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existing = conn.read(ttl=0).dropna(subset=["Makanan"])
    df_existing["Kalori"] = pd.to_numeric(df_existing["Kalori"], errors='coerce').fillna(0)
except Exception as e:
    df_existing = pd.DataFrame(columns=["Tanggal", "Makanan", "Kalori"])

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    # Menggunakan HTML sederhana untuk Logo agar lebih estetik
    st.markdown("<h2 style='text-align: center; color: #2ECC71;'>🍃 KaloriGlobal</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio(
        "Pilih Halaman:",
        ["Dashboard", "Analitik", "Input Makanan"],
        label_visibility="collapsed"
    )
    st.write("---")
    st.markdown("<div style='opacity: 0.7; text-align: center;'>👤 <b>Admin Dashboard</b></div>", unsafe_allow_html=True)

# --- KONTEN HALAMAN ---

if menu == "Dashboard":
    st.markdown("<h1>Dashboard <span style='color: #2ECC71;'>Ringkasan</span></h1>", unsafe_allow_html=True)
    
    if df_existing.empty:
        st.info("Belum ada data makanan. Silakan ke menu 'Input Makanan'.")
    else:
        # GRID MODERN
        col1, col2, col3 = st.columns(3)
        
        total_kalori = df_existing["Kalori"].sum()
        makanan_terakhir = df_existing.iloc[-1]["Makanan"]
        total_entri = len(df_existing)
        
        with col1:
            st.metric(label="Total Kalori (kcal)", value=f"{int(total_kalori)}")
        with col2:
            st.metric(label="Total Porsi", value=f"{total_entri}")
        with col3:
            st.metric(label="Konsumsi Terakhir", value=makanan_terakhir)
            
        st.write("---")
        st.markdown("### 📈 Tren Konsumsi Terakhir")
        df_recent = df_existing.tail(5)
        df_recent['Label'] = df_recent['Tanggal'].str.slice(11, 16) + " - " + df_recent['Makanan']
        st.bar_chart(df_recent.set_index('Label')['Kalori'], color="#2ECC71")

elif menu == "Analitik":
    st.markdown("<h1>Analitik <span style='color: #2ECC71;'>Mendalam</span></h1>", unsafe_allow_html=True)
    
    if df_existing.empty:
        st.warning("Data masih kosong.")
    else:
        st.markdown("#### Riwayat Konsumsi Keseluruhan")
        df_chart = df_existing.copy()
        df_chart['Label'] = df_chart['Tanggal'].str.slice(5, 10) + " - " + df_chart['Makanan']
        
        st.area_chart(df_chart.set_index('Label')['Kalori'], color="#2ECC71")
        
        st.markdown("#### Tabel Data Mentah")
        st.dataframe(df_existing, use_container_width=True)

elif menu == "Input Makanan":
    st.markdown("<h1>Ceritakan <span style='color: #2ECC71;'>Makananmu</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.8;'>AI cerdas kami akan mengekstrak data kalori secara otomatis ke dalam grid modern Anda.</p>", unsafe_allow_html=True)
    
    if not api_key:
        st.error("API Key belum diatur.")
    else:
        client = genai.Client(api_key=api_key)
        user_input = st.text_area("Contoh: 'Tadi siang makan nasi goreng kambing 1 piring...'", height=150)
        
        if st.button("✨ Analisis & Simpan ke Database"):
            if user_input:
                with st.spinner("AI sedang memproses pesanan Anda..."):
                    prompt_instruksi = f"""
                    Kamu adalah ahli gizi. Keluarkan jawaban HANYA dalam format JSON.
                    Contoh: {{"makanan_terdeteksi": "Nasi Goreng Kambing", "estimasi_kalori": 750}}
                    Teks pengguna: "{user_input}"
                    """
                    try:
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_instruksi)
                        data_kalori = json.loads(response.text.strip())
                        
                        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M")
                        new_row = pd.DataFrame([{"Tanggal": waktu_sekarang, "Makanan": data_kalori["makanan_terdeteksi"], "Kalori": int(data_kalori["estimasi_kalori"])}])
                        df_updated = pd.concat([df_existing, new_row], ignore_index=True)
                        
                        conn.update(data=df_updated)
                        st.success(f"Berhasil disimpan! ({data_kalori['estimasi_kalori']} kcal)")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")
            else:
                st.warning("Kolom tidak boleh kosong!")
