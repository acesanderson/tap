import argparse


def create_parser():
    parser = argparse.ArgumentParser(
        prog="tap", description="Search and compose context from your Obsidian vault"
    )

    # Create subparsers for main commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ============================================================================
    # STOW command
    # ============================================================================
    stow_parser = subparsers.add_parser(
        "stow", help="Add an item from last search to the pool"
    )
    stow_parser.add_argument(
        "index", type=int, help="Index of item from last search to stow"
    )

    # ============================================================================
    # POOL command
    # ============================================================================
    pool_parser = subparsers.add_parser("pool", help="Manage workspace pool")
    pool_subparsers = pool_parser.add_subparsers(
        dest="pool_action", help="Pool actions"
    )

    # tap pool (no action = show)
    # This is handled by checking if pool_action is None

    # tap pool pour
    pool_subparsers.add_parser(
        "pour", help="Output pool as XML context, keep pool intact"
    )

    # tap pool drain
    pool_subparsers.add_parser(
        "drain", help="Output pool as XML context, then clear pool"
    )

    # tap pool remove
    remove_parser = pool_subparsers.add_parser(
        "remove", help="Remove item from pool by index"
    )
    remove_parser.add_argument(
        "index", type=int, help="Index of item in pool to remove"
    )

    # tap pool clear
    pool_subparsers.add_parser("clear", help="Clear pool without output")

    # ============================================================================
    # ALIAS command
    # ============================================================================
    alias_parser = subparsers.add_parser("alias", help="Manage note aliases")
    alias_subparsers = alias_parser.add_subparsers(
        dest="alias_action", help="Alias actions"
    )

    # tap alias (no action = list)
    # This is handled by checking if alias_action is None

    # tap alias <name> <target>
    # We need to handle this specially since it's not a subcommand
    # Add positional args to the main alias parser
    alias_parser.add_argument("name", nargs="?", help="Alias name")
    alias_parser.add_argument(
        "target", nargs="?", help="Target note title or use -g flag for index"
    )
    alias_parser.add_argument(
        "-g",
        "--get",
        type=int,
        metavar="INDEX",
        help="Use item at index from last search as target",
    )

    # tap alias rm <name>
    rm_parser = alias_subparsers.add_parser("rm", help="Remove an alias")
    rm_parser.add_argument("name", help="Alias name to remove")

    # ============================================================================
    # DEFAULT (search) command - when no subcommand is provided
    # ============================================================================
    # These are added to the main parser for when command is None
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query (alias name, note title, or fuzzy search)",
    )
    parser.add_argument(
        "-L",
        "--limit",
        type=int,
        default=5,
        help="Number of search results to return (default: 5)",
    )
    parser.add_argument(
        "-l", "--last", action="store_true", help="Show last search results"
    )
    parser.add_argument(
        "-g",
        "--get",
        type=int,
        metavar="INDEX",
        help="Get item at index from last search",
    )
    parser.add_argument(
        "-d",
        "--date-range",
        type=str,
        metavar="YYYY-MM-DD:YYYY-MM-DD",
        help="Get daily notes in date range",
    )
    parser.add_argument(
        "--fuzzy", action="store_true", help="Force fuzzy search (ignore aliases)"
    )
    parser.add_argument(
        "--exact", action="store_true", help="Force exact title match only"
    )

    return parser
