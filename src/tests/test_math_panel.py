import unittest
import math
from PySide6.QtWidgets import QApplication, QPushButton
from pinq.main import MainWindow
from pinq.math_panel import MathModuleWidget

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
