import math
import types
from PySide6.QtWidgets import (QWidget, QScrollArea, QGridLayout, QPushButton,
                             QVBoxLayout, QLabel, QTabWidget)
from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtGui import QDesktopServices

MODULE_DOC_URLS = {
    "Math": "https://docs.python.org/3/library/math.html",
    "NumPy": "https://numpy.org/doc/",
    "Pandas": "https://pandas.pydata.org/docs/",
    "Matplotlib": "https://matplotlib.org/",
}

def create_module_scroll_grid(module_obj, prefix, on_click_signal):
    """Creates a scroll area with a grid of buttons for module exported symbols."""
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    
    container = QWidget()
    scroll_area.setWidget(container)
    
    grid_layout = QGridLayout(container)
    grid_layout.setContentsMargins(5, 5, 5, 5)
    grid_layout.setSpacing(5)
    
    cols = 3
    row = 0
    col = 0
    
    symbols = sorted([k for k in dir(module_obj) if not k.startswith('_')])
    
    for name in symbols:
        try:
            obj = getattr(module_obj, name)
            if isinstance(obj, types.ModuleType):
                continue
            
            is_func = callable(obj)
            val = f"{prefix}{name}()" if is_func else f"{prefix}{name}"
            
            btn = QPushButton(name)
            btn.setMinimumHeight(32)
            
            doc = getattr(obj, "__doc__", "") or ""
            if doc:
                first_line = doc.strip().split('\n')[0]
                btn.setToolTip(f"{prefix}{name}: {first_line}")
            else:
                btn.setToolTip(f"{prefix}{name}")
                
            btn.clicked.connect(lambda checked, v=val: on_click_signal.emit(v))
            
            grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        except Exception:
            pass
            
    return scroll_area

def create_not_installed_widget(module_name, install_cmd):
    """Creates a placeholder widget when a library is not installed."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignCenter)
    
    msg = QLabel(f"<b>{module_name}</b> is not installed.<br><br>To install, run:<br><code>{install_cmd}</code>")
    msg.setAlignment(Qt.AlignCenter)
    msg.setWordWrap(True)
    msg.setTextFormat(Qt.RichText)
    msg.setStyleSheet("padding: 15px; font-size: 13px;")
    
    layout.addWidget(msg)
    return widget

class MathModuleWidget(QWidget):
    button_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)
        
        header = QLabel("Modules")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        main_layout.addWidget(header)

        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setCursor(Qt.PointingHandCursor)
        main_layout.addWidget(self.tab_widget)
        
        self.lazy_tabs = {}
        
        # Tab 1: Math (built immediately)
        math_tab = create_module_scroll_grid(math, "", self.button_clicked)
        self.tab_widget.addTab(math_tab, "Math")
        
        # Tabs 2-4: Lazy container tabs
        self._add_lazy_tab("NumPy", self._build_numpy_tab)
        self._add_lazy_tab("Pandas", self._build_pandas_tab)
        self._add_lazy_tab("Matplotlib", self._build_matplotlib_tab)
        
        for idx in range(self.tab_widget.count()):
            title = self.tab_widget.tabText(idx)
            url = MODULE_DOC_URLS.get(title)
            if url:
                self.tab_widget.setTabToolTip(idx, f"Documentation: {url}")
        
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabBarClicked.connect(self._on_tab_bar_clicked)

    def _on_tab_bar_clicked(self, index):
        title = self.tab_widget.tabText(index)
        url = MODULE_DOC_URLS.get(title)
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def _add_lazy_tab(self, title, builder_fn):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        index = self.tab_widget.addTab(container, title)
        self.lazy_tabs[index] = (container, builder_fn, False)

    def _on_tab_changed(self, index):
        if index in self.lazy_tabs:
            container, builder_fn, populated = self.lazy_tabs[index]
            if not populated:
                widget = builder_fn()
                container.layout().addWidget(widget)
                self.lazy_tabs[index] = (container, builder_fn, True)

    def _build_numpy_tab(self):
        try:
            import numpy as np
            return create_module_scroll_grid(np, "np.", self.button_clicked)
        except ImportError:
            return create_not_installed_widget("NumPy", "pip install numpy")

    def _build_pandas_tab(self):
        try:
            import pandas as pd
            return create_module_scroll_grid(pd, "pd.", self.button_clicked)
        except ImportError:
            return create_not_installed_widget("Pandas", "pip install pandas")

    def _build_matplotlib_tab(self):
        try:
            import matplotlib.pyplot as plt
            return create_module_scroll_grid(plt, "plt.", self.button_clicked)
        except ImportError:
            return create_not_installed_widget("Matplotlib", "pip install matplotlib")
