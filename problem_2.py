"""
Exam #2 (practice) / Problem set #2.
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
    Ask the user to enter an integer between 1 and 20, inclusive.

    Behavior:
    - If the user enters an invalid response (not an integer, or an integer
      outside the range 1 to 20 inclusive), print "Invalid number!" and do
      nothing further.
    - Otherwise, if the user's response is valid, print "Hello world!" the number
      of times indicated by the user's response.
    - If the user's response was a number greater than 5, print "Phew!" at the end.
    - The program must not crash under any circumstances.

    Example runs:

        Please enter an integer between 1 and 20, inclusive:  foobar
        Invalid number!

        Please enter an integer between 1 and 20, inclusive:  2
        Hello world!
        Hello world!

        Please enter an integer between 1 and 20, inclusive:  6
        Hello world!
        Hello world!
        Hello world!
        Hello world!
        Hello world!
        Hello world!
        Phew!
    """
    # write your code below this line


# -------------------------------------- #
# Do not modify the code below this line #
if __name__ == "__main__":
    # call the function if this file is being run directly
    main()
