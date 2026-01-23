from pathlib import Path
import json
import logging
import os
from functools import cached_property

logger = logging.getLogger(__name__)

ALIAS_FILE = Path(__file__).parent / "aliases.json"
assert ALIAS_FILE.exists(), f"Alias file not found: {ALIAS_FILE}"
OBSIDIAN_PATH = Path(str(os.getenv("OBSIDIAN_PATH")))
assert OBSIDIAN_PATH is not None, "OBSIDIAN_PATH environment variable not set"
CODE_ROOT_PATH = Path(str(os.getenv("BC")))
assert CODE_ROOT_PATH is not None, "BC environment variable not set"


class AliasStore:
    def __init__(self):
        self.aliases_dict: dict[str, dict[str, str]] = json.loads(
            ALIAS_FILE.read_text(encoding="utf-8")
        )

    # Membership check
    @cached_property
    def aliases(self) -> set[str]:
        alias_set = set()
        for category_key in self.aliases_dict.keys():
            for alias_key in self.aliases_dict[category_key].keys():
                alias_set.add(alias_key)
        return alias_set

    def is_alias(self, input: str) -> bool:
        """
        Check if input is a known alias.
        """
        return input in self.aliases

    # Retrieval methods
    def retrieve_alias(self, input: str) -> str | None:
        """
        Check for hit; return document text if found.
        """
        alias_json = ALIAS_FILE.read_text(encoding="utf-8")
        aliases = json.loads(alias_json)
        if input in aliases["aliases"]:
            obsidian_file_prefix = aliases["aliases"][input]
            obsidian_file_name = obsidian_file_prefix + ".md"
            obsidian_file_path = OBSIDIAN_PATH / obsidian_file_name
            assert obsidian_file_path.exists(), (
                f"Obsidian file not found: {obsidian_file_path}"
            )
            return obsidian_file_path.read_text(encoding="utf-8")
        return None

    def retrieve_repo(self, input: str) -> str | None:
        """
        Check for hit; return repository URL if found.
        """
        alias_json = ALIAS_FILE.read_text(encoding="utf-8")
        aliases = json.loads(alias_json)
        if input in aliases["repos"]:
            repo_name = aliases["repos"][input]
            repo_path = CODE_ROOT_PATH / repo_name
            if repo_path.exists():
                from tap.scripts.flatten.flatten_directory import flatten_directory

                repo_xml = flatten_directory(str(repo_path))
                if not repo_xml:
                    logger.warning(f"Failed to flatten repository for input: {input}")
                    return None
                return repo_xml
        return None

    def route_alias(self, input: str) -> str | None:
        """
        Wrapper function.
        Route to the appropriate alias retrieval function.
        """
        if not self.is_alias(input):
            return None
        else:
            # Obsidian file aliases
            alias_result = self.retrieve_alias(input)
            if alias_result:
                return alias_result
            # Repo aliases
            repo_result = self.retrieve_repo(input)
            if repo_result:
                return repo_result
            return None

    def display(self):
        from rich.console import Console

        console = Console()
        console.print_json(json.dumps(self.aliases_dict, indent=2))


if __name__ == "__main__":
    alias_store = AliasStore()
    alias_store.display()

    test_input = "lic"
    result = alias_store.route_alias(test_input)
    if result:
        print(f"Alias found for '{test_input}':\n{(result[:20])}")
    else:
        print(f"No alias found for '{test_input}'.")

    test_repo = "conduit"
    repo_result = alias_store.route_alias(test_repo)
    if repo_result:
        print(f"Repository found for '{test_repo}':\n{str(repo_result[:20])}")
    else:
        print(f"No repository found for '{test_repo}'.")
