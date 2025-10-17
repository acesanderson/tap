import argparse
import json
import re
import sys
from rich.console import Console
from rich.markdown import Markdown

console = Console()


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


def validate_date_range(date_range: str) -> bool:
    pattern = r"^\d{4}-\d{2}-\d{2}:\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, date_range))


def get_date_range(date_range: str) -> str:
    date_one = date_range.split(":")[0]
    date_two = date_range.split(":")[1]
    notes = vault.get_daily_notes_in_date_range(date_one, date_two)
    # Combine notes into one markdown string with horizontal rules and # date headers
    combined_notes = ""
    for note in notes:
        # Extract date from the first line of the note if it starts with a date
        first_line = note.split("\n")[0]
        if re.match(r"^\d{4}-\d{2}-\d{2}", first_line):
            date_header = first_line
        else:
            date_header = "Note"
        combined_notes += f"\n\n---\n\n# {date_header}\n\n{note}"
    return combined_notes


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
    parser.add_argument(
        "-d",
        "--date_range",
        type=str,
        help="Retrieve daily notes for the specified date range (YYYY-MM-DD:YYYY-MM-DD).",
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
    date_range: str = args.date_range
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
    elif date_range:
        if not validate_date_range(date_range):
            console.print(
                f"[red]Error:[/red] Invalid date range format. Use YYYY-MM-DD:YYYY-MM-DD"
            )
            sys.exit(1)
        else:
            combined_notes = get_date_range(date_range)
            print_markdown(combined_notes)
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


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace


def route_command(args: Namespace):
    """
    Route to appropriate handler based on parsed args.
    This function shows the routing logic.
    """

    # SUBCOMMANDS
    if args.command == "stow":
        return handle_stow(args.index)

    elif args.command == "pool":
        if args.pool_action is None:
            # tap pool (no action)
            return handle_pool_show()
        elif args.pool_action == "pour":
            return handle_pool_pour()
        elif args.pool_action == "drain":
            return handle_pool_drain()
        elif args.pool_action == "remove":
            return handle_pool_remove(args.index)
        elif args.pool_action == "clear":
            return handle_pool_clear()

    elif args.command == "alias":
        if args.alias_action == "rm":
            # tap alias rm <name>
            return handle_alias_remove(args.name)
        elif args.alias_action is None:
            # Could be: tap alias, tap alias <name> <target>, or tap alias <name> -g <index>
            if args.name is None:
                # tap alias (list all)
                return handle_alias_list()
            elif args.get is not None:
                # tap alias <name> -g <index>
                return handle_alias_create(args.name, index=args.get)
            elif args.target is not None:
                # tap alias <name> <target>
                return handle_alias_create(args.name, title=args.target)
            else:
                # Just name provided, ambiguous
                print("Error: Provide either a target title or use -g flag with index")
                sys.exit(1)

    # DEFAULT COMMAND (search/retrieval)
    elif args.command is None:
        # Flags take precedence
        if args.last:
            return handle_show_last()
        elif args.get is not None:
            return handle_get(args.get)
        elif args.date_range:
            return handle_date_range(args.date_range)
        elif args.query:
            # Main search with resolution
            return handle_search(
                args.query,
                limit=args.limit,
                force_fuzzy=args.fuzzy,
                force_exact=args.exact,
            )
        else:
            # No query, no flags
            print("Error: Provide a query or use a flag")
            parser.print_help()
            sys.exit(1)

    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


# Placeholder handler functions (to be implemented)
def handle_stow(index):
    pass


def handle_pool_show():
    pass


def handle_pool_pour():
    pass


def handle_pool_drain():
    pass


def handle_pool_remove(index):
    pass


def handle_pool_clear():
    pass


def handle_alias_remove(name):
    pass


def handle_alias_list():
    pass


def handle_alias_create(name, index=None, title=None):
    pass


def handle_show_last():
    pass


def handle_get(index):
    pass


def handle_date_range(date_range):
    pass


def handle_search(query, limit, force_fuzzy, force_exact):
    pass
