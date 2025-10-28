from tap.database.vault import Vault
from tap.search.match_class import Match, Matches


def fuzzy_search(query: str, limit: int, vault: Vault) -> Matches:
    from rapidfuzz import process, fuzz

    choices = vault.titles
    results = process.extract(query, choices, scorer=fuzz.WRatio, limit=limit)
    matches = [
        Match(title=title, score=score, rank=rank + 1)
        for rank, (title, score, _) in enumerate(results)
    ]
    matches_obj = Matches(query=query, results=matches)
    return matches_obj
