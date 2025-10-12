import click


@click.command()
@click.argument("index", type=int)
def stow(index: int):
    """Add item from last search to pool"""
    raise NotImplementedError("Stow command not implemented yet")
