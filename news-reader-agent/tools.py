from crewai.tools import tool


@tool
def count_letters(sentence: str):
    """
    This function is to count the amount of letters in a sentence.
    The input is a `sentence` string.
    The output is a number.
    """
    print("tool called with input:", sentence)
    return len(sentence)
