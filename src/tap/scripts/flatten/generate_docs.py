from conduit.sync import Conduit, Prompt, Model, Response, Verbosity
from pathlib import Path
from typing import Literal
from rich.console import Console

# Constants
PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_FILES = {
    "terse": PROMPT_DIR / "terse_docs_prompt.jinja2",
    "verbose": PROMPT_DIR / "verbose_docs_prompt.jinja2",
    "critique": PROMPT_DIR / "docs_critique_prompt.jinja2",
}
PREFERRED_MODEL = "gemini2.5"
VERBOSITY = Verbosity.COMPLETE
CONSOLE = Console()

# Our singleton
Model.console = CONSOLE

# Verify prompt_files exist
for key in PROMPT_FILES:
    if not PROMPT_FILES[key].exists():
        raise FileNotFoundError(
            f"Prompt file for '{key}' not found: {PROMPT_FILES[key]}"
        )


def generate_docs(project_string: str, prompt_type: Literal["t", "v", "c"]) -> Response:
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
    model = Model(PREFERRED_MODEL)
    conduit = Conduit(prompt=prompt, model=model)
    response = conduit.run(input_variables={"code": project_string}, verbose=VERBOSITY)
    # Validate response type
    if not isinstance(response, Response):
        raise ValueError(
            f"Expected response to be of type Response, got {type(response)}"
        )
    return response
