# from context.query.vector import vector_search
from contex.query.fuzzy import fuzzy_search
from contex.database.obsidian.vault import Vault
import argparse
import sys
import json
from rich.console import Console
from pathlib import Path

vault = Vault()
console = Console()
dir_path = Path(__file__).parent.resolve()
matches_file = dir_path / ".matches.json"


def display_titles(titles: list[str]):
    for index, title in enumerate(titles):
        console.print(
            f"[yellow]{index + 1}[/yellow] - [green]{title}[/green][blue].md[/blue]"
        )


def shelve_matches(matches: list[tuple[str, int, int]]):
    with open(matches_files, "w") as f:
        json.dump(matches, f)


def retrieve_matches() -> list[tuple[str, int, int]]:
    if matches_file.exists():
        with open(matches_file, "r") as f:
            matches = json.load(f)
            return matches
    return []


def get_fuzzy_matches(query: str, limit: int = 5):
    titles = vault.titles
    matches: list[tuple[str, int, int]] = fuzzy_search(query, titles, limit)
    titles = [title for title, _, _ in matches]
    display_titles(titles)


# def get_similarity_matches(query, limit=5):
#     titles = get_titles()
#     matches = vector_search(query, titles, limit)
#     print(f"Top {limit} similarity matches for '{query}':")
#     for match, score in matches:
#         print(f"Match: {match}, Similarity Score: {score}")


def main():
    parser = argparse.ArgumentParser(description="Fuzzy search for titles.")
    parser.add_argument("query", type=str, help="The search query.")
    parser.add_argument(
        "-l", "--limit", type=int, default=5, help="Number of top matches to return."
    )
    # Define mutually exclusive group for search type (-f / fuzzy or -s / similarity)
    # group = parser.add_mutually_exclusive_group(required=True)
    # group.add_argument(
    #     "-f", "--fuzzy", action="store_true", help="Use fuzzy search (default)."
    # )
    # group.add_argument(
    #     "-s", "--similarity", action="store_true", help="Use similarity
    args = parser.parse_args()
    query = args.query
    limit = args.limit
    # if args.fuzzy:
    get_fuzzy_matches(query, limit)
    sys.exit(0)
    # elif args.similarity:
    #     get_similarity_matches(args.query, args.limit)
    #     sys.exit(0)


if __name__ == "__main__":
    main()
