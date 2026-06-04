import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import json
from google import genai 

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Kalori AI Workspace", page_icon="🍏", layout="wide", initial_sidebar_state="expanded")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
import gspread
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KaloriKu") 
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
    
    # Ambil data global
    data_semua = worksheet.get_all_records()
    df = pd.DataFrame(data_semua) if len(data_semua) > 0 else pd.DataFrame()
    kalori_hari_ini = 0
    
    if not df.empty:
        df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
        df['Kalori'] = pd.to_numeric(df['Kalori'])
        df['Protein'] = pd.to_numeric(df['Protein'])
        df['Karbohidrat'] = pd.to_numeric(df['Karbohidrat'])
        df['Lemak'] = pd.to_numeric(df['Lemak'])
        kalori_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Kalori'].sum()
        
    persen_kalori = min((kalori_hari_ini / target_kalori) if target_kalori > 0 else 0, 1.0)
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

    # --- FITUR TABEL RIWAYAT MAKANAN SEPERTI GAMBAR ---
    st.write("")
    st.markdown("#### 📋 History Konsumsi Makanan")
    
    if not df.empty:
        # Meniru desain filter berdampingan dari referensi gambar
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            filter_tabel = st.selectbox("Filter Periode:", 
                ["Hari Ini", "Minggu Ini", "Bulan Ini", "3 Bulan Terakhir", "6 Bulan Terakhir", "Tahun Ini", "Semua Waktu"],
                index=2, key="dash_time"
            )
            
        with col_f2:
            pil_waktu = st.multiselect("Filter Waktu Makan:", 
                ["Sarapan", "Makan Siang", "Makan Malam", "Cemilan"], 
                default=["Sarapan", "Makan Siang", "Makan Malam", "Cemilan"], 
                key="dash_waktu"
            )
        
        # Logika filter waktu
        hari_ini_tabel = datetime.today().date()
        if filter_tabel == "Hari Ini": start_date_tabel = hari_ini_tabel
        elif filter_tabel == "Minggu Ini": start_date_tabel = hari_ini_tabel - timedelta(days=hari_ini_tabel.weekday())
        elif filter_tabel == "Bulan Ini": start_date_tabel = hari_ini_tabel.replace(day=1)
        elif filter_tabel == "3 Bulan Terakhir": start_date_tabel = hari_ini_tabel - timedelta(days=90)
        elif filter_tabel == "6 Bulan Terakhir": start_date_tabel = hari_ini_tabel - timedelta(days=180)
        elif filter_tabel == "Tahun Ini": start_date_tabel = hari_ini_tabel.replace(month=1, day=1)
        else: start_date_tabel = hari_ini_tabel - timedelta(days=3650)
        
        # Terapkan filter Waktu Makan & Periode ke Dataframe
        df_tabel_dash = df[(df['Tanggal'] >= start_date_tabel) & 
                           (df['Tanggal'] <= hari_ini_tabel) & 
                           (df['Waktu'].isin(pil_waktu))]
        
        # Tampilkan DataFrame
        st.dataframe(df_tabel_dash.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada riwayat jurnal makanan untuk ditampilkan.")

# ==========================================
# HALAMAN 2: ANALITIK
# ==========================================
elif menu_pilihan == "Analitik":
    buat_banner("📈 Deep Analytics", "Analisis pola makan, konsistensi target, dan kebiasaan nutrisi Anda.", "linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%)")
    
    if not df.empty:
        df_daily = df.groupby('Tanggal')['Kalori'].sum().reset_index()
        df_daily['Status'] = df_daily['Kalori'].apply(lambda x: 'Tercapai' if x <= target_kalori else 'Melebihi Target')
        
        win_rate = (len(df_daily[df_daily['Status'] == 'Tercapai']) / len(df_daily)) * 100
        streak_saat_ini = 0
        df_daily_sorted = df_daily.sort_values('Tanggal', ascending=False)
        for stat in df_daily_sorted['Status']:
            if stat == 'Tercapai': streak_saat_ini += 1
            else: break
                
        st.markdown("### 🏆 Consistency Target & Streak")
        c1, c2 = st.columns([1, 2.5])
        with c1:
            buat_kartu("🎯", "WIN RATE", f"{win_rate:.1f}%", "#10b981", "Persentase tepat target")
            st.write("")
            buat_kartu("🔥", "CURRENT STREAK", f"{streak_saat_ini} Hari", "#f59e0b", "Berturut-turut sesuai target")
        
        with c2:
            with st.container():
                st.markdown("**📅 Daily Calorie Heatmap**")
                fig_cal = px.bar(df_daily, x='Tanggal', y='Kalori', color='Status', color_discrete_map={'Tercapai': '#10b981', 'Melebihi Target': '#ef4444'})
                fig_cal.add_hline(y=target_kalori, line_dash="dash", line_color="gray", annotation_text="Batas Target")
                fig_cal.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
                st.plotly_chart(fig_cal, use_container_width=True)

        st.divider()
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("### 🕒 Meal Timing Distribution")
            st.caption("Porsi kalori berdasarkan waktu makan")
            df_waktu = df.groupby('Waktu')['Kalori'].sum().reset_index()
            fig_timing = px.pie(df_waktu, values='Kalori', names='Waktu', hole=0.5, color_discrete_sequence=["#f59e0b", "#3b82f6", "#8b5cf6", "#ec4899"])
            fig_timing.update_traces(textposition='inside', textinfo='percent+label')
            fig_timing.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
            st.plotly_chart(fig_timing, use_container_width=True)

        with col_m2:
            st.markdown("### 🔥 Top 5 Burner Foods")
            st.caption("Makanan paling sering dikonsumsi")
            df_top = df.groupby('Makanan').agg(Frekuensi=('Makanan', 'count'), Total_Kalori=('Kalori', 'sum')).reset_index()
            df_top['Rata_Kalori'] = df_top['Total_Kalori'] / df_top['Frekuensi']
            df_top5 = df_top.nlargest(5, 'Frekuensi').sort_values('Frekuensi', ascending=True)
            
            fig_top = px.bar(df_top5, x='Frekuensi', y='Makanan', orientation='h', text=df_top5['Rata_Kalori'].apply(lambda x: f"{x:.0f} Kcal"), color_discrete_sequence=["#ec4899"])
            fig_top.update_traces(textposition='inside')
            fig_top.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0), xaxis_title="Jumlah Kali Dimakan", yaxis_title="")
            st.plotly_chart(fig_top, use_container_width=True)

        st.divider()
        st.markdown("### ⚖️ Macro Split Trend")
        st.caption("Keseimbangan asupan Protein, Karbohidrat, dan Lemak harian")
        df_macro_trend = df.groupby('Tanggal')[['Protein', 'Karbohidrat', 'Lemak']].sum().reset_index()
        fig_area = px.area(df_macro_trend, x='Tanggal', y=['Protein', 'Karbohidrat', 'Lemak'], color_discrete_map={'Protein': '#3b82f6', 'Karbohidrat': '#f59e0b', 'Lemak': '#ec4899'})
        fig_area.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0), yaxis_title="Total Gram (g)", xaxis_title="")
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("Belum ada data analitik.")

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
            
            if submit_ai and makanan_input:
                with st.spinner("Gemini sedang menganalisis nutrisi makanan Anda..."):
                    try:
                        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                        prompt = f"""
                        Anda adalah ahli gizi. Berikan estimasi total nutrisi untuk porsi makanan ini: '{makanan_input}'.
                        PENTING: Balas HANYA dengan format JSON persis seperti ini (tanpa backtick, tanpa teks pembuka/penutup):
                        {{"kalori": 0, "protein": 0, "karbohidrat": 0, "lemak": 0}}
                        """
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                        teks_bersih = response.text.replace('```json', '').replace('```', '').strip()
                        data_nutrisi = json.loads(teks_bersih)
                        
                        kalori = int(data_nutrisi.get("kalori", 0))
                        protein = int(data_nutrisi.get("protein", 0))
                        karbo = int(data_nutrisi.get("karbohidrat", 0))
                        lemak = int(data_nutrisi.get("lemak", 0))
                        
                        tanggal_teks = datetime.today().strftime("%Y-%m-%d")
                        worksheet.append_row([tanggal_teks, waktu_makan, makanan_input, kalori, protein, karbo, lemak])
                        
                        st.success(f"✅ Berhasil dicatat: **{makanan_input}**")
                        st.info(f"📊 **Estimasi AI:** {kalori} Kcal | Protein: {protein}g | Karbo: {karbo}g | Lemak: {lemak}g")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Gagal menganalisis. Error: {e}")
