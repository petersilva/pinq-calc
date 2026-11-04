import unittest
from PySide6.QtWidgets import QApplication, QLabel
from pinq.main import MainWindow
from pinq.keypad import KeypadWidget

app = QApplication.instance() or QApplication([])

class TestKeypadAndWindow(unittest.TestCase):
    def test_window_size(self):
        window = MainWindow()
        self.assertEqual(window.width(), 750)
        self.assertEqual(window.height(), 750)

    def test_right_column_header(self):
        window = MainWindow()
        labels = [w.text() for w in window.findChildren(QLabel)]
        self.assertIn("User Defined", labels)
        self.assertIn("Math Module", labels)

    def test_keypad_toggle_button(self):
        window = MainWindow()
        window.show()
        self.assertTrue(window.keypad.isVisible())
        self.assertEqual(window.keypad_toggle_btn.text(), "▼ Keypad")

        # Click toggle button to hide keypad
        window.keypad_toggle_btn.click()
        self.assertTrue(window.keypad.isHidden())
        self.assertEqual(window.keypad_toggle_btn.text(), "▲ Keypad")

        # Click toggle button to show keypad again
        window.keypad_toggle_btn.click()
        self.assertFalse(window.keypad.isHidden())
        self.assertEqual(window.keypad_toggle_btn.text(), "▼ Keypad")

    def test_keypad_view_menu_action(self):
        window = MainWindow()
        window.show()
        self.assertTrue(window.show_keypad_action.isChecked())
        self.assertTrue(window.keypad.isVisible())

        # Trigger view action to hide keypad
        window.show_keypad_action.trigger()
        self.assertTrue(window.keypad.isHidden())
        self.assertEqual(window.keypad_toggle_btn.text(), "▲ Keypad")

        # Trigger view action to show keypad
        window.show_keypad_action.trigger()
        self.assertFalse(window.keypad.isHidden())
        self.assertEqual(window.keypad_toggle_btn.text(), "▼ Keypad")

    def test_keypad_labels_omit_open_paren(self):
        keypad = KeypadWidget()
        buttons = keypad.findChildren(type(keypad.children()[1]))
        labels = [btn.text() for btn in buttons if hasattr(btn, 'text')]
        # Check that hex, oct, () are present, but sqrt, sin, cos, tan, pi, e are omitted
        self.assertIn('hex', labels)
        self.assertIn('oct', labels)
        self.assertIn('()', labels)
        self.assertNotIn('sqrt', labels)
        self.assertNotIn('sin', labels)
        self.assertNotIn('cos', labels)
        self.assertNotIn('tan', labels)
        self.assertNotIn('π', labels)
        self.assertNotIn('e', labels)

    def test_keypad_hex_and_oct_buttons(self):
        window = MainWindow()
        window.show()
        interpreter = window.interpreter
        keypad = window.keypad

        buttons = {btn.text(): btn for btn in keypad.findChildren(type(keypad.children()[1])) if hasattr(btn, 'text')}
        self.assertIn('hex', buttons)
        self.assertIn('oct', buttons)

        # Click 'hex' button
        buttons['hex'].click()
        self.assertEqual(interpreter.get_current_line(), "hex()")

        interpreter.replace_current_line("")

        # Click 'oct' button
        buttons['oct'].click()
        self.assertEqual(interpreter.get_current_line(), "oct()")

    def test_interpreter_append_text_positions_cursor(self):
        window = MainWindow()
        interpreter = window.interpreter

        # Test appending sin()
        interpreter.append_text("sin()")
        line = interpreter.get_current_line()
        self.assertEqual(line, "sin()")
        
        # Cursor should be between ( and ), at position input_start_pos + len("sin(")
        expected_pos = interpreter.input_start_pos + len("sin(")
        self.assertEqual(interpreter.textCursor().position(), expected_pos)

        # Typing additional input inserts inside parens
        interpreter.append_text("5")
        self.assertEqual(interpreter.get_current_line(), "sin(5)")

    def test_symbol_table_click_name(self):
        window = MainWindow()
        session = window.session
        symbol_table = window.symbol_table
        interpreter = window.interpreter

        # Verify vertical header (numbering) is hidden
        self.assertFalse(symbol_table.verticalHeader().isVisible())

        # Define variable and function
        session.execute("my_var = 123")
        session.execute("def my_func(a):\n    return a + 1")
        symbol_table.refresh()

        # Find row for my_var and my_func
        var_row = -1
        func_row = -1
        for row in range(symbol_table.rowCount()):
            item = symbol_table.item(row, 0)
            if item.text() == "my_var":
                var_row = row
            elif item.text() == "my_func":
                func_row = row

        self.assertNotEqual(var_row, -1)
        self.assertNotEqual(func_row, -1)

        # Verify cell widgets are QPushButtons
        var_btn = symbol_table.cellWidget(var_row, 0)
        func_btn = symbol_table.cellWidget(func_row, 0)
        self.assertIsNotNone(var_btn)
        self.assertIsNotNone(func_btn)

        # Click on variable button
        var_btn.click()
        self.assertEqual(interpreter.get_current_line(), "my_var")

        # Clear interpreter line
        interpreter.replace_current_line("")

        # Click on function button
        func_btn.click()
        self.assertEqual(interpreter.get_current_line(), "my_func()")
        expected_pos = interpreter.input_start_pos + len("my_func(")
        self.assertEqual(interpreter.textCursor().position(), expected_pos)

    def test_equals_key_evaluates_expression(self):
        window = MainWindow()
        interpreter = window.interpreter

        # Enter expression
        interpreter.append_text("10")
        interpreter.append_text("+")
        interpreter.append_text("32")

        # Click '=' button
        interpreter.append_text("=")

        output = interpreter.toPlainText()
        self.assertIn("42", output)
        self.assertEqual(interpreter.get_current_line(), "")

    def test_smart_equals_for_assignment_and_comparisons(self):
        window = MainWindow()
        interpreter = window.interpreter

        # 1. Bare identifier 'x' -> clicking '=' inserts ' = '
        interpreter.append_text("x")
        interpreter.append_text("=")
        self.assertEqual(interpreter.get_current_line(), "x = ")

        # Complete assignment 'x = 5' and click '=' -> executes assignment
        interpreter.append_text("5")
        interpreter.append_text("=")
        self.assertEqual(interpreter.get_current_line(), "")
        self.assertEqual(window.session.locals.get("x"), 5)

        # 2. Click '=' twice on 'x' -> 'x = ' then 'x =='
        interpreter.append_text("x")
        interpreter.append_text("=")
        self.assertEqual(interpreter.get_current_line(), "x = ")
        interpreter.append_text("=")
        self.assertEqual(interpreter.get_current_line(), "x ==")

        # Complete comparison 'x == 5' and click '=' -> evaluates comparison
        interpreter.append_text("5")
        interpreter.append_text("=")
        self.assertIn("True", interpreter.toPlainText())
        self.assertEqual(interpreter.get_current_line(), "")

        # 2. Incomplete comparison 'x !' -> clicking '=' inserts '=' (making 'x!=')
        interpreter.append_text("x")
        interpreter.append_text("!")
        interpreter.append_text("=")
        self.assertEqual(interpreter.get_current_line(), "x!=")

        # Complete comparison 'x != 10' -> clicking '=' evaluates comparison
        interpreter.append_text("10")
        interpreter.append_text("=")
        self.assertIn("True", interpreter.toPlainText())
        self.assertEqual(interpreter.get_current_line(), "")

    def test_nested_function_execution_does_not_split_closing_parens(self):
        window = MainWindow()
        interpreter = window.interpreter

        # Define deg function in session first
        window.session.execute("def deg(rad):\n    return rad * pi / 180")

        # Enter sin(deg(90)) via append_text calls
        interpreter.append_text("sin()")
        interpreter.append_text("deg()")
        interpreter.append_text("90")

        self.assertEqual(interpreter.get_current_line(), "sin(deg(90))")

        # Execute current line (e.g. press Enter or '=')
        interpreter.execute_current_line()

        # Check current input line is empty and not containing left-over '))'
        self.assertEqual(interpreter.get_current_line(), "")
        full_text = interpreter.toPlainText()
        self.assertIn("1.0", full_text)
        self.assertNotIn(">>> ))", full_text)

if __name__ == "__main__":
    unittest.main()
