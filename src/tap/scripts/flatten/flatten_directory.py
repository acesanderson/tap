"""
Local directory processing for the Flatten tool.
Handles flattening local project directories into XML format.
"""

import os
from pathlib import Path
from typing import Callable
from collections.abc import Iterable

from siphon.ingestion.github.flatten_xml import (
    package_to_xml,
    should_exclude_path,
    should_include_file,
)


def read_local_file(file_path: str) -> str:
    """Read content from a local file."""
    with open(file_path, encoding="utf-8") as f:
        return f.read()


def get_local_file_iterator(directory: Path) -> Callable:
    """
    Return a function that iterates over files in a local directory.

    Args:
        directory: Path to the directory to iterate

    Returns:
        Function that yields (file_path, filename) tuples
    """

    def iterator() -> Iterable[tuple[str, str]]:
        for dirpath, dirnames, filenames in os.walk(directory):
            # Skip excluded directories
            path_str = str(dirpath)
            if should_exclude_path(path_str):
                continue

            # Modify dirnames in-place to prevent os.walk from entering excluded dirs
            i = 0
            while i < len(dirnames):
                dirname = dirnames[i]
                test_path = os.path.join(dirpath, dirname)
                if should_exclude_path(test_path):
                    dirnames.pop(i)
                else:
                    i += 1

            # Process files in non-excluded directories
            for filename in filenames:
                if should_include_file(filename):
                    file_path = os.path.join(dirpath, filename)
                    # Convert to relative path from the base directory
                    relative_path = os.path.relpath(file_path, directory)
                    # Normalize path separators for consistency
                    relative_path = relative_path.replace(os.sep, "/")
                    yield (relative_path, filename)

    return iterator


def flatten_directory(directory_path: str = ".") -> str:
    """
    Flatten a local directory into XML format.

    Args:
        directory_path: Path to the directory to flatten (default: current directory)

    Returns:
        XML string representation of the directory
    """
    directory = Path(directory_path).resolve()
    project_name = directory.name

    # Create the path iterator for this directory
    path_iterator = get_local_file_iterator(directory)

    # Create file reader that handles absolute paths
    def file_reader(relative_path: str) -> str:
        absolute_path = directory / relative_path
        return read_local_file(str(absolute_path))

    return package_to_xml(project_name, file_reader, path_iterator)
