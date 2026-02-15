import os
from pathlib import Path

# --- Configuration ---

# Directories to ignore during walk
IGNORE_DIRS = {
    "dev",
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    "tests",
    "docs",
    "site-packages",
    ".idea",
    ".vscode",
    "target",
    "build",
    "dist",
    ".egg-info",
    ".mypy_cache",
    ".pytest_cache",
}

# Specific filenames to ignore (exact match)
IGNORE_FILES = {
    "uv.lock",
    "poetry.lock",
    "package-lock.json",
    "yarn.lock",
    "Cargo.lock",
    "Gemfile.lock",
    "composer.lock",
    ".DS_Store",
    ".env",  # Security: never print env files
}

# Optional: strict extension filtering.
# If you want ALL text files, leave this empty or remove the check.
# Currently configured to allow standard dev files but filter out binaries/images.
INCLUDE_EXTENSIONS = {
    ".py",
    ".toml",
    ".lua",
    ".jinja2",
}


def collect_files(root_path: Path, include_extensions: set[str] | None = None) -> list[Path]:
    """
    Walks the directory recursively and collects all valid file paths.
    Respects IGNORE_DIRS and IGNORE_FILES.

    Args:
        root_path: Directory to walk
        include_extensions: Set of extensions to include (e.g., {'.py', '.json'}).
                          If None, uses INCLUDE_EXTENSIONS default.
    """
    if include_extensions is None:
        include_extensions = INCLUDE_EXTENSIONS

    collected_files = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Modify dirnames in-place to prevent os.walk from entering ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            # 1. Check specific file blocks
            if filename in IGNORE_FILES:
                continue

            file_path = Path(dirpath) / filename

            # 2. Check extensions
            if file_path.suffix not in include_extensions:
                continue

            collected_files.append(file_path)

    return collected_files


def _generate_tree_string(files: list[Path], project_root: Path) -> str:
    """Generates a visual tree structure string."""
    lines = []
    try:
        rel_paths = sorted([f.relative_to(project_root) for f in files])
    except ValueError:
        rel_paths = sorted([f for f in files])

    lines.append(f"🌳 Project Tree for: {project_root.name}")
    lines.append(f"📍 Root: {project_root}")

    printed_dirs = set()

    for path in rel_paths:
        parts = path.parts
        # Directory structure
        for i in range(len(parts) - 1):
            current_dir = Path(*parts[: i + 1])
            if current_dir not in printed_dirs:
                indent = "│   " * i
                lines.append(f"{indent}├── 📂 {parts[i]}/")
                printed_dirs.add(current_dir)

        # File
        depth = len(parts) - 1
        indent = "│   " * depth
        lines.append(f"{indent}├── 📜 {parts[-1]}")

    lines.append(f"\nTotal files: {len(files)}")
    lines.append("=" * 40)

    return "\n".join(lines)


def _generate_blob_string(files: list[Path], project_root: Path) -> str:
    """Generates the content blob string in Markdown format."""
    lines = []
    lines.append(f"CONTEXT: {len(files)} files found in {project_root.name}.\n")

    # Sort files for deterministic output
    try:
        sorted_files = sorted(files, key=lambda f: f.relative_to(project_root))
    except ValueError:
        sorted_files = sorted(files)

    for f in sorted_files:
        try:
            rel_path = f.relative_to(project_root)

            # Try reading as text
            content = f.read_text(encoding="utf-8")

            # Skip empty files if desired
            if not content.strip():
                continue

            # Determine language for code block
            ext = f.suffix.lower().replace(".", "")
            lang = ext if ext else "text"

            lines.append(f"## FILE: {rel_path}")
            lines.append(f"```{lang}")
            lines.append(content)
            lines.append("```\n")
        except UnicodeDecodeError:
            # Skip binary files silently
            pass
        except Exception as e:
            lines.append(f"## FILE: {rel_path} (Error reading file: {e})\n")

    return "\n".join(lines)


def flatten_directory(directory_path: Path | str, include_extensions: set[str] | None = None) -> tuple[str, str]:
    """
    Flattens a directory into a dependency tree and a markdown content blob.

    Args:
        directory_path: Path to the directory to flatten.
        include_extensions: Set of extensions to include (e.g., {'.py', '.json'}).
                          If None, uses INCLUDE_EXTENSIONS default.

    Returns:
        tuple[str, str]: (tree_visualization, content_blob)
    """
    root = Path(directory_path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    # 1. Collect all relevant files
    files = collect_files(root, include_extensions)

    # 2. Generate Strings
    tree_str = _generate_tree_string(files, root)
    blob_str = _generate_blob_string(files, root)

    return tree_str, blob_str
