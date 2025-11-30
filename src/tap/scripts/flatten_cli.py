"""
Flatten - CLI tool for converting GitHub repositories and local directories
into LLM-friendly XML format.

Usage:
    python Flatten.py .                                    # Flatten current directory
    python Flatten.py /path/to/directory                   # Flatten specific directory
    python Flatten.py https://github.com/owner/repo        # Flatten GitHub repository

Options:
    -l, --last        Retrieve and display the last stored response
    -d, --docs        Generate project README documentation
    -p, --pretty      Pretty-print the output XML
    -v, --verbose     Enable verbose readme generation (default is terse)
"""

from tap.scripts.flatten.flatten_directory import flatten_directory
from tap.scripts.flatten.flatten_script import flatten_script
from rich.console import Console
from rich.markdown import Markdown
from conduit.sync import Response
from pathlib import Path
import argparse
import sys


def main():
    """Main CLI entry point for the Flatten tool."""
    parser = argparse.ArgumentParser(
        description="Flatten a local directory or a local script (with deps) into LLM-friendly Markdown format",
    )
    # Basic use case: generate XML as LLM context
    parser.add_argument(
        "target",
        type=str,
        nargs="?",
        help="Directory path, or '.' for current directory",
    )
    # Docs generation args
    parser.add_argument(
        "-d",
        "--docs",
        action="store_true",
        help="Generate project README.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        nargs="?",
        choices=["t", "v", "c"],
        help="Enable verbose readme. Options: 't' (terse, default), 'v' (verbose), 'c' (critique'.",
    )
    parser.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="Pretty-print the output",
    )
    parser.add_argument(
        "-t",
        "--tree",
        action="store_true",
        help="Print the tree structure of the flattened target",
    )

    args = parser.parse_args()
    target = args.target

    # Detect no input, if no args provided, show help
    # If no args provided, show help and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Create output (flattened XML) based on target type
    output: str | None = None
    tree: str | None = None

    try:
        input_path = Path(target).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Path '{target}' does not exist.")
        if input_path.is_dir():
            tree, output = flatten_directory(input_path)
        elif input_path.is_file():
            tree, output = flatten_script(input_path)
    except Exception:
        raise ValueError(f"Invalid target path: '{target}'")

    assert output is not None, "No output generated from the target."
    assert tree is not None, "No tree structure generated from the target."

    # Handle --docs flag to generate README
    if args.docs:
        from tap.scripts.flatten.generate_docs import generate_docs

        prompt_type = args.verbose
        response = generate_docs(project_string=output, prompt_type=prompt_type)
        assert isinstance(response, Response), (
            f"Expected Response object from generate_docs, got {type(response)}"
        )
        if args.pretty:
            console = Console()
            md = Markdown(str(response.content))
            console.print(md)
            exit(0)
        else:
            print(response.content)
            exit(0)

    # Finally, print output
    if args.tree:
        print("Tree Structure:\n")
        print(tree)
        exit(0)
    if args.pretty:
        console = Console()
        md = Markdown(output)
        console.print(md)
        exit(0)
    else:
        print(output)
        exit(0)


if __name__ == "__main__":
    main()
