import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from streamlit_gsheets import GSheetsConnection

# 1. Membaca API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Pelacak Kalori AI", page_icon="🍏")
st.title("🍏 Dashboard Pelacak Kalori AI")

# --- FITUR BARU: Hubungkan ke Google Sheets ---
# Streamlit akan membaca URL Google Sheets dari konfigurasi rahasia nanti
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Membaca data yang sudah ada di Sheets
    df_existing = conn.read(ttl="5m") # cache selama 5 menit agar hemat kuota
except Exception as e:
    df_existing = pd.DataFrame(columns=["Tanggal", "Makanan", "Kalori"])

if not api_key:
    st.error("Peringatan: API Key tidak ditemukan. Pastikan file .env sudah dibuat dan diisi.")
else:
    client = genai.Client(api_key=api_key)
    
    st.write("Ceritakan apa yang baru saja Anda makan/minum dengan bahasa santai.")
    user_input = st.text_area("Contoh: 'Tadi siang makan bakso seporsi sama es jeruk'", height=100)
    
    if st.button("Analisis Kalori & Simpan"):
        if user_input:
            with st.spinner("AI sedang menganalisis dan menyimpan data..."):
                prompt_instruksi = f"""
                Kamu adalah ahli gizi. Pengguna akan memberikan teks santai tentang apa yang mereka makan.
                Tugasmu adalah memperkirakan jumlah kalori total dari makanan tersebut.
                Keluarkan jawabanmu HANYA dalam format JSON persis seperti contoh di bawah ini, tanpa menggunakan block markdown (```json) dan tanpa teks pembuka/penutup apapun.
                
                Contoh output:
                {{
                    "makanan_terdeteksi": "Bakso Seporsi, Es Jeruk",
                    "estimasi_kalori": 650
                }}
                
                Teks pengguna: "{user_input}"
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_instruksi
                    )
                    
                    raw_json = response.text.strip()
                    data_kalori = json.loads(raw_json)
                    
                    # --- FITUR BARU: Menyiapkan Baris Data Baru ---
                    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_row = pd.DataFrame([{
                        "Tanggal": waktu_sekarang,
                        "Makanan": data_kalori["makanan_terdeteksi"],
                        "Kalori": int(data_kalori["estimasi_kalori"])
                    }])
                    
                    # Menggabungkan data lama di Sheets dengan baris baru
                    df_updated = pd.concat([df_existing, new_row], ignore_index=True)
                    
                    # Menulis kembali seluruh data ke Google Sheets
                    conn.update(data=df_updated)
                    
                    st.success("Berhasil dianalisis dan disimpan permanen ke Google Sheets!")
                    st.metric(label="Kalori Terdeteksi", value=f"{data_kalori['estimasi_kalori']} kcal")
                    
                    # Memaksa halaman muat ulang agar tabel & grafik langsung terupdate
                    st.rerun()
                    
                except json.JSONDecodeError:
                    st.error("Format AI salah, coba ulangi input kalimat Anda.")
                except Exception as e:
                    st.error(f"Gagal menyimpan ke Google Sheets: {e}")
        else:
            st.warning("Silakan ketikkan makanan Anda terlebih dahulu.")
    
    # --- FITUR BARU: Analitik & Dashboard Permanen ---
    if not df_existing.empty:
        st.divider()
        st.subheader("📊 Analitik & Riwayat Makan Permanen")
        
        # Konversi kolom kalori ke angka agar bisa dijumlahkan
        df_existing["Kalori"] = pd.to_numeric(df_existing["Kalori"], errors='coerce').fillna(0)
        
        total_kalori = df_existing["Kalori"].sum()
        st.info(f"**Total Kalori yang Pernah Tercatat:** {int(total_kalori)} kcal")
        
        # Membuat Dua Kolom untuk Grafik dan Tabel agar Desainnya Bagus
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Grafik Konsumsi:**")
            # Menggunakan Tanggal dan Makanan sebagai sumbu grafik
            df_chart = df_existing.copy()
            df_chart['Label'] = df_chart['Tanggal'].str.slice(5, 10) + " - " + df_chart['Makanan']
            st.bar_chart(df_chart.set_index('Label')['Kalori'])
            
        with col2:
            st.write("**Tabel Data Konten:**")
            st.dataframe(df_existing, use_container_width=True)
