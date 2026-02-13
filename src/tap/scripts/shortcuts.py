import sys
from pathlib import Path
from rich.console import Console
from tap.scripts.flatten.flatten_directory import flatten_directory
from tap.scripts.flatten.generate_docs import generate_docs, install_manpage

console = Console()


def get_codebase(target="."):
    path = Path(target).resolve()
    if not path.exists():
        console.print(f"[red]Error: Path {target} not found.[/red]")
        sys.exit(1)

    # Minimal logic: assuming directory for "." context
    _, content = flatten_directory(path)
    return content


def manpage_entrypoint():
    """
    Equivalent to: flatten . -d -v m -s <project_name>
    Usage: manpage <project_name>
    """
    if len(sys.argv) < 2:
        console.print("[red]Usage: manpage <project_name>[/red]")
        sys.exit(1)

    project_name = sys.argv[1]

    with console.status(f"[bold green]Generating manpage for {project_name}..."):
        codebase = get_codebase()
        # 'm' maps to manpage prompt
        response = generate_docs(project_string=codebase, prompt_type="m")

    install_manpage(manpage_text=str(response.content), project_name=project_name)


def readme_entrypoint():
    """
    Equivalent to: flatten . -d -v v > README.md
    Usage: readme
    """
    out_file = Path("README.md")

    with console.status("[bold green]Generating README.md..."):
        codebase = get_codebase()
        # 'v' maps to verbose prompt
        response = generate_docs(project_string=codebase, prompt_type="v")

    out_file.write_text(str(response.content), encoding="utf-8")
    console.print(f"[bold green]✓ Wrote {out_file.absolute()}[/bold green]")
