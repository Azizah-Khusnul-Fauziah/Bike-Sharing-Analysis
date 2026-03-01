import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# KONFIGURASI HALAMAN
st.set_page_config(page_title="Bike Sharing Analytics", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid")


# FUNGSI LOAD & PREPROCESS DATA
# Menambahkan dekorator @st.cache_data agar data tidak perlu di-load ulang setiap kali ada interaksi
@st.cache_data
def load_data():
    day_df = pd.read_csv("day_df.csv")
    hour_df = pd.read_csv("hour_df.csv")
    
    # Standarisasi kolom tahun (jika masih 0 dan 1)
    for df in [day_df, hour_df]:
        if df['yr'].max() <= 1:
            df['yr'] = df['yr'].map({0: 2011, 1: 2012})
            
        # Standarisasi workingday (jika masih 0 dan 1)
        if df['workingday'].dtype in ['int64', 'float64']:
            df['workingday'] = df['workingday'].map({0: 'Akhir Pekan', 1: 'Hari Kerja'})
            
    # Membuat kolom waktu_hari di hour_df jika belum ada
    if 'waktu_hari' not in hour_df.columns:
        bins = [-1, 5, 10, 14, 18, 23]
        labels = ['Dini Hari', 'Pagi', 'Siang', 'Sore', 'Malam']
        hour_df['waktu_hari'] = pd.cut(hour_df['hr'], bins=bins, labels=labels)
        
    return day_df, hour_df

day_df, hour_df = load_data()


# 1. PANEL KONTROL (SIDEBAR)
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🚲</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Bike Sharing Analytics</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("⚙️ Filter Data")
    
    # Filter Tahun
    year_options = ["Semua", 2011, 2012]
    selected_year = st.radio("Pilih Tahun:", year_options)
    
    # Filter Jenis Hari
    day_options = ["Semua", "Hari Kerja", "Akhir Pekan"]
    selected_day = st.selectbox("Pilih Jenis Hari:", day_options)

# Terapkan Filter ke Dataframe
filtered_day = day_df.copy()
filtered_hour = hour_df.copy()

if selected_year != "Semua":
    filtered_day = filtered_day[filtered_day['yr'] == selected_year]
    filtered_hour = filtered_hour[filtered_hour['yr'] == selected_year]

if selected_day != "Semua":
    filtered_day = filtered_day[filtered_day['workingday'] == selected_day]
    filtered_hour = filtered_hour[filtered_hour['workingday'] == selected_day]


# 2. TINGKAT 1: EXECUTIVE SUMMARY (KPI)
st.title("📊 Executive Dashboard: Capital Bikeshare")
st.markdown("---")

# Hitung Metrik
total_rentals = filtered_day['cnt'].sum()
total_casual = filtered_day['casual'].sum()
total_registered = filtered_day['registered'].sum()

# Hitung YoY Growth (Hanya relevan jika filter tahun adalah 'Semua')
if selected_year == "Semua":
    rentals_2011 = day_df[day_df['yr'] == 2011]['cnt'].sum()
    rentals_2012 = day_df[day_df['yr'] == 2012]['cnt'].sum()
    yoy_growth = ((rentals_2012 - rentals_2011) / rentals_2011) * 100
else:
    yoy_growth = None

# Rasio
if total_rentals > 0:
    pct_casual = (total_casual / total_rentals) * 100
    pct_registered = (total_registered / total_rentals) * 100
else:
    pct_casual = pct_registered = 0

# Menampilkan Scorecards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Penyewaan (Volume)", f"{total_rentals:,.0f}")
with col2:
    if yoy_growth is not None:
        st.metric("Pertumbuhan YoY", f"{yoy_growth:.1f}%", f"{yoy_growth:.1f}% dari 2011")
    else:
        st.metric("Pertumbuhan YoY", "N/A", "Pilih 'Semua' tahun")
with col3:
    st.metric("Pelanggan Registered", f"{pct_registered:.1f}%", f"{total_registered:,.0f} sewa")
with col4:
    st.metric("Pelanggan Casual", f"{pct_casual:.1f}%", f"{total_casual:,.0f} sewa", delta_color="off")

st.markdown("<br>", unsafe_allow_html=True)

# 3. TINGKAT 2: TREN & PERTUMBUHAN MAKRO
st.header("📈 Tren Pertumbuhan Makro")
col_chart1, col_insight1 = st.columns([3, 1])

with col_chart1:
    # Menggunakan data dari yoy_df yang sudah di-filter
    yoy_df = filtered_day.groupby("yr")[["casual", "registered"]].sum().reset_index()
    
    x = np.arange(len(yoy_df["yr"]))
    width = 0.35

    fig_macro, ax_macro = plt.subplots(figsize=(8,5))

    # Membuat bar chart 
    bars1 = ax_macro.bar(x - width/2, yoy_df["casual"], width, label="Casual", color="#D3D3D3")
    bars2 = ax_macro.bar(x + width/2, yoy_df["registered"], width, label="Registered", color="#5DC0C0")

    # Menambahkan label angka di atas batang
    ax_macro.bar_label(bars1, fmt='{:,.0f}')
    ax_macro.bar_label(bars2, fmt='{:,.0f}')

    # Mempercantik sumbu dan judul
    ax_macro.set_xticks(x)
    ax_macro.set_xticklabels(yoy_df["yr"])
    ax_macro.set_title("Pertumbuhan Penyewaan per Segmen")
    ax_macro.set_xlabel("Tahun")
    ax_macro.set_ylabel("Total Penyewaan")
    ax_macro.legend()

    st.pyplot(fig_macro)

with col_insight1:
    st.info("""
*   🚀 Pertumbuhan Signifikan: Lonjakan penyewaan di 2012 didorong kuat oleh peningkatan pengguna Registered (+68%) dan Casual (+50%).
*   👑 Dominasi Pelanggan: Pengguna Registered adalah tulang punggung bisnis, mendominasi >80% total transaksi (1,67 juta penyewaan di 2012).
*   💡 Actionable Insight: Lonjakan angka yang signifikan di tahun 2012 menandakan bahwa layanan penyewaan ini semakin populer dan diterima dengan baik oleh masyarakat secara umum.
""")

st.markdown("---")

# 4. TINGKAT 3: ANALISIS PERILAKU OPERASIONAL
st.header("🚲 Analisis Perilaku Operasional (Mikro)")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Waktu Puncak Harian")
    
    # Menyiapkan data
    peak_hours = (
        filtered_hour
        .groupby(["workingday", "hr"])["cnt"]
        .mean()
        .reset_index()
    )
    
    # Membuat figure (Pengganti plt.figure di Streamlit)
    fig_peak, ax_peak = plt.subplots(figsize=(8, 5))
    
    # Membuat Line Chart
    sns.lineplot(
        data=peak_hours,
        x="hr",
        y="cnt",
        hue="workingday",
        marker="o",
        palette={
            "Hari Kerja": "#5DC0C0",   
            "Akhir Pekan": "#D3D3D3"   
        },
        ax=ax_peak
    )
    # Mempercantik grafik
    ax_peak.set_title("Perbandingan Peak Hours: Hari Kerja vs Libur")
    ax_peak.set_xlabel("Jam")
    ax_peak.set_ylabel("Rata-rata Penyewaan")
    ax_peak.legend(title="Jenis Hari")
    
    st.pyplot(fig_peak)

with col_right:
    st.subheader("Intensitas Penyewaan")
    
    # Menyiapkan data menggunakan pivot_table dari data yang sudah difilter
    heatmap_data = filtered_hour.pivot_table(
        values="cnt",
        index="workingday",
        columns="waktu_hari",
        aggfunc="mean"
    )
    
    # Membuat figure
    fig_heat, ax_heat = plt.subplots(figsize=(8, 5))
    
    # Membuat Heatmap 
    sns.heatmap(
        heatmap_data, 
        cmap="YlGnBu", 
        annot=True,       # memunculkan angka di dalam kotak
        fmt=".0f",        # format angka dibulatkan (tanpa koma desimal)
        linewidths=0.5,   # memberi garis batas tipis antar kotak agar lebih rapi
        ax=ax_heat
    )
    
    # Mempercantik grafik
    ax_heat.set_title("Intensitas Penyewaan Sepeda (Rata-rata)", fontsize=12)
    ax_heat.set_xlabel("Kategori Waktu")
    ax_heat.set_ylabel("Jenis Hari")
    
    # Menampilkan di Streamlit
    st.pyplot(fig_heat)

# Insight Box di bawah grafik tingkat 3
st.info("""
*   🚲 Pola Komuter vs. Rekreasi: Terdapat perbedaan perilaku yang kontras. Hari Kerja didominasi aktivitas komuter dengan dua lonjakan tajam pada jam berangkat (08:00) 
        dan pulang kerja (17:00-18:00). Sebaliknya, Akhir Pekan menunjukkan pola rekreasi dengan volume yang stabil dari siang hingga sore hari.
*   🔥 Intensitas Puncak: Beban operasional tertinggi terjadi pada Sore hari di Hari Kerja (rata-rata 437 sewa), 
        jauh melampaui puncak di akhir pekan (Siang hari, 356 sewa). Pagi hari kerja juga menunjukkan intensitas tinggi (249 sewa).
""")

st.markdown("---")


# 5. TINGKAT 4: REKOMENDASI BISNIS
st.header("🎯 Kesimpulan & Insight Utama")
st.markdown("""


- **Kapan waktu puncak (peak hours) penyewaan sepeda terjadi, dan bagaimana perbedaannya antara hari kerja dan akhir pekan?**

  Waktu puncak penyewaan sepeda menunjukkan pola yang sangat berbeda antara hari kerja dan akhir pekan:
  - Pada **Hari Kerja**, penyewaan memuncak pada jam sibuk mobilitas (komuter), yaitu saat orang berangkat beraktivitas sekitar pukul **08:00 pagi** dan lonjakan paling tinggi terjadi saat pulang beraktivitas sekitar pukul **17:00 - 18:00 sore** (dengan rata-rata mencapai 490 - 525 penyewaan).
  - Pada **Akhir Pekan**, tren penyewaan lebih santai dan merata. Puncaknya terjadi di siang hari, khususnya pada rentang pukul **12:00 hingga 13:00 siang** (rata-rata 360 - 370 penyewaan). Hal ini mengindikasikan bahwa pada akhir pekan, sepeda lebih banyak dimanfaatkan untuk aktivitas rekreasi atau olahraga siang.

- **Bagaimana tingkat pertumbuhan penyewaan sepeda dari tahun 2011 ke tahun 2012? Segmen pelanggan mana yang tumbuh paling pesat?**
  
  Secara keseluruhan, tingkat penyewaan sepeda mengalami pertumbuhan (*Year-over-Year*) yang sangat positif. Total penyewaan melonjak pesat dari **1.243.103** pada tahun 2011 menjadi **2.049.576** pada tahun 2012 (tumbuh sekitar 64,8%).
  Jika dilihat lebih rinci berdasarkan segmen pelanggannya:
  - Pelanggan **Casual** (musiman) meningkat dari 247.252 menjadi 372.765 (tumbuh sekitar 50,7%).
  - Pelanggan **Registered** (terdaftar/berlangganan) meningkat pesat dari 995.851 menjadi 1.676.811 (tumbuh sekitar 68,3%).
  Oleh karena itu, dapat disimpulkan bahwa segmen pelanggan **Registered** adalah penyumbang jumlah sewa terbesar sekaligus segmen yang tumbuh paling pesat dibandingkan pelanggan Casual.
""")

st.caption('Copyright (c) Azizah Khusnul Fauziah 2026')