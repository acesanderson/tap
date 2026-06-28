# Tap

Tap is a CLI workspace orchestrator designed to search Obsidian vaults and assemble structured context for Large Language Models using a monadic, pipe-based architecture.

## Quick Start

### Installation

Tap requires Python 3.12+ and uses `uv` for dependency management.

```bash
# Set required environment variables
export OBSIDIAN_PATH="~/Documents/my-vault"
export BC="~/code" # Root directory for code repositories

# Install the package
pip install .
```

### Basic Search

Find a note using fuzzy matching (default):

```bash
tap search "project ideas"
```

## Core Value Demonstration

Tap is designed to be piped. It wraps outputs in XML tags, allowing for the composition of complex context blobs from multiple sources.

### Context Composition Example

The following command sequence searches for a project note, retrieves the codebase for a referenced repository, and saves the combined result to a persistent buffer for LLM consumption:

```bash
# Search for a note, pipe to tap alias to get repository XML, and buffer it
tap search "Conduit" --get 0 | tap alias conduit | flatten . -b

# View the accumulated context
flatten -b
```

## Architecture and Design

### Monadic Design
Tap follows a monadic pattern where commands consume and produce structured XML. When input is piped to `tap`, it is automatically wrapped in `<context>` tags, allowing subsequent commands to maintain a chain of thought or a growing knowledge base.

### Component Overview

| Component | Responsibility |
| :--- | :--- |
| **Vault** | High-level interface for reading and parsing Obsidian `.md` files. |
| **Search Engine** | Supports Exact (prefix), Fuzzy (Levenshtein), and Semantic (Vector) search. |
| **Flatten** | Converts directories or Python dependency graphs into LLM-friendly Markdown. |
| **Implicit Input** | Detects `stdin` and wraps content to preserve structure across pipes. |

## Command Reference

Tap installs several specialized CLI utilities for data extraction and research.

### Search and Vault Management
| Command | Description |
| :--- | :--- |
| `tap search` | Search vault notes (supports `--fuzzy`, `--exact`, `--semantic`). |
| `tap alias` | Map short names to specific Obsidian notes or local repositories. |
| `tap pool` | Manage a temporary workspace pool of context items. |

### LLM Context Tools
| Command | Description |
| :--- | :--- |
| `flatten` | Convert a directory or script + dependencies into a single Markdown file. |
| `survey` | Perform multi-document synthesis based on a specific research focus. |
| `readme` | Generate a `README.md` for the current project using a VLM/LLM. |
| `manpage` | Generate and install a system manpage for a project. |

### Media and Extraction
| Command | Description |
| :--- | :--- |
| `ocr` | Extract text from clipboard or file using Tesseract or a VLM (`--llm`). |
| `record` | CLI audio recorder (outputs MP3). |
| `play` | Play MP3 files via the terminal. |
| `peek` | Render images directly in the terminal using `chafa`. |
| `url` | Extract clean text content from any URL. |

## Configuration

### Environment Variables

| Variable | Description | Required |
| :--- | :--- | :--- |
| `OBSIDIAN_PATH` | Absolute path to your Obsidian vault. | Yes |
| `BC` | Root path where your code repositories are located. | Yes |
| `HEADWATER_API_KEY` | Key for LLM services (if using `survey`, `ocr --llm`, or `readme`). | Optional |

### Search Modes

1.  **Fuzzy**: Uses `rapidfuzz` to find titles with high similarity scores.
2.  **Exact**: Fast prefix matching for known note titles.
3.  **Semantic**: Uses `chromadb` and `sentence-transformers` to find notes by meaning rather than keywords.

To initialize the semantic search index:
```bash
python -m tap.database.chroma.load_vault
```

## Usage Examples

### Research Synthesis
Analyze multiple meeting transcripts to find specific strategy mentions:
```bash
survey "What is our Q4 hiring plan?" --dir ./transcripts/ --pattern "*.md"
```

### Dependency Flattening
Create a context blob of a specific script and all its local imports:
```bash
flatten src/tap/cli/main.py > context.xml
```

### Documentation Generation
Generate a manpage for the current project and install it to `~/.local/share/man/`:
```bash
manpage my-tool-name
man my-tool-name
```
