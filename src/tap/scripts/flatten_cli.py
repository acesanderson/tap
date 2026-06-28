"""
CLI tool for flattening codebases and directories into LLM-friendly markdown context.

This script converts directories or Python scripts into structured markdown blobs suitable for feeding to language models, enabling code analysis, documentation generation, and context preservation. It handles both directory traversal (collecting files by extension) and dependency graph walking (for Python scripts), producing both a visual tree structure and full content blob.

The main workflow chains together flatten_directory() or flatten_script() to generate output, with optional post-processing via the generate_docs() pipeline to create READMEs or manpages. A persistent buffer system allows accumulating multiple flattened outputs with timestamps and metadata, supporting monadic composition where multiple flattening operations can be queued and processed together—aligned with tap's broader design of piping structured XML context between CLI commands.

Usage:
```bash
flatten /path/to/project                    # Flatten a directory, output markdown
flatten script.py                            # Flatten a script with its dependencies
flatten . -d -v v                            # Generate verbose README for current project
flatten /path -b                             # Append flattening to persistent buffer
flatten -b                                   # Display accumulated buffer contents
flatten /path -i .py .toml                   # Include only specific file extensions
```
"""

from tap.scripts.flatten.flatten_directory import flatten_directory, INCLUDE_EXTENSIONS
from tap.scripts.flatten.flatten_script import flatten_script
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path
from datetime import datetime
import argparse
import sys
import re


def normalize_extension(ext: str) -> str:
    """
    Normalize extension format: strip whitespace, lowercase, ensure leading dot.

    Examples:
        'json' -> '.json'
        '.JSON' -> '.json'
        ' .md ' -> '.md'
    """
    ext = ext.strip().lower()
    return ext if ext.startswith(".") else f".{ext}"


# Buffer configuration
BUFFER_PATH = Path.home() / ".cache" / "flatten" / "buffer.md"


def append_to_buffer(tree: str, content: str, source_path: str):
    """Append flatten output to buffer with XML wrapping and metadata."""
    BUFFER_PATH.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    entry = f'<entry source="{source_path}" timestamp="{timestamp}">\n'
    entry += f"{tree}\n\n{content}\n"
    entry += "</entry>\n\n"

    with BUFFER_PATH.open("a", encoding="utf-8") as f:
        f.write(entry)


def show_buffer():
    """Output buffer contents to stdout."""
    if not BUFFER_PATH.exists() or BUFFER_PATH.stat().st_size == 0:
        return
    print(BUFFER_PATH.read_text(encoding="utf-8"), end="")


def clear_buffer():
    """Delete buffer file silently."""
    BUFFER_PATH.unlink(missing_ok=True)


