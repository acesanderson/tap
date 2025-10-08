from rapidfuzz import process, fuzz


def fuzzy_search(
    query: str, choices: list[str], limit: int = 5
) -> list[tuple[str, int, int]]:
    """
    Perform a fuzzy search to find the best matches for a given query from a list of choices.

    Parameters:
    query (str): The search query.
    choices (list): A list of strings to search within.
    limit (int): The maximum number of matches to return.

    Returns:
    list: A list of tuples containing the best matches and their scores.
    """
    results = process.extract(query, choices, scorer=fuzz.WRatio, limit=limit)
    return results
