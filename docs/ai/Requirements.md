


1. make a GUI app in Python. portable, using PySide6


1. UI:
  * have a python interpreter window prompt (with the >>>, just as it would appear in a terminal emulator)
    past commands scroll up just as in a terminal.  commands are interpreted as standard python. It is just
    a python interpreter in a window with two addenda.

    * the interpreter should have "import * from math" so that items like sin, cos, and pi are available
      in the interpreter.

    * when assigning values, e.g. p=4, the variable and value should be displayed in a table to the right.
      (described below.)

    * when the "def" keyword is used to define a function, say def timestwo(n) return 2*n  ... then an
      entry will be created in the table at right for that as well.

  * To the right, have a table of variables/entities defined in the session key:value.  If there are too many
    defined, then make the table scrollable.

    * if you click on a line in the table, it makes the value on that line editable.

    * if the item corresponds to a function, then pop up an editor window with the code in the function. 

  * below the interpreter line, have a screen keypad with digits and operations, as is traditional for caluclators.


but with a calculator keypad below it, that can be  
used to enter numbers and operators like a calculator. It should interpret python source commands and mathematice in the normal way, and act as if "import * from math" had been run, so items like pi, sin, and cos from that module are available without a prefix. when I set a variable in python, I'd like it added to a scrollable list of variables+values shown to the right. If I use the *def* keyword interactively to define a python function, it should go in the list to the right also. If I select a value in the scrollable table on the right, I should be able to change the value.  if the item is a function, then it should bring up a simple text editor with the function body in it.                                      
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
