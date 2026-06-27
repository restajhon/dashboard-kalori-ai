import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import json
from google import genai 
import gspread
import hashlib 

# --- PENGATURAN HALAMAN WEB ---
st.set_page_config(page_title="Kalori AI Workspace", page_icon="🍏", layout="wide", initial_sidebar_state="expanded")

# --- KONEKSI KE GOOGLE SHEETS ---
kredensial = st.secrets["gcp_service_account"]
gc = gspread.service_account_from_dict(kredensial)
sheet_file = gc.open("KaloriKu") 

# Koneksi Langsung ke Worksheet (Pastikan nama tab di Google Sheets persis seperti ini)
worksheet = sheet_file.sheet1 
ws_users = sheet_file.worksheet("Users")
ws_kegiatan = sheet_file.worksheet("Kegiatan")

# --- FUNGSI KEAMANAN & AUTH ---
def hash_pass(password):
    # Memastikan tidak ada spasi tak terlihat sebelum enkripsi
    password_bersih = str(password).strip()
    return "SECURE_" + hashlib.sha256(str.encode(password_bersih)).hexdigest()

def check_login(username, password):
    users_data = ws_users.get_all_records()
    
    # Membersihkan input dari spasi yang tidak sengaja terketik
    input_u = str(username).strip()
    input_p = str(password).strip()
    
    for user in users_data:
        # Membersihkan data yang ditarik dari Google Sheets
        sheet_u = str(user.get('Username', '')).strip()
        sheet_p = str(user.get('Password', '')).strip()
        
        if sheet_u == input_u and sheet_p == hash_pass(input_p):
            return str(user.get('Name', 'User')).strip()
    return None

def signup_user(username, password, name):
    users_data = ws_users.get_all_records()
    input_u = str(username).strip()
    input_p = str(password).strip()
    input_n = str(name).strip()
    
    if any(str(u.get('Username', '')).strip() == input_u for u in users_data):
        return False
        
    ws_users.append_row([input_u, hash_pass(input_p), input_n])
    return True

# --- SESSION STATE UNTUK LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_display_name = ""

