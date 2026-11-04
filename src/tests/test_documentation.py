import os
import unittest
from PySide6.QtWidgets import QApplication
from pinq.main import MainWindow, get_documentation_text

app = QApplication.instance() or QApplication([])

class TestDocumentation(unittest.TestCase):
    def test_get_documentation_text(self):
        doc = get_documentation_text()
        self.assertIn("Pinq-calc Documentation", doc)
        self.assertIn("Terminal", doc)
        self.assertIn("Keypad", doc)
        self.assertIn("Symbol Table", doc)

    def test_main_window_documentation_dialog(self):
        window = MainWindow()
        dialog = window.show_documentation(exec_dialog=False)
        self.assertEqual(dialog.windowTitle(), "Pinq-calc Documentation")
        self.assertEqual(dialog.width(), 600)
        self.assertEqual(dialog.height(), 600)

    def test_doc_action_triggers_show_documentation(self):
        window = MainWindow()
        called_args = []
        def mock_show_doc(exec_dialog=True):
            called_args.append(exec_dialog)
            return None
        window.show_documentation = mock_show_doc
        
        window.doc_action.trigger()
        self.assertEqual(called_args, [True])

if __name__ == "__main__":
    unittest.main()
