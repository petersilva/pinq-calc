# Pinq-calc Documentation

Pinq-calc: calculate things obviously, it turns out to be python.

## Introduction

Python is a very natural way for humans to write simple calculations so a computer can compute results.
For those learning Python, or who like Python, or people who want a
calculator that is just a little more powerful than standard calculator apps.
This app acts like calculator, but also like a python interpreter, with 
some small wrinkles to make it more intuitive to use as a calculator.

Can use on-screen keypad & keyboard when touch makes more sense, 
or you can hide those, and use a standard computer keyboard & keypad. 

## Terminal
- Type any Python expression or statement at the **>>>** prompt.
- The **Enter** key acts like an *=* on a traditional calculator, just as in python.
- Mathematical expressions (e.g., `2 + 2`) are evaluated immediately.
- The python **math** library is pre-imported. Use `sin()`, `cos()`, `pi`, `sqrt()`, etc.
- Use **Up/Down** arrows for command history.
- Type `clear()` to reset the session.
- Type 'quit()' to exit.
- If you have a long series of calculations, the old results scroll off the top, and the 
  interpreter window becomes scrollable, so you can still go back and see them.
- To refer to the last calculation result, it's in underscore, just like in the python interpreter.
- To store values, create a python assignment statement:  LengthOfThing=34.5
  You then have a LengthOfThing button you can use for inclusion in later calculations.

## Modules Column (Math, NumPy, Pandas)

- The middle column features tabs for **Math**, **NumPy**, and **Pandas**.
- The **Math** tab provides buttons for functions and constants in Python's standard `math` module.
- The **NumPy** and **Pandas** tabs provide interactive buttons for top-level entry points (`np.array()`, `pd.DataFrame()`, etc.) when those libraries are installed.
- Clicking any button inserts the function or symbol directly into the interpreter.


## User Defined Variables and functions
- type an assignment in python, like *p=3* and in the right side column, a *p* button will be created, with the value 3.
- You can now change the value of p by clicking on the number.
- You can still change the value of p in the interpreter, say *p=25*
- You can also define python functions as you would in a python interpreter:
     ```

      def doublen(n):
          return 2*n

     ```
     now you have a key labelled doublen and it can invoked like any other button
  
## Keypad
- Use the on-screen buttons for digits and operators.
- The **clear** button resets the entire session.
- Click the button (**▼ Keypad** / **▲ Keypad**) at the bottom of the left column (or use **View -> Show Keypad**) to toggle keypad visibility. When hidden, the interpreter expands to fill the left column.

## On-Screen Keyboard
- Click the toggle bar (**▲ Keyboard** / **▼ Keyboard**) at the very bottom of the application (or use **View -> Show On-Screen Keyboard**) to display a full QWERTY keyboard spanning under all three columns.
- Hidden by default. Includes shift, caps lock, backspace, navigation arrows, space, and clear keys.

## Symbol Table
- **Variables**: Double-click to edit values inline.
- **Functions**: Double-click to open the code editor.

## Sessions

- if you make some functions and variable your would like to save for later, you can save it to a session file.
- Using the Menu: File/Save As... or Save
- The file is plain python (with a .py suffix).
- The app will remember the last session and reload it automatically.


## Settings
- Toggle between **Pinq Pink** and **System Colours** in the `File -> Settings` menu.


## Installation


* from PIP:
  * pip install pinq-calc

* from Source:
  * pip install -e . --break-system-packages

## Contributions

This was just something I personally wanted. Suggestions and Contributions welcome.
It was entirely written using Gemini, guided by my taste, such as it is.
The home is: https://github.com/petersilva/pinq-calc
