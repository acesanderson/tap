# from context.query.vector import vector_search
from contex.query.fuzzy import fuzzy_search
from contex.database.obsidian.vault import Vault
import argparse
import sys
import json
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path

vault = Vault()
console = Console()
dir_path = Path(__file__).parent.resolve()
matches_file = dir_path / ".matches.json"


def print_markdown(text: str):
    """
    Pretty print markdown text to the console.
    """
    md = Markdown(text)
    console.print(md)


def display_titles(titles: list[str]):
    """
    Pretty print titles with index numbers.
    """
    for index, title in enumerate(titles):
        console.print(
            f"[yellow]{index + 1}[/yellow] - [green]{title}[/green][blue].md[/blue]"
        )


def shelve_matches(matches: list[tuple[str, int, int]]):
    """
    Store full matches in a .matches.json file.
    """
    with open(matches_file, "w") as f:
        json.dump(matches, f)


def retrieve_matches() -> list[tuple[str, int, int]]:
    """
    Retrieve full matches from the .matches.json file.
    """
    if matches_file.exists():
        with open(matches_file, "r") as f:
            matches = json.load(f)
            return matches
    return []


def retrieve_titles() -> list[str]:
    """
    Retrieve only titles from the .matches.json file.
    """
    matches = retrieve_matches()
    return [title for title, _, _ in matches]


def get_fuzzy_matches(query: str, limit: int = 5) -> list[str]:
    titles = vault.titles
    matches: list[tuple[str, int, int]] = fuzzy_search(query, titles, limit)
    shelve_matches(matches)
    titles = [title for title, _, _ in matches]
    return titles


def get_document(index: int) -> str | None:
    title = retrieve_titles()[index]
    text = vault.get_document_by_title(title)
    return text


# def get_similarity_matches(query, limit=5):
#     titles = get_titles()
#     matches = vector_search(query, titles, limit)
#     print(f"Top {limit} similarity matches for '{query}':")
#     for match, score in matches:
#         print(f"Match: {match}, Similarity Score: {score}")


def main():
    parser = argparse.ArgumentParser(description="Fuzzy search for titles.")
    parser.add_argument("query", type=str, nargs="?", help="The search query.")
    parser.add_argument(
        "-L", "--limit", type=int, default=5, help="Number of top matches to return."
    )
    parser.add_argument(
        "-l",
        "--last",
        action="store_true",
        help="Display last search results from .matches.json.",
    )
    # Next argument, a str, called "get", takes an integer index
    parser.add_argument(
        "-g",
        "--get",
        type=int,
        help="Get the title at the specified index from the last search results.",
    )
    # Define mutually exclusive group for search type (-f / fuzzy or -s / similarity)
    # group = parser.add_mutually_exclusive_group(required=True)
    # group.add_argument(
    #     "-f", "--fuzzy", action="store_true", help="Use fuzzy search (default)."
    # )
    # group.add_argument(
    #     "-s", "--similarity", action="store_true", help="Use similarity
    args = parser.parse_args()
    query: str = args.query
    limit: int = args.limit
    last: bool = args.last
    get: int = args.get
    # Archival functions
    if last:
        titles = [title for title, _, _ in retrieve_matches()]
        display_titles(titles)
        sys.exit(0)
    elif get:
        text = get_document(get - 1)
        if text:
            print_markdown(text)
        else:
            console.print(f"[red]Error:[/red] No document found at index {get}")
        sys.exit(0)
    # Query
    # if args.fuzzy:
    titles = get_fuzzy_matches(query, limit)
    display_titles(titles)

    sys.exit(0)
    # elif args.similarity:
    #     get_similarity_matches(args.query, args.limit)
    #     sys.exit(0)


if __name__ == "__main__":
    main()
