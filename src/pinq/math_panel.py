import math
from PySide6.QtWidgets import (QWidget, QScrollArea, QGridLayout, QPushButton,
                             QVBoxLayout, QLabel)
from PySide6.QtCore import Signal, Qt

class MathModuleWidget(QWidget):
    button_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Math Module")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        main_layout.addWidget(header)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        container = QWidget()
        scroll_area.setWidget(container)
        
        grid_layout = QGridLayout(container)
        grid_layout.setContentsMargins(5, 5, 5, 5)
        grid_layout.setSpacing(5)
        
        math_symbols = sorted([k for k in dir(math) if not k.startswith('_')])
        
        cols = 2
        row = 0
        col = 0
        
        for name in math_symbols:
            obj = getattr(math, name)
            is_func = callable(obj)
            
            label = name
            val = f"{name}()" if is_func else name
            
            btn = QPushButton(label)
            btn.setMinimumHeight(32)
            
            doc = getattr(obj, "__doc__", "")
            if doc:
                first_line = doc.strip().split('\n')[0]
                btn.setToolTip(f"{name}: {first_line}")
            
            btn.clicked.connect(lambda checked, v=val: self.button_clicked.emit(v))
            
            grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1
