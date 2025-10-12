import click


@click.group(name="tap", invoke_without_command=True)
@click.argument("query", required=False)
@click.option("--limit", "-L", default=5, help="Number of results")
@click.option("--last", "-l", is_flag=True, help="Show last search results")
@click.option("--get", "-g", type=int, help="Get item at index")
@click.option("--date-range", "-d", help="Date range YYYY-MM-DD:YYYY-MM-DD")
@click.option("--fuzzy", is_flag=True, help="Force fuzzy search")
@click.option("--exact", is_flag=True, help="Force exact match")
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


def handle_show_last():
    raise NotImplementedError("Show last search results not implemented yet")


def handle_get(index: int):
    raise NotImplementedError("Get item at index not implemented yet")


def handle_date_range(date_range: str):
    raise NotImplementedError("Date range search not implemented yet")


def handle_search(query: str, limit: int, fuzzy: bool, exact: bool):
    raise NotImplementedError("Search command not implemented yet")
