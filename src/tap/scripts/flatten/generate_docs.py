from __future__ import annotations
from conduit.sync import Conduit, Prompt, Verbosity
from pathlib import Path
from typing import Literal, TYPE_CHECKING
from rich.console import Console

if TYPE_CHECKING:
    from conduit.domain.conversation.conversation import Conversation

# Constants
PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_FILES = {
    "terse": PROMPT_DIR / "terse_docs_prompt.jinja2",
    "verbose": PROMPT_DIR / "verbose_docs_prompt.jinja2",
    "critique": PROMPT_DIR / "docs_critique_prompt.jinja2",
}
PREFERRED_MODEL = "flash"
VERBOSITY = Verbosity.COMPLETE
CONSOLE = Console()


# Verify prompt_files exist
for key in PROMPT_FILES:
    if not PROMPT_FILES[key].exists():
        raise FileNotFoundError(
            f"Prompt file for '{key}' not found: {PROMPT_FILES[key]}"
        )


def generate_docs(
    project_string: str, prompt_type: Literal["t", "v", "c"]
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
        case _:
            raise ValueError(f"Invalid prompt type: {prompt_type}")

    prompt_file = PROMPT_FILES[prompt_type]
    # Build the conduit
    prompt = Prompt(prompt_file.read_text())
    conduit = Conduit.create(
        prompt=prompt, model=PREFERRED_MODEL, verbosity=VERBOSITY, console=CONSOLE
    )
    response = conduit.run(input_variables={"code": project_string})
    return response
