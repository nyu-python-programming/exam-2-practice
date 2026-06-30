"""
Exam #2 (practice) / Problem set #3.
- Your job is to complete the program in this file so that it achieves the behavior described below.
- You are welcome to create any additional functions you desire.
- Do not write any code in the global scope, i.e. do not write code that is not within a function definition.
- Grading uses more tests than those in `tests` (including a hidden test suite not shipped with your copy); passing the provided tests does not guarantee full credit, so write a correct, general solution, following the patterns and best practices we have covered in class.

Run this file directly to try it out.

▶ BEFORE YOU START: the exam autosave program must be running. It usually starts
  automatically when you open this project in VS Code. If you do NOT see a green
  "EXAM AUTOSAVE IS RUNNING" terminal, start it from the VS Code menu bar:
  Terminal -> Run Task... -> "Exam Autosave". (Double-clicking a file in the VS
  Code Explorer only OPENS it -- it does not run it.) Running it is REQUIRED --
  see the "Exam monitoring" section of the README.
"""


def main():
    """
    Ask the user to enter their birthdate in yyyy/mm/dd format and report their age.

    Behavior:
    - If the user enters a response that is not in the correct yyyy/mm/dd format
      (a 4-digit year, 2-digit month, and 2-digit day), or a birthdate that would
      make the user less than 0 or greater than 122 years old, print "Invalid date!"
      and repeat the process of asking for and validating the birthdate until a
      correctly-formatted, valid date is entered.
    - Once a valid response has been entered, print "You are X years old!", where X
      is the user's current age in years (taking the current month and day into
      account, not just the year).
    - The program must not crash under any circumstances.

    Example runs:

        Enter your birthdate (yyyy/mm/dd):  foobar
        Invalid date!
        Enter your birthdate (yyyy/mm/dd):  13/6/1
        Invalid date!
        Enter your birthdate (yyyy/mm/dd):  2013/6/1
        Invalid date!
        Enter your birthdate (yyyy/mm/dd):  2013/06/01
        You are 10 years old!

        Enter your birthdate (yyyy/mm/dd): 2003/11/01
        You are 19 years old!
    """
    # write your code below this line


# -------------------------------------- #
# Do not modify the code below this line #
if __name__ == "__main__":
    # call the function if this file is being run directly
    main()
