import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text

st.set_page_config(
    page_title="Dashboard Prediksi Antam",
    layout="wide"
)

st.markdown("""
<style>
    /* Styling global */
    .reportview-container {
        background: #f8fafc;
    }
    h1, h2, h3 {
        color: #0f172a;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 600 !important;
    }
    /* Kustomisasi kontainer metrik Streamlit */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 12px 16px;
        border-radius: 6px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        color: #0f172a !important;
        font-weight: 700;
    }
    /* Pembatas kustom */
    hr {
        margin: 1.5rem 0 !important;
        border-color: #e2e8f0 !important;
    }
    /* Styling st.radio horizontal agar tampak seperti tab formal */
    div[role="radiogroup"] {
        background-color: #f1f5f9;
        padding: 4px;
        border-radius: 8px;
        width: fit-content;
        border: 1px solid #e2e8f0;
        gap: 4px !important;
    }
    div[role="radiogroup"] > label {
        padding: 6px 16px !important;
        border-radius: 6px !important;
        background: transparent !important;
        border: none !important;
        margin: 0 !important;
        transition: all 0.2s ease;
    }
    div[role="radiogroup"] > label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {
        color: #475569 !important;
        font-weight: 500 !important;
    }
    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    }
    div[role="radiogroup"] > label[data-checked="true"] div[data-testid="stMarkdownContainer"] p {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# KONEKSI DATABASE
try:
    conn = st.connection("postgresql", type="sql")
except Exception as e:
    st.error(f"Gagal terhubung ke database Supabase: {e}")
    st.stop()

def get_grams():
    query = "SELECT DISTINCT gram FROM historis_harga_antam ORDER BY gram ASC;"
    df = conn.query(query)
    return df['gram'].tolist()

def get_regions():
    try:
        query = "SELECT DISTINCT butik FROM stok_antam_butik ORDER BY butik ASC;"
        df = conn.query(query)
        return df['butik'].tolist()
    except Exception:
        return 

try:
    list_gram = get_grams()
    list_regions = get_regions()
    if not list_gram:
        st.warning("Koneksi sukses, tabel historis_harga_antam kosong.")
        st.stop()
except Exception as db_error:
    st.error("Terjadi kegagalan saat membaca database Supabase.")
    st.code(str(db_error))
    st.stop()
    

def get_last_update():
    try:
        query = "SELECT MAX(scraped_at) as last_update FROM stok_antam_butik;"
        df = conn.query(query)
        if not df.empty and pd.notna(df.iloc[0]['last_update']):
            return df.iloc[0]['last_update']
    except Exception:
        pass
    
    try:
        query_alt = "SELECT MAX(scraped_at) as last_update FROM harga_antam_harian;"
        df_alt = conn.query(query_alt)
        if not df_alt.empty and pd.notna(df_alt.iloc[0]['last_update']):
            return df_alt.iloc[0]['last_update']
    except Exception:
        pass
        
    try:
        query_hist = "SELECT MAX(tanggal) as last_date FROM historis_harga_antam;"
        df_hist = conn.query(query_hist)
        if not df_hist.empty and pd.notna(df_hist.iloc[0]['last_date']):
            return df_hist.iloc[0]['last_date']
    except Exception:
        pass
    return None

def get_formatted_last_update():
    last_update = get_last_update()
    if last_update:
        try:
            dt = pd.to_datetime(last_update)
            # Konversi timezone dari UTC ke WIB (Asia/Jakarta)
            if dt.tzinfo is None:
                dt = dt.tz_localize('UTC')
            dt_wib = dt.tz_convert('Asia/Jakarta')
            
            if dt_wib.hour == 0 and dt_wib.minute == 0:
                return f"Terakhir diperbarui: {dt_wib.strftime('%d-%m-%Y')}"
            return f"Terakhir diperbarui: {dt_wib.strftime('%d-%m-%Y %H:%M')} WIB"
        except Exception:
            try:
                # Fallback manual menambahkan 7 jam jika konversi timezone gagal
                dt = pd.to_datetime(last_update)
                dt_wib = dt + pd.Timedelta(hours=7)
                if dt_wib.hour == 0 and dt_wib.minute == 0:
                    return f"Terakhir diperbarui: {dt_wib.strftime('%d-%m-%Y')}"
                return f"Terakhir diperbarui: {dt_wib.strftime('%d-%m-%Y %H:%M')} WIB"
            except Exception:
                return f"Terakhir diperbarui: {last_update}"
    return "Terakhir diperbarui: Waktu tidak tersedia"

formatted_time = get_formatted_last_update()

st.title("Dashboard Analisis dan Prediksi Harga Emas Antam")
st.markdown(
    f"<div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 5px; color: #475569; font-size: 0.9rem;'>"
    f"<span>Sistem monitoring harga emas harian dan prediksi 7 hari ke depan berbasis Prophet Model.</span>"
    f"<span style='color: #64748b; font-size: 0.85rem; font-weight: 500;'>{formatted_time}</span>"
    f"</div>", 
    unsafe_allow_html=True
)
st.write("---")

# TAB
active_menu = st.radio(
    label="Pilih Halaman Dashboard:",
    options=["Analisis & Prediksi", "Informasi Stok"],
    horizontal=True,
    label_visibility="collapsed"
)

# SIDEBAR
st.sidebar.markdown("### Parameter Analisis")
selected_gram = st.sidebar.selectbox("Pilih Varian Berat (Gram):", list_gram)

if active_menu == "Informasi Stok":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filter Stok")
    selected_region = st.sidebar.selectbox("Pilih Butik:", list_regions)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Informasi Sistem
- **Model Prediksi**: Prophet Model
- **Tujuan**: Prediksi Harga Emas
- **Horizon Prediksi**: 7 Hari Ke Depan
- **Sumber Data**: Website Official Emas Antam
""")

