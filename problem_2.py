"""
Exam #1 / Problem set #2.
- Your job is to complete the definitions of each function so that it achieves its indicated behavior.
- You are welcome to create any additional functions you desire.
- Do not write any code in the global scope, i.e. do not write code that is not within a function definition.

Run this file directly to try it out.
"""


def encode(filepath):
    """
    Write code that opens up the text file specified in the argument,
    swaps out certain words in the text with replacement phrases (i.e. encodes it),
    and overwrites the original file text with the new modified text.

    Requirements:
    - The words to find and replace are given in a dictionary below, which must be used.
    - You are forbidden from hard-coding any of the string literals you see in this dictionary anywhere else in your program.
    - The program must not crash under any circumstances.

    Example:
    - An example file is given in data/secret_message.txt.  The original text is as follows:

        The professor was dull, and I was failing.
        But with a bit of effort, I was finally able to get an excellent score on the final exam.
        Thankfully, despite being strict, the professor was fair.

    - If implemented correctly, the text in this file would be encoded into the following:

        The professor was a few sandwiches short of a picnic, and I was a temporarily-embarrassed honors student.
        But with a bit of elbow grease, I was finally able to get an better-than-anticipated score on the final exam.
        Thankfully, despite being a bit more demanding than one might otherwise have anticipated, the professor was exceedingly generous.

    :params filepath: The path of the text file to encode.
    :returns: True if one or more words in the original text were swapped for their replacements.  False otherwise.
    """

    # the keys in the given dictionary are words you must to replace with their corresponding values in the text file
    swaps = {
        "dull": "a few sandwiches short of a picnic",
        "failing": "a temporarily-embarrassed honors student",
        "effort": "elbow grease",
        "excellent": "better-than-anticipated",
        "strict": "a bit more demanding than one might otherwise have anticipated",
        "fair": "exceedingly generous",
    }
    # write your code below this line


# -------------------------------------- #
# Do not modify the code below this line #
# running this file tries out the encoding on the file at: data/secret_message.txt
if __name__ == "__main__":
    # call the function if this file is being run directly
    import os

    filepath = os.path.join(os.path.curdir, "data", "secret_message.txt")
    result = encode(filepath)
    if result:
        print("Swapped at least one word!")
    else:
        print("No words swapped!")
