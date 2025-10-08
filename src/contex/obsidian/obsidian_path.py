import os
from pathlib import Path


def get_obsidian_path():
    obsidian_path = os.environ.get("OBSIDIAN_PATH")
    if not obsidian_path:
        raise ValueError("OBSIDIAN_PATH environment variable not set")

    # Expand ~ to actual home directory
    obsidian_path = os.path.expanduser(obsidian_path)

    if not os.path.isdir(obsidian_path):
        raise NotADirectoryError(
            f"The path '{obsidian_path}' is not a valid directory."
        )
    return Path(obsidian_path)
