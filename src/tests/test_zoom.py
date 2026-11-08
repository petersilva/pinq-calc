import tempfile, os
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from pinq.main import MainWindow

app = QApplication.instance() or QApplication([])
TEST_CONFIG = os.path.join(tempfile.gettempdir(), "pinq_test_zoom_config.ini")

class TestFontZooming(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_CONFIG):
            os.remove(TEST_CONFIG)

    def tearDown(self):
        if os.path.exists(TEST_CONFIG):
            os.remove(TEST_CONFIG)

    def test_zoom_actions_exist(self):
        window = MainWindow(config_file=TEST_CONFIG)
        self.assertIsNotNone(window.zoom_in_action)
        self.assertIsNotNone(window.zoom_out_action)
        self.assertIsNotNone(window.reset_zoom_action)

    def test_zoom_in_out_reset(self):
        from PySide6.QtWidgets import QLabel
        window = MainWindow(config_file=TEST_CONFIG)
        initial_interp_font_size = window.interpreter.font().pointSize()
        initial_app_font_size = app.font().pointSize()
        self.assertEqual(window.font_size_delta, 0)

        # Zoom in
        window.zoom_in_action.trigger()
        self.assertEqual(window.font_size_delta, 1)
        self.assertEqual(window.interpreter.font().pointSize(), initial_interp_font_size + 1)
        self.assertEqual(app.font().pointSize(), initial_app_font_size + 1)

        # Zoom in again
        window.zoom_in()
        self.assertEqual(window.font_size_delta, 2)
        self.assertEqual(window.interpreter.font().pointSize(), initial_interp_font_size + 2)
        self.assertEqual(app.font().pointSize(), initial_app_font_size + 2)

        # Zoom out
        window.zoom_out_action.trigger()
        self.assertEqual(window.font_size_delta, 1)
        self.assertEqual(window.interpreter.font().pointSize(), initial_interp_font_size + 1)
        self.assertEqual(app.font().pointSize(), initial_app_font_size + 1)

        # Reset zoom
        window.reset_zoom_action.trigger()
        self.assertEqual(window.font_size_delta, 0)
        self.assertEqual(window.interpreter.font().pointSize(), initial_interp_font_size)
        self.assertEqual(app.font().pointSize(), initial_app_font_size)
        modules_header = window.math_panel.findChild(QLabel)
        self.assertEqual(modules_header.font().pointSize(), initial_app_font_size)
        self.assertEqual(window.math_panel.tab_widget.tabBar().font().pointSize(), initial_app_font_size)

    def test_zoom_config_persistence(self):
        window = MainWindow(config_file=TEST_CONFIG)
        window.zoom_in()
        window.zoom_in()
        self.assertEqual(window.font_size_delta, 2)

        # Reload window from config
        window2 = MainWindow(config_file=TEST_CONFIG)
        self.assertEqual(window2.font_size_delta, 2)

    def test_key_events_trigger_zoom(self):
        from PySide6.QtCore import Qt, QEvent
        from PySide6.QtGui import QKeyEvent

        window = MainWindow(config_file=TEST_CONFIG)
        initial_interp_font_size = window.interpreter.font().pointSize()
        self.assertEqual(window.font_size_delta, 0)

        # Send Ctrl+= key press
        evt_in = QKeyEvent(QEvent.KeyPress, Qt.Key_Equal, Qt.ControlModifier)
        app.sendEvent(window.interpreter, evt_in)
        self.assertEqual(window.font_size_delta, 1)
        self.assertEqual(window.interpreter.font().pointSize(), initial_interp_font_size + 1)

        # Send Ctrl+Plus key press
        evt_plus = QKeyEvent(QEvent.KeyPress, Qt.Key_Plus, Qt.ControlModifier)
        app.sendEvent(window.interpreter, evt_plus)
        self.assertEqual(window.font_size_delta, 2)
        self.assertEqual(window.interpreter.font().pointSize(), initial_interp_font_size + 2)

        # Send Ctrl+- key press
        evt_out = QKeyEvent(QEvent.KeyPress, Qt.Key_Minus, Qt.ControlModifier)
        app.sendEvent(window.interpreter, evt_out)
        self.assertEqual(window.font_size_delta, 1)
        self.assertEqual(window.interpreter.font().pointSize(), initial_interp_font_size + 1)

        # Send Ctrl+0 key press
        evt_zero = QKeyEvent(QEvent.KeyPress, Qt.Key_0, Qt.ControlModifier)
        app.sendEvent(window.interpreter, evt_zero)
        self.assertEqual(window.font_size_delta, 0)
        self.assertEqual(window.interpreter.font().pointSize(), initial_interp_font_size)

if __name__ == "__main__":
    unittest.main()
