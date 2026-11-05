import sys
import os
import signal
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QFileDialog, QMessageBox,
                             QDialog, QTextEdit, QPushButton, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon

from pinq._version import __version__
from pinq.session import PythonSession
from pinq.interpreter import InterpreterWidget
from pinq.symbols import SymbolTableWidget
from pinq.keypad import KeypadWidget
from pinq.math_panel import MathModuleWidget
from pinq.keyboard import KeyboardWidget

def get_app_icon() -> QIcon:
    """Reads and returns the application QIcon from icon.png."""
    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    return QIcon()

def ensure_desktop_integration():
    """Installs XDG .desktop file and icon for Wayland / X11 taskbar integration on Linux."""
    if not sys.platform.startswith("linux"):
        return
        
    try:
        home = os.path.expanduser("~")
        apps_dir = os.path.join(home, ".local", "share", "applications")
        icons_dir = os.path.join(home, ".local", "share", "icons", "hicolor", "128x128", "apps")
        os.makedirs(apps_dir, exist_ok=True)
        os.makedirs(icons_dir, exist_ok=True)
        
        target_icon = os.path.join(icons_dir, "pinq-calc.png")
        source_icon = os.path.join(os.path.dirname(__file__), "icon.png")
            
        if os.path.exists(source_icon):
            import shutil
            shutil.copy2(source_icon, target_icon)
            
        desktop_file = os.path.join(apps_dir, "pinq-calc.desktop")
        desktop_content = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Pinq-calc\n"
            "Comment=Python Interpreted Nifty Qt Calculator\n"
            "Exec=pinq-calc\n"
            f"Icon={target_icon if os.path.exists(target_icon) else 'pinq-calc'}\n"
            "Terminal=false\n"
            "Categories=Utility;Calculator;\n"
            "StartupWMClass=pinq-calc\n"
        )
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(desktop_content)
    except Exception as e:
        print(f"Failed to setup desktop integration: {e}")

def get_documentation_text() -> str:
    """Reads and returns the contents of DOCUMENTATION.md."""
    doc_path = os.path.join(os.path.dirname(__file__), "DOCUMENTATION.md")
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"# Pinq-Calc Documentation\n\nFailed to load documentation file: {e}"

PINK_THEME = """
    QMainWindow {
        background-color: #FFF0F5;
    }
    QTableWidget {
        background-color: #FFF0F5;
        color: #2D2D2D;
        gridline-color: #E6E6E6;
        border: none;
    }
    QHeaderView::section {
        background-color: #FFD1DC;
        color: #2D2D2D;
        padding: 4px;
        border: 1px solid #E6E6E6;
    }
    QPushButton {
        background-color: #FFE4E1;
        color: #2D2D2D;
        border: 1px solid #FFC0CB;
        border-radius: 4px;
        font-size: 14px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #FFC0CB;
    }
    QPushButton:pressed {
        background-color: #FFB6C1;
    }
    QPushButton#keypad_toggle_btn, QPushButton#keyboard_toggle_btn {
        background-color: #FFE4E1;
        color: #2D2D2D;
        border: 1px solid #FFC0CB;
        border-radius: 2px;
        font-size: 11px;
        padding: 1px;
    }
    QSplitter::handle {
        background-color: #FFD1DC;
    }
    QTextEdit {
        background-color: #FFF0F5;
        color: #2D2D2D;
        border: 1px solid #FFC0CB;
    }
    QTabWidget::pane {
        border: 1px solid #FFC0CB;
        background-color: #FFF0F5;
    }
    QTabBar::tab {
        background-color: #FFE4E1;
        color: #2D2D2D;
        border: 1px solid #FFC0CB;
        padding: 4px 8px;
        font-weight: bold;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #FFD1DC;
        border-bottom-color: #FFD1DC;
    }
    QTabBar::tab:hover {
        background-color: #FFC0CB;
    }
"""

