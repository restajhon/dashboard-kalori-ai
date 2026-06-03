import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from streamlit_gsheets import GSheetsConnection

# 1. Konfigurasi Halaman Utama
st.set_page_config(page_title="Dashboard Kalori", page_icon="🍏", layout="wide")

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
    st.title("🍏 Kalori AI")
    st.write("---")
    
    # Menggunakan selectbox agar sama persis dengan menu referensi Anda
    menu = st.selectbox(
        "Buka Halaman Utama",
        ["Dashboard", "Analitik", "Input Makanan"]
    )
    
    st.write("---")
    st.write("👤 **Admin Dashboard**")

# --- KONTEN HALAMAN ---

if menu == "Dashboard":
    # Meniru judul besar rata tengah
    st.markdown("<h1 style='text-align: center;'>DASHBOARD PELACAK KALORI</h1>", unsafe_allow_html=True)
    
    # Menambahkan gambar banner utama (mirip referensi)
    st.image("https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=2053&auto=format&fit=crop", use_container_width=True)
    st.write("---")
    
    if df_existing.empty:
        st.info("Belum ada data makanan. Silakan ke menu 'Input Makanan'.")
    else:
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
            
        st.divider()
        st.subheader("📈 Tren Konsumsi Terakhir")
        df_recent = df_existing.tail(5)
        df_recent['Label'] = df_recent['Tanggal'].str.slice(11, 16) + " - " + df_recent['Makanan']
        st.bar_chart(df_recent.set_index('Label')['Kalori'])

elif menu == "Analitik":
    st.markdown("<h1 style='text-align: center;'>ANALITIK MENDALAM</h1>", unsafe_allow_html=True)
    st.write("---")
    
    if df_existing.empty:
        st.warning("Data masih kosong.")
    else:
        st.subheader("Riwayat Konsumsi Keseluruhan")
        df_chart = df_existing.copy()
        df_chart['Label'] = df_chart['Tanggal'].str.slice(5, 10) + " - " + df_chart['Makanan']
        st.area_chart(df_chart.set_index('Label')['Kalori'])
        
        st.subheader("Tabel Data Mentah")
        st.dataframe(df_existing, use_container_width=True)

elif menu == "Input Makanan":
    st.markdown("<h1 style='text-align: center;'>INPUT MAKANAN HARIAN</h1>", unsafe_allow_html=True)
    st.write("---")
    st.write("Ceritakan apa yang baru saja Anda makan. AI kami akan otomatis mengekstrak data kalorinya.")
    
    if not api_key:
        st.error("API Key belum diatur.")
    else:
        client = genai.Client(api_key=api_key)
        user_input = st.text_area("Contoh: 'Tadi siang makan nasi padang lauk rendang...'", height=150)
        
        if st.button("Analisis & Simpan"):
            if user_input:
                with st.spinner("AI sedang memproses data..."):
                    prompt_instruksi = f"""
                    Kamu adalah ahli gizi. Keluarkan jawaban HANYA dalam format JSON.
                    Contoh: {{"makanan_terdeteksi": "Nasi Padang Rendang", "estimasi_kalori": 750}}
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
                st.warning("Kolom input tidak boleh kosong!")
