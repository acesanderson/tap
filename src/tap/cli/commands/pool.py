import click


@click.group()
def pool_group():
    """Manage workspace pool"""
    pass


@pool_group.command(name="show")
def show():
    """Display pool contents"""
    raise NotImplementedError("Show command not implemented yet")


@pool_group.command(name="pour")
def pour():
    """Output pool as XML, keep intact"""
    raise NotImplementedError("Pour command not implemented yet")


@pool_group.command(name="drain")
def drain():
    """Output pool as XML, then clear"""
    raise NotImplementedError("Drain command not implemented yet")


@pool_group.command(name="remove")
@click.argument("index", type=int)
def remove(index):
    """Remove item from pool"""
    raise NotImplementedError("Remove command not implemented yet")


@pool_group.command(name="clear")
def clear():
    """Clear pool without output"""
    raise NotImplementedError("Clear command not implemented yet")
