import math
import types
from PySide6.QtWidgets import (QWidget, QScrollArea, QGridLayout, QPushButton,
                             QVBoxLayout, QLabel, QTabWidget)
from PySide6.QtCore import Signal, Qt

def create_module_scroll_grid(module_obj, prefix, on_click_signal):
    """Creates a scroll area with a grid of buttons for module exported symbols."""
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    
    container = QWidget()
    scroll_area.setWidget(container)
    
    grid_layout = QGridLayout(container)
    grid_layout.setContentsMargins(5, 5, 5, 5)
    grid_layout.setSpacing(5)
    
    cols = 2
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
        main_layout.addWidget(self.tab_widget)
        
        # Tab 1: Math
        math_tab = create_module_scroll_grid(math, "", self.button_clicked)
        self.tab_widget.addTab(math_tab, "Math")
        
        # Tab 2: NumPy
        try:
            import numpy as np
            numpy_tab = create_module_scroll_grid(np, "np.", self.button_clicked)
        except ImportError:
            numpy_tab = create_not_installed_widget("NumPy", "pip install numpy")
        self.tab_widget.addTab(numpy_tab, "NumPy")
        
        # Tab 3: Pandas
        try:
            import pandas as pd
            pandas_tab = create_module_scroll_grid(pd, "pd.", self.button_clicked)
        except ImportError:
            pandas_tab = create_not_installed_widget("Pandas", "pip install pandas")
        self.tab_widget.addTab(pandas_tab, "Pandas")
