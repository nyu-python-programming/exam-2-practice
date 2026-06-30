"""
Exam #1 / Problem set #1.
- Your job is to complete the definitions of each function so that it achieves its indicated behavior.
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


def generate_shopping_list():
    """
    Complete this function so that each time it is run, it generates a shopping list for the user.
    - 1. The program asks the user to enter an item to add to their shopping list.
    - 2. The program then asks the user how many of that item they need.
    - The program repeats steps 1 and 2 until the user enters 'finished' or 'done' instead of an item.
    - When the user is finished, the program outputs the entire shopping list.

    Technical requirements:
    - Convert all user input to lowercase.
    - Assume the user enters valid responses to all questions.
    - You are free to solve this problem any way you wish.
    - There is no need to save the shopping list data to a file.

    Example session:
    The following example session illustrates the desired behavior and text output format of the program:

        Welcome to the shopping list generator!

        Enter an item to your shopping list: arugula
        How many arugula would you like? 2

        Enter an item to your shopping list: TOMATOES
        How many tomatoes would you like? 2LB

        Enter an item to your shopping list: Cheddar
        How many cheddar would you like? 4

        Enter an item to your shopping list: finished

        Here is your complete shopping list:
        - arugula (2)
        - tomatoes (2lb)
        - cheddar (4)

        Thank you!

    """
    # write your answer below this line


# -------------------------------------- #
# Do not modify the code below this line #
if __name__ == "__main__":
    # call the function if this file is being run directly
    generate_shopping_list()
