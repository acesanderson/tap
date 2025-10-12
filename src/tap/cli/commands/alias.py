import click


@click.group(invoke_without_command=True)
@click.argument("name", required=False)
@click.argument("target", required=False)
@click.option("--get", "-g", type=int, help="Use item at index")
@click.pass_context
def alias_group(ctx, name, target, get):
    """Manage note aliases"""
    if ctx.invoked_subcommand:
        return  # Subcommand will handle it

    if name is None:
        # tap alias (list)
        handle_alias_list()
    elif get is not None:
        # tap alias <name> -g <index>
        handle_alias_create(name, index=get)
    elif target is not None:
        # tap alias <name> <target>
        handle_alias_create(name, title=target)
    else:
        click.echo("Error: Provide either a target title or use -g flag")


@alias_group.command(name="rm")
@click.argument("name")
def remove(name):
    """Remove an alias"""
    handle_alias_remove(name)


# Handlers
def handle_alias_list():
    raise NotImplementedError("Alias list command not implemented yet")


def handle_alias_create(name: str, title: str = None, index: int = None):
    raise NotImplementedError("Alias create command not implemented yet")


def handle_alias_remove(name: str):
    raise NotImplementedError("Alias remove command not implemented yet")
