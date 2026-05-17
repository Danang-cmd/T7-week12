import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from PySide6.QtGui import QColor, QFont

class DataTableWidget(QWidget):

    COLUMN_COLORS = {
        "Branch":        "#e8f4fd",
        "City":          "#e8f4fd",
        "Product line":  "#fef9e7",
        "Total":         "#eafaf1",
        "gross income":  "#eafaf1",
        "Rating":        "#fdf2f8",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._full_df: pd.DataFrame = pd.DataFrame()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ── Header Row
        header_row = QHBoxLayout()
        title = QLabel("📋  Data Mentah Supermarket Sales")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")

        self._row_count_label = QLabel("")
        self._row_count_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(self._row_count_label)
        layout.addLayout(header_row)

        # ── Search Bar
        search_row = QHBoxLayout()
        search_icon = QLabel("🔍")
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("Cari di semua kolom…")
        self._search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                background: #fafafa;
            }
            QLineEdit:focus { border-color: #3498db; background: #fff; }
        """)
        self._search_box.textChanged.connect(self._on_search)
        search_row.addWidget(search_icon)
        search_row.addWidget(self._search_box)
        layout.addLayout(search_row)

        # ── Table Widget
        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # PERBAIKAN KOLOM TERPOTONG: Gunakan Interactive agar bisa di-resize manual 
        # dan beri ruang minimum di bagian isi sel datanya.
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self._table.horizontalHeader().setMinimumSectionSize(120) # Mencegah kolom menyempit ekstrim
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        
        # PERBAIKAN SCROLL BAR: Paksa scrollbar horizontal dan vertikal agar selalu muncul
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self._table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # STYLING BARU: Desain tabel dan custom scrollbar modern (tidak kaku bawaan OS Windows)
        self._table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dfe6e9;
                background-color: #ffffff;
                gridline-color: #e2e8f0;
                font-size: 12px;
                color: #2d3748; 
            }
            
            QTableWidget::item { 
                padding: 8px 12px; /* Perbesar padding horizontal agar teks tengah tidak terpotong */
                color: #2d3748;
            }
            
            QTableWidget::item:selected { 
                background-color: #3182ce; 
                color: #ffffff; 
            }
            
            QTableWidget::item:alternate { 
                background-color: #f7fafc; 
            }
            
            QHeaderView::section {
                background-color: #edf2f7;
                color: #2d3748;
                padding: 10px 6px; /* Tingkatkan padding atas-bawah header */
                font-weight: bold;
                border: 1px solid #cbd5e0;
            }
            
            /* ── STYLING SCROLLBAR HORIZONTAL ── */
            QScrollBar:horizontal {
                border: none;
                background: #f1f5f9;
                height: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #cbd5e0;
                min-width: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            
            /* ── STYLING SCROLLBAR VERTIKAL ── */
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        layout.addWidget(self._table)

    def load_dataframe(self, df: pd.DataFrame):
        self._full_df = df.copy()
        self._search_box.clear()
        self._populate(df)

    def _populate(self, df: pd.DataFrame):
        self._table.clearContents()
        self._table.setRowCount(0)

        if df.empty:
            self._row_count_label.setText("Tidak ada data")
            return

        cols = list(df.columns)
        self._table.setColumnCount(len(cols))
        self._table.setHorizontalHeaderLabels(cols)
        self._table.setRowCount(len(df))

        for row_idx, (_, row) in enumerate(df.iterrows()):
            for col_idx, col in enumerate(cols):
                val = row[col]
                # Format nomor desimal & uang agar lebih rapi
                if isinstance(val, float):
                    text = f"{val:,.2f}"
                elif hasattr(val, 'strftime'):  # format tanggal
                    text = val.strftime("%d %b %Y")
                else:
                    text = str(val)

                item = QTableWidgetItem(text)
                
                # Menggunakan AlignVCenter + AlignLeft untuk data teks, atau AlignRight untuk angka 
                # seringkali lebih aman daripada Center murni agar teks panjang tidak terpotong di kiri-kanan.
                # Namun di sini kita pakai Center yang aman berkat penambahan padding horizontal di CSS.
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                bg = self.COLUMN_COLORS.get(col)
                if bg:
                    item.setBackground(QColor(bg))

                self._table.setItem(row_idx, col_idx, item)

        # PERBAIKAN UTAMA NAMA KOLOM TERPOTONG:
        # Jalankan penyesuaian otomatis dulu, lalu ubah mode header ke Interactive.
        # Cara ini memastikan kolom otomatis melar mengikuti isi data TERPANJANG atau JUDUL KOLOM saat data pertama dimuat.
        self._table.resizeColumnsToContents()
        
        # Berikan padding bonus ekstra lebar pada setiap kolom setelah kalkulasi resize agar teks judul aman 100%
        for i in range(self._table.columnCount()):
            current_width = self._table.columnWidth(i)
            self._table.setColumnWidth(i, current_width + 24)

        count = len(df)
        total = len(self._full_df)
        self._row_count_label.setText(f"Menampilkan {count:,} dari {total:,} baris")

    def _on_search(self, text: str):
        if self._full_df.empty:
            return
        if not text.strip():
            self._populate(self._full_df)
            return
        mask = self._full_df.apply(
            lambda col: col.astype(str).str.contains(text, case=False, na=False)
        ).any(axis=1)
        self._populate(self._full_df[mask])