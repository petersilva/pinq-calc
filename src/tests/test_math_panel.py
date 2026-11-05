import unittest
from unittest.mock import patch
import math
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import Qt, QUrl
from pinq.main import MainWindow
from pinq.math_panel import MathModuleWidget, MODULE_DOC_URLS

app = QApplication.instance() or QApplication([])

class TestMathModulePanel(unittest.TestCase):
    def test_tabs_exist(self):
        panel = MathModuleWidget()
        tab_widget = panel.tab_widget
        self.assertIsNotNone(tab_widget)
        tab_titles = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        self.assertIn("Math", tab_titles)
        self.assertIn("NumPy", tab_titles)
        self.assertIn("Pandas", tab_titles)
        self.assertIn("Matplotlib", tab_titles)

    def test_switching_tabs(self):
        panel = MathModuleWidget()
        tab_widget = panel.tab_widget
        # Switch to NumPy (index 1), Pandas (index 2), Matplotlib (index 3)
        for idx in range(tab_widget.count()):
            tab_widget.setCurrentIndex(idx)
            self.assertEqual(tab_widget.currentIndex(), idx)

    def test_documentation_urls_and_tooltips(self):
        panel = MathModuleWidget()
        tab_widget = panel.tab_widget
        expected_modules = ["Math", "NumPy", "Pandas", "Matplotlib"]
        for mod in expected_modules:
            self.assertIn(mod, MODULE_DOC_URLS)
            self.assertTrue(MODULE_DOC_URLS[mod].startswith("https://"))

        for idx in range(tab_widget.count()):
            title = tab_widget.tabText(idx)
            tooltip = tab_widget.tabToolTip(idx)
            self.assertIn(MODULE_DOC_URLS[title], tooltip)

    def test_tab_bar_cursor(self):
        panel = MathModuleWidget()
        self.assertEqual(panel.tab_widget.tabBar().cursor().shape(), Qt.PointingHandCursor)

    def test_tab_click_opens_documentation(self):
        panel = MathModuleWidget()
        tab_widget = panel.tab_widget
        with patch("pinq.math_panel.QDesktopServices.openUrl") as mock_open_url:
            for idx in range(tab_widget.count()):
                title = tab_widget.tabText(idx)
                expected_url = MODULE_DOC_URLS[title]
                tab_widget.tabBarClicked.emit(idx)
                mock_open_url.assert_called_with(QUrl(expected_url))

    def test_math_panel_buttons_exist(self):
        panel = MathModuleWidget()
        buttons = panel.findChildren(QPushButton)
        button_labels = [btn.text() for btn in buttons]

        math_symbols = [k for k in dir(math) if not k.startswith('_')]
        for symbol in math_symbols:
            self.assertIn(symbol, button_labels)

    def test_math_panel_button_click_appends_to_interpreter(self):
        window = MainWindow()
        interpreter = window.interpreter
        math_panel = window.math_panel

        buttons = {btn.text(): btn for btn in math_panel.findChildren(QPushButton)}
        
        # Test clicking a function button (e.g. 'factorial')
        self.assertIn("factorial", buttons)
        buttons["factorial"].click()

        self.assertEqual(interpreter.get_current_line(), "factorial()")
        expected_pos = interpreter.input_start_pos + len("factorial(")
        self.assertEqual(interpreter.textCursor().position(), expected_pos)

        # Clear line
        interpreter.replace_current_line("")

        # Test clicking a constant button if present (e.g. 'tau' or 'e')
        const_name = "tau" if "tau" in buttons else "e"
        buttons[const_name].click()
        self.assertEqual(interpreter.get_current_line(), const_name)

if __name__ == "__main__":
    unittest.main()
