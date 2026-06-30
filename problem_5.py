"""
Exam #2 (practice) / Problem set #5.
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
    Look up a person by name in the data and report their details.

    The file `people.csv` in the `data` subdirectory contains data about people.
    Read that data into a list of dictionaries, where each dictionary represents
    one person, then ask the user to enter a name.

    Behavior:
    - If the name entered by the user is not found in the data, print "Name not
      found!" and do nothing further.
    - If the name is found, print the person's name, country, and email address,
      one per line, in this format:

        Name: <name>
        Country: <country>
        Email: <email>

    - The capitalization of the name should not matter when matching.
    - The name and country should be properly capitalized in the output.
    - The email address should be printed in all lowercase letters.
    - The program must not crash under any circumstances.

    Example runs:

        Enter a name:  Foo Bar
        Name not found!

        Enter a name:  nevins bussel
        Name: Nevins Bussel
        Country: Indonesia
        Email: nbussel1@1688.com
    """
    # write your code below this line


# -------------------------------------- #
# Do not modify the code below this line #
if __name__ == "__main__":
    # call the function if this file is being run directly
    main()
