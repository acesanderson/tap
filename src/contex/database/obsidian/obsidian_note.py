from pydantic import BaseModel, Field
from pathlib import Path


class ObsidianNote(BaseModel):
    title: str = Field(..., description="The title of the note")
    content: str = Field(..., description="The main content of the note")
    created_at: str = Field(..., description="The creation date of the note")
    updated_at: str = Field(..., description="The last updated date of the note")
    wiki_links: list[str] = Field(
        default_factory=list,
        description="A list of links to other notes within the vault",
    )
    links: list[str] = Field(
        default_factory=list, description="A list of external links related to the note"
    )

    @classmethod
    def from_file(cls, file_path: str | Path) -> "ObsidianNote":
        """
        Create an ObsidianNote instance from a markdown file.
        """
        file_path = Path(file_path)
        # Check if *.md
        assert file_path.suffix == ".md", (
            "File must be a markdown file with .md extension"
        )
        assert file_path.exists(), f"File {file_path} does not exist"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple parsing logic (this can be expanded based on actual file structure)
        title = file_path.stem
        wiki_links = []
        links = []

        for line in content.splitlines():
            if "[[" in line and "]]" in line:
                wiki_links.append(line[line.index("[[") + 2 : line.index("]]")].strip())
            if "http" in line:
                # Retrieve the link in markdown format [text](url)
                start = line.index("http")
                end = line.find(" ", start)
                if end == -1:
                    end = len(line)
                links.append(line[start:end].strip())

        created_at = file_path.stat().st_ctime
        updated_at = file_path.stat().st_mtime

        return cls(
            title=title,
            content=content,
            created_at=str(created_at),
            updated_at=str(updated_at),
            wiki_links=wiki_links,
            links=links,
        )


if __name__ == "__main__":
    import os

    obsidian_path = Path(os.getenv("OBSIDIAN_PATH")).expanduser()
    example_file = Path(obsidian_path) / "2025-10-02.md"
    note = ObsidianNote.from_file(example_file)
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    console.print(Markdown(note.model_dump_json(indent=2)))
