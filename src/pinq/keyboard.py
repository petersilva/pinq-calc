from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QSizePolicy)
from PySide6.QtCore import Signal, Qt

SHIFT_MAP = {
    '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
    '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
    '-': '_', '=': '+', '[': '{', ']': '}', ';': ':',
    "'": '"', ',': '<', '.': '>', '/': '?'
}

ROW_LAYOUTS = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '+', 'Backspace'],
    ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '(', ')', '['],
    ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ':', '"', 'Enter'],
    ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', '_', 'Shift'],
    ['Space', '←', '→', 'Clear']
]

class KeyboardWidget(QWidget):
    key_pressed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_shift = False
        self.is_caps = False
        self.buttons = {}
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(3)
        
        for row in ROW_LAYOUTS:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(3)
            for key in row:
                btn = QPushButton(key)
                btn.setFocusPolicy(Qt.NoFocus)
                btn.setMinimumHeight(28)
                
                if key == 'Space':
                    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif key in ('Backspace', 'Enter', 'Shift', 'Caps', 'Tab', 'Clear'):
                    btn.setMinimumWidth(55)
                else:
                    btn.setMinimumWidth(26)
                    
                btn.clicked.connect(lambda checked, k=key: self._handle_key_click(k))
                row_layout.addWidget(btn)
                self.buttons[key] = btn
                
            main_layout.addLayout(row_layout)

    def _handle_key_click(self, key_name):
        if key_name == 'Shift':
            self.is_shift = not self.is_shift
            self._update_button_labels()
            return
        elif key_name == 'Caps':
            self.is_caps = not self.is_caps
            self._update_button_labels()
            return

        # Determine character to emit
        char_to_emit = key_name
        if key_name == 'Space':
            char_to_emit = ' '
        elif key_name == '←':
            char_to_emit = 'Left'
        elif key_name == '→':
            char_to_emit = 'Right'
        elif len(key_name) == 1:
            if key_name.isalpha():
                if self.is_shift or self.is_caps:
                    char_to_emit = key_name.upper()
                else:
                    char_to_emit = key_name.lower()
            else:
                if self.is_shift and key_name in SHIFT_MAP:
                    char_to_emit = SHIFT_MAP[key_name]
                else:
                    char_to_emit = key_name

        self.key_pressed.emit(char_to_emit)

        # Reset Shift after typing a character
        if self.is_shift and not self.is_caps:
            self.is_shift = False
            self._update_button_labels()

    def _update_button_labels(self):
        use_upper = self.is_shift or self.is_caps
        for key_name, btn in self.buttons.items():
            if key_name in ('Shift', 'Caps', 'Tab', 'Enter', 'Backspace', 'Space', 'Clear', '←', '→'):
                if key_name == 'Shift':
                    btn.setText("SHIFT" if self.is_shift else "Shift")
                elif key_name == 'Caps':
                    btn.setText("CAPS" if self.is_caps else "Caps")
                continue
                
            if len(key_name) == 1 and key_name.isalpha():
                btn.setText(key_name.upper() if use_upper else key_name.lower())
            elif self.is_shift and key_name in SHIFT_MAP:
                btn.setText(SHIFT_MAP[key_name])
            else:
                btn.setText(key_name)
