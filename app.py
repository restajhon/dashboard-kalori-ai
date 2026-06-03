import streamlit as st
import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai

# 1. Membaca API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Pelacak Kalori AI", page_icon="🍏")
st.title("🍏 Dashboard Pelacak Kalori AI")

# --- FITUR BARU: Membuat "Ingatan" Sementara (Session State) ---
# Streamlit selalu memuat ulang halaman dari atas ke bawah setiap kali tombol ditekan.
# Session State digunakan agar data riwayat tidak hilang saat halaman dimuat ulang.
if "riwayat_makanan" not in st.session_state:
    st.session_state.riwayat_makanan = []

if not api_key:
    st.error("Peringatan: API Key tidak ditemukan. Pastikan file .env sudah dibuat dan diisi.")
else:
    client = genai.Client(api_key=api_key)
    
    st.write("Ceritakan apa yang baru saja Anda makan/minum dengan bahasa santai.")
    user_input = st.text_area("Contoh: 'Tadi pagi aku makan nasi 150 gram, gorengan tahu 2...'", height=100)
    
    if st.button("Analisis Kalori"):
        if user_input:
            with st.spinner("AI sedang menganalisis makanan Anda..."):
                prompt_instruksi = f"""
                Kamu adalah ahli gizi. Pengguna akan memberikan teks santai tentang apa yang mereka makan.
                Tugasmu adalah memperkirakan jumlah kalori total dari makanan tersebut.
                Keluarkan jawabanmu HANYA dalam format JSON persis seperti contoh di bawah ini, tanpa menggunakan block markdown (```json) dan tanpa teks pembuka/penutup apapun.
                
                Contoh output:
                {{
                    "makanan_terdeteksi": "Nasi Padang + Rendang",
                    "estimasi_kalori": 850
                }}
                
                Teks pengguna: "{user_input}"
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_instruksi
                    )
                    
                    # --- FITUR BARU: Membersihkan Data ---
                    # Menghilangkan spasi ekstra di awal/akhir
                    raw_json = response.text.strip()
                    
                    # Mengubah teks JSON menjadi Dictionary Python agar angkanya bisa dihitung
                    data_kalori = json.loads(raw_json)
                    
                    # Menyimpan data baru ke dalam "Ingatan" (Session State)
                    st.session_state.riwayat_makanan.append({
                        "Makanan": data_kalori["makanan_terdeteksi"],
                        "Kalori": data_kalori["estimasi_kalori"]
                    })
                    
                    st.success("Berhasil ditambahkan!")
                    
                    # Menampilkan metrik kalori tunggal dengan desain UI yang lebih rapi
                    st.metric(label="Kalori dari input terakhir", value=f"{data_kalori['estimasi_kalori']} kcal")
                    
                except json.JSONDecodeError:
                    st.error("Maaf, AI sedang bingung dan tidak memberikan format data yang benar. Coba ubah susunan kalimat Anda.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan jaringan/sistem: {e}")
        else:
            st.warning("Silakan ketikkan makanan Anda terlebih dahulu sebelum menekan tombol.")
    
    # --- FITUR BARU: Menampilkan Grafik dan Tabel Riwayat ---
    # Jika "Ingatan" sudah terisi minimal 1 data, maka tampilkan area riwayat ini
    if len(st.session_state.riwayat_makanan) > 0:
        st.divider() # Garis pembatas
        st.subheader("📊 Ringkasan Hari Ini")
        
        # Mengubah data dari Session State menjadi format Tabel Pandas yang mudah diolah
        df_riwayat = pd.DataFrame(st.session_state.riwayat_makanan)
        
        # Menghitung total keseluruhan kalori di tabel
        total_kalori_hari_ini = df_riwayat["Kalori"].sum()
        
        # Menampilkan indikator total harian
        st.info(f"**Total Kalori Sementara:** {total_kalori_hari_ini} kcal")
        
        # Menampilkan grafik batang (Bar Chart)
        # Sumbu X (bawah) akan mengambil kolom "Makanan"
        st.bar_chart(df_riwayat.set_index("Makanan"))
        
        # Menampilkan tabel data mentahnya secara rapi
        st.write("Detail Makanan:")
        st.dataframe(df_riwayat, use_container_width=True)