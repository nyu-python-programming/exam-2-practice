"""
Exam #2 (practice) / Problem set #4.
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
    Report the number of entry-level jobs listed for each unique NYC government agency.

    The file `nyc_jobs.csv` in the `data` subdirectory contains data about open
    jobs in NYC government (from NYC's open data portal). Each line describes one
    job; the agency name is in the second field (e.g. "DEPT OF HEALTH/MENTAL
    HYGIENE") and the career level is in the third field (e.g. "Entry-Level",
    "Experienced (non-manager)", "Manager", etc.).

    Behavior:
    - Output the name of each unique agency and how many "Entry-Level" jobs are
      listed for that agency.
    - Ignore the header line of the file.
    - Ignore the capitalization of the agency names when determining uniqueness,
      but print all agency names in uppercase in the final output.
    - Neatly align the output into two columns: agency names left-aligned and the
      numbers right-aligned. The amount of space between the two columns is up to you.
    - The program must not crash under any circumstances.

    Example output (the numbers below are not correct and the order is not important):

        DEPT OF HEALTH/MENTAL HYGIENE     121
        DEPT OF ENVIRONMENT PROTECTION     62
        DEPT OF PARKS & RECREATION         55
        POLICE DEPARTMENT                 401

    ... and so on for all agencies that have at least one entry-level job.
    """
    # write your code below this line


# -------------------------------------- #
# Do not modify the code below this line #
if __name__ == "__main__":
    # call the function if this file is being run directly
    main()
