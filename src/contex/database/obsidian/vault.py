from functools import cached_property, lru_cache
from contex.database.obsidian.obsidian_note import ObsidianNote
from typing import override
from pathlib import Path
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
        # Recursively find all .md files in the obsidian_path directory and subdirectories;
        # if duplicates, keep the first one found
        md_files = list(self.obsidian_path.rglob("*.md"))
        seen: set[str] = set()
        unique_files: list[Path] = []
        for file in md_files:
            if file.name not in seen:
                seen.add(file.name)
                unique_files.append(file)
        return unique_files

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

    @lru_cache
    def get_document_by_title(self, title: str) -> str | None:
        for file in self.paths:
            if file.stem == title:
                try:
                    with file.open("r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    return None
        return None

    @lru_cache
    def get_daily_notes_in_date_range(self, date_one: str, date_two: str) -> list[str]:
        # Create a list of dates in the range date_one to date_two (inclusive)
        from datetime import datetime, timedelta

        start_date = datetime.strptime(date_one, "%Y-%m-%d")
        end_date = datetime.strptime(date_two, "%Y-%m-%d")
        delta = end_date - start_date
        date_list = [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(delta.days + 1)
        ]
        # Find files with titles matching any date in the date_list. Daily notes are strictly named "YYYY-MM-DD.md"
        notes: list[str] = []
        for date in date_list:
            for file in self.paths:
                if file.stem == date:
                    try:
                        with file.open("r", encoding="utf-8") as f:
                            notes.append(f.read())
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
        # Return the list of notes found
        assert len(notes) > 0, "No daily notes found in the given date range."
        return notes

    @lru_cache
    def get_obsidian_note_objects(self) -> list[ObsidianNote]:
        notes: list[ObsidianNote] = []
        for file in self.paths:
            try:
                with file.open("r", encoding="utf-8") as f:
                    content = f.read()
                    note = ObsidianNote.from_file(file)
                    notes.append(note)
            except Exception as e:
                print(f"Error reading {file}: {e}")
        return notes

    @override
    def __repr__(self):
        return f"Vault({self.obsidian_path})"
