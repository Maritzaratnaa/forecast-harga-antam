# Dashboard Prediksi Harga Antam

Dashboard untuk melakukan pemantauan harga aktual emas Antam dan prediksi harga 7 hari ke depan menggunakan model Prophet, serta pengecekan ketersediaan stok emas Antam berdasarkan butik.

Link Dashboard: https://prediksi-harga-antam.streamlit.app/

---

## Overview

- **Automated Scraper**: Pengambilan data harga aktual dan ketersediaan stok emas Antam secara otomatis setiap hari melalui GitHub Actions.
- **AI Price Forecasting**: Prediksi tren harga emas untuk 7 hari ke depan dengan evaluasi performa model.
- **Interactive Dashboard**: Visualisasi data interaktif menggunakan Streamlit yang terdiri dari:
  - Analisis & Proyeksi Harga Emas.
  - Pengecekan Stok Emas berdasarkan Butik.
- **Cloud Database**: Penyimpanan data menggunakan Supabase (PostgreSQL).

---

## Arsitektur & Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Dashboard | Streamlit |
| Data Science | Python, Pandas, Scikit-Learn, Prophet |
| Database | Supabase (PostgreSQL) |
| ETL & Automation | GitHub Actions |
| Web Scraping | Python, Requests / BeautifulSoup |

---

## Struktur Direktori

```text
.
├── .github/
│   └── workflows/
│       └── pipeline.yml
├── dashboard/
│   ├── .streamlit/
│   ├    └── secrets.toml
│   └── app.py
├── database/
│   ├── connection.py
│   ├── models.py
│   └── repository.py
├── etl/
│   ├── historical_extract.py
│   ├── historical_transform.py
│   ├── historical_load.py
│   ├── historical_pipeline.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── validation.py
├── forecast/
│   ├── predict.py
│   └── train.py
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Cara Menjalankan Proyek Secara Lokal

### 1. Clone Repository

```bash
git clone https://github.com/Maritzaratnaa/forecast-harga-antam.git
cd forecast-harga-antam
```

### 2. Install Dependencies

Pastikan Python 3.9 atau lebih baru telah terinstal.

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment Variables

Buat file `.env` pada root project.

```ini
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:6543/postgres
```

Contoh:

```ini
DATABASE_URL=postgresql://postgres:yourpassword@aws-0-ap-northeast-1.ipv4.pooler.supabase.com:6543/postgres
```

### 4. Jalankan Dashboard

```bash
streamlit run app.py
```

Dashboard akan berjalan pada:

```text
http://localhost:8501
```

---

## Otomatisasi Pipeline (GitHub Actions)

Pipeline dijalankan secara otomatis setiap hari menggunakan GitHub Actions untuk:

1. Mengambil data harga emas terbaru.
2. Menyimpan data ke database Supabase.
3. Melatih dan memperbarui model prediksi.
4. Menghasilkan prediksi harga 7 hari ke depan.

Cron job dijadwalkan pada pukul 10:25 WIB (UTC+7)**.

---

## Evaluasi Model

Model forecasting dievaluasi menggunakan **Mean Absolute Percentage Error (MAPE)**.

| Nilai MAPE | Interpretasi |
|------------|--------------|
| < 10% | Sangat Akurat (Highly Accurate) |
| 10–20% | Baik |
| 20–50% | Cukup |
| > 50% | Kurang Akurat |

Target performa model adalah **MAPE < 10%** agar hasil prediksi tetap andal sebagai informasi pendukung analisis harga emas.

---

## Dashboard

Dashboard terdiri dari dua halaman utama:

### Analisisi & Prediksi

- Harga emas terkini
- Grafik historis harga
- Prediksi harga 7 hari ke depan
- Tren kenaikan/penurunan
- Nilai MAPE model

### Informasi Stok

- Stok emas Antam
- Filter berdasarkan wilayah
- Filter berdasarkan butik
- Informasi berat emas yang tersedia

---

## Database

Data disimpan pada **Supabase PostgreSQL** yang terdiri dari 5 tabel:
- harga_antam_harian
- historis_harga_antame
- stok_antam_butik
- prediksi_harga_antam
- detail_prediksi
  
---

## Workflow Sistem

```text
Website Antam
      │
      ▼
Web Scraping
      │
      ▼
ETL
      │
      ▼
Supabase PostgreSQL
      │
      ▼
Forecasting Model
      │
      ▼
Dashboard
```
