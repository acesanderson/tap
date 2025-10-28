import click
import json
from xdg_base_dirs import xdg_data_home
from tap.search.match_class import Matches
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tap.database.obsidian.vault import Vault

LATEST_MATCHES_FILE = xdg_data_home() / "tap" / "latest_matches.json"


@click.command()
@click.argument("query", required=False)
@click.option("--limit", "-L", default=5, help="Number of results")
@click.option("--last", "-l", is_flag=True, help="Show last search results")
@click.option("--get", "-g", type=int, help="Get item at index")
@click.option("--date-range", "-d", help="Date range YYYY-MM-DD:YYYY-MM-DD")
@click.option("--fuzzy", "-f", is_flag=True, help="Use fuzzy search")
@click.option("--exact", "-e", is_flag=True, help="Use exact match search")
@click.option(
    "--semantic", "-s", is_flag=True, help="Use semantic search")
)
@click.pass_context
def search(
    ctx,
    query,
    limit,
    last,
    get,
    date_range: str,
    fuzzy: bool = True,
    exact: bool = False,
):
    """
    Search vault notes
    """
    # Unpack context
    implicit_input = ctx.obj.get("implicit")
    vault = ctx.obj.get("vault")
    # Handle different cases
    if last:
        handle_show_last()
    elif get is not None:
        handle_get(get)
    elif date_range:
        handle_date_range(date_range)
    elif query:
        handle_search(query, limit, fuzzy, exact, semantic)
    else:
        click.echo(ctx.get_help())


# Functions
def save_latest_matches(results: Matches):
    LATEST_MATCHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LATEST_MATCHES_FILE, "w") as f:
        json.dump(results, f)


def load_latest_matches() -> Matches:
    if not LATEST_MATCHES_FILE.exists():
        return None
    with open(LATEST_MATCHES_FILE, "r") as f:
        return Matches(**json.load(f))


# Our handlers
def handle_show_last():
    matches = load_latest_matches()
    if matches is None:
        click.echo("No previous search results found.")
        return
    click.echo(str(matches))


def handle_get(index: int):
    raise NotImplementedError("Get item at index not implemented yet")


def handle_date_range(date_range: str):
    raise NotImplementedError("Date range search not implemented yet")

def handle_search(query: str, limit: int, fuzzy: bool, exact: bool, semantic: bool, vault: Vault):
    # Default to fuzzy search
    if all(not flag for flag in [fuzzy, exact, semantic]):
        fuzzy = True  
    # Exact/semantic/vault are mutually exclusive
    if sum(flag for flag in [fuzzy, exact, semantic]) > 1:
        raise click.UsageError(
            "Options --fuzzy, --exact, and --semantic are mutually exclusive."
        )
    # Perform the search
    if fuzzy:
        from tap.search.fuzzy import fuzzy_search
        return fuzzy_search(query, limit, vault)

    if exact:
        from tap.search.exact import exact_search
        return exact_search(query, limit, vault)

    if semantic:
        from tap.search.semantic import semantic_search
        return semantic_search(query, limit, vault)
