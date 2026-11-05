import tempfile, os
import unittest
from PySide6.QtWidgets import QApplication
from pinq.main import MainWindow
from pinq.keyboard import KeyboardWidget

app = QApplication.instance() or QApplication([])
TEST_CONFIG = os.path.join(tempfile.gettempdir(), "pinq_test_keyboard_config.ini")

class TestKeyboardWidgetAndWindow(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_CONFIG):
            os.remove(TEST_CONFIG)

    def test_keyboard_default_hidden(self):
        window = MainWindow(config_file=TEST_CONFIG)
        window.show()
        # By default, on-screen keyboard should NOT be shown
        self.assertTrue(window.keyboard_panel.isHidden())
        self.assertEqual(window.keyboard_toggle_btn.text(), "▲ Keyboard")
        self.assertFalse(window.show_keyboard_action.isChecked())

    def test_keyboard_toggle_button(self):
        window = MainWindow(config_file=TEST_CONFIG)
        window.show()
        self.assertTrue(window.keyboard_panel.isHidden())

        # Click toggle button to show keyboard
        window.keyboard_toggle_btn.click()
        self.assertFalse(window.keyboard_panel.isHidden())
        self.assertEqual(window.keyboard_toggle_btn.text(), "▼ Keyboard")
        self.assertTrue(window.show_keyboard_action.isChecked())

        # Click toggle button again to hide keyboard
        window.keyboard_toggle_btn.click()
        self.assertTrue(window.keyboard_panel.isHidden())
        self.assertEqual(window.keyboard_toggle_btn.text(), "▲ Keyboard")
        self.assertFalse(window.show_keyboard_action.isChecked())

    def test_keyboard_menu_action(self):
        window = MainWindow()
        window.show()
        self.assertFalse(window.show_keyboard_action.isChecked())

        # Trigger menu action to show keyboard
        window.show_keyboard_action.trigger()
        self.assertFalse(window.keyboard_panel.isHidden())
        self.assertEqual(window.keyboard_toggle_btn.text(), "▼ Keyboard")

        # Trigger menu action again to hide keyboard
        window.show_keyboard_action.trigger()
        self.assertTrue(window.keyboard_panel.isHidden())
        self.assertEqual(window.keyboard_toggle_btn.text(), "▲ Keyboard")

    def test_keyboard_typing_into_interpreter(self):
        window = MainWindow()
        window.show()
        interpreter = window.interpreter
        keyboard = window.keyboard_panel

        # Type 'x = 42' using keyboard buttons
        keyboard.buttons['x'].click()
        keyboard.buttons['='].click()
        keyboard.buttons['4'].click()
        keyboard.buttons['2'].click()

        self.assertEqual(interpreter.get_current_line(), "x = 42")

        # Backspace
        keyboard.buttons['Backspace'].click()
        self.assertEqual(interpreter.get_current_line(), "x = 4")

        # Enter
        keyboard.buttons['Enter'].click()
        self.assertEqual(window.session.locals.get('x'), 4)

    def test_keyboard_shift_and_caps(self):
        keyboard = KeyboardWidget()
        emitted = []
        keyboard.key_pressed.connect(emitted.append)

        # Test parenthesis buttons
        self.assertIn('(', keyboard.buttons)
        self.assertIn(')', keyboard.buttons)
        keyboard.buttons[')'].click()
        self.assertEqual(emitted[-1], ')')

        # Test lowercase
        keyboard.buttons['a'].click()
        self.assertEqual(emitted[-1], 'a')

        # Test shift (single char upper)
        keyboard.buttons['Shift'].click()
        keyboard.buttons['b'].click()
        self.assertEqual(emitted[-1], 'B')

        # Shift should reset automatically
        keyboard.buttons['c'].click()
        self.assertEqual(emitted[-1], 'c')

        # Test caps lock
        keyboard.buttons['Caps'].click()
        keyboard.buttons['d'].click()
        self.assertEqual(emitted[-1], 'D')
        keyboard.buttons['e'].click()
        self.assertEqual(emitted[-1], 'E')

if __name__ == "__main__":
    unittest.main()
