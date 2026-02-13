from __future__ import annotations
from conduit.config import settings
from conduit.sync import Conduit, Prompt, Verbosity
from pathlib import Path
from typing import Literal, TYPE_CHECKING
from rich.console import Console
import os
import gzip

if TYPE_CHECKING:
    from conduit.domain.conversation.conversation import Conversation

# Constants
PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_FILES = {
    "terse": PROMPT_DIR / "terse_docs_prompt.jinja2",
    "verbose": PROMPT_DIR / "verbose_docs_prompt.jinja2",
    "critique": PROMPT_DIR / "docs_critique_prompt.jinja2",
    "manpage": PROMPT_DIR / "man_page.jinja2",
}
PREFERRED_MODEL = "flash"
VERBOSITY = Verbosity.SILENT
CACHE = settings.default_cache("flatten")
CONSOLE = Console()


# Verify prompt_files exist
for key in PROMPT_FILES:
    if not PROMPT_FILES[key].exists():
        raise FileNotFoundError(
            f"Prompt file for '{key}' not found: {PROMPT_FILES[key]}"
        )


def generate_docs(
    project_string: str, prompt_type: Literal["t", "v", "c", "m"]
) -> Conversation:
    """
    Generate documentation from an XML string using a predefined prompt and model.
    """
    match prompt_type:
        case "t":
            prompt_type = "terse"
        case "v":
            prompt_type = "verbose"
        case "c":
            prompt_type = "critique"
        case "m":
            prompt_type = "manpage"
        case _:
            raise ValueError(f"Invalid prompt type: {prompt_type}")

    prompt_file = PROMPT_FILES[prompt_type]
    # Build the conduit
    prompt = Prompt(prompt_file.read_text())
    conduit = Conduit.create(
        project_name="flatten",
        prompt=prompt,
        model=PREFERRED_MODEL,
        verbosity=VERBOSITY,
        console=CONSOLE,
        cache=True,
    )
    response = conduit.run(input_variables={"code": project_string})
    return response


def install_manpage(manpage_text: str, project_name: str, user_local: bool = True):
    """
    Install a man page for a CLI project.

    Automatically compresses to .gz and updates man database if system-wide.

    Args:
        manpage_text: The man page content in troff/groff format.
        project_name: Name of the CLI command/project (used for filename).
        user_local: If True (default), installs to user-local manpath (~/.local/share/man/man1).
                    If False, installs system-wide (/usr/local/share/man/man1) and updates mandb.
    """
    section = "1"
    filename = f"{project_name}.{section}"

    if user_local:
        man_dir = Path.home() / ".local" / "share" / "man" / f"man{section}"
    else:
        man_dir = Path("/usr/local/share/man") / f"man{section}"

    man_dir.mkdir(parents=True, exist_ok=True)

    man_path = man_dir / filename
    gz_path = man_path.with_suffix(man_path.suffix + ".gz")

    # Write compressed man page
    with gzip.open(gz_path, "wt", encoding="utf-8") as f:
        f.write(manpage_text)

    print(f"Man page installed to: {gz_path}")

    if not user_local:
        # Update system-wide man database
        os.system("mandb")
        print("System man database updated.")