def show_buffer_info():
    """Show buffer metadata without full content."""
    if not BUFFER_PATH.exists() or BUFFER_PATH.stat().st_size == 0:
        print("Buffer is empty", file=sys.stderr)
        return

    content = BUFFER_PATH.read_text(encoding="utf-8")
    # Match only at line start to avoid matching code snippets
    pattern = r'^<entry source="([^"]+)" timestamp="([^"]+)">'
    matches = re.findall(pattern, content, re.MULTILINE)

    if not matches:
        print("Buffer is empty", file=sys.stderr)
        return

    # Try to extract file counts from each entry
    file_count_pattern = r"CONTEXT: (\d+) files"
    file_counts = re.findall(file_count_pattern, content)

    print(f"Buffer contains {len(matches)} entries:")
    for i, (source, timestamp) in enumerate(matches, 1):
        # Parse timestamp for human-readable format
        dt_parts = timestamp.split("T")
        date = dt_parts[0]
        time = dt_parts[1].split(".")[0] if len(dt_parts) > 1 else ""

        # Add file count if available
        if i <= len(file_counts):
            print(f"  {i}. {source} ({file_counts[i - 1]} files) - {date} {time}")
        else:
            print(f"  {i}. {source} - {date} {time}")


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
        choices=["t", "v", "c", "m"],
        default="t",
        help="Enable verbose readme. Options: 't' (terse, default), 'v' (verbose), 'c' (critique'), 'm' ('manpage').",
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
    parser.add_argument(
        "-s",
        "--save",
        type=str,
        help="Save the generated manpage for a provided project name.",
    )
    parser.add_argument(
        "--list-extensions",
        action="store_true",
        help="Show default file extensions and exit.",
    )

    # Buffer operations
    parser.add_argument(
        "-b",
        "--buffer",
        action="store_true",
        help="Append flatten output to buffer (with target) or show buffer contents (without target).",
    )
    parser.add_argument(
        "-w",
        "--wipe",
        action="store_true",
        help="Clear the buffer.",
    )
    parser.add_argument(
        "--buffer-info",
        action="store_true",
        help="Show buffer metadata (entry count, sources, timestamps).",
    )

    # Extension filtering (mutually exclusive)
    ext_group = parser.add_mutually_exclusive_group()
    ext_group.add_argument(
        "-i",
        "--include",
        nargs="+",
        metavar="EXT",
        help="Include only these extensions (e.g., -i .json .md .yaml). Replaces defaults. Use '*' to include all files except binaries. Only applies to directory targets.",
    )
    ext_group.add_argument(
        "-e",
        "--exclude",
        nargs="+",
        metavar="EXT",
        help="Exclude these extensions from defaults (e.g., -e .toml .lua). Only applies to directory targets.",
    )

    args = parser.parse_args()

    # Handle --list-extensions early exit
    if args.list_extensions:
        print("Default file extensions:")
        for ext in sorted(INCLUDE_EXTENSIONS):
            print(f"  {ext}")
        sys.exit(0)

    # Mutual exclusion checks (do these first, before any operations)
    if args.buffer and args.wipe:
        parser.error("-b/--buffer and -w/--wipe are mutually exclusive")

    if args.buffer and (args.docs or args.tree or args.pretty):
        parser.error("-b/--buffer is incompatible with --docs, --tree, and --pretty")

    # Handle buffer operations
    if args.buffer_info:
        show_buffer_info()
        sys.exit(0)

    if args.wipe:
        clear_buffer()
        sys.exit(0)

    # Handle -b without target: show buffer
    if args.buffer and not args.target:
        show_buffer()
        sys.exit(0)

    target = args.target

    # Detect no input, if no args provided, show help
    # If no args provided, show help and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Compute final extension set based on -i/-e flags
    include_extensions = None  # None means use defaults
    if args.include:
        # Handle '*' wildcard - means all extensions except binaries
        if "*" in args.include:
            if len(args.include) > 1:
                raise ValueError("Cannot mix '*' wildcard with specific extensions")
            # '*' means include all text files, but we'll let the directory walker handle binary filtering
            include_extensions = set()  # Empty set means include all files, let the walker handle filtering
        else:
            include_extensions = {normalize_extension(ext) for ext in args.include}
    elif args.exclude:
        exclude_set = {normalize_extension(ext) for ext in args.exclude}
        include_extensions = INCLUDE_EXTENSIONS - exclude_set

    # Create output (flattened XML) based on target type
    output: str | None = None
    tree: str | None = None

    try:
        input_path = Path(target).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Path '{target}' does not exist.")
        if input_path.is_dir():
            tree, output = flatten_directory(input_path, include_extensions)
        elif input_path.is_file():
            tree, output = flatten_script(input_path)
    except Exception:
        raise ValueError(f"Invalid target path: '{target}'")

    assert output is not None, "No output generated from the target."
    assert tree is not None, "No tree structure generated from the target."

    # Append to buffer if requested
    if args.buffer:
        append_to_buffer(tree, output, target)

    # Handle --docs flag to generate README
    if args.docs:
        from tap.scripts.flatten.generate_docs import generate_docs

        prompt_type = args.verbose
        response = generate_docs(project_string=output, prompt_type=prompt_type)
        if args.save:
            from tap.scripts.flatten.generate_docs import install_manpage

            project_name = args.save
            print(project_name)
            manpage_text = str(response.content)
            install_manpage(project_name=project_name, manpage_text=manpage_text)
            exit()
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
