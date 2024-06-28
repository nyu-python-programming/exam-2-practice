"""
Exam #1 / Problem set #3.
- Your job is to complete the definitions of each function so that it achieves its indicated behavior.
- You are welcome to create any additional functions you desire.
- Do not write any code in the global scope, i.e. do not write code that is not within a function definition.

Run this file directly to try it out.
"""


def qualify():
    """
    Write a program that qualifies the user for a particular credit card.

    Qualification criteria:
    - Make at least $30,000 per year.
    - If the user rents a home, their rent payment must not be more than 5% of their yearly income (i.e. $1,500 is the max rent that they can pay while making $30,000 per year).
    - However, if they own their home, you do not need to take their monthly house payment into account.

    Technical requirements:
    - You can assume the user will enter valid responses to each question.
    - You can assume the user will enter dollar amounts in the format indicated in the examples below.
    - Your program must not crash under any circumstances

    Example sessions - your output should match these, given the same user responses:
    - Session with a homeowner who qualifies:

        Welcome to the credit card qualifier!
        How much do you make per year? $30,000
        Do you own your home? (y/n) y
        You qualify!

    - Session with a homeowner who does not qualify:

        Welcome to the credit card qualifier!
        How much do you make per year? $16,000
        Do you own your home? (y/n) y
        Sorry, you don't qualify. Your income is too low.

    - Session with a renter who qualifies:

        Welcome to the credit card qualifier!
        How much do you make per year? $110,000
        Do you own your home? (y/n) n
        How much do you pay in rent per month? $5,000
        You qualify!

    - Session with a renter who does not qualify:

        Welcome to the credit card qualifier!
        How much do you make per year? $50,000
        Do you own your home? (y/n) n
        How much do you pay in rent per month? $5,000
        Sorry, you don't qualify. Your rent is too high.

    """
    # write your code below this line


# -------------------------------------- #
# Do not modify the code below this line #
if __name__ == "__main__":
    # call the function if this file is being run directly
    qualify()