class MainWindow(QMainWindow):
    def __init__(self, config_file=None):
        super().__init__()
        self.setWindowTitle("Pinq-Calc (Python Interpreted Nifty Qt Calculator)")
        self.setWindowIcon(get_app_icon())
        self.resize(840, 750)

        self.session = PythonSession()
        self.current_file = None
        self.auto_save_file = os.path.expanduser("~/.pinq_session.py")
        self.config_file = config_file if config_file is not None else os.path.expanduser("~/.pinq_config.ini")
        self.use_system_colors = False
        self.show_keypad = True
        self.show_keyboard = False

        self.load_config()
        self.init_ui()
        self.create_menus()
        self.apply_theme()
        self.set_keypad_visible(self.show_keypad)
        self.set_keyboard_visible(self.show_keyboard)
        self.load_auto_session()

    def load_config(self):
        self.show_keypad = True
        self.show_keyboard = False
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    for line in f:
                        if line.startswith("use_system_colors="):
                            self.use_system_colors = line.strip().split('=')[1].lower() == 'true'
                        elif line.startswith("show_keypad="):
                            self.show_keypad = line.strip().split('=')[1].lower() == 'true'
                        elif line.startswith("show_keyboard="):
                            self.show_keyboard = line.strip().split('=')[1].lower() == 'true'
            except Exception as e:
                print(f"Failed to load config: {e}")

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                f.write(f"use_system_colors={self.use_system_colors}\n")
                f.write(f"show_keypad={self.show_keypad}\n")
                f.write(f"show_keyboard={self.show_keyboard}\n")
        except Exception as e:
            print(f"Failed to save config: {e}")

    def toggle_keypad(self):
        visible = not self.keypad.isVisible()
        self.set_keypad_visible(visible)

    def set_keypad_visible(self, visible: bool):
        self.keypad.setVisible(visible)
        if visible:
            self.keypad_toggle_btn.setText("▼ Keypad")
            self.keypad_toggle_btn.setToolTip("Click to hide keypad")
        else:
            self.keypad_toggle_btn.setText("▲ Keypad")
            self.keypad_toggle_btn.setToolTip("Click to show keypad")
        
        if hasattr(self, 'show_keypad_action'):
            self.show_keypad_action.setChecked(visible)
            
        self.show_keypad = visible
        self.save_config()

    def toggle_keyboard(self):
        visible = not self.keyboard_panel.isVisible()
        self.set_keyboard_visible(visible)

    def set_keyboard_visible(self, visible: bool):
        self.keyboard_panel.setVisible(visible)
        if visible:
            self.keyboard_toggle_btn.setText("▼ Keyboard")
            self.keyboard_toggle_btn.setToolTip("Click to hide on-screen keyboard")
        else:
            self.keyboard_toggle_btn.setText("▲ Keyboard")
            self.keyboard_toggle_btn.setToolTip("Click to show on-screen keyboard")
        
        if hasattr(self, 'show_keyboard_action'):
            self.show_keyboard_action.setChecked(visible)
            
        self.show_keyboard = visible
        self.save_config()

    def handle_keyboard_input(self, key_str):
        if key_str == "Enter":
            self.interpreter.execute_current_line()
        elif key_str == "Backspace":
            self.interpreter.handle_backspace()
        elif key_str == "Tab":
            self.interpreter.append_text("    ")
        elif key_str == "Clear":
            self.interpreter.process_command("clear()")
        elif key_str == "Left":
            cursor = self.interpreter.textCursor()
            if cursor.position() > self.interpreter.input_start_pos:
                cursor.movePosition(QTextCursor.Left)
                self.interpreter.setTextCursor(cursor)
        elif key_str == "Right":
            cursor = self.interpreter.textCursor()
            cursor.movePosition(QTextCursor.Right)
            self.interpreter.setTextCursor(cursor)
        else:
            self.interpreter.append_text(key_str)

    def apply_theme(self):
        if self.use_system_colors:
            QApplication.instance().setStyleSheet("")
        else:
            QApplication.instance().setStyleSheet(PINK_THEME)

    def init_ui(self):
        # Main Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)

        # Splitter for Left (Interpreter/Keypad), Middle (Math), and Right (Symbol Table)
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter, 1)

        # Left Side Container
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        
        # Interpreter
        self.interpreter = InterpreterWidget(self.session, self)
        left_layout.addWidget(self.interpreter, 3) 

        # Keypad
        self.keypad = KeypadWidget(self)
        left_layout.addWidget(self.keypad, 1)

        # Keypad Toggle Bar at bottom of left-hand column
        self.keypad_toggle_btn = QPushButton("▼ Keypad")
        self.keypad_toggle_btn.setObjectName("keypad_toggle_btn")
        self.keypad_toggle_btn.setToolTip("Click to hide/show keypad")
        self.keypad_toggle_btn.setMaximumHeight(20)
        self.keypad_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.keypad_toggle_btn.clicked.connect(self.toggle_keypad)
        left_layout.addWidget(self.keypad_toggle_btn, 0)

        # Middle Side Container (Math Module Panel)
        self.math_panel = MathModuleWidget(self)

        # Right Side Container (Symbol Table with Header)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_header = QLabel("User Defined")
        right_header.setAlignment(Qt.AlignCenter)
        right_header.setStyleSheet("font-weight: bold; padding: 5px;")
        right_layout.addWidget(right_header)

        self.symbol_table = SymbolTableWidget(self.session, self)
        right_layout.addWidget(self.symbol_table)
        
        self.splitter.addWidget(left_container)
        self.splitter.addWidget(self.math_panel)
        self.splitter.addWidget(right_container)

        # On-Screen Keyboard Panel (spans under all 3 columns)
        self.keyboard_panel = KeyboardWidget(self)
        main_layout.addWidget(self.keyboard_panel, 0)

        # Keyboard Toggle Bar (at bottom of application)
        self.keyboard_toggle_btn = QPushButton("▲ Keyboard")
        self.keyboard_toggle_btn.setObjectName("keyboard_toggle_btn")
        self.keyboard_toggle_btn.setToolTip("Click to show/hide on-screen keyboard")
        self.keyboard_toggle_btn.setMaximumHeight(20)
        self.keyboard_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.keyboard_toggle_btn.clicked.connect(self.toggle_keyboard)
        main_layout.addWidget(self.keyboard_toggle_btn, 0)
        
        # Connections
        self.interpreter.command_executed.connect(self.symbol_table.refresh)
        self.keypad.button_clicked.connect(self.interpreter.append_text)
        self.math_panel.button_clicked.connect(self.interpreter.append_text)
        self.symbol_table.name_clicked.connect(self.interpreter.append_text)
        self.keyboard_panel.key_pressed.connect(self.handle_keyboard_input)
        
        # Initial proportions
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.setStretchFactor(2, 2)
        
        # Set initial sizes to ensure clean split across 3 columns
        self.splitter.setSizes([220, 300, 220])

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        load_action = QAction("&Load", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_file)
        file_menu.addAction(load_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()
        
        settings_menu = file_menu.addMenu("&Settings")
        
        self.pinq_theme_action = QAction("Use &Pinq-calc Defaults", self, checkable=True)
        self.pinq_theme_action.setChecked(not self.use_system_colors)
        self.pinq_theme_action.triggered.connect(lambda: self.set_theme(system=False))
        settings_menu.addAction(self.pinq_theme_action)

        self.system_colors_action = QAction("Use System &Colours", self, checkable=True)
        self.system_colors_action.setChecked(self.use_system_colors)
        self.system_colors_action.triggered.connect(lambda: self.set_theme(system=True))
        settings_menu.addAction(self.system_colors_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View Menu
        view_menu = menubar.addMenu("&View")
        self.show_keypad_action = QAction("Show &Keypad", self, checkable=True)
        self.show_keypad_action.setShortcut("Ctrl+K")
        self.show_keypad_action.setChecked(self.show_keypad)
        self.show_keypad_action.triggered.connect(lambda checked: self.set_keypad_visible(checked))
        view_menu.addAction(self.show_keypad_action)

        self.show_keyboard_action = QAction("Show On-Screen &Keyboard", self, checkable=True)
        self.show_keyboard_action.setShortcut("Ctrl+Shift+K")
        self.show_keyboard_action.setChecked(self.show_keyboard)
        self.show_keyboard_action.triggered.connect(lambda checked: self.set_keyboard_visible(checked))
        view_menu.addAction(self.show_keyboard_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        self.doc_action = QAction("&Documentation", self)
        self.doc_action.setShortcut("F1")
        self.doc_action.triggered.connect(lambda: self.show_documentation())
        help_menu.addAction(self.doc_action)
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        QMessageBox.about(self, "About Pinq-calc", 
            "<h3>Pinq-calc</h3>"
            "<p>Python Interpreted Nifty Calculator</p>"
            "<p>A portable GUI calculator built with PySide6.</p>"
            f"<p>Version {__version__} </p>")

    def show_documentation(self, exec_dialog=True):
        doc_text = get_documentation_text()
        doc_dialog = QDialog(self)
        doc_dialog.setWindowTitle("Pinq-calc Documentation")
        doc_dialog.resize(600, 600)
        layout = QVBoxLayout(doc_dialog)
        
        view = QTextEdit()
        view.setReadOnly(True)
        view.setMarkdown(doc_text)
        layout.addWidget(view)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(doc_dialog.accept)
        layout.addWidget(close_btn)
        
        if exec_dialog:
            doc_dialog.exec()
        return doc_dialog

    def set_theme(self, system):
        self.use_system_colors = system
        self.pinq_theme_action.setChecked(not system)
        self.system_colors_action.setChecked(system)
        self.apply_theme()
        self.save_config()

    def load_auto_session(self):
        """Loads the session from the auto-save file if it exists."""
        if os.path.exists(self.auto_save_file):
            try:
                with open(self.auto_save_file, 'r') as f:
                    content = f.read()
                if content.strip():
                    self.session.execute(content)
                    self.symbol_table.refresh()
                    self.interpreter.append_text("# Restored previous session\n")
                    self.interpreter.process_command("")
            except Exception as e:
                print(f"Failed to load auto-save: {e}")

    def closeEvent(self, event: QCloseEvent):
        """Auto-save session before closing."""
        try:
            self._perform_save(self.auto_save_file, silent=True)
        except Exception as e:
            print(f"Failed to auto-save session: {e}")
        super().closeEvent(event)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Python File", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Execute content in session
                self.session.execute(content)
                self.symbol_table.refresh()
                self.interpreter.append_text(f"# Loaded: {file_path}\n")
                self.interpreter.process_command("") # Refresh prompt
                self.current_file = file_path
                self.setWindowTitle(f"Pinq - {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Could not load file: {e}")

    def save_file(self):
        if self.current_file:
            self._perform_save(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Session", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            if not file_path.endswith('.py'):
                file_path += '.py'
            self._perform_save(file_path)

    def _perform_save(self, file_path, silent=False):
        try:
            symbols = self.session.get_user_symbols()
            content = []
            
            # Save variables first
            for name, value in sorted(symbols.items()):
                if not callable(value):
                    content.append(f"{name} = {repr(value)}")
            
            if content: content.append("") # Spacer
            
            # Save functions from source cache
            for name in sorted(self.session.source_cache.keys()):
                if name in symbols and callable(symbols[name]):
                    content.append(self.session.source_cache[name])
                    content.append("")
            
            with open(file_path, 'w') as f:
                f.write("\n".join(content))
            
            if not silent:
                self.current_file = file_path
                self.setWindowTitle(f"Pinq - {file_path}")
                QMessageBox.information(self, "Success", f"Session saved to {file_path}")
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "Save Error", f"Could not save file: {e}")
            else:
                raise e

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    ensure_desktop_integration()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("pinq-calc")
    app.setDesktopFileName("pinq-calc")
    app.setWindowIcon(get_app_icon())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
