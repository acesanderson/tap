import ast
from pathlib import Path

# --- Configuration ---
VALID_EXTENSIONS = {".py"}
# Directories to ignore during graph walk
IGNORE_DIRS = {
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    "tests",
    "docs",
    "site-packages",
}


class ImportVisitor(ast.NodeVisitor):
    """AST Visitor to capture all import statements."""

    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)


def get_file_imports(file_path):
    """Parses a file and returns a set of imported module strings."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        visitor = ImportVisitor()
        visitor.visit(tree)
        return visitor.imports
    except Exception:
        return set()


def find_project_root(start_path):
    """
    Climbs the directory tree looking for a project marker.
    Priority: pyproject.toml -> .git -> CWD
    """
    current_path = start_path.resolve()
    if current_path.is_file():
        current_path = current_path.parent

    # Traverse up the parents
    for parent in [current_path] + list(current_path.parents):
        if (parent / "pyproject.toml").exists():
            return parent
        if (parent / ".git").exists():
            return parent

    # Fallback
    return Path.cwd()


def resolve_path(import_str, current_file, project_root):
    """Maps an import string (conduit.sync) to a real file path."""
    base_path = import_str.replace(".", "/")

    candidates = [
        f"{base_path}.py",
        f"{base_path}/__init__.py",
        f"src/{base_path}.py",
        f"src/{base_path}/__init__.py",
    ]

    # Handle relative imports logic (e.g. 'from . import utils')
    if current_file.is_absolute():
        try:
            rel_dir = current_file.parent.relative_to(project_root)
            candidates.append(f"{rel_dir}/{base_path}.py")
        except ValueError:
            pass  # current_file is not relative to project_root

    for c in candidates:
        candidate_path = project_root / c
        if candidate_path.exists() and candidate_path.is_file():
            return candidate_path.resolve()

    return None


def walk_graph(entry_file, project_root):
    """BFS walk of the dependency graph."""
    queue = [Path(entry_file).resolve()]
    visited = set()
    visited.add(queue[0])

    results = []

    while queue:
        current_file = queue.pop(0)
        results.append(current_file)

        raw_imports = get_file_imports(current_file)

        for imp in raw_imports:
            resolved_file = resolve_path(imp, current_file, project_root)

            # GUARD: Only process if inside project root
            if resolved_file and project_root in resolved_file.parents:
                if any(part in IGNORE_DIRS for part in resolved_file.parts):
                    continue

                if resolved_file not in visited:
                    visited.add(resolved_file)
                    queue.append(resolved_file)

    return results


def _generate_tree_string(files, project_root) -> str:
    """Generates a visual tree structure string."""
    lines = []
    try:
        rel_paths = sorted([f.relative_to(project_root) for f in files])
    except ValueError:
        rel_paths = sorted([f for f in files])

    lines.append(f"🌳 Dependency Tree for: {project_root.name}")
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


def _generate_blob_string(files, project_root) -> str:
    """Generates the content blob string."""
    lines = []
    lines.append(f"CONTEXT: {len(files)} files found in {project_root.name}.\n")

    for f in files:
        try:
            rel_path = f.relative_to(project_root)
            content = f.read_text(encoding="utf-8")

            lines.append(f"## FILE: {rel_path}")
            lines.append("```python")
            lines.append(content)
            lines.append("```\n")
        except Exception:
            pass

    return "\n".join(lines)


def flatten_script(script_path: Path | str) -> tuple[str, str]:
    """
    Analyzes imports recursively and returns a dependency tree and content blob.

    Args:
        script_path: Path to the python script to analyze

    Returns:
        tuple[str, str]: (tree_visualization, content_blob)
    """
    target = Path(script_path)

    if not target.exists():
        raise FileNotFoundError(f"Script not found: {target}")

    # 1. Detect Project Root
    project_root = find_project_root(target)

    # 2. Walk Dependencies
    dependencies = walk_graph(target, project_root)

    # 3. Generate Strings
    tree_str = _generate_tree_string(dependencies, project_root)
    blob_str = _generate_blob_string(dependencies, project_root)

    return tree_str, blob_str
