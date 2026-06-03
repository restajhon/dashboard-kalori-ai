import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from streamlit_gsheets import GSheetsConnection

# 1. Konfigurasi Halaman (WAJIB DI PALING ATAS)
st.set_page_config(page_title="Dashboard Kalori", page_icon="🍃", layout="wide")

# 2. Membaca API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 3. Mengambil Data dari Google Sheets (Ditaruh di luar agar semua menu bisa akses)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existing = conn.read(ttl=0).dropna(subset=["Makanan"])
    df_existing["Kalori"] = pd.to_numeric(df_existing["Kalori"], errors='coerce').fillna(0)
except Exception as e:
    df_existing = pd.DataFrame(columns=["Tanggal", "Makanan", "Kalori"])

# --- FITUR BARU: SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("## 🍃 KaloriGlobal") # Meniru logo kiri atas referensi
    st.write("---")
    st.write("NAVIGATION")
    # Membuat menu pilihan
    menu = st.radio(
        "Pilih Halaman:",
        ["Dashboard", "Analitik", "Input Makanan"],
        label_visibility="collapsed" # Menyembunyikan label radio button agar lebih bersih
    )
    st.write("---")
    st.write("👤 **Akun Pengguna**\n\nAdmin Dashboard")

# --- KONTEN HALAMAN BERDASARKAN MENU YANG DIPILIH ---

if menu == "Dashboard":
    st.title("Dashboard Ringkasan")
    
    if df_existing.empty:
        st.info("Belum ada data makanan. Silakan ke menu 'Input Makanan' terlebih dahulu.")
    else:
        # Meniru gaya kotak-kotak metrik di gambar referensi
        col1, col2, col3 = st.columns(3)
        
        total_kalori = df_existing["Kalori"].sum()
        makanan_terakhir = df_existing.iloc[-1]["Makanan"]
        total_entri = len(df_existing)
        
        with col1:
            st.metric(label="Total Kalori Terkumpul", value=f"{int(total_kalori)} kcal")
        with col2:
            st.metric(label="Total Porsi Dicatat", value=f"{total_entri} Porsi")
        with col3:
            st.metric(label="Konsumsi Terakhir", value=makanan_terakhir)
            
        st.divider()
        st.subheader("Tren Konsumsi Terakhir")
        # Mengambil 5 data terakhir untuk grafik sederhana di dashboard
        df_recent = df_existing.tail(5)
        df_recent['Label'] = df_recent['Tanggal'].str.slice(11, 16) + " - " + df_recent['Makanan']
        st.bar_chart(df_recent.set_index('Label')['Kalori'])

elif menu == "Analitik":
    st.title("Analitik Mendalam")
    
    if df_existing.empty:
        st.warning("Data masih kosong.")
    else:
        st.write("Grafik Seluruh Riwayat Konsumsi Anda:")
        df_chart = df_existing.copy()
        df_chart['Label'] = df_chart['Tanggal'].str.slice(5, 10) + " - " + df_chart['Makanan']
        
        # Menampilkan grafik area yang lebih estetik dari bar chart
        st.area_chart(df_chart.set_index('Label')['Kalori'])
        
        st.write("Tabel Data Lengkap:")
        st.dataframe(df_existing, use_container_width=True)

elif menu == "Input Makanan":
    st.title("Ceritakan Makanan Anda")
    st.write("AI kami akan otomatis mengekstrak kalori dari cerita Anda.")
    
    if not api_key:
        st.error("API Key belum diatur.")
    else:
        client = genai.Client(api_key=api_key)
        user_input = st.text_area("Contoh: 'Tadi siang makan bakso seporsi sama es jeruk'", height=150)
        
        if st.button("Analisis & Simpan", type="primary"): # type=primary membuat tombol jadi warna hijau (primaryColor)
            if user_input:
                with st.spinner("Menghitung kalori dan menyimpan ke database..."):
                    prompt_instruksi = f"""
                    Kamu adalah ahli gizi. Keluarkan jawaban HANYA dalam format JSON.
                    Contoh: {{"makanan_terdeteksi": "Bakso, Es Jeruk", "estimasi_kalori": 650}}
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
                        st.rerun() # Refresh agar data baru masuk ke memory
                        
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")
            else:
                st.warning("Ketik sesuatu dulu ya!")