# --- TAMPILAN LOGIN / SIGNUP ---
if not st.session_state.logged_in:
    st.markdown("""
        <style>
        .login-box {
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
            backdrop-filter: blur(10px); border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 16px; padding: 40px; margin-top: 50px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🍏 Kalori AI</h1>", unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["Masuk", "Daftar Baru"])
        
        with tab_login:
            with st.form("login_form"):
                u_in = st.text_input("Username")
                p_in = st.text_input("Password", type="password")
                btn_login = st.form_submit_button("Masuk Sekarang", use_container_width=True)
                if btn_login:
                    name = check_login(u_in, p_in)
                    if name:
                        st.session_state.logged_in = True
                        st.session_state.username = u_in
                        st.session_state.user_display_name = name
                        st.rerun()
                    else:
                        st.error("Username atau Password salah!")
        
        with tab_signup:
            with st.form("signup_form"):
                new_name = st.text_input("Nama Panggilan")
                new_u = st.text_input("Username Baru (Tanpa Spasi)")
                new_p = st.text_input("Password Baru", type="password")
                btn_signup = st.form_submit_button("Buat Akun", use_container_width=True)
                if btn_signup:
                    if len(new_u) > 2 and len(new_p) > 2:
                        if signup_user(new_u, new_p, new_name):
                            st.success("✅ Akun berhasil dibuat! Silakan pindah ke tab 'Masuk'.")
                        else:
                            st.error("Username sudah dipakai orang lain.")
                    else:
                        st.warning("Username dan Password minimal 3 karakter.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() 

# --- GAYA DESAIN CUSTOM (CSS) UNTUK DASHBOARD ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    [data-testid="stSidebar"] .block-container { padding-top: 1.5rem !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(128, 128, 128, 0.2); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
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
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 20px;'>👋 Hai, {st.session_state.user_display_name}!</h3>", unsafe_allow_html=True)
    menu_pilihan = option_menu(
        menu_title=None,  
        options=["Dashboard", "Analitik Nutrisi", "Analitik Kebugaran", "Input Makanan", "Input Kegiatan"], 
        icons=["grid-1x2-fill", "pie-chart-fill", "activity", "egg-fried", "lightning-fill"], 
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
    target_kalori = st.number_input("Target Nutrisi (kcal)", value=1500, step=100)
    
    # AMBIL & FILTER DATA BERDASARKAN USERNAME
    data_semua = worksheet.get_all_records()
    df_raw = pd.DataFrame(data_semua) if len(data_semua) > 0 else pd.DataFrame()
    if not df_raw.empty and 'User' in df_raw.columns:
        df = df_raw[df_raw['User'] == st.session_state.username].copy()
    else:
        df = pd.DataFrame()

    data_keg = ws_kegiatan.get_all_records()
    df_keg_raw = pd.DataFrame(data_keg) if len(data_keg) > 0 else pd.DataFrame()
    if not df_keg_raw.empty and 'User' in df_keg_raw.columns:
        df_keg = df_keg_raw[df_keg_raw['User'] == st.session_state.username].copy()
    else:
        df_keg = pd.DataFrame()
    
    kalori_hari_ini = 0
    kalori_keluar_hari_ini = 0
    
    if not df.empty:
        df['Tanggal'] = pd.to_datetime(df['Tanggal']).dt.date
        df['Kalori'] = pd.to_numeric(df['Kalori'], errors='coerce').fillna(0)
        df['Protein'] = pd.to_numeric(df['Protein'], errors='coerce').fillna(0)
        df['Karbohidrat'] = pd.to_numeric(df['Karbohidrat'], errors='coerce').fillna(0)
        df['Lemak'] = pd.to_numeric(df['Lemak'], errors='coerce').fillna(0)
        kalori_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Kalori'].sum()
        
    if not df_keg.empty:
        df_keg['Tanggal'] = pd.to_datetime(df_keg['Tanggal']).dt.date
        df_keg['Kalori'] = pd.to_numeric(df_keg['Kalori'], errors='coerce').fillna(0)
        kalori_keluar_hari_ini = df_keg[df_keg['Tanggal'] == datetime.today().date()]['Kalori'].sum()

    net_kalori_hari_ini = kalori_hari_ini - kalori_keluar_hari_ini
    persen_kalori = min(max((net_kalori_hari_ini / target_kalori), 0.0), 1.0) if target_kalori > 0 else 0
    st.progress(persen_kalori)
    st.caption(f"{net_kalori_hari_ini:,.0f} / {target_kalori:,.0f} Net Kcal Terpenuhi")
    
    st.write("")
    if st.button("🚪 Keluar Akun", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# HALAMAN 1: DASHBOARD
# ==========================================
if menu_pilihan == "Dashboard":
    buat_banner(f"Welcome to your Workspace, {st.session_state.user_display_name} ✨", "Fitness & Nutrition Tracker Hub — Pantau balans kalori dan progres latihanmu.")
    
    protein_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Protein'].sum() if not df.empty else 0
    karbo_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Karbohidrat'].sum() if not df.empty else 0
    lemak_hari_ini = df[df['Tanggal'] == datetime.today().date()]['Lemak'].sum() if not df.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1: buat_kartu("🔥", "KALORI MASUK", f"{kalori_hari_ini:,.0f} Kcal", "#10b981", "Total asupan makanan hari ini")
    with k2: buat_kartu("🏃‍♂️", "KALORI KELUAR", f"{kalori_keluar_hari_ini:,.0f} Kcal", "#ef4444", "Kalori terbakar dari gym harian")
    with k3: buat_kartu("⚖️", "NET CALORIES", f"{net_kalori_hari_ini:,.0f} Kcal", "#3b82f6", "Sisa sirkulasi energi bersih")
    with k4: buat_kartu("🥩", "PROTEIN INTAKE", f"{protein_hari_ini:,.0f}g", "#f59e0b", "Makro utama untuk otot & pemulihan")
    
    st.write("")
    g1, g2 = st.columns([6, 4])
    
    with g1:
        st.markdown("#### 📊 Perbandingan Kalori Masuk vs Keluar (7 Hari Terakhir)")
        hari_list = [datetime.today().date() - timedelta(days=i) for i in range(7)]
        hari_list.reverse()
        
        data_gabung = []
        for h in hari_list:
            c_in = df[df['Tanggal'] == h]['Kalori'].sum() if not df.empty else 0
            c_out = df_keg[df_keg['Tanggal'] == h]['Kalori'].sum() if not df_keg.empty else 0
            data_gabung.append({"Tanggal": h.strftime("%d %b"), "Kategori": "Masuk (Makanan)", "Kcal": c_in})
            data_gabung.append({"Tanggal": h.strftime("%d %b"), "Kategori": "Keluar (Gym/Aktivitas)", "Kcal": c_out})
            
        df_compare = pd.DataFrame(data_gabung)
        fig_compare = px.bar(df_compare, x='Tanggal', y='Kcal', color='Kategori', barmode='group',
                             color_discrete_map={"Masuk (Makanan)": "#10b981", "Keluar (Gym/Aktivitas)": "#ef4444"})
        fig_compare.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
        st.plotly_chart(fig_compare, use_container_width=True)
            
    with g2:
        st.markdown("#### 🥗 Macros Breakdown (Hari Ini)")
        if kalori_hari_ini > 0:
            df_macros = pd.DataFrame({"Makro": ["Protein", "Karbohidrat", "Lemak"], "Gram": [protein_hari_ini, karbo_hari_ini, lemak_hari_ini]})
            fig_pie = px.pie(df_macros, values='Gram', names='Makro', hole=0.6, color_discrete_sequence=["#3b82f6", "#f59e0b", "#ec4899"])
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)
        else: st.info("Belum ada asupan makanan hari ini.")

    st.write("")
    st.markdown("#### 📋 Jurnal Aktivitas Harian")
    
    tab_makanan_tabel, tab_kegiatan_tabel = st.tabs(["🥗 Jurnal Riwayat Makanan", "🏋️‍♂️ Jurnal Riwayat Kegiatan Gym"])
    
    with tab_makanan_tabel:
        if not df.empty:
            col_m1, col_m2 = st.columns(2)
            with col_m1: filter_t1 = st.selectbox("Filter Periode Makanan:", ["Hari Ini", "Minggu Ini", "Bulan Ini", "Semua Waktu"], index=2, key="ft1")
            with col_m2: pil_w1 = st.multiselect("Filter Waktu Makan:", ["Sarapan", "Makan Siang", "Makan Malam", "Cemilan"], default=["Sarapan", "Makan Siang", "Makan Malam", "Cemilan"], key="pw1")
            
            h_ini = datetime.today().date()
            if filter_t1 == "Hari Ini": s_date = h_ini
            elif filter_t1 == "Minggu Ini": s_date = h_ini - timedelta(days=h_ini.weekday())
            elif filter_t1 == "Bulan Ini": s_date = h_ini.replace(day=1)
            else: s_date = h_ini - timedelta(days=365)
            
            df_m_dash = df[(df['Tanggal'] >= s_date) & (df['Tanggal'] <= h_ini) & (df['Waktu'].isin(pil_w1))]
            st.dataframe(df_m_dash.drop(columns=['User'], errors='ignore').iloc[::-1], use_container_width=True, hide_index=True)
        else: st.info("Belum ada data jurnal makanan.")
        
    with tab_kegiatan_tabel:
        if not df_keg.empty:
            col_k1, col_k2 = st.columns(2)
            with col_k1: filter_t2 = st.selectbox("Filter Periode Kegiatan:", ["Hari Ini", "Minggu Ini", "Bulan Ini", "Semua Waktu"], index=2, key="fk1")
            with col_k2: pil_w2 = st.multiselect("Filter Waktu Latihan:", ["Pagi", "Siang", "Sore", "Malam"], default=["Pagi", "Siang", "Sore", "Malam"], key="pw2")
            
            h_ini = datetime.today().date()
            if filter_t2 == "Hari Ini": s_date_k = h_ini
            elif filter_t2 == "Minggu Ini": s_date_k = h_ini - timedelta(days=h_ini.weekday())
            elif filter_t2 == "Bulan Ini": s_date_k = h_ini.replace(day=1)
            else: s_date_k = h_ini - timedelta(days=365)
            
            df_k_dash = df_keg[(df_keg['Tanggal'] >= s_date_k) & (df_keg['Tanggal'] <= h_ini) & (df_keg['Waktu'].isin(pil_w2))]
            st.dataframe(df_k_dash.drop(columns=['User'], errors='ignore').iloc[::-1], use_container_width=True, hide_index=True)
        else: st.info("Belum ada data jurnal latihan gym.")

# ==========================================
# HALAMAN 2: ANALITIK NUTRISI
# ==========================================
elif menu_pilihan == "Analitik Nutrisi":
    buat_banner("🥗 Analitik Nutrisi Makanan", "Analisis pola makan, konsistensi target, dan kebiasaan nutrisi Anda.", "linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%)")
    
    if not df.empty:
        df_daily = df.groupby('Tanggal')['Kalori'].sum().reset_index()
        df_daily['Status'] = df_daily['Kalori'].apply(lambda x: 'Tercapai' if x <= target_kalori else 'Melebihi Target')
        win_rate = (len(df_daily[df_daily['Status'] == 'Tercapai']) / len(df_daily)) * 100
        
        c1, c2 = st.columns([1, 2.5])
        with c1: buat_kartu("🎯", "WIN RATE NUTRISI", f"{win_rate:.1f}%", "#10b981", "Kepatuhan asupan kalori makanan")
        with c2:
            fig_cal = px.bar(df_daily, x='Tanggal', y='Kalori', color='Status', color_discrete_map={'Tercapai': '#10b981', 'Melebihi Target': '#ef4444'})
            fig_cal.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_cal, use_container_width=True)
            
        st.write("")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### 🕒 Distribusi Waktu Makan")
            df_waktu = df.groupby('Waktu')['Kalori'].sum().reset_index()
            fig_timing = px.pie(df_waktu, values='Kalori', names='Waktu', hole=0.5, color_discrete_sequence=["#f59e0b", "#3b82f6", "#8b5cf6", "#ec4899"])
            st.plotly_chart(fig_timing, use_container_width=True)
        with col_m2:
            st.markdown("##### 🔥 Top Makanan Dikonsumsi")
            df_top = df.groupby('Makanan')['Kalori'].mean().reset_index().nlargest(5, 'Kalori')
            fig_top = px.bar(df_top, x='Kalori', y='Makanan', orientation='h', color_discrete_sequence=["#ec4899"])
            st.plotly_chart(fig_top, use_container_width=True)
            
        st.divider()
        st.markdown("### ⚖️ Macro Split Trend")
        st.caption("Keseimbangan asupan Protein, Karbohidrat, dan Lemak harian")
        df_macro_trend = df.groupby('Tanggal')[['Protein', 'Karbohidrat', 'Lemak']].sum().reset_index()
        fig_area = px.area(df_macro_trend, x='Tanggal', y=['Protein', 'Karbohidrat', 'Lemak'], color_discrete_map={'Protein': '#3b82f6', 'Karbohidrat': '#f59e0b', 'Lemak': '#ec4899'})
        fig_area.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0), yaxis_title="Total Gram (g)", xaxis_title="")
        st.plotly_chart(fig_area, use_container_width=True)
    else: st.info("Belum ada data asupan nutrisi makanan.")

# ==========================================
# HALAMAN 3: ANALITIK KEBUGARAN
# ==========================================
elif menu_pilihan == "Analitik Kebugaran":
    buat_banner("🏋️‍♂️ Analitik Kebugaran & Gym", "Pantau performa latihan, kalori terbakar, dan aktivitas terfavorit Anda.", "linear-gradient(90deg, #db2777 0%, #f43f5e 100%)")
    
    if not df_keg.empty:
        df_daily_keg = df_keg.groupby('Tanggal')['Kalori'].sum().reset_index()
        total_burned_all = df_keg['Kalori'].sum()
        avg_burned_daily = df_daily_keg['Kalori'].mean()
        
        cf1, cf2 = st.columns([1, 2.5])
        with cf1:
            buat_kartu("💪", "TOTAL BURNED", f"{total_burned_all:,.0f} Kcal", "#ef4444", "Seluruh energi terbakar")
            st.write("")
            buat_kartu("⚡", "AVG WORKOUT BURN", f"{avg_burned_daily:,.0f} Kcal", "#f59e0b", "Rata-rata kalori keluar per hari")
        with cf2:
            st.markdown("##### 📈 Tren Kalori Terbakar Harian")
            fig_keg_trend = px.area(df_daily_keg, x='Tanggal', y='Kalori', color_discrete_sequence=["#ef4444"])
            fig_keg_trend.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_keg_trend, use_container_width=True)
            
        st.divider()
        col_f_plot1, col_f_plot2 = st.columns(2)
        with col_f_plot1:
            st.markdown("##### 🕒 Waktu Gym Terfavorit")
            df_w_keg = df_keg.groupby('Waktu')['Kalori'].count().reset_index().rename(columns={'Kalori': 'Frekuensi'})
            fig_t_keg = px.pie(df_w_keg, values='Frekuensi', names='Waktu', hole=0.5, color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"])
            st.plotly_chart(fig_t_keg, use_container_width=True)
        with col_f_plot2:
            st.markdown("##### 🏋️‍♂️ Top 5 Aktivitas Paling Efektif Membakar Kalori")
            df_top_burn = df_keg.groupby('Kegiatan')['Kalori'].mean().reset_index().nlargest(5, 'Kalori').sort_values('Kalori', ascending=True)
            fig_b_keg = px.bar(df_top_burn, x='Kalori', y='Kegiatan', orientation='h', color_discrete_sequence=["#10b981"], text_auto='.2s')
            st.plotly_chart(fig_b_keg, use_container_width=True)
    else: st.info("Mulai catat kegiatan latihan gym Anda untuk memunculkan visualisasi analitik.")

# ==========================================
# HALAMAN 4: INPUT MAKANAN 
# ==========================================
elif menu_pilihan == "Input Makanan":
    buat_banner("✨ Jurnal Pintar Makanan AI", "Cukup ketik apa yang Anda makan, biarkan Gemini AI menghitung nutrisinya!", "linear-gradient(90deg, #8b5cf6 0%, #a855f7 100%)")
    with st.container(border=True):
        with st.form("form_ai", clear_on_submit=True):
            col_t1, col_w1 = st.columns(2)
            with col_t1: 
                tanggal_makan = st.date_input("Tanggal", datetime.today(), key="tgl_makan")
            with col_w1: 
                waktu_makan = st.selectbox("Waktu Makan", ["Sarapan", "Makan Siang", "Makan Malam", "Cemilan"])
                
            makanan_input = st.text_input("Apa yang Anda makan? (Sertakan porsinya)", placeholder="Contoh: 1 porsi dada ayam panggang dan nasi merah")
            submit_ai = st.form_submit_button("🧠 Hitung & Simpan Makanan", use_container_width=True)
            
            if submit_ai and makanan_input:
                with st.spinner("Gemini sedang menganalisis makanan..."):
                    try:
                        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                        prompt = f"Anda adalah ahli gizi. Berikan estimasi total nutrisi untuk porsi makanan ini: '{makanan_input}'. Balas HANYA dengan format JSON persis seperti ini: {{\"kalori\": 0, \"protein\": 0, \"karbohidrat\": 0, \"lemak\": 0}}"
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                        teks_bersih = response.text.replace('```json', '').replace('```', '').strip()
                        data_nutrisi = json.loads(teks_bersih)
                        
                        kalori = int(data_nutrisi.get("kalori", 0))
                        protein = int(data_nutrisi.get("protein", 0))
                        karbo = int(data_nutrisi.get("karbohidrat", 0))
                        lemak = int(data_nutrisi.get("lemak", 0))
                        
                        # SIMPAN DENGAN TAGGING USERNAME
                        worksheet.append_row([tanggal_makan.strftime("%Y-%m-%d"), waktu_makan, makanan_input, kalori, protein, karbo, lemak, st.session_state.username])
                        st.success(f"✅ Berhasil dicatat ke database pribadi Anda untuk tanggal {tanggal_makan.strftime('%d %b %Y')}!")
                        st.balloons()
                    except Exception as e: st.error(f"Gagal menganalisis. Error: {e}")

# ==========================================
# HALAMAN 5: INPUT KEGIATAN GYM & OLAHRAGA 
# ==========================================
elif menu_pilihan == "Input Kegiatan":
    buat_banner("✨ Jurnal Pintar Kebugaran AI", "Cukup ketik aktivitas latihan atau gym Anda, biarkan Gemini AI memprediksi kalori terbakar!", "linear-gradient(90deg, #db2777 0%, #f43f5e 100%)")
    with st.container(border=True):
        with st.form("form_kegiatan_ai", clear_on_submit=True):
            col_t2, col_w2 = st.columns(2)
            with col_t2: 
                tanggal_kegiatan = st.date_input("Tanggal Latihan", datetime.today(), key="tgl_keg")
            with col_w2: 
                waktu_kegiatan = st.selectbox("Waktu Latihan", ["Pagi", "Siang", "Sore", "Malam"])
                
            kegiatan_input = st.text_input("Aktivitas gym / olahraga apa yang kamu lakukan?", placeholder="Contoh: Angkat beban dada (chest press) 45 menit, atau Lari treadmill speed 9 selama 25 menit")
            submit_keg_ai = st.form_submit_button("🏃‍♂️ Hitung & Simpan Aktivitas", use_container_width=True)
            
            if submit_keg_ai and kegiatan_input:
                with st.spinner("Gemini sedang mengestimasi pembakaran energi latihanmu..."):
                    try:
                        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                        prompt = f"Anda adalah pakar sports science dan fitness trainer. Berikan estimasi kalori yang terbakar untuk kegiatan olahraga ini: '{kegiatan_input}'. Balas HANYA dengan format JSON persis seperti ini: {{\"kalori\": 0}}"
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                        teks_bersih = response.text.replace('```json', '').replace('```', '').strip()
                        data_kegiatan = json.loads(teks_bersih)
                        
                        kalori_burn = int(data_kegiatan.get("kalori", 0))
                        
                        # SIMPAN DENGAN TAGGING USERNAME
                        ws_kegiatan.append_row([tanggal_kegiatan.strftime("%Y-%m-%d"), waktu_kegiatan, kegiatan_input, kalori_burn, st.session_state.username])
                        st.success(f"🔥 Luar biasa! Berhasil dicatat ke data pribadi Anda: **{kegiatan_input}** terbakar sekitar **{kalori_burn} Kcal**")
                        st.snow()
                    except Exception as e: st.error(f"Gagal menghitung kalori aktivitas. Error: {e}")
