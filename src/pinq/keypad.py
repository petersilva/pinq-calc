from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton
from PySide6.QtCore import Signal

class KeypadWidget(QWidget):
    button_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # (Display Label, Input String, Row, Col)
        buttons = [
            ('7', '7', 0, 0), ('8', '8', 0, 1), ('9', '9', 0, 2), ('/', '/', 0, 3),
            ('4', '4', 1, 0), ('5', '5', 1, 1), ('6', '6', 1, 2), ('*', '*', 1, 3),
            ('1', '1', 2, 0), ('2', '2', 2, 1), ('3', '3', 2, 2), ('-', '-', 2, 3),
            ('0', '0', 3, 0), ('.', '.', 3, 1), ('()', '()', 3, 2), ('+', '+', 3, 3),
            ('**', '**', 4, 0), ('sqrt', 'sqrt()', 4, 1), (')', ')', 4, 2), (',', ',', 4, 3),
            ('clear', 'clear()', 5, 0, 1, 2),
            ('=', '=', 5, 2, 1, 2),
        ]

        for button_data in buttons:
            if len(button_data) == 4:
                label, val, row, col = button_data
                row_span, col_span = 1, 1
            else:
                label, val, row, col, row_span, col_span = button_data
                
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, v=val: self.button_clicked.emit(v))
            layout.addWidget(btn, row, col, row_span, col_span)
