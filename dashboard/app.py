import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Antam Gold Forecast Dashboard",
    page_icon="🪙",
    layout="wide"
)

st.title("🪙 Dashboard Prediksi & Analisis Harga Emas Antam")
st.markdown("Aplikasi monitoring harga emas harian dan forecasting 7 hari ke depan menggunakan *Prophet Model*.")
st.write("---")

# 1. KONEKSI DATABASE
try:
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.error(f"Gagal terhubung ke database Supabase: {e}")
    st.stop()

# 2. FILTER DROPDOWN (PILIH GRAM)
# Mengambil varian gram yang tersedia di database
def get_grams():
    query = "SELECT DISTINCT gram FROM historis_harga_antam ORDER BY gram ASC;"
    df = conn.query(query)
    return df['gram'].tolist()

try:
    list_gram = get_grams()
    if not list_gram:
        st.warning("Koneksi sukses, tapi isi tabel 'historis_harga_antam' masih kosong!")
        st.stop()
    selected_gram = st.selectbox("⚖️ Pilih Varian Berat Emas (Gram):", list_gram)
except Exception as db_error:
    st.error("🚨 Terjadi kegagalan saat membaca database Supabase!")
    st.code(str(db_error)) # Ini akan memunculkan detail error aslinya (misal: Relation does not exist)
    st.stop()

# 3. AMBIL DATA DARI SUPABASE BASED ON GRAM YANG DIPILIH
def load_dashboard_data(gram):
    # Ambil data historis (30 hari terakhir agar grafik tidak terlalu padat)
    query_hist = """
        SELECT tanggal as date, harga_antam as price, 'Historis' as status 
        FROM historis_harga_antam 
        WHERE gram = :gram 
        ORDER BY tanggal DESC LIMIT 30
    """
    df_hist = conn.query(query_hist, params={"gram": gram})
    df_hist = df_hist.sort_values(by="date") # Urutkan dari terlama ke terbaru

    # Ambil data prediksi masa depan
    query_pred = """
        SELECT tanggal_prediksi as date, harga_prediksi as price, yhat_lower, yhat_upper, 'Prediksi' as status 
        FROM prediksi_harga_antam 
        WHERE gram = :gram 
        ORDER BY tanggal_prediksi ASC
    """
    df_pred = conn.query(query_pred, params={"gram": gram})

    # Ambil metrik performa AI
    query_metrics = """SELECT mae, rmse, mape FROM detail_prediksi WHERE gram = :gram"""
    df_metrics = conn.query(query_metrics, params={"gram": gram})
    
    return df_hist, df_pred, df_metrics

df_hist, df_pred, df_metrics = load_dashboard_data(selected_gram)

# 4. TAMPILKAN METRIK PERFORMA AI (MAE, RMSE, MAPE) DI ATAS GRAFIK
st.subheader("📊 Performa Akurasi Model AI (Prophet)")
if not df_metrics.empty:
    col1, col2, col3 = st.columns(3)
    mae_val = df_metrics.iloc[0]['mae']
    rmse_val = df_metrics.iloc[0]['rmse']
    mape_val = df_metrics.iloc[0]['mape']

    col1.metric(label="Mean Absolute Error (MAE)", value=f"Rp {mae_val:,.0f}", help="Rata-rata melesetnya prediksi dari harga asli secara riil.")
    col2.metric(label="Root Mean Squared Error (RMSE)", value=f"Rp {rmse_val:,.0f}", help="Mengukur besarnya error (sensitif terhadap selisih ekstrem).")
    col3.metric(label="Mean Absolute Percentage Error (MAPE)", value=f"{mape_val:.2f}%", help="Persentase rata-rata error. Di bawah 5% artinya model SANGAT AKURAT.")
else:
    st.info("Data performa model belum tersedia di database.")

st.write("---")

# 5. PEMBUATAN GRAFIK INTERAKTIF (PLOTLY)
st.subheader(f"📈 Tren & Ramalan Harga Emas - Varian {selected_gram} Gram")

fig = go.Figure()

# Garis Data Historis
fig.add_trace(go.Scatter(
    x=df_hist['date'], y=df_hist['price'],
    mode='lines+markers',
    name='Harga Historis',
    line=dict(color='#2b5c8f', width=3)
))

# Jika ada data prediksi, gambarkan garis kelanjutannya beserta uncertainty band
if not df_pred.empty:
    # Gabungkan titik terakhir historis ke prediksi agar garisnya menyambung di grafik
    last_hist = df_hist.iloc[[-1]][['date', 'price']]
    
    # Area Ketidakpastian (Upper & Lower yhat)
    fig.add_trace(go.Scatter(
        x=pd.concat([last_hist['date'], df_pred['date']]),
        y=pd.concat([last_hist['price'], df_pred['yhat_upper']]),
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=pd.concat([last_hist['date'], df_pred['date']]),
        y=pd.concat([last_hist['price'], df_pred['yhat_lower']]),
        mode='lines',
        fill='tonexty', # Mengisi warna di antara upper dan lower
        fillcolor='rgba(255, 193, 7, 0.2)', 
        line=dict(width=0),
        name='Rentang Kemungkinan (Uncertainty)',
    ))

    fig.add_trace(go.Scatter(
        x=pd.concat([last_hist['date'], df_pred['date']]),
        y=pd.concat([last_hist['price'], df_pred['price']]),
        mode='lines+markers',
        name='Prediksi 7 Hari ke Depan',
        line=dict(color='#ffc107', width=3, dash='dash')
    ))

fig.update_layout(
    xaxis_title="Tanggal",
    yaxis_title="Harga Emas (Rp)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=40, b=40),
    plot_bgcolor="white"
)
fig.update_xaxes(showgrid=True, gridcolor='#eee')
fig.update_yaxes(showgrid=True, gridcolor='#eee')

st.plotly_chart(fig, use_container_width=True)

if not df_pred.empty:
    st.write("### Detail Angka Ramalan 7 Hari Ke Depan")
    df_tabel_tampil = df_pred[['date', 'price', 'yhat_lower', 'yhat_upper']].copy()
    df_tabel_tampil.columns = ['Tanggal', 'Prediksi Harga (Rp)', 'Batas Bawah (Rp)', 'Batas Atas (Rp)']
    
    for col in df_tabel_tampil.columns[1:]:
        df_tabel_tampil[col] = df_tabel_tampil[col].apply(lambda x: f"Rp {x:,.0f}")
        
    st.dataframe(df_tabel_tampil, use_container_width=True, hide_index=True)