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
from tap.scripts.flatten.flatten_url import flatten_github_repo
from tap.scripts.flatten.flatten_script import flatten_script
from rich.console import Console
from rich.markdown import Markdown
from xdg_base_dirs import xdg_state_home
from conduit.sync import Response
from pathlib import Path
import argparse
import sys
import json

PREVIOUS_RESPONSE_FILE = xdg_state_home() / "flatten" / "previous_response.json"


def store_response(response: Response) -> None:
    cache_dict = response.to_cache_dict()
    with PREVIOUS_RESPONSE_FILE.open("w", encoding="utf-8") as f:
        json.dump(cache_dict, f, indent=2)


def retrieve_response() -> Response | None:
    if not PREVIOUS_RESPONSE_FILE.exists():
        return None
    with PREVIOUS_RESPONSE_FILE.open("r", encoding="utf-8") as f:
        cache_dict = json.load(f)
    return Response.from_cache_dict(cache_dict)


def main():
    """Main CLI entry point for the Flatten tool."""
    parser = argparse.ArgumentParser(
        description="Flatten a GitHub repo or local directory into LLM-friendly XML format",
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
        "-l",
        "--last",
        action="store_true",
        help="Retrieve and display the last stored response",
    )
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
        help="Pretty-print the output XML",
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

    # Handle --docs flag to generate README
    if args.docs:
        from tap.scripts.flatten.generate_docs import generate_docs

        prompt_type = args.verbose
        response = generate_docs(xml_string=output, prompt_type=prompt_type)
        assert isinstance(response, Response), (
            f"Expected Response object from generate_docs, got {type(response)}"
        )
        store_response(response)
        if args.pretty:
            console = Console()
            md = Markdown(response.content)
            console.print(md)
            exit(0)
        else:
            print(response.content)
            exit(0)

    # Create output (flattened XML) based on target type
    output: str | None = None
    tree: str | None = None

    try:
        if target.startswith("https://github.com/"):
            # Process GitHub repository
            output = flatten_github_repo(target)
        else:
            try:
                input_path = Path(target).resolve()
                if not input_path.exists():
                    raise FileNotFoundError(f"Path '{target}' does not exist.")
                if input_path.is_dir():
                    output = flatten_directory(input_path)
                elif input_path.is_file():
                    tree, output = flatten_script(input_path)
            except Exception:
                raise ValueError(f"Invalid target path: '{target}'")
    except Exception as e:
        print(f"Error processing target '{target}': {e}", file=sys.stderr)
        sys.exit(1)

    assert output is not None, "No output generated from the target."

    # Print output
    if args.tree and tree is not None:
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
