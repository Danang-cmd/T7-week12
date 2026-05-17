import pandas as pd
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTabWidget, QLabel, QPushButton, QComboBox,
    QGroupBox, QFrame, QSizePolicy, QStatusBar, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette

from utils.data_loader import load_data, get_filter_options, apply_filters
from ui.summary_widget import SummaryWidget
from ui.table_widget import DataTableWidget
from ui.chart_widget import ChartWidget

class DataLoader(QThread):
    done = Signal(object) 

    def run(self):
        df = load_data()
        self.done.emit(df)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Supermarket Sales Dashboard")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        self._raw_df: pd.DataFrame = pd.DataFrame()
        self._filter_options: dict = {}

        self._build_ui()
        self._apply_global_stylesheet()
        self._load_data_async()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self._tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dfe6e9; background: #ffffff; border-radius: 4px;
            }
            QTabBar::tab {
                padding: 8px 16px; font-size: 13px;
                background: #ecf0f1; color: #555;
                border: 1px solid #dfe6e9;
                border-bottom-color: #dfe6e9;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff; color: #2c3e50;
                border-bottom-color: #ffffff; font-weight: bold;
            }
            QTabBar::tab:hover:!selected { background: #dfe6e9; }
        """)

        self._summary_tab = SummaryWidget()
        self._table_tab = DataTableWidget()
        self._chart_tab = ChartWidget()

        self._tabs.addTab(self._chart_tab, "📊  Chart")
        self._tabs.addTab(self._summary_tab, "🏠  Ringkasan")
        self._tabs.addTab(self._table_tab, "📋  Data Mentah")

        content.addWidget(self._tabs)
        main_layout.addLayout(content)

        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Memuat data…")

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background: #2c3e50;
                border: none;
            }
        """)
        
        main_layout = QVBoxLayout(sidebar)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(16)
        
        logo = QLabel(" 🛒 ")
        logo.setFont(QFont("Segoe UI Emoji", 32))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: white;")
        
        app_name = QLabel("Supermarket\nDashboard")
        app_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet("color: white; line-height: 1.3;")
        
        layout.addWidget(logo)
        layout.addWidget(app_name)
        layout.addWidget(self._divider())
        
        filter_title = QLabel(" 🔽  Filter Global")
        filter_title.setStyleSheet("color: #bdc3c7; font-size: 11px; font-weight: bold;")
        layout.addWidget(filter_title)
        
        filter_defs = [
            ("Cabang",          "branch"),
            ("Kota",            "city"),
            ("Jenis Pelanggan", "customer_type"),
            ("Gender",          "gender"),
            ("Kategori Produk", "product_line"),
            ("Pembayaran",      "payment"),
        ]
        
        self._filter_combos: dict[str, QComboBox] = {}
        for label_text, key in filter_defs:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #ecf0f1; font-size: 11px;")
            combo = QComboBox()
            combo.addItem("Semua")
            combo.setStyleSheet("""
                QComboBox {
                    background: #34495e; color: white;
                    border: 1px solid #4a6278; border-radius: 4px;
                    padding: 4px 8px; font-size: 11px;
                }
                QComboBox:hover { border-color: #3498db; }
                QComboBox QAbstractItemView {
                    background: #2c3e50; color: white;
                    selection-background-color: #3498db;
                    border: 1px solid #4a6278;
                }
            """)
            self._filter_combos[key] = combo
            layout.addWidget(lbl)
            layout.addWidget(combo)
            
        apply_btn = QPushButton(" ✅   Terapkan Filter")
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #3498db; color: white;
                border: none; border-radius: 6px;
                padding: 8px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background: #2980b9; }
        """)
        apply_btn.clicked.connect(self._apply_filters)
        
        reset_btn = QPushButton(" 🔄  Reset Filter")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #7f8c8d; color: white;
                border: none; border-radius: 6px;
                padding: 8px; font-size: 12px;
            }
            QPushButton:hover { background: #636e72; }
        """)
        reset_btn.clicked.connect(self._reset_filters)
        
        layout.addWidget(apply_btn)
        layout.addWidget(reset_btn)
        layout.addStretch()
        
        footer = QLabel("Pemrograman Visual\n© 2024")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #636e72; font-size: 10px;")
        layout.addWidget(footer)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        return sidebar

    def _load_data_async(self):
        self._loader = DataLoader()
        self._loader.done.connect(self._on_data_loaded)
        self._loader.start()

    def _on_data_loaded(self, df: pd.DataFrame):
        self._raw_df = df
        self._filter_options = get_filter_options(df)
        self._populate_filter_combos()
        self._push_data(df)
        self._statusbar.showMessage(
            f"✅  Data berhasil dimuat: {len(df):,} baris, {len(df.columns)} kolom  |  "
            f"Dataset: Supermarket Sales (Kaggle)"
        )

    def _push_data(self, df: pd.DataFrame):
        self._summary_tab.load_dataframe(df)
        self._table_tab.load_dataframe(df)
        self._chart_tab.load_dataframe(df)

    def _populate_filter_combos(self):
        col_map = {
            "branch":        "Branch",
            "city":          "City",
            "customer_type": "Customer type",
            "gender":        "Gender",
            "product_line":  "Product line",
            "payment":       "Payment",
        }
        for key, combo in self._filter_combos.items():
            col = col_map[key]
            combo.clear()
            combo.addItems(self._filter_options.get(col, ["Semua"]))

    def _apply_filters(self):
        col_map = {
            "branch":        "Branch",
            "city":          "City",
            "customer_type": "Customer type",
            "gender":        "Gender",
            "product_line":  "Product line",
            "payment":       "Payment",
        }
        filters = {}
        for key, combo in self._filter_combos.items():
            val = combo.currentText()
            if val and val != "Semua":
                filters[col_map[key]] = val

        filtered = apply_filters(self._raw_df, filters)
        self._push_data(filtered)
        self._statusbar.showMessage(
            f"🔽  Filter diterapkan — {len(filtered):,} dari {len(self._raw_df):,} baris ditampilkan"
        )

    def _reset_filters(self):
        for combo in self._filter_combos.values():
            combo.setCurrentIndex(0)
        self._push_data(self._raw_df)
        self._statusbar.showMessage("🔄  Filter direset — menampilkan semua data")

    @staticmethod
    def _divider() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #4a6278;")
        return line

    def _apply_global_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow { background: #f5f6fa; }
            QStatusBar {
                background: #2c3e50; color: #bdc3c7;
                font-size: 11px; padding: 2px 8px;
            }
            QScrollBar:vertical {
                width: 8px; background: #ecf0f1; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7; border-radius: 4px;
            }
        """)