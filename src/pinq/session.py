import sys
import io
import code
import math
import contextlib
from typing import Dict, Any, List

class PythonSession:
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Resets the session to its initial state."""
        self.locals = {'__builtins__': __builtins__}
        self.source_cache = {}
        # Pre-import math symbols
        self.locals.update({k: v for k, v in vars(math).items() if not k.startswith('_')})
        
        # Add a clear function to the namespace
        self.locals['clear'] = self.reset
        
        self.interpreter = code.InteractiveInterpreter(locals=self.locals)
        self.stdout_buffer = io.StringIO()
        self.stderr_buffer = io.StringIO()

    def execute(self, command: str) -> bool:
        """
        Executes a command. Returns True if more input is required (multi-line).
        """
        self.stdout_buffer = io.StringIO()
        self.stderr_buffer = io.StringIO()

        def custom_displayhook(value):
            if value is not None:
                self.locals['_'] = value
                print(repr(value))

        old_displayhook = sys.displayhook
        sys.displayhook = custom_displayhook

        with contextlib.redirect_stdout(self.stdout_buffer), contextlib.redirect_stderr(self.stderr_buffer):
            try:
                # 1. Try to evaluate as a single expression first to get the result
                # This handles inputs like "p*q" or "5+5"
                try:
                    # We check if it's a single line and looks like an expression
                    if "\n" not in command.strip():
                        result = eval(command.strip(), self.locals)
                        if result is not None:
                            self.locals['_'] = result
                            print(repr(result))
                        return False
                except Exception:
                    # Not a simple expression (could be assignment, def, etc.)
                    pass

                # 2. Check if it's a multi-line block (like a loaded file)
                # or a statement that can be exec'd
                stripped = command.strip()
                
                # Extract function definitions for the source cache before execution
                import re
                # Find all top-level 'def' blocks
                # This is a simplified regex; for complex files we might need a proper parser
                # but it works for our "Save" format.
                def_matches = re.finditer(r"^def\s+(\w+)\(.*?:\s*$.*?(?=^def|\Z)", command, re.MULTILINE | re.DOTALL)
                for match in def_matches:
                    func_name = match.group(1)
                    self.source_cache[func_name] = match.group(0).strip()

                # If it contains multiple lines, use exec instead of runsource
                if "\n" in stripped:
                    exec(command, self.locals)
                    return False

                # 3. Fallback to standard runsource for single-line interactive statements
                # This handles interactive "p=4", "def func():", etc.
                if stripped.startswith("def "):
                    match = re.match(r"def\s+(\w+)", stripped)
                    if match:
                        func_name = match.group(1)
                        self.source_cache[func_name] = command

                more = self.interpreter.runsource(command)
                return more

            except Exception as e:
                # print(f"Error: {e}", file=sys.stderr) # Original error handling
                # Re-raise to let the caller handle it or print it to stderr_buffer
                import traceback
                traceback.print_exc()
                return False
            finally:
                sys.displayhook = old_displayhook

    def get_output(self) -> str:
        return self.stdout_buffer.getvalue()

    def get_error(self) -> str:
        return self.stderr_buffer.getvalue()

    def get_user_symbols(self) -> Dict[str, Any]:
        """
        Returns variables and functions defined by the user, 
        filtering out math functions and internal python stuff.
        """
        ignored = set(vars(math).keys())
        ignored.add('__builtins__')
        ignored.add('clear')
        
        return {k: v for k, v in self.locals.items() if k not in ignored and not k.startswith('_')}

    def update_variable(self, name: str, value_expr: str):
        """Used to update a variable from the symbol table."""
        try:
            # Evaluate the expression in the current context
            value = eval(value_expr, self.locals)
            self.locals[name] = value
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")

    def update_function(self, name: str, code_str: str):
        """Used to update/redefine a function from the editor."""
        # This is a bit trickier; we execute the code string which should contain 'def name(...): ...'
        self.source_cache[name] = code_str
        self.execute(code_str)
