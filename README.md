# Scorify - Predictive Lead Scoring Portal for Banking Sales

Repositori ini berisi kode backend dan layanan Machine Learning yang digunakan oleh aplikasi web **Scorify – Predictive Lead Scoring for Banking Sales**. Layanan ini menyediakan API untuk menghitung skor prioritas prospek berdasarkan data nasabah menggunakan model klasifikasi yang dilatih pada *Bank Marketing Dataset*. Backend ML ini membantu tim sales memprioritaskan nasabah yang paling berpotensi menerima penawaran deposito berjangka secara data‑driven.

## 📂 Dataset & Pemodelan

Pengembangan model dilakukan di notebook:

- **File notebook**: [Lead_Scoring_Model_BankMarketing.ipynb](https://colab.research.google.com/drive/1r5zFDuOx5J5awtuLxa4hjYeGk3Hgi347?usp=sharing)
- **Sumber data**: [Bank Marketing Dataset– UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/222/bank+marketing)
- **File dataset**: `bank-additional-full.csv` (versi dengan 21 fitur).
- Jumlah data: 41.188 baris.
- Jumlah fitur awal: 21 kolom termasuk variabel target `y`.

**Target variable**

- `y`: Menunjukkan apakah nasabah berlangganan deposito berjangka (`yes` / `no`).
- Distribusi target bersifat highly imbalanced (mayoritas kelas `no`).

**Contoh fitur yang digunakan**

- **age** – usia nasabah.
- **job**, **marital**, **education** – karakteristik demografis dan pekerjaan.
- **housing**, **loan**, **default** – status pinjaman dan riwayat kredit.
- **campaign**, **pdays**, **previous**, **poutcome** – histori kampanye sebelumnya.
- **emp.var.rate**, **cons.price.idx**, **cons.conf.idx**, **euribor3m**, **nr.employed** – indikator kondisi ekonomi makro.

Variabel target `y` yang imbalanced membuat perlunya penanganan khusus saat training model, baik melalui pemilihan metrik maupun teknik penyeimbangan kelas.

### Langkah utama di notebook

1. **Exploratory Data Analysis**
   - Pemeriksaan tipe data dan ringkasan statistik.
   - Analisis distribusi fitur numerik dan kategorikal.
   - Visualisasi distribusi target dan identifikasi ketidakseimbangan kelas.

2. **Preprocessing**
   - Pemisahan kolom numerik dan kategorikal.
   - Penanganan nilai hilang dengan `SimpleImputer`.
   - Penanganan nilai `unknown` sesuai konteks fitur.
   - Standardisasi fitur numerik dan encoding fitur kategorikal menggunakan `ColumnTransformer` dan `Pipeline` scikit‑learn.
   - Penanganan data imbalanced dengan pengaturan `class_weight`.

3. **Modeling**
   - Pelatihan beberapa model *gradient boosting*:
     - `XGBClassifier` (XGBoost)
     - `CatBoostClassifier`
     - `LGBMClassifier` (LightGBM)
   - Tuning hiperparameter dengan `GridSearchCV` dan pemisahan train/test menggunakan `train_test_split`.
   - Penyesuaian *decision threshold* untuk mengoptimalkan F1‑Score mengingat distribusi kelas yang timpang.

## 📊 Performa Model

Ringkasan hasil evaluasi pada data uji:

| Model    | F1-Score | ROC AUC | Threshold |
|----------|---------:|--------:|----------:|
| XGBoost  | 0.52     | 0.81    | 0.64      |
| CatBoost | 0.52     | 0.81    | 0.61      |
| LightGBM | 0.52     | 0.81    | 0.67      |

Nilai F1‑Score dan ROC AUC menunjukkan bahwa ketiga model memiliki performa yang seimbang dan cukup baik untuk kebutuhan ranking prioritas nasabah pada kampanye telemarketing deposito.  

## 🏗️ Arsitektur Batch ML & Backend

Berikut adalah diagram arsitektur sistem batch Machine Learning dan backend Scorify yang berjalan di Google Cloud Platform.

![Batch ML & BE System Architecture](https://storage.googleapis.com/scorify-diagrams/scorify.jpg)

Diagram ini menggambarkan integrasi Cloud Scheduler, layanan backend (misalnya Cloud Run/FastAPI), Cloud SQL sebagai database utama, pipeline ML yang memuat model terlatih, serta monitoring dan alerting untuk memantau jumlah leads yang diproses dan durasi batch.

## 🔍 Interpretasi Model

Untuk menjelaskan prediksi ke pihak bisnis digunakan library **SHAP**:

- *Global explanation*:
  - Summary plot, bar plot, dan violin plot untuk melihat fitur yang paling berpengaruh secara keseluruhan.
- *Local explanation*:
  - Force plot per contoh nasabah untuk mengilustrasikan kontribusi tiap fitur terhadap skor prediksi.

Pendekatan ini membantu menjelaskan mengapa seorang nasabah mendapatkan skor tinggi atau rendah dan mendukung pengambilan keputusan yang lebih transparan.

## 🔗 Integrasi dengan Scorify (API / Output)

Backend ML ini berperan sebagai penyedia skor untuk aplikasi Scorify:

- **Input**: data nasabah dengan struktur yang konsisten dengan dataset pelatihan.
- **Proses**:
  - Pipeline preprocessing yang sama seperti di notebook diterapkan pada data input.
  - Model terpilih mengeluarkan probabilitas dan label klasifikasi.
- **Output**: skor probabilitas dan label yang kemudian digunakan front‑end Scorify untuk:
  - Memberi warna prioritas (misalnya hijau/kuning/merah).
  - Menyediakan data untuk laporan performa sales.
