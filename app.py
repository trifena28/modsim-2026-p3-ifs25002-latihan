import streamlit as st
import random
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Simulasi Sistem Piket IT Del",
    layout="wide",
    page_icon="📊"
)

# =============================
# SIMPLE CLEAN STYLE
# =============================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.metric-container {
    background: #f8fafc;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# =============================
# HEADER
# =============================
st.title("📊 Simulasi Sistem Piket IT Del")
st.caption("Monte Carlo Simulation untuk estimasi waktu distribusi ompreng")
st.divider()

# =============================
# SIDEBAR
# =============================
st.sidebar.header("⚙️ Parameter Simulasi")

jumlah_meja = st.sidebar.number_input("Jumlah Meja", 1, 200, 60)
mahasiswa_per_meja = st.sidebar.number_input("Mahasiswa per Meja", 1, 5, 3)

st.sidebar.subheader("👥 Pembagian Petugas")
petugas_lauk = st.sidebar.slider("Petugas Lauk", 1, 5, 2)
petugas_angkut = st.sidebar.slider("Petugas Angkut", 1, 5, 2)
petugas_nasi = st.sidebar.slider("Petugas Nasi", 1, 5, 3)

simulasi = st.sidebar.slider("Jumlah Simulasi", 100, 5000, 1000)

st.sidebar.divider()

jumlah_ompreng = jumlah_meja * mahasiswa_per_meja
st.sidebar.success(f"Total Ompreng: {jumlah_ompreng}")

# =============================
# FUNGSI SIMULASI
# =============================
def jalankan_simulasi():
    hasil_total = []
    detail_lauk = []
    detail_angkut = []
    detail_nasi = []

    progress = st.progress(0)

    for i in range(simulasi):

        waktu_lauk = sum(random.uniform(30, 60) for _ in range(jumlah_ompreng)) / petugas_lauk

        total_angkut = 0
        sisa = jumlah_ompreng
        while sisa > 0:
            total_angkut += random.uniform(20, 60)
            sisa -= random.randint(4, 7)
        waktu_angkut = total_angkut / petugas_angkut

        waktu_nasi = sum(random.uniform(30, 60) for _ in range(jumlah_ompreng)) / petugas_nasi

        total = max(waktu_lauk, waktu_angkut, waktu_nasi)

        hasil_total.append(total)
        detail_lauk.append(waktu_lauk)
        detail_angkut.append(waktu_angkut)
        detail_nasi.append(waktu_nasi)

        progress.progress((i + 1) / simulasi)

    progress.empty()

    return hasil_total, detail_lauk, detail_angkut, detail_nasi

# =============================
# MAIN BUTTON
# =============================
if st.button("🚀 Jalankan Simulasi", use_container_width=True):

    with st.spinner("Menjalankan simulasi..."):
        hasil, lauk, angkut, nasi = jalankan_simulasi()

    rata_detik = np.mean(hasil)
    rata_menit = rata_detik / 60
    jam_selesai = timedelta(hours=7) + timedelta(minutes=rata_menit)

    st.success("Simulasi selesai!")

    # =============================
    # METRICS
    # =============================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("⏱ Rata-rata (Detik)", f"{rata_detik:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("⏳ Rata-rata (Menit)", f"{rata_menit:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("🕖 Estimasi Selesai", str(jam_selesai)[:5])
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # =============================
    # TABS
    # =============================
    tab1, tab2, tab3 = st.tabs([
        "📊 Distribusi Waktu",
        "📈 Analisis Tahap",
        "🚨 Bottleneck"
    ])

    # =============================
    # TAB 1
    # =============================
    with tab1:
        fig_hist = px.histogram(
            hasil,
            nbins=30,
            color_discrete_sequence=["#4f46e5"]
        )
        fig_hist.update_layout(
            template="plotly_white",
            title="Distribusi Total Waktu (Detik)"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # =============================
    # TAB 2
    # =============================
    with tab2:
        rata_lauk = np.mean(lauk)
        rata_angkut = np.mean(angkut)
        rata_nasi = np.mean(nasi)

        colA, colB = st.columns(2)

        with colA:
            fig_bar = go.Figure()
            fig_bar.add_bar(
                x=["Lauk", "Angkut", "Nasi"],
                y=[rata_lauk, rata_angkut, rata_nasi],
                marker_color=["#ef4444", "#f59e0b", "#3b82f6"]
            )
            fig_bar.update_layout(
                template="plotly_white",
                title="Rata-rata Waktu per Tahap (Detik)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with colB:
            fig_pie = px.pie(
                names=["Lauk", "Angkut", "Nasi"],
                values=[rata_lauk, rata_angkut, rata_nasi],
                color_discrete_sequence=["#ef4444", "#f59e0b", "#3b82f6"]
            )
            fig_pie.update_layout(
                template="plotly_white",
                title="Proporsi Waktu per Tahap"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # =============================
    # TAB 3
    # =============================
    with tab3:
        tahap = {
            "Lauk": rata_lauk,
            "Angkut": rata_angkut,
            "Nasi": rata_nasi
        }

        bottleneck = max(tahap, key=tahap.get)

        st.subheader("Tahap Terlama")

        st.error(f"🚨 Bottleneck Sistem: **{bottleneck}**")

        st.dataframe(
            {
                "Tahap": list(tahap.keys()),
                "Rata-rata Waktu (Detik)": list(tahap.values())
            },
            use_container_width=True
        )