import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import random
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Gizi Balita", page_icon="👶", layout="wide")

# --- 2. FUNGSI UTAMA ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# --- 3. LOGIKA KEAMANAN ---
if 'verified' not in st.session_state:
    st.session_state.verified = False
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'cooldown_until' not in st.session_state:
    st.session_state.cooldown_until = 0

# Fungsi pengecekan otomatis saat input berubah
def check_answer():
    user_val = st.session_state.captcha_input
    correct_val = st.session_state.num1 + st.session_state.num2
    if user_val == correct_val:
        st.session_state.verified = True
        st.session_state.attempts = 0
    else:
        st.session_state.attempts += 1
        if st.session_state.attempts >= 3:
            st.session_state.cooldown_until = time.time() + 30
        # Reset soal
        st.session_state.num1 = random.randint(1, 10)
        st.session_state.num2 = random.randint(1, 10)

# --- 4. TAMPILAN HALAMAN VERIFIKASI ---
if not st.session_state.verified:
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #f0f2f5; }
        .meme-box {
            background-color: white; padding: 30px; border-radius: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center;
            margin: 30px auto; max-width: 700px;
        }
        .meme-text {
            color: #1a1a1a; font-size: 4rem; font-weight: 900;
            margin: 0; font-family: 'Arial Black', sans-serif;
        }
        .captcha-container {
            background-color: white; padding: 40px; border-radius: 20px;
            box-shadow: 0 12px 35px rgba(0,0,0,0.1); max-width: 500px;
            margin: auto; text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    st.title("🛡️ Keamanan Akses")
    st.markdown('<div class="meme-box"><p class="meme-text">verif dlu woi😹🗿</p></div>', unsafe_allow_html=True)

    # Cooldown Logic
    current_time = time.time()
    if current_time < st.session_state.cooldown_until:
        remaining = int(st.session_state.cooldown_until - current_time)
        st.error(f"Sabar woi! Tunggu {remaining} detik lagi.")
        time.sleep(1)
        st.rerun()
    
    if 'num1' not in st.session_state:
        st.session_state.num1 = random.randint(1, 10)
        st.session_state.num2 = random.randint(1, 10)

    st.markdown('<div class="captcha-container">', unsafe_allow_html=True)
    st.subheader("Verifikasi Manusia")
    st.write("Ketik jawaban dan dashboard akan terbuka otomatis!")
    st.warning(f"Salah: {st.session_state.attempts}")
    
    # Otomatis verifikasi tanpa tekan tombol
    st.number_input(
        f"Berapa {st.session_state.num1} + {st.session_state.num2}?", 
        step=1, value=0, 
        key="captcha_input", 
        on_change=check_answer
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. DASHBOARD UTAMA ---
else:
    img_base = get_base64_of_bin_file('wow.jpg')
    if img_base:
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{img_base}");
                background-size: cover; background-attachment: fixed;
            }}
            .stApp::before {{
                content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background-color: rgba(255, 255, 255, 0.4); z-index: -1;
            }}
            [data-testid="stMetric"], .stPlotlyChart, .stDataFrame {{
                background-color: rgba(255, 255, 255, 0.8) !important;
                backdrop-filter: blur(8px); border-radius: 15px; padding: 15px;
            }}
            </style>
        """, unsafe_allow_html=True)

    try:
        df = pd.read_csv('data_balita.csv')
        st.title("📊 Dashboard Monitoring Gizi Balita")
        
        # Metrics
        m = st.columns(4)
        m[0].metric("Total Balita", len(df))
        m[1].metric("Rerata Tinggi", f"{df['Tinggi Badan (cm)'].mean():.1f}")
        m[2].metric("Rerata Umur", f"{df['Umur (bulan)'].mean():.1f}")
        m[3].metric("Status Normal", len(df[df['Status Gizi'] == 'normal']))

        st.markdown("---")

        # Grid Visualisasi
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🗓️ Distribusi Umur")
            # Histogram dengan outline merah sesuai gambar
            fig1 = px.histogram(df, x="Umur (bulan)", nbins=10, template="plotly_white")
            fig1.update_traces(
                marker_color='#5dade2',
                marker_line_color='red', 
                marker_line_width=1.5
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("🚻 Distribusi Jenis Kelamin")
            # Warna berbeda untuk tiap gender
            gc = df['Jenis Kelamin'].value_counts().reset_index()
            fig2 = px.bar(gc, x="Jenis Kelamin", y="count", color="Jenis Kelamin",
                         color_discrete_map={'laki-laki': '#3498db', 'perempuan': '#e67e22'})
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("🥗 Status Gizi")
            st.plotly_chart(px.pie(df, names='Status Gizi', hole=0.4), use_container_width=True)
        with col4:
            st.subheader("📏 Boxplot Tinggi")
            st.plotly_chart(px.box(df, y="Tinggi Badan (cm)"), use_container_width=True)

        # --- TABEL DATA ---
        st.markdown("---")
        st.subheader("📋 Tabel Data Balita")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Gagal memuat data: {e}")