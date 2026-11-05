import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QMimeData
from pinq.session import PythonSession
from pinq.interpreter import InterpreterWidget

app = QApplication.instance() or QApplication([])

class TestInterpreterWidgetPaste(unittest.TestCase):
    def setUp(self):
        self.session = PythonSession()
        self.widget = InterpreterWidget(self.session)

    def test_single_line_paste(self):
        mime = QMimeData()
        mime.setText("x = 42")
        self.widget.insertFromMimeData(mime)

        # Single line should be inserted at prompt without immediately executing
        self.assertEqual(self.widget.get_current_line(), "x = 42")
        self.assertNotIn("x", self.session.locals)

    def test_multiline_paste_u2028(self):
        mime = QMimeData()
        # Qt line separator \u2028
        mime.setText("a = 10\u2028b = 20\u2028c = a + b\u2028")
        self.widget.insertFromMimeData(mime)

        # All lines ended with \u2028, so all should be executed sequentially
        self.assertEqual(self.session.locals.get("a"), 10)
        self.assertEqual(self.session.locals.get("b"), 20)
        self.assertEqual(self.session.locals.get("c"), 30)
        self.assertEqual(self.widget.get_current_line(), "")

    def test_multiline_paste_u2029(self):
        mime = QMimeData()
        # Qt paragraph separator \u2029
        mime.setText("val1 = 100\u2029val2 = 200\u2029")
        self.widget.insertFromMimeData(mime)

        self.assertEqual(self.session.locals.get("val1"), 100)
        self.assertEqual(self.session.locals.get("val2"), 200)

    def test_multiline_paste_without_trailing_newline(self):
        mime = QMimeData()
        mime.setText("p1 = 5\np2 = p1 * 2")
        self.widget.insertFromMimeData(mime)

        # First line (terminated by \n) executed, second line inserted into current prompt line
        self.assertEqual(self.session.locals.get("p1"), 5)
        self.assertEqual(self.widget.get_current_line(), "p2 = p1 * 2")

    def test_multiline_paste_function_definition(self):
        mime = QMimeData()
        mime.setText("def multiply(a, b):\n    return a * b\n\n")
        self.widget.insertFromMimeData(mime)

        self.assertIn("multiply", self.session.locals)
        func = self.session.locals["multiply"]
        self.assertEqual(func(6, 7), 42)

    def test_paste_when_cursor_in_history_area(self):
        # Move cursor to top of widget (in output area)
        cursor = self.widget.textCursor()
        cursor.setPosition(0)
        self.widget.setTextCursor(cursor)

        mime = QMimeData()
        mime.setText("k = 77\n")
        self.widget.insertFromMimeData(mime)

        # Paste should happen at input area, not top of document
        self.assertEqual(self.session.locals.get("k"), 77)

    def test_user_reported_two_lines_paste(self):
        mime = QMimeData()
        mime.setText("l = [5, 6]\u2028ll = [1, 2]\u2028")
        self.widget.insertFromMimeData(mime)

        self.assertEqual(self.session.locals.get("l"), [5, 6])
        self.assertEqual(self.session.locals.get("ll"), [1, 2])

    def test_process_command_with_multiline_u2028(self):
        # Directly call process_command with U+2028 separated string
        self.widget.process_command("r1 = 10\u2028r2 = 20")
        self.assertEqual(self.session.locals.get("r1"), 10)
        self.assertEqual(self.session.locals.get("r2"), 20)

    def test_clipboard_paste_method(self):
        QApplication.clipboard().setText("m = 99\n")
        self.widget.paste()
        self.assertEqual(self.session.locals.get("m"), 99)

if __name__ == "__main__":
    unittest.main()
