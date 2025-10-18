import click
import json
from xdg_base_dirs import xdg_data_home
from tap.search.match_class import Matches

LATEST_MATCHES_FILE = xdg_data_home() / "tap" / "latest_matches.json"


@click.group(name="tap", invoke_without_command=True)
@click.argument("query", required=False)
@click.option("--limit", "-L", default=5, help="Number of results")
@click.option("--last", "-l", is_flag=True, help="Show last search results")
@click.option("--get", "-g", type=int, help="Get item at index")
@click.option("--date-range", "-d", help="Date range YYYY-MM-DD:YYYY-MM-DD")
@click.pass_context
def search_group(ctx, query, limit, last, get, date_range, fuzzy, exact):
    """Search vault notes"""
    if last:
        handle_show_last()
    elif get is not None:
        handle_get(get)
    elif date_range:
        handle_date_range(date_range)
    elif query:
        handle_search(query, limit, fuzzy, exact)
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


def handle_search(query: str, limit: int):
    raise NotImplementedError("Search command not implemented yet")
