import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavToolbar
from matplotlib.figure import Figure

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFileDialog, QMessageBox, QGroupBox, QSizePolicy, QFrame
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

matplotlib.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

PALETTE = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]

CHART_TYPES = [
    "Bar – Penjualan per Cabang",
    "Bar – Produk Terlaris",
    "Line – Tren Penjualan Harian",
    "Pie – Distribusi Metode Pembayaran",
    "Pie – Distribusi Jenis Pelanggan",
    "Scatter – Harga vs Jumlah Beli",
    "Histogram – Distribusi Rating",
    "Box – Total per Kategori Produk",
]

class ChartWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._df: pd.DataFrame = pd.DataFrame()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("📊  Visualisasi Data")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        root.addWidget(title)

        ctrl_box = QGroupBox("Pengaturan Chart")
        ctrl_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 11px; color: #2d3748;
                border: 1px solid #cbd5e0; border-radius: 6px;
                margin-top: 10px; padding: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px; 
            }
        """)
        
        ctrl_layout = QVBoxLayout(ctrl_box)
        ctrl_layout.setSpacing(10)

        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(12)
        
        lbl_jenis = QLabel("Jenis Chart:")
        lbl_jenis.setStyleSheet("color: #2d3748; font-weight: 500;")
        row1_layout.addWidget(lbl_jenis)

        self._chart_combo = QComboBox()
        self._chart_combo.addItems(CHART_TYPES)
        self._chart_combo.setMinimumWidth(200) 
        self._chart_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._chart_combo.setStyleSheet(self._combo_style())
        row1_layout.addWidget(self._chart_combo)

        row1_layout.addStretch() 

        self._refresh_btn = QPushButton(" 🔄  Refresh")
        self._refresh_btn.setMinimumWidth(100)
        self._refresh_btn.setStyleSheet(self._btn_style("#3498db"))
        self._refresh_btn.clicked.connect(self.refresh_chart)
        row1_layout.addWidget(self._refresh_btn)

        self._export_btn = QPushButton(" 💾  Export PNG")
        self._export_btn.setMinimumWidth(110)
        self._export_btn.setStyleSheet(self._btn_style("#27ae60"))
        self._export_btn.clicked.connect(self._export_png)
        row1_layout.addWidget(self._export_btn)

        ctrl_layout.addLayout(row1_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #edf2f7;")
        ctrl_layout.addWidget(sep)

        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(12)

        lbl_cabang = QLabel("Cabang:")
        lbl_cabang.setStyleSheet("color: #2d3748; font-weight: 500;")
        row2_layout.addWidget(lbl_cabang)
        self._branch_combo = QComboBox()
        self._branch_combo.setMinimumWidth(100)
        self._branch_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._branch_combo.setStyleSheet(self._combo_style())
        row2_layout.addWidget(self._branch_combo)

        lbl_gender = QLabel("Gender:")
        lbl_gender.setStyleSheet("color: #2d3748; font-weight: 500;")
        row2_layout.addWidget(lbl_gender)
        self._gender_combo = QComboBox()
        self._gender_combo.setMinimumWidth(100)
        self._gender_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._gender_combo.setStyleSheet(self._combo_style())
        row2_layout.addWidget(self._gender_combo)

        lbl_pembayaran = QLabel("Pembayaran:")
        lbl_pembayaran.setStyleSheet("color: #2d3748; font-weight: 500;")
        row2_layout.addWidget(lbl_pembayaran)
        self._payment_combo = QComboBox()
        self._payment_combo.setMinimumWidth(100)
        self._payment_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._payment_combo.setStyleSheet(self._combo_style())
        row2_layout.addWidget(self._payment_combo)

        row2_layout.addStretch() 
        ctrl_layout.addLayout(row2_layout)
        
        root.addWidget(ctrl_box)

        self._figure = Figure(figsize=(10, 5), dpi=100)
        self._figure.patch.set_facecolor("#ffffff") 
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root.addWidget(self._canvas)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        root.addWidget(self._status_label)

    def load_dataframe(self, df: pd.DataFrame):
        self._df = df.copy()
        self._populate_filters()
        self.refresh_chart()

    def refresh_chart(self):
        df = self._filtered_df()
        if df.empty:
            self._show_empty()
            return

        chart_name = self._chart_combo.currentText()
        self._figure.clear()

        try:
            if chart_name.startswith("Bar – Penjualan per Cabang"):
                self._chart_bar_branch(df)
            elif chart_name.startswith("Bar – Produk Terlaris"):
                self._chart_bar_product(df)
            elif chart_name.startswith("Line – Tren"):
                self._chart_line_trend(df)
            elif chart_name.startswith("Pie – Distribusi Metode"):
                self._chart_pie_payment(df)
            elif chart_name.startswith("Pie – Distribusi Jenis"):
                self._chart_pie_customer(df)
            elif chart_name.startswith("Scatter"):
                self._chart_scatter(df)
            elif chart_name.startswith("Histogram"):
                self._chart_histogram(df)
            elif chart_name.startswith("Box"):
                self._chart_box(df)

            self._figure.tight_layout(pad=2)
            self._canvas.draw()
            self._status_label.setText(
                f"✅  Menampilkan data {len(df):,} transaksi | Filter aktif: {self._active_filters()}"
            )
        except Exception as exc:
            self._show_empty(str(exc))

    def _chart_bar_branch(self, df: pd.DataFrame):
        ax = self._figure.add_subplot(111)
        data = df.groupby("Branch")["Total"].sum().sort_values(ascending=False)
        bars = ax.bar(data.index, data.values, color=PALETTE[:len(data)], edgecolor="white", linewidth=1.5)
        ax.set_title("Total Penjualan per Cabang", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Cabang"); ax.set_ylabel("Total Penjualan (USD)")
        ax.bar_label(bars, fmt="${:,.0f}", padding=4, fontsize=10)
        ax.set_facecolor("#f8f9fa")

    def _chart_bar_product(self, df: pd.DataFrame):
        ax = self._figure.add_subplot(111)
        data = df.groupby("Product line")["Total"].sum().sort_values()
        colors = PALETTE[:len(data)]
        bars = ax.barh(data.index, data.values, color=colors, edgecolor="white")
        ax.set_title("Total Penjualan per Kategori Produk", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Total Penjualan (USD)")
        ax.bar_label(bars, fmt="${:,.0f}", padding=4, fontsize=9)
        ax.set_facecolor("#f8f9fa")

    def _chart_line_trend(self, df: pd.DataFrame):
        ax = self._figure.add_subplot(111)
        if "Date" not in df.columns or df["Date"].isna().all():
            ax.text(0.5, 0.5, "Kolom Date tidak tersedia", ha="center", va="center")
            return
        daily = df.groupby("Date")["Total"].sum().sort_index()
        ax.plot(daily.index, daily.values, color=PALETTE[0], linewidth=2, marker="o",
                markersize=4, markerfacecolor=PALETTE[2])
        ax.fill_between(daily.index, daily.values, alpha=0.15, color=PALETTE[0])
        ax.set_title("Tren Total Penjualan Harian", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Tanggal"); ax.set_ylabel("Total Penjualan (USD)")
        ax.tick_params(axis="x", rotation=30)
        ax.set_facecolor("#f8f9fa")

    def _chart_pie_payment(self, df: pd.DataFrame):
        ax = self._figure.add_subplot(111)
        data = df["Payment"].value_counts()
        wedges, texts, autotexts = ax.pie(
            data.values, labels=data.index, autopct="%1.1f%%",
            colors=PALETTE[:len(data)], startangle=140,
            wedgeprops={"edgecolor": "white", "linewidth": 2}
        )
        for at in autotexts:
            at.set_fontsize(10); at.set_fontweight("bold")
        ax.set_title("Distribusi Metode Pembayaran", fontsize=14, fontweight="bold", pad=15)

    def _chart_pie_customer(self, df: pd.DataFrame):
        ax = self._figure.add_subplot(111)
        data = df["Customer type"].value_counts()
        wedges, texts, autotexts = ax.pie(
            data.values, labels=data.index, autopct="%1.1f%%",
            colors=[PALETTE[0], PALETTE[1]], startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2},
            explode=[0.05] * len(data)
        )
        for at in autotexts:
            at.set_fontsize(11); at.set_fontweight("bold")
        ax.set_title("Distribusi Jenis Pelanggan", fontsize=14, fontweight="bold", pad=15)

    def _chart_scatter(self, df: pd.DataFrame):
        ax = self._figure.add_subplot(111)
        colors_map = {g: PALETTE[i] for i, g in enumerate(df["Gender"].unique())}
        for gender, grp in df.groupby("Gender"):
            ax.scatter(grp["Unit price"], grp["Quantity"],
                       alpha=0.6, color=colors_map[gender], label=gender,
                       edgecolors="white", linewidths=0.5, s=60)
        ax.set_title("Harga Satuan vs Jumlah Pembelian", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Harga Satuan (USD)"); ax.set_ylabel("Jumlah Item")
        ax.legend(title="Gender")
        ax.set_facecolor("#f8f9fa")

    def _chart_histogram(self, df: pd.DataFrame):
        ax = self._figure.add_subplot(111)
        ax.hist(df["Rating"].dropna(), bins=15, color=PALETTE[4],
                edgecolor="white", linewidth=1.2, alpha=0.85)
        mean_val = df["Rating"].mean()
        ax.axvline(mean_val, color=PALETTE[1], linestyle="--", linewidth=2,
                   label=f"Rata-rata: {mean_val:.2f}")
        ax.set_title("Distribusi Rating Pelanggan", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Rating"); ax.set_ylabel("Frekuensi")
        ax.legend()
        ax.set_facecolor("#f8f9fa")

    def _chart_box(self, df: pd.DataFrame):
        ax = self._figure.add_subplot(111)
        groups = [grp["Total"].dropna().values
                  for _, grp in df.groupby("Product line")]
        labels = [k for k, _ in df.groupby("Product line")]
        bp = ax.boxplot(groups, patch_artist=True, notch=False,
                        medianprops={"color": "white", "linewidth": 2})
        for patch, color in zip(bp["boxes"], PALETTE):
            patch.set_facecolor(color); patch.set_alpha(0.8)
        ax.set_xticks(range(1, len(labels) + 1))
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
        ax.set_title("Distribusi Total Transaksi per Kategori Produk",
                     fontsize=14, fontweight="bold", pad=15)
        ax.set_ylabel("Total (USD)")
        ax.set_facecolor("#f8f9fa")

    def _populate_filters(self):
        for combo, col in [
            (self._branch_combo, "Branch"),
            (self._gender_combo, "Gender"),
            (self._payment_combo, "Payment"),
        ]:
            combo.clear()
            combo.addItem("Semua")
            if col in self._df.columns:
                combo.addItems(sorted(self._df[col].dropna().unique().tolist()))

    def _filtered_df(self) -> pd.DataFrame:
        df = self._df.copy()
        mapping = [
            (self._branch_combo, "Branch"),
            (self._gender_combo, "Gender"),
            (self._payment_combo, "Payment"),
        ]
        for combo, col in mapping:
            val = combo.currentText()
            if val and val != "Semua":
                df = df[df[col] == val]
        return df

    def _active_filters(self) -> str:
        parts = []
        for combo, label in [
            (self._branch_combo, "Cabang"),
            (self._gender_combo, "Gender"),
            (self._payment_combo, "Pembayaran"),
        ]:
            if combo.currentText() not in ("Semua", ""):
                parts.append(f"{label}={combo.currentText()}")
        return ", ".join(parts) if parts else "Tidak ada"

    def _show_empty(self, msg: str = "Tidak ada data untuk filter ini."):
        self._figure.clear()
        ax = self._figure.add_subplot(111)
        ax.text(0.5, 0.5, f"⚠  {msg}", ha="center", va="center",
                fontsize=12, color="#e74c3c",
                transform=ax.transAxes)
        ax.set_axis_off()
        self._canvas.draw()

    def _export_png(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Chart sebagai PNG",
            os.path.expanduser("~/supermarket_chart.png"),
            "PNG Image (*.png)"
        )
        if path:
            self._figure.savefig(path, dpi=150, bbox_inches="tight",
                                 facecolor=self._figure.get_facecolor())
            QMessageBox.information(self, "Berhasil", f"Chart berhasil disimpan:\n{path}")

    @staticmethod
    def _combo_style() -> str:
        return """
            QComboBox {
                border: 1px solid #cbd5e0; 
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 12px; 
                background-color: #ffffff;
                color: #2d3748; 
            }
            QComboBox:hover { 
                border-color: #3182ce; 
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #2d3748;
                selection-background-color: #ebf8ff;
                selection-color: #2b6cb0;
                border: 1px solid #cbd5e0;
            }
        """

    @staticmethod
    def _btn_style(color: str) -> str:
        return f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 6px;
                padding: 6px 12px; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {color}cc; }}
            QPushButton:pressed {{ background: {color}99; }}
        """