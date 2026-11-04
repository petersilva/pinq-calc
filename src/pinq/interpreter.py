import code
import re
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QApplication
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QFont, QTextCursor

class InterpreterWidget(QTextEdit):
    command_executed = Signal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.history = []
        self.history_index = -1
        self.current_multiline = []
        
        self.setFont(QFont("Courier New", 10))
        # Stylesheet removed to respect global application theme
        
        self.prompt = ">>> "
        self.multiline_prompt = "... "
        self.insertPlainText("Pinq-calc\n" + self.prompt)
        self.set_input_start()

    def set_input_start(self):
        """Mark the start of the current input line."""
        self.moveCursor(QTextCursor.End)
        self.input_start_pos = self.textCursor().position()

    def get_current_line(self):
        cursor = self.textCursor()
        cursor.setPosition(self.input_start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        return cursor.selectedText()

    def execute_current_line(self):
        self.moveCursor(QTextCursor.End)
        command = self.get_current_line()
        self.insertPlainText("\n")
        self.process_command(command)

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        
        # Prevent editing outside the input area
        if cursor.position() < self.input_start_pos:
            self.moveCursor(QTextCursor.End)
            cursor = self.textCursor()

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.execute_current_line()
            return

        if event.key() == Qt.Key_Backspace:
            if cursor.position() <= self.input_start_pos:
                return # Don't delete the prompt
        
        if event.key() == Qt.Key_Up:
            self.navigate_history(-1)
            return
        
        if event.key() == Qt.Key_Down:
            self.navigate_history(1)
            return

        if event.key() == Qt.Key_Home:
            cursor.setPosition(self.input_start_pos)
            self.setTextCursor(cursor)
            return

        if event.text() == '(':
            cursor.insertText("()")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cursor)
            return

        super().keyPressEvent(event)

    def process_command(self, text):
        if not text and not self.current_multiline:
            self.insertPlainText(self.prompt)
            self.set_input_start()
            return

        # Check if clear was called
        if text.strip() == "clear()":
            self.session.execute("clear()") # Reset the session
            self.clear()
            self.current_multiline = []
            self.insertPlainText("Python Interactive Interpreter (with math pre-imported)\n" + self.prompt)
            self.set_input_start()
            self.command_executed.emit()
            return

        if not self.current_multiline and text:
            self.history.append(text)
            self.history_index = len(self.history)

        self.current_multiline.append(text)
        full_command = "\n".join(self.current_multiline)

        # Execute
        more = self.session.execute(full_command)
        
        if not more:
            # Finished command
            output = self.session.get_output()
            error = self.session.get_error()
            
            if output:
                self.insertPlainText(output)
                if not output.endswith("\n"):
                    self.insertPlainText("\n")
            
            if error:
                self.insertPlainText(error)
                if not error.endswith("\n"):
                    self.insertPlainText("\n")
            
            self.current_multiline = []
            self.insertPlainText(self.prompt)
            self.command_executed.emit()
        else:
            # Multi-line
            self.insertPlainText(self.multiline_prompt)
        
        self.set_input_start()

    def navigate_history(self, delta):
        if not self.history:
            return
            
        if delta == -1: # Up
            if self.history_index > 0:
                self.history_index -= 1
        else: # Down
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
            else:
                self.history_index = len(self.history)
                self.replace_current_line("")
                return

        self.replace_current_line(self.history[self.history_index])

    def replace_current_line(self, new_text):
        cursor = self.textCursor()
        cursor.setPosition(self.input_start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(new_text)
        self.setTextCursor(cursor)

    def should_evaluate_on_equals(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False

        # If line ends with an incomplete operator / symbol, do not evaluate (insert '=' instead)
        if stripped[-1] in ('!', '=', '<', '>', '+', '-', '*', '/', '%', '^', '&', '|', '~', '(', ','):
            return False

        # If line is a single bare identifier (like 'x' or 'my_var'), treat keypad '=' as starting assignment 'x = '
        if re.match(r'^[a-zA-Z_]\w*$', stripped):
            return False

        # Check Python syntax completeness
        try:
            compiled = code.compile_command(stripped)
            return compiled is not None
        except Exception:
            return False
    def append_text(self, text):
        """For keypad input."""
        if text == '=':
            current_line = self.get_current_line()
            if self.should_evaluate_on_equals(current_line):
                self.execute_current_line()
                return
            else:
                stripped = current_line.strip()
                match = re.search(r'([!=<>])\s*$', current_line)
                if match:
                    op_pos = match.start(1)
                    op_char = match.group(1)
                    self.replace_current_line(current_line[:op_pos] + op_char + "=")
                    self.setFocus()
                    return
                elif re.match(r'^[a-zA-Z_]\w*$', stripped):
                    text = " = "
                elif not stripped:
                    text = "="
                else:
                    text = "="
        cursor = self.textCursor()
        if cursor.position() < self.input_start_pos:
            self.moveCursor(QTextCursor.End)
            cursor = self.textCursor()

        cursor.insertText(text)
        if text.endswith("()") and text != "clear()":
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
        self.setTextCursor(cursor)
        self.setFocus()