# TAB 1: ANALISIS & PREDIKSI
if active_menu == "Analisis & Prediksi":
    def load_dashboard_data(gram):
        query_hist = """
            SELECT tanggal as date, harga_antam as price, 'Historis' as status 
            FROM historis_harga_antam 
            WHERE gram = :gram 
            ORDER BY tanggal DESC LIMIT 30
        """
        df_hist = conn.query(query_hist, params={"gram": gram})
        df_hist = df_hist.sort_values(by="date")

        query_pred = """
            SELECT tanggal_prediksi as date, harga_prediksi as price, yhat_lower, yhat_upper, 'Prediksi' as status 
            FROM prediksi_harga_antam 
            WHERE gram = :gram 
            ORDER BY tanggal_prediksi ASC
        """
        df_pred = conn.query(query_pred, params={"gram": gram})

        query_metrics = """SELECT mae, rmse, mape FROM detail_prediksi WHERE gram = :gram"""
        df_metrics = conn.query(query_metrics, params={"gram": gram})
        
        return df_hist, df_pred, df_metrics

    df_hist, df_pred, df_metrics = load_dashboard_data(selected_gram)

    last_price = 0
    last_date = ""
    next_price = 0
    future_price = 0
    diff_tomorrow = 0
    pct_tomorrow = 0.0
    diff_7day = 0
    pct_7day = 0.0

    if not df_hist.empty:
        last_row = df_hist.iloc[-1]
        last_price = last_row['price']
        if hasattr(last_row['date'], 'strftime'):
            last_date = last_row['date'].strftime('%d %b %Y')
        else:
            last_date = str(last_row['date'])

    if not df_hist.empty and not df_pred.empty:
        next_row = df_pred.iloc[0]
        next_price = next_row['price']
        tomorrow_date = next_row['date'].strftime('%d %b %Y') if hasattr(next_row['date'], 'strftime') else str(next_row['date'])
        diff_tomorrow = next_price - last_price
        pct_tomorrow = (diff_tomorrow / last_price) * 100
        
        future_row = df_pred.iloc[-1]
        future_price = future_row['price']
        future_date = future_row['date'].strftime('%d %b %Y') if hasattr(future_row['date'], 'strftime') else str(future_row['date'])
        diff_7day = future_price - last_price
        pct_7day = (diff_7day / last_price) * 100

    col_kpi, col_perf = st.columns([1, 1])

    with col_kpi:
        st.markdown("### Harga Terkini dan Prediksi")
        kpi_sub1, kpi_sub2, kpi_sub3 = st.columns(3)
        if not df_hist.empty:
            delta_hist_str = None
            if len(df_hist) >= 2:
                prev_price = df_hist.iloc[-2]['price']
                diff_hist = last_price - prev_price
                pct_hist = (diff_hist / prev_price) * 100
                
                sign_hist = "+" if diff_hist >= 0 else "-"
                delta_hist_str = f"{sign_hist} Rp {abs(diff_hist):,.0f} ({pct_hist:+.2f}%)"

            kpi_sub1.metric(
                label="Harga Terakhir",
                value=f"Rp {last_price:,.0f}",
                delta=delta_hist_str,
                help=f"Harga emas aktual terakhir pada tanggal {last_date}."
            )
            if not df_pred.empty:
                sign_tomorrow = "+" if diff_tomorrow >= 0 else "-"
                kpi_sub2.metric(
                    label="Prediksi Besok",
                    value=f"Rp {next_price:,.0f}",
                    delta=f"{sign_tomorrow} Rp {abs(diff_tomorrow):,.0f} ({pct_tomorrow:+.2f}%)",
                    help=f"Prediksi harga emas pada tanggal {tomorrow_date}."
                )
                
                sign_7day = "+" if diff_7day >= 0 else "-"
                kpi_sub3.metric(
                    label="Prediksi Hari ke-7",
                    value=f"Rp {future_price:,.0f}",
                    delta=f"{sign_7day} Rp {abs(diff_7day):,.0f} ({pct_7day:+.2f}%)",
                    help=f"Prediksi harga emas pada tanggal {future_date}."
                )
        else:
            st.info("Data historis tidak tersedia.")

    with col_perf:
        st.markdown("### Akurasi Model Forecasting (Prophet)")
        perf_sub1, perf_sub2, perf_sub3 = st.columns(3)
        if not df_metrics.empty:
            mae_val = df_metrics.iloc[0]['mae']
            rmse_val = df_metrics.iloc[0]['rmse']
            mape_val = df_metrics.iloc[0]['mape']
            
            perf_sub1.metric(
                label="Mean Absolute Error (MAE)",
                value=f"Rp {mae_val:,.0f}",
                help="Rata-rata selisih antara harga prediksi dan harga asli dalam rupiah."
            )
            perf_sub2.metric(
                label="Root Mean Squared Error (RMSE)",
                value=f"Rp {rmse_val:,.0f}",
                help="Mengukur besarnya error dengan sensitivitas terhadap selisih ekstrem."
            )
            perf_sub3.metric(
                label="Mean Absolute Percentage Error (MAPE)",
                value=f"{mape_val:.2f}%",
                help="Persentase rata-rata error prediksi. Nilai di bawah 5% menunjukkan akurasi model yang sangat tinggi."
            )
        else:
            st.info("Data metrik performa model tidak tersedia.")

    st.write("---")

    col_chart, col_table = st.columns([13, 7])

    with col_chart:
        st.markdown(f"### Tren dan Prediksi Harga Emas (Varian {selected_gram} Gram)")
        
        fig = go.Figure()
        
        # Garis Data Historis
        fig.add_trace(go.Scatter(
            x=df_hist['date'], y=df_hist['price'],
            mode='lines+markers',
            name='Harga Historis (30 Hari Terakhir)',
            line=dict(color='#1e3d59', width=3),
            marker=dict(size=4)
        ))
        
        if not df_pred.empty:
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
                fill='tonexty', 
                fillcolor='rgba(212, 175, 55, 0.12)', 
                line=dict(width=0),
                name='Rentang Ketidakpastian (Confidence Interval)',
            ))
            
            # Garis Prediksi
            fig.add_trace(go.Scatter(
                x=pd.concat([last_hist['date'], df_pred['date']]),
                y=pd.concat([last_hist['price'], df_pred['price']]),
                mode='lines+markers',
                name='Proyeksi Harga (7 Hari Ke Depan)',
                line=dict(color='#d4af37', width=3, dash='dash'),
                marker=dict(size=4)
            ))
            
        fig.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Harga Emas (Rp)",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)"
            ),
            margin=dict(l=40, r=40, t=50, b=40),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            height=450
        )
        fig.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
        fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
        
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("### Detail Angka Prediksi 7 Hari")
        if not df_pred.empty:
            df_tabel_tampil = df_pred[['date', 'price', 'yhat_lower', 'yhat_upper']].copy()
            df_tabel_tampil.columns = ['Tanggal', 'Proyeksi Harga', 'Batas Bawah', 'Batas Atas']
            
            if pd.api.types.is_datetime64_any_dtype(df_tabel_tampil['Tanggal']):
                df_tabel_tampil['Tanggal'] = df_tabel_tampil['Tanggal'].dt.strftime('%d-%m-%Y')
            else:
                df_tabel_tampil['Tanggal'] = df_tabel_tampil['Tanggal'].apply(
                    lambda x: pd.to_datetime(x).strftime('%d-%m-%Y') if pd.notna(x) else ""
                )
                
            for col in df_tabel_tampil.columns[1:]:
                df_tabel_tampil[col] = df_tabel_tampil[col].apply(lambda x: f"Rp {x:,.0f}")
                
            st.dataframe(df_tabel_tampil, use_container_width=True, hide_index=True, height=350)
        else:
            st.info("Data tabel prediksi tidak tersedia.")

