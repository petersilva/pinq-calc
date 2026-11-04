import inspect
from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, 
                             QDialog, QTextEdit, QPushButton, QHBoxLayout, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, Signal

class FunctionEditorDialog(QDialog):
    def __init__(self, name, current_code, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Function: {name}")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        self.editor = QTextEdit()
        self.editor.setPlainText(current_code)
        self.editor.setFontPointSize(10)
        layout.addWidget(self.editor)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save && Redefine")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_code(self):
        return self.editor.toPlainText()

class SymbolTableWidget(QTableWidget):
    symbol_changed = Signal()
    name_clicked = Signal(str)

    def __init__(self, session, parent=None):
        super().__init__(0, 2, parent)
        self.session = session
        self.setHorizontalHeaderLabels(["Name", "Value / Type"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.itemClicked.connect(self.handle_item_clicked)
        self.itemDoubleClicked.connect(self.handle_double_click)
        self.itemChanged.connect(self.handle_item_changed)
        self._is_updating = False

    def handle_item_clicked(self, item):
        if item.column() == 0:
            name = item.text()
            val_item = self.item(item.row(), 1)
            type_role = val_item.data(Qt.UserRole) if val_item else None
            
            if type_role == "function" or callable(self.session.locals.get(name)):
                insert_text = f"{name}()"
            else:
                insert_text = name
            
            self.name_clicked.emit(insert_text)

    def refresh(self):
        self._is_updating = True
        self.setRowCount(0)
        symbols = self.session.get_user_symbols()
        
        for name, value in sorted(symbols.items()):
            row = self.rowCount()
            self.insertRow(row)
            
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            self.setItem(row, 0, name_item)
            
            is_func = callable(value)
            display_name = f"{name}()" if is_func else name
            insert_text = display_name
            
            btn = QPushButton(display_name)
            btn.setToolTip(f"Click to insert '{display_name}' into interpreter")
            btn.clicked.connect(lambda checked, t=insert_text: self.name_clicked.emit(t))
            self.setCellWidget(row, 0, btn)
            
            if is_func:
                display_val = f"<function {name}>"
                value_item = QTableWidgetItem(display_val)
                value_item.setFlags(value_item.flags() ^ Qt.ItemIsEditable)
                value_item.setData(Qt.UserRole, "function")
            else:
                display_val = repr(value)
                value_item = QTableWidgetItem(display_val)
                value_item.setData(Qt.UserRole, "variable")
            
            self.setItem(row, 1, value_item)
        self._is_updating = False

    def handle_double_click(self, item):
        if item.column() != 1:
            return
            
        name = self.item(item.row(), 0).text()
        type_role = item.data(Qt.UserRole)
        
        if type_role == "function":
            # Try to get from source cache first, then fall back to inspect
            code_str = self.session.source_cache.get(name)
            if not code_str:
                func = self.session.locals.get(name)
                try:
                    code_str = inspect.getsource(func)
                except Exception:
                    code_str = f"# Could not retrieve source for {name}\n# Please define it using 'def {name}(...):' in the interpreter"
            
            dialog = FunctionEditorDialog(name, code_str, self)
            if dialog.exec():
                new_code = dialog.get_code()
                try:
                    self.session.update_function(name, new_code)
                    self.refresh()
                    self.symbol_changed.emit()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to redefine function: {e}")

    def handle_item_changed(self, item):
        if self._is_updating or item.column() != 1:
            return
            
        name = self.item(item.row(), 0).text()
        type_role = item.data(Qt.UserRole)
        
        if type_role == "variable":
            new_value_expr = item.text()
            try:
                self.session.update_variable(name, new_value_expr)
                self.refresh() # Normalize display
                self.symbol_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "Invalid Value", str(e))
                self.refresh()
