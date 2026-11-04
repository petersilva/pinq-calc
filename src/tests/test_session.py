import unittest
from pinq.session import PythonSession

class TestPythonSession(unittest.TestCase):
    def test_multiline_function_execution_with_math_symbols(self):
        session = PythonSession()
        code_str = "def deg(rad):\n    return rad * pi / 180"
        session.execute(code_str)
        
        # Test executing function that uses math symbol 'pi'
        session.execute("deg(180)")
        output = session.get_output().strip()
        self.assertIn("3.141592653589793", output)
        self.assertEqual(session.get_error(), "")

    def test_save_and_load_session_with_functions(self):
        session = PythonSession()
        func_code = "def rad2deg(x):\n    return x * 180 / pi"
        session.execute(func_code)

        user_symbols = session.get_user_symbols()
        self.assertIn('rad2deg', user_symbols)

        # Execute rad2deg(pi)
        session.execute("rad2deg(pi)")
        output = session.get_output().strip()
        self.assertIn("180.0", output)

    def test_underscore_variable(self):
        session = PythonSession()
        session.execute("10 + 20")
        self.assertEqual(session.get_output().strip(), "30")
        self.assertEqual(session.locals.get('_'), 30)

        session.execute("_ * 2")
        self.assertEqual(session.get_output().strip(), "60")
        self.assertEqual(session.locals.get('_'), 60)

        session.execute("_ + 5")
        self.assertEqual(session.get_output().strip(), "65")
        self.assertEqual(session.locals.get('_'), 65)

        # '_' should be excluded from get_user_symbols()
        user_symbols = session.get_user_symbols()
        self.assertNotIn('_', user_symbols)

if __name__ == "__main__":
    unittest.main()
