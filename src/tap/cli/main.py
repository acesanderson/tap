"""
Tap CLI - Main Entry Point
Search is the default command when no subcommand is provided, hence the logic is in this file.
"""

import click
from tap.cli.commands import alias, pool, stow, search


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Tap - Search and compose context from your Obsidian vault"""
    # This is the root command
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register other command groups
cli.add_command(search.search_group, name="search")
cli.add_command(alias.alias_group, name="alias")
cli.add_command(pool.pool_group, name="pool")
cli.add_command(stow.stow, name="stow")


def main():
    cli()


if __name__ == "__main__":
    main()