# TAB 2: INFORMASI STOK
else:
    st.markdown("### Ketersediaan Stok")
    st.markdown("Berikut adalah informasi ketersediaan keping emas Antam di butik resmi terpilih.")

    def load_stock_data(butik, gram):
        try:
            query = """
                SELECT tanggal as date, stok as stock 
                FROM stok_antam_butik 
                WHERE butik = :butik AND gram = :gram
                ORDER BY tanggal DESC LIMIT 30
            """
            df = conn.query(query, params={"butik": butik, "gram": gram})
            df = df.sort_values(by="date")
            return df
        except Exception:
            return

    df_stock = load_stock_data(selected_region, selected_gram)

    if not df_stock.empty:
        current_stock = int(df_stock.iloc[-1]['stock'])
        prev_stock = int(df_stock.iloc[-2]['stock']) if len(df_stock) >= 2 else current_stock
        stock_diff = current_stock - prev_stock
        
        st.write("")
        c_kpi1, c_kpi2 = st.columns([1, 3])
        with c_kpi1:
            st.metric(
                label="Stok Tersedia Saat Ini",
                value=f"{current_stock} Pcs",
                delta=f"{stock_diff:+d} Pcs dari hari sebelumnya",
                help="Jumlah keping emas yang siap dijual di butik terpilih."
            )

        with c_kpi2:
            fig_stock = go.Figure()
            fig_stock.add_trace(go.Scatter(
                x=df_stock['date'], 
                y=df_stock['stock'],
                mode='lines+markers',
                name='Jumlah Stok',
                line=dict(color='#0284c7', width=3),
                marker=dict(size=6, color='#0369a1')
            ))
            fig_stock.update_layout(
                title=f"Tren Logistik Perubahan Stok ({selected_region} - Varian {selected_gram} Gram)",
                xaxis_title="Tanggal",
                yaxis_title="Jumlah Keping (Pcs)",
                hovermode="x unified",
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                height=250,
                margin=dict(l=40, r=40, t=40, b=40)
            )
            fig_stock.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
            fig_stock.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
            st.plotly_chart(fig_stock, use_container_width=True)

        st.write("---")
        st.markdown("#### Log Riwayat Perubahan Stok Lengkap")
        df_stock_table = df_stock.copy()
        
        if pd.api.types.is_datetime64_any_dtype(df_stock_table['date']):
            df_stock_table['date'] = df_stock_table['date'].dt.strftime('%d-%m-%Y')
        else:
            df_stock_table['date'] = df_stock_table['date'].apply(
                lambda x: pd.to_datetime(x).strftime('%d-%m-%Y') if pd.notna(x) else ""
            )
            
        df_stock_table.columns = ['Tanggal Update', 'Jumlah Stok Tersedia (Pcs)']
        st.dataframe(df_stock_table.sort_values('Tanggal Update', ascending=False), use_container_width=True, hide_index=True)
        
    else:
        st.info("Data logistik stok untuk kombinasi butik dan gram ini tidak ditemukan.")
