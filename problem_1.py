"""
Exam #2 (practice) / Problem set #1.
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
    Ask the user to enter two integers that are each greater than or equal to 10.

    Behavior:
    - Prompt the user (twice) to enter an integer >= 10.
    - If, for either number, the user enters a response that is not an integer
      or is a negative number, print "Invalid number!" and do nothing further.
    - Otherwise, if either number is a valid integer that is less than 10, print
      "Too small!" and do nothing further.
    - Otherwise, if both numbers are valid, print "X + Y = Z", where X is the
      first number entered, Y is the second number entered, and Z is their sum.
    - The program must not crash under any circumstances.

    Example runs:

        Please enter an integer >= 10:  blah
        Invalid number!

        Please enter an integer >= 10:  5
        Too small!

        Please enter an integer >= 10: 10
        Please enter an integer >= 10: 5
        Too small!

        Please enter an integer >= 10: 15
        Please enter an integer >= 10: 20
        15 + 20 = 35
    """
    # write your code below this line


# -------------------------------------- #
# Do not modify the code below this line #
if __name__ == "__main__":
    # call the function if this file is being run directly
    main()
