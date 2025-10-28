from __future__ import annotations

from tap.search.match_class import Match, Matches
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tap.database.vault import Vault


def semantic_search(query: str, limit: int, vault: Vault) -> Matches:
    import asyncio

    async def _vector_search():
        collection = await vault.get_chroma_collection()
        results = await collection.query(
            query_texts=[query],
            n_results=limit,
        )
        return results

    results = asyncio.run(_vector_search())
    matches = []
    for doc, score in zip(results["ids"][0], results["distances"][0]):
        matches.append(Match(title=doc, score=score, rank=len(matches) + 1))
    matches_obj = Matches(query=query, results=matches)
    return matches_obj


if __name__ == "__main__":
    from tap.database.vault import Vault

    vault = Vault()
    query = "getting laid"
    limit = 5
    matches = semantic_search(query, limit, vault)
    print(matches)
