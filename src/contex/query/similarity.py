"""
end user example:

def get_similarity_matches(query, limit=5):
    titles = get_titles()
    matches = vector_search(query, titles, limit)
    print(f"Top {limit} similarity matches for '{query}':")
    for match, score in matches:
        print(f"Match: {match}, Similarity Score: {score}")
"""

from contex.database.chroma.load_vault import get_vault_collection


def vector_search(query: str, limit: int = 5) -> list[tuple[str, float]]:
    import asyncio

    async def _vector_search():
        collection = await get_vault_collection()
        results = await collection.query(
            query_texts=[query],
            n_results=limit,
        )
        return results

    results = asyncio.run(_vector_search())
    matches = []
    for doc, score in zip(results["documents"][0], results["distances"][0]):
        matches.append((doc, score))
    return matches


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Similarity search for titles.")
    parser.add_argument("query", type=str, help="The search query.")
    parser.add_argument(
        "--limit", type=int, default=5, help="Number of top matches to return."
    )
    args = parser.parse_args()
    query = args.query
    matches = vector_search(query, args.limit)
    print(f"Top {args.limit} similarity matches for '{query}':")
    for match, score in matches:
        print(f"Match: {match}, Similarity Score: {score}")
    sys.exit(0)


if __name__ == "__main__":
    main()
