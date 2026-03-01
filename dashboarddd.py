import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. KONFIGURASI HALAMAN
# Mengatur judul tab browser dan layout halaman
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# Mengatur tema warna untuk grafik Seaborn
sns.set_theme(style="darkgrid")

# 2. FUNGSI LOAD DATA
# Menambahkan dekorator @st.cache_data agar data tidak perlu di-load ulang setiap kali ada interaksi
@st.cache_data
def load_data():
    day_df = pd.read_csv("day_df.csv")
    hour_df = pd.read_csv("hour_df.csv")
    return day_df, hour_df

day_df, hour_df = load_data()


# 3. MEMBUAT SIDEBAR
with st.sidebar:
    # Menggunakan HTML untuk membuat logo sepeda yang besar dan posisinya di tengah
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🚲</h1>", unsafe_allow_html=True)
    
    # Menambahkan judul di bawah logo
    st.markdown("<h3 style='text-align: center;'>Bike Sharing System</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Menambahkan penjelasan data 2011-2012 yang simpel dan rapi
    st.write(
        "Selamat datang di Dashboard Analisis Sepeda! 🚴‍♂️ \n\n"
        "Dashboard ini menyajikan wawasan mengenai tren penyewaan sepeda berdasarkan data historis dari sistem Capital Bikeshare "
        "selama periode **2011 hingga 2012**."
    )
    
    st.markdown("---")
    st.write("**Dibuat oleh:** Azizah Khusnul Fauziah")

# 4. HALAMAN UTAMA (HEADER)
st.title("Bike Sharing Dashboard 🚲")
st.markdown("---")


# 5. VISUALISASI PERTANYAAN 1
st.header("1. Waktu Puncak Penyewaan Sepeda (Hari Kerja vs Akhir Pekan)")

# Menyiapkan data agregasi rata-rata penyewaan per jam
peak_hours = hour_df.groupby(["workingday", "hr"])["cnt"].mean().reset_index()

# Membuat figure matplotlib
fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.lineplot(
    data=peak_hours, 
    x="hr", 
    y="cnt", 
    hue="workingday", 
    marker="o", 
    palette=[ "#D3D3D3", "#5DC0C0"],
    ax=ax1
)

# Mempercantik grafik
ax1.set_title("Rata-Rata Penyewaan Sepeda per Jam", fontsize=16)
ax1.set_xlabel("Jam (0-23)", fontsize=12)
ax1.set_ylabel("Rata-Rata Jumlah Penyewaan", fontsize=12)
ax1.set_xticks(range(0, 24))

# Menampilkan grafik di Streamlit
st.pyplot(fig1)

# Menambahkan penjelasan (bisa di-klik untuk buka-tutup)
with st.expander("💡 Lihat Penjelasan Analisis Waktu Puncak"):
    st.write("""
     **Pola Hari Kerja (Garis Teal)**
             
      Lonjakan pertama terjadi pada pukul 08:00 pagi, di mana rata-rata penyewaan mendekati angka 500 dan lonjakan kedua (yang merupakan titik tertinggi) terjadi antara pukul 17:00 hingga 18:00 sore, menyentuh angka di atas 500 penyewaan.
      Pola ini sangat identik dengan mobilitas komuter (pekerja atau pelajar). Orang-orang menggunakan layanan penyewaan (kemungkinan sepeda atau skuter listrik) untuk berangkat kerja/sekolah di pagi hari, dan menggunakannya kembali untuk pulang di sore hari. Di sela-sela jam kerja (pukul 10:00 - 15:00), penyewaan menurun tajam karena mayoritas orang sedang beraktivitas di dalam gedung.
     
     **Pola Akhir Pekan (Garis Abu)**
             
      Jumlah penyewaan baru mulai naik perlahan sejak jam 08:00 pagi. Tingkat penyewaan tertinggi terjadi dan bertahan pada rentang pukul 12:00 siang hingga 15:00 sore (berada di sekitar angka 350 - 380 rata-rata penyewaan).
      Pola ini mencerminkan penggunaan untuk rekreasi, olahraga santai, atau pariwisata. Karena tidak terikat jadwal masuk kerja atau sekolah, pengguna cenderung menyewa di siang hari untuk berjalan-jalan santai, dan penggunaannya berangsur turun menjelang malam.
    """)

st.markdown("---")

# 6. VISUALISASI PERTANYAAN 2
st.header("2. Pertumbuhan Penyewaan Sepeda (2011 vs 2012)")

# Menyiapkan data agregasi total penyewaan (casual vs registered) per tahun
yoy_df = day_df.groupby("yr")[["casual", "registered"]].sum().reset_index()

# Me-melt data agar formatnya cocok untuk barplot Seaborn (menggabungkan kolom casual & registered)
yoy_melted = yoy_df.melt(id_vars="yr", value_vars=["casual", "registered"], var_name="Tipe Pelanggan", value_name="Total Penyewaan")

# Membuat figure matplotlib
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=yoy_melted, 
    x="yr", 
    y="Total Penyewaan", 
    hue="Tipe Pelanggan", 
    palette=["#D3D3D3", "#5DC0C0"],
)

# Mempercantik grafik
ax2.set_title("Total Penyewaan: Casual vs Registered (2011 - 2012)", fontsize=16)
ax2.set_xlabel("Tahun", fontsize=12)
ax2.set_ylabel("Total Penyewaan (Juta)", fontsize=12)

# Menampilkan grafik di Streamlit
st.pyplot(fig2)

# Menambahkan penjelasan
with st.expander("💡 Lihat Penjelasan Analisis Pertumbuhan"):
    st.write("""
*   **Dominasi Pengguna Terdaftar (Registered - Bar Teal)**
      
      Pengguna yang sudah terdaftar merupakan tulang punggung utama dari bisnis ini. Jumlah penyewaan oleh segmen ini jauh melampaui pengguna kasual. Terdapat peningkatan yang sangat pesat, dari 995.851 penyewaan di tahun 2011 menjadi 1.676.811 penyewaan di tahun 2012 (meningkat sekitar 68%).
*   **Pertumbuhan Pengguna Kasual (Casual - Bar Abu)**

      Meskipun proporsinya jauh lebih kecil dibandingkan pengguna terdaftar, segmen kasual juga menunjukkan tren positif.Penyewaan meningkat dari 247.252 di tahun 2011 menjadi 372.765 di tahun 2012 (meningkat sekitar 50%)
*   **Pertumbuhan Skala Bisnis**
             
      Lonjakan angka yang signifikan di tahun 2012 menandakan bahwa layanan penyewaan ini semakin populer dan diterima dengan baik oleh masyarakat secara umum.
    """)