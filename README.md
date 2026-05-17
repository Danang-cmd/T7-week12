# 🛒 Supermarket Sales Dashboard

Aplikasi dashboard PySide6 untuk memvisualisasikan dataset **Supermarket Sales** dari Kaggle.

---

## 📦 Struktur Proyek

```
supermarket_dashboard/
│
├── main.py                  ← Entry point, jalankan ini
│
├── data/
│   └── supermarket_sales.csv  ← Dataset (200 baris, 16 kolom)
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py       ← Jendela utama + sidebar filter global
│   ├── summary_widget.py    ← Tab Ringkasan: KPI cards
│   ├── table_widget.py      ← Tab Data Mentah: QTableWidget
│   └── chart_widget.py      ← Tab Chart: 6+ jenis chart Matplotlib
│
├── utils/
│   ├── __init__.py
│   └── data_loader.py       ← Load CSV, filter, preprocessing
│
├── requirements.txt
└── README.md
```

---

## 🚀 Cara Menjalankan

```bash
# 1. Install dependensi
pip install -r requirements.txt

# 2. Jalankan aplikasi
python main.py
```

---

## ✅ Fitur yang Diimplementasikan

| No | Ketentuan | Status |
|----|-----------|--------|
| 1 | Data minimal 50 baris (CSV Kaggle) | ✅ 200 baris, 16 kolom |
| 2 | Tampilkan data mentah di QTableWidget | ✅ Tab "Data Mentah" + live search |
| 3 | Minimal 2 jenis chart (Matplotlib) | ✅ 8 jenis chart tersedia |
| 4 | Filter kategori / pilihan tipe chart | ✅ Sidebar filter global + combo chart |
| 5 | Tombol Refresh dan Export PNG | ✅ Tersedia di tab Chart |

---

## 📊 Jenis Chart yang Tersedia

1. **Bar** – Total penjualan per cabang
2. **Bar Horizontal** – Produk terlaris per kategori
3. **Line** – Tren penjualan harian
4. **Pie** – Distribusi metode pembayaran
5. **Pie** – Distribusi jenis pelanggan
6. **Scatter** – Harga satuan vs jumlah pembelian
7. **Histogram** – Distribusi rating pelanggan
8. **Box Plot** – Distribusi total transaksi per kategori

---

## 🗂️ Dataset

**Supermarket Sales Dataset**  
Sumber: [Kaggle – faresashraf1001/supermarket-sales](https://www.kaggle.com/datasets/faresashraf1001/supermarket-sales)

### Kolom Utama:

| Kolom | Deskripsi |
|-------|-----------|
| Invoice ID | ID unik setiap transaksi |
| Branch | Cabang toko (A, B, C) |
| City | Kota (Yangon, Mandalay, Naypyitaw) |
| Customer type | Jenis pelanggan (Member / Normal) |
| Gender | Gender pelanggan |
| Product line | Kategori produk (6 kategori) |
| Unit price | Harga satuan (USD) |
| Quantity | Jumlah item yang dibeli |
| Tax 5% | Pajak 5% dari subtotal |
| Total | Total pembayaran termasuk pajak |
| Date | Tanggal transaksi |
| Time | Waktu transaksi |
| Payment | Metode pembayaran (Ewallet, Cash, Credit card) |
| cogs | Cost of Goods Sold |
| gross income | Pendapatan kotor (= Tax 5%) |
| Rating | Rating kepuasan pelanggan (4–10) |

---

## 🎨 Teknologi

- **PySide6** – GUI framework
- **Matplotlib** – Visualisasi chart
- **Pandas** – Manipulasi data
- **NumPy** – Komputasi numerik
