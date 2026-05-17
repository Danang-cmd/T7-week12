import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class KpiCard(QFrame):
    def __init__(self, icon_char: str, title: str, value: str, color: str, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(f"QFrame {{ background-color: {color}; border-radius: 10px; }}")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(110)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 12, 15, 12)
        main_layout.setSpacing(10)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self._title_lbl = QLabel(title)
        self._title_lbl.setFont(QFont("Segoe UI", 10))
        self._title_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.85); background: transparent;")
        self._title_lbl.setWordWrap(True)
        
        self._value_lbl = QLabel(value) 
        self._value_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._value_lbl.setStyleSheet("color: white; background: transparent;")
        self._value_lbl.setWordWrap(True)
        
        text_layout.addWidget(self._title_lbl)
        text_layout.addWidget(self._value_lbl)
        
        self._icon_lbl = QLabel(icon_char)
        self._icon_lbl.setFont(QFont("Segoe UI", 28))
        self._icon_lbl.setStyleSheet("color: rgba(255, 255, 255, 0.4); background: transparent;")
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_lbl.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        main_layout.addLayout(text_layout, stretch=3)
        main_layout.addWidget(self._icon_lbl, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_value(self, new_value: str):
        self._value_lbl.setText(new_value)

class SummaryWidget(QWidget):

    CARD_DEFS = [
        ("💰", "Total Pendapatan",   "#3498db"),
        ("🧾", "Total Transaksi",    "#e74c3c"),
        ("⭐", "Rating Rata-rata",   "#f39c12"),
        ("📦", "Rata-rata / Transaksi", "#2ecc71"),
        ("👥", "Pelanggan Member",   "#9b59b6"),
        ("🏪", "Cabang Aktif",       "#1abc9c"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: list[KpiCard] = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        title = QLabel("🏬  Dashboard Supermarket Sales")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        root.addWidget(title)

        subtitle = QLabel(
            "Dataset: Supermarket Sales  ·  Sumber: Kaggle (faresashraf1001/supermarket-sales)"
        )
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        root.addWidget(subtitle)

        for row_icons in [self.CARD_DEFS[:3], self.CARD_DEFS[3:]]:
            row = QHBoxLayout()
            row.setSpacing(16)
            for icon, title_text, color in row_icons:
                card = KpiCard(icon, title_text, "—", color)
                self._cards.append(card)
                row.addWidget(card)
            root.addLayout(row)

        desc_frame = QFrame()
        desc_frame.setStyleSheet("""
            QFrame {
                background: #f0f8ff;
                border: 1px solid #aed6f1;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(16, 12, 16, 12)

        desc_title = QLabel("ℹ️  Tentang Dataset")
        desc_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        desc_title.setStyleSheet("color: #1a5276;")

        desc_text = QLabel(
            "Dataset ini berisi transaksi penjualan dari supermarket fiktif dengan tiga cabang "
            "(A – Yangon, B – Mandalay, C – Naypyitaw). Kolom utama meliputi:\n"
            "  • Invoice ID, Branch, City, Customer type, Gender\n"
            "  • Product line, Unit price, Quantity, Tax 5%, Total\n"
            "  • Date, Time, Payment, cogs, gross income, Rating\n\n"
        )
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("color: #2c3e50; font-size: 12px; line-height: 1.5;")

        desc_layout.addWidget(desc_title)
        desc_layout.addWidget(desc_text)
        root.addWidget(desc_frame)
        root.addStretch()

    def load_dataframe(self, df: pd.DataFrame):
        if df.empty:
            return
            
        total_rev = df["Total"].sum()
        n_transactions = len(df)
        avg_rating = df["Rating"].mean()
        avg_total = df["Total"].mean()
        member_pct = (df["Customer type"] == "Member").mean() * 100
        n_branches = df["Branch"].nunique()
        
        values = [
            f"${total_rev:,.2f}",
            f"{n_transactions:,}",
            f"{avg_rating:.2f} / 10",
            f"${avg_total:,.2f}",
            f"{member_pct:.1f}%",
            f"{n_branches}"
        ]
        
        for card, val_str in zip(self._cards, values):
            card.update_value(val_str)