from pathlib import Path
from functools import cached_property
from typing import override
import os


class Vault:
    @cached_property
    def obsidian_path(self) -> Path:
        obsidian_path = os.environ.get("OBSIDIAN_PATH")
        if not obsidian_path:
            raise ValueError("OBSIDIAN_PATH environment variable not set")

        path = Path(obsidian_path).expanduser()

        if not path.is_dir():
            raise NotADirectoryError(f"'{path}' is not a valid directory.")

        return path

    @cached_property
    def paths(self) -> list[Path]:
        return list(self.obsidian_path.rglob("*.md"))

    @cached_property
    def titles(self) -> list[str]:
        return [file.stem for file in self.paths]

    @cached_property
    def documents(self) -> list[str]:
        documents: list[str] = []
        for file in self.paths:
            try:
                with file.open("r", encoding="utf-8") as f:
                    documents.append(f.read())
            except Exception as e:
                print(f"Error reading {file}: {e}")
                documents.append("")  # Append empty string on error
        return documents

    @override
    def __repr__(self):
        return f"Vault({self.obsidian_path})"
