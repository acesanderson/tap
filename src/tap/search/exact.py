from tap.database.vault import Vault
from tap.search.match_class import Match, Matches


def exact_search(query: str, limit: int, vault: Vault) -> Matches:
    """Perform an exact search for the target in the data."""
    titles = vault.titles
    matching_titles = [title for title in titles if title.startswith(query)]
    matching_titles = sorted(matching_titles)
    matches = [
        Match(title=title, score=1.0, rank=i + 1)
        for i, title in enumerate(matching_titles)
    ]
    if len(matches) > limit:
        matches = matches[:limit]
    matches_obj = Matches(query=query, results=matches)
    return matches_obj
