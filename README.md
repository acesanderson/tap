# contex

**Compose Obsidian knowledge artifacts into LLM-ready context streams.**

A minimal, POSIX-compliant CLI tool for injecting Obsidian notes into LLM pipelines. Supports fuzzy matching, vector similarity search, aliasing, and stream composition.

---

## Table of Contents

- [Philosophy](#philosophy)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Command Reference](#command-reference)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Implementation Details](#implementation-details)
- [Relationship to Twig and Siphon](#relationship-to-twig-and-siphon)
- [Roadmap](#roadmap)

---

## Philosophy

### POSIX Composition Over Monolithic Tools

`contex` does one thing: injects Obsidian content into stdout as XML-tagged streams. It composes with other tools via pipes rather than trying to be an all-in-one solution.

### The Sourdough Model

Like sourdough starter, knowledge artifacts need continuous cultivation. `contex` makes it frictionless to "feed" context into LLM conversations, laying the groundwork for auto-maintained knowledge bases (the "Sourdough" vision).

### Design Constraints

- **No preprocessing**: Context artifacts are human-maintained markdown files
- **No local caching**: Files are small, reads are fast, Obsidian is the source of truth
- **Pure stdin/stdout**: Composes with any tool via pipes
- **Single responsibility**: Context injection only
- **Vector search as optional enhancement**: Fuzzy matching works for 80% of cases

These constraints keep `contex` simple and fast for personal use. [Siphon](#relationship-to-twig-and-siphon) handles complex ingestion, caching, and multi-source synthesis.

---

## Quick Start

### Installation

```bash
pip install -e .

# Set Obsidian vault location
export OBSIDIAN_VAULT="$HOME/Documents/Obsidian"

# Optional: Vector search requires running Chroma server
# (contex imports your existing Chroma connection library)
```

### Basic Usage

```bash
# Find a file
contex "mental health" -s
# → Matched: Mental Health Context.md

# Pipe to LLM
contex "mental health" | twig "Analyze my triggers"

# Chain multiple contexts
contex -a "linkedin" | contex "mental health" | twig "Career burnout advice"

# Tag arbitrary content
cat data.csv | contex -p "product-catalog" | twig "Analyze this data"
```

---

## Core Concepts

### Three Operating Modes

#### 1. Lookup Mode (Default)
Searches Obsidian vault using fuzzy matching or vector similarity, wraps result in XML tags.

```bash
contex "linkedin" -t "profile"
# → <profile>[content of LinkedIn Professional Context.md]</profile>
```

#### 2. Passthrough Mode (`-p` flag)
Tags stdin without performing any file lookup. Enables tagging arbitrary content streams.

```bash
cat file.txt | contex -p "data"
# → <data>[stdin content]</data>
```

#### 3. Alias Mode (`-a` flag)
Uses predefined shortcuts for frequently accessed contexts. Aliases map to specific files with custom tags.

```bash
contex -a "linkedin"
# → <linkedin>[content from aliased file]</linkedin>
```

### Query Methods

#### Fuzzy Matching (Default)
Uses RapidFuzz for fast, deterministic title matching. Handles typos and partial queries.

```bash
contex "mental health"
# Matches: "Mental Health Context.md"
```

#### Vector Similarity Search (`-v` flag)
Uses your existing Chroma server for semantic search. Better for conceptual queries.

```bash
contex -v "stuff about emotional triggers"
# Finds semantically related content even if title doesn't match
```

### XML Tag Generation

Tags follow kebab-case convention and are derived from filenames:

```
"LinkedIn Professional Context.md" → <linkedin-professional-context>
"Mental Health Context.md"         → <mental-health-context>
"Sales Strategy FY26.md"           → <sales-strategy-fy26>
```

**Transformation rules:**
1. Remove `.md` extension
2. Convert to lowercase
3. Replace spaces and underscores with hyphens
4. Optionally strip "Context" suffix: `<linkedin-professional-context>` → `<linkedin-professional>`

Override with `-t` flag:
```bash
contex "linkedin" -t "profile"
# → <profile>...</profile>
```

### Stream Composition

`contex` reads from stdin and appends its output, enabling chaining:

```bash
contex -a "linkedin" | contex "mental health" | twig "..."
# Produces: <linkedin>...</linkedin><mental-health-context>...</mental-health-context>
```

Order matters—LLMs have recency bias, so place most important context last.

### Aliases

Aliases are predefined mappings stored in `~/.config/contex/aliases.json`:

```json
{
  "linkedin": {
    "file": "LinkedIn Professional Context.md",
    "tag": "linkedin",
    "description": "Professional background and experience",
    "last_used": "2025-09-29T10:23:15Z",
    "use_count": 47
  },
  "mental-health": {
    "file": "Mental Health Context.md",
    "tag": "mental-health-context",
    "description": "Therapeutic frameworks and trigger patterns",
    "last_used": "2025-09-28T14:12:03Z",
    "use_count": 23
  }
}
```

**Why track usage?**
- Identifies which contexts provide real value vs. premature abstraction
- Informs Siphon's auto-curation features later
- Helps prune unused contexts

---

## Command Reference

### Command Signature

```
contex [QUERY] [OPTIONS]
contex -a <ALIAS> [OPTIONS]
contex -p <TAG> [OPTIONS]
```

**Mutually exclusive modes:**
- Cannot use `QUERY` with `-a` (alias mode)
- Cannot use `QUERY` with `-p` (passthrough mode)
- Cannot use `-a` with `-p`

### Flags

#### Query Options
| Flag | Long Form | Argument | Description |
|------|-----------|----------|-------------|
| `-t` | `--tag` | `<name>` | Override auto-generated XML tag name |
| `-s` | `--source` | none | Show matched filename to stderr |
| `-v` | `--vector` | none | Use vector similarity search instead of fuzzy matching |

#### Mode Flags
| Flag | Long Form | Argument | Description |
|------|-----------|----------|-------------|
| `-a` | `--alias` | `<name>` | Use predefined alias instead of query |
| `-p` | `--passthrough` | `<tag>` | Tag stdin without file lookup |

#### Alias Management
| Flag | Long Form | Argument | Description |
|------|-----------|----------|-------------|
| `-m` | `--make-alias` | `<name>` | Create alias from query result |
| | `--list-aliases` | none | Show all defined aliases |
| | `--remove-alias` | `<name>` | Delete specified alias |

#### Utility
| Flag | Long Form | Description |
|------|-----------|-------------|
| | `--help` | Show help message |
| | `--version` | Show version |

### Exit Codes

```
0 - Success
1 - No match found (fuzzy or vector search)
2 - Ambiguous match (multiple candidates with equal scores)
3 - File read error
4 - Configuration error (missing vault path, invalid alias)
5 - Mode conflict (mutually exclusive flags used together)
```

---

## Usage Examples

### Basic Queries

#### Simple lookup with default tag
```bash
contex "mental health"
# Output: <mental-health-context>[file content]</mental-health-context>
```

#### Custom tag override
```bash
contex "sales strategy" -t "strategy"
# Output: <strategy>[file content]</strategy>
```

#### Show matched filename
```bash
contex "linkedin professional" -s
# stderr: Matched: LinkedIn Professional Context.md
# stdout: <linkedin-professional-context>[file content]</linkedin-professional-context>
```

### Vector Search

#### Semantic query
```bash
contex -v "stuff about emotional triggers and work avoidance"
# Uses Chroma vector similarity instead of fuzzy matching
# Might match "Mental Health Context.md" even though query doesn't contain those words
```

#### Vector search with source display
```bash
contex -v "burnout and isolation" -s
# stderr: Vector match: Mental Health Context.md (similarity: 0.87)
# stdout: <mental-health-context>[file content]</mental-health-context>
```

### Alias Workflows

#### Create alias (interactive)
```bash
contex "linkedin professional" -m
# Matched: LinkedIn Professional Context.md
# Create alias? (y/n): y
# Alias name [linkedin-professional-context]: linkedin
# Tag name [linkedin]: linkedin
# ✓ Alias created

# Or non-interactive:
contex "linkedin professional" -m "linkedin"
```

#### Use alias
```bash
contex -a "linkedin"
# Output: <linkedin>[file content]</linkedin>
```

#### List all aliases
```bash
contex --list-aliases
# Available aliases:
#   linkedin          → LinkedIn Professional Context.md (used 47 times)
#   mental-health     → Mental Health Context.md (used 23 times)
#   dad-health        → Dad Health Context.md (used 12 times)
```

#### Remove alias
```bash
contex --remove-alias "old-context"
# ✓ Alias 'old-context' removed
```

### Passthrough Mode

#### Tag arbitrary stdin
```bash
cat work_report.txt | contex -p "report"
# Output: <report>[stdin content]</report>
```

#### Chain passthrough with lookup
```bash
cat data.csv | contex -p "product-catalog" | contex -a "linkedin"
# Output: <product-catalog>[csv]</product-catalog><linkedin>[context]</linkedin>
```

### Stream Composition

#### Two contexts
```bash
contex -a "linkedin" | contex "mental health" | twig "Analyze career burnout"
# Combines: <linkedin>...</linkedin><mental-health-context>...</mental-health-context>
```

#### Three contexts with custom tags
```bash
contex -a "linkedin" | \
  contex "mental health" -t "therapy" | \
  contex "work projects" -t "current-work" | \
  twig "Help me prioritize tasks"
```

#### Mixed passthrough and lookup
```bash
cat current_resume.pdf | \
  contex -p "resume" | \
  contex -a "linkedin" | \
  twig "Compare my resume to my LinkedIn profile"
```

### Integration with Twig

#### Basic question with context
```bash
contex -a "mental-health" | twig "What are my trigger patterns?" -a "Focus on work domain"
```

#### Multi-turn conversation
```bash
contex -a "linkedin" | contex -a "mental-health" | twig "Career advice" --chat
# --chat flag preserves conversation history in twig
```

### Integration with Siphon

#### Siphon output → contex tagging → LLM
```bash
siphon sales_presentation.pptx -r c | \
  contex -p "sales-deck" | \
  contex "sales strategy for FY26" -t "strategy" | \
  contex -a "linkedin" | \
  twig "Look at my job, our strategy, and our pitch deck" \
       -a "Critique the deck and suggest additional collateral"
```

**Explanation:**
1. `siphon sales_presentation.pptx -r c`: Converts PowerPoint to text using MarkItDown
2. `contex -p "sales-deck"`: Tags Siphon output as `<sales-deck>`
3. `contex "sales strategy for FY26" -t "strategy"`: Adds `<strategy>` from Obsidian
4. `contex -a "linkedin"`: Adds `<linkedin>` context
5. `twig`: Sends composed context to LLM

#### Audio transcription with context
```bash
siphon meeting_recording.m4a -r c | \
  contex -p "meeting-transcript" | \
  contex -a "work-projects" | \
  twig "Summarize action items and assign to projects"
```

---

## Configuration

### Environment Variables

```bash
# Required: Obsidian vault location
export OBSIDIAN_VAULT="$HOME/Documents/Obsidian"

# Optional: Specific directory within vault for context artifacts
export CONTEX_CONTEXT_DIR="$OBSIDIAN_VAULT/context-artifacts"
# Defaults to searching entire vault if not set

# Optional: Chroma server connection (for vector search)
# If your Chroma library requires custom config, set here
export CHROMA_HOST="localhost"
export CHROMA_PORT="8000"
```

### Alias File

**Location:** `~/.config/contex/aliases.json`

**Structure:**
```json
{
  "alias-name": {
    "file": "Exact Filename.md",
    "tag": "xml-tag-name",
    "description": "Human-readable description",
    "last_used": "ISO8601 timestamp",
    "use_count": 0
  }
}
```

**Auto-generated fields:**
- `last_used`: Updated every time alias is used
- `use_count`: Incremented on each use

### Fuzzy Match Configuration

**Default confidence threshold:** 60 (0-100 scale)

**Ambiguous match handling:** If multiple files score within 5 points of top result, treat as ambiguous.

**Example ambiguous scenario:**
```bash
contex "health"
# Error: Ambiguous match. Did you mean:
#   1. Mental Health Context.md (score: 85)
#   2. Dad Health Context.md (score: 85)
# Use -v for vector search, be more specific, or create an alias with -m
```

### Vector Search Configuration

**Backend:** Chroma server (imports existing connection library)

**Search scope:**
- **v0.1:** Title-only embeddings (fast, covers most use cases)
- **v0.2+:** Full-content embeddings (semantic search within notes)

**Similarity threshold:** 0.70 (cosine similarity, 0-1 scale)

---

## Implementation Details

### Project Structure

```
contex/
├── contex/
│   ├── __init__.py
│   ├── cli.py              # Argument parsing, main entry point
│   ├── query.py            # Fuzzy matching and vector search
│   ├── obsidian.py         # Vault interaction, file reading
│   ├── aliases.py          # Alias management (CRUD)
│   ├── tags.py             # XML tag generation and wrapping
│   ├── stream.py           # Stdin/stdout composition logic
│   └── chroma_client.py    # Import wrapper for your Chroma library
├── tests/
├── setup.py
└── README.md
```

### Core Logic Flow

#### Lookup Mode
```python
1. Parse arguments (query, flags)
2. If -a flag: Load alias from JSON, skip to step 5
3. If -v flag: Vector search via Chroma
   Else: Fuzzy match via RapidFuzz
4. Validate match confidence (error if below threshold or ambiguous)
5. Read file from Obsidian vault
6. Generate XML tag (from -t flag, alias, or filename)
7. Read stdin if present
8. Output: stdin_content + <tag>file_content</tag>
```

#### Passthrough Mode
```python
1. Parse arguments (must have -p flag with tag name)
2. Read stdin (error if empty? No—allow empty tags)
3. Output: <tag>stdin_content</tag>
```

### Tag Generation Algorithm

```python
def generate_tag(filename: str, override: Optional[str] = None) -> str:
    if override:
        return override
    
    # Strip extension
    stem = filename.replace(".md", "")
    
    # Lowercase and replace spaces/underscores with hyphens
    tag = stem.lower().replace(" ", "-").replace("_", "-")
    
    # Optional: Strip "context" suffix
    if tag.endswith("-context"):
        tag = tag[:-8]
    
    return tag
```

**Examples:**
```
"LinkedIn Professional Context.md" → "linkedin-professional-context" → "linkedin-professional"
"Sales Strategy FY26.md"           → "sales-strategy-fy26"
"Dad Health Context.md"            → "dad-health-context" → "dad-health"
```

### Fuzzy Matching (RapidFuzz)

```python
from rapidfuzz import process, fuzz

def fuzzy_match(query: str, files: List[Path], threshold: int = 60) -> Optional[Path]:
    file_stems = [f.stem for f in files]
    result = process.extractOne(query, file_stems, scorer=fuzz.WRatio)
    
    if not result or result[1] < threshold:
        return None
    
    # Check for ambiguous matches (within 5 points of top score)
    all_results = process.extract(query, file_stems, scorer=fuzz.WRatio, limit=5)
    ambiguous = [r for r in all_results if abs(r[1] - result[1]) < 5]
    
    if len(ambiguous) > 1:
        raise AmbiguousMatchError(ambiguous)
    
    return next(f for f in files if f.stem == result[0])
```

### Vector Search (Chroma)

```python
from your_chroma_library import ChromaClient  # Your existing library

def vector_search(query: str, threshold: float = 0.70) -> Optional[Path]:
    client = ChromaClient()  # Uses your existing connection logic
    
    # v0.1: Search title embeddings only
    results = client.query(
        collection_name="obsidian_titles",
        query_texts=[query],
        n_results=5
    )
    
    if not results or results['distances'][0][0] > threshold:
        return None
    
    # Return path to matched file
    matched_filename = results['metadatas'][0][0]['filename']
    return Path(OBSIDIAN_VAULT) / matched_filename
```

**Vector index creation** (separate initialization script):
```python
# scripts/index_vault.py
from your_chroma_library import ChromaClient
from pathlib import Path

def index_obsidian_vault(vault_path: Path):
    client = ChromaClient()
    collection = client.get_or_create_collection("obsidian_titles")
    
    for md_file in vault_path.rglob("*.md"):
        collection.add(
            documents=[md_file.stem],  # v0.1: Title only
            metadatas=[{"filename": md_file.name, "path": str(md_file)}],
            ids=[str(md_file)]
        )
```

Run this manually or via cron to keep index updated.

### Stdin Handling

```python
import sys

def read_stdin() -> str:
    """Read from stdin if available, return empty string otherwise."""
    if sys.stdin.isatty():
        return ""  # No piped input
    return sys.stdin.read()
```

### Alias Management

```python
import json
from pathlib import Path
from datetime import datetime

ALIAS_FILE = Path.home() / ".config" / "contex" / "aliases.json"

def load_aliases() -> dict:
    if not ALIAS_FILE.exists():
        return {}
    return json.loads(ALIAS_FILE.read_text())

def save_aliases(aliases: dict):
    ALIAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    ALIAS_FILE.write_text(json.dumps(aliases, indent=2))

def create_alias(name: str, file: str, tag: str, description: str = ""):
    aliases = load_aliases()
    aliases[name] = {
        "file": file,
        "tag": tag,
        "description": description,
        "last_used": datetime.now().isoformat(),
        "use_count": 0
    }
    save_aliases(aliases)

def use_alias(name: str) -> dict:
    aliases = load_aliases()
    if name not in aliases:
        raise ValueError(f"Alias '{name}' not found")
    
    alias = aliases[name]
    alias["last_used"] = datetime.now().isoformat()
    alias["use_count"] += 1
    save_aliases(aliases)
    
    return alias
```

### Error Messages

#### No match found
```
Error: No match found for query 'xyz'

Try:
  - Use -v flag for vector similarity search
  - Check spelling or try a more specific query
  - Use --list-aliases to see available aliases
  - Run with -s flag to see fuzzy match candidates
```

#### Ambiguous match
```
Error: Ambiguous match for query 'health'

Multiple files matched with similar scores:
  1. Mental Health Context.md (score: 85)
  2. Dad Health Context.md (score: 85)

To resolve:
  - Be more specific: 'mental health' or 'dad health'
  - Use vector search: contex -v 'health'
  - Create an alias: contex 'mental health' -m 'mental-health'
```

#### File not found (alias pointing to deleted file)
```
Error: File not found: 'LinkedIn Professional Context.md'

Alias 'linkedin' points to a file that no longer exists.
Remove outdated alias: contex --remove-alias linkedin
```

#### Mode conflict
```
Error: Cannot use -a (alias) and -p (passthrough) together

Usage:
  contex [QUERY] [OPTIONS]       # Lookup mode
  contex -a <ALIAS> [OPTIONS]    # Alias mode
  contex -p <TAG> [OPTIONS]      # Passthrough mode
```

### Deduplication (v0.2 feature)

Track content hashes in the stream to avoid duplicate context:

```python
import hashlib

def compose_stream(stdin_content: str, new_content: str, tag: str, 
                   seen_hashes: set) -> tuple[str, set]:
    """
    Compose stream with deduplication.
    Returns: (output_string, updated_seen_hashes)
    """
    content_hash = hashlib.sha256(new_content.encode()).hexdigest()
    
    if content_hash in seen_hashes:
        print(f"Warning: Duplicate content for tag '{tag}' (skipping)", 
              file=sys.stderr)
        return stdin_content, seen_hashes
    
    seen_hashes.add(content_hash)
    output = stdin_content + f"<{tag}>\n{new_content}\n</{tag}>\n"
    return output, seen_hashes
```

**Usage in chained calls:**
```bash
contex -a "linkedin" | contex "LinkedIn Professional Context.md" | twig "..."
# stderr: Warning: Duplicate content for tag 'linkedin-professional-context' (skipping)
```

### Performance Considerations

**File reading:** Direct file I/O is sufficient (no caching needed)
- Typical context artifact: 5-50KB
- Read time: <10ms on SSD
- Premature optimization to cache

**Fuzzy matching:** RapidFuzz is fast enough for hundreds of files
- 500 files: ~5ms
- 5000 files: ~50ms
- Only becomes bottleneck at 10k+ files

**Vector search:** Depends on Chroma server performance
- Typically <100ms for small collections
- Add `--verbose` timing info in future version

---

## Relationship to Twig and Siphon

### Twig: The LLM Query Interface

**What Twig does:**
- Sends queries to LLMs (OpenAI, Anthropic, local models)
- Manages conversation history
- Handles image input from clipboard
- Provides chat mode for multi-turn conversations

**How contex complements Twig:**

`contex` injects **persistent knowledge artifacts** into Twig queries:

```bash
# Without contex: Manual context pasting
twig "I'm feeling burned out at work. Here's my background: [paste 300 lines]"

# With contex: Automatic context injection
contex -a "linkedin" | contex -a "mental-health" | twig "I'm feeling burned out at work"
```

**Division of labor:**
- **contex**: Context retrieval and composition
- **Twig**: LLM interaction and response handling

### Siphon: The Universal Ingestion Engine

**What Siphon does:**
- Ingests 11+ source types (PDFs, audio, video, GitHub repos, etc.)
- Caches processed content in PostgreSQL
- Generates AI-enriched metadata (titles, summaries, descriptions)
- Provides "Sourdough" auto-maintained knowledge bases (future)

**How contex relates to Siphon:**

#### Current State (v0.1)
`contex` and Siphon are **complementary tools** that compose via pipes:

```bash
# Siphon processes complex sources
siphon presentation.pptx -r c | \
  contex -p "deck" | \           # contex tags Siphon output
  contex -a "strategy" | \       # contex adds Obsidian context
  twig "Critique this deck"
```

**Division of labor:**
- **Siphon**: Complex ingestion (audio transcription, PDF parsing, YouTube download)
- **contex**: Simple ingestion (markdown files you already maintain)

#### Future Integration (v0.3+)

`contex` becomes **Siphon's CLI interface for personal knowledge artifacts:**

```bash
# v0.3: Siphon backend option
contex -v "burnout patterns" --backend siphon
# Uses Siphon's PostgreSQL cache instead of direct Obsidian access

# v0.4: Automatic Siphon fallback
contex "that podcast about AI agents"
# Searches Obsidian first, falls back to Siphon cache if not found
```

**Benefits of integration:**
- Single vector index for both Obsidian and Siphon content
- Unified caching layer (Obsidian files cached in Siphon's PostgreSQL)
- Cross-source semantic search ("find anything about AI strategy")
- Automatic alias creation from frequently used Siphon sources

#### The "Sourdough" Vision

Both `contex` and Siphon are building toward **auto-maintained knowledge bases:**

**contex contribution:**
- Tracks which contexts are used together (co-occurrence patterns)
- Records usage frequency and recency
- Identifies stale contexts (not updated in 30+ days)

**Siphon contribution:**
- Continuously ingests new sources (emails, Slack, meetings)
- AI-powered summarization and entity extraction
- Intelligent pruning (removes outdated info, retains evergreen insights)

**Combined "Sourdough" workflow (future):**
```bash
# Initialize a living knowledge base
contex --sourdough create "ai-strategy" \
  --sources "Obsidian:AI Strategy/*.md" \
            "Siphon:tag=competitors" \
            "Siphon:source_type=earnings_call"

# Auto-maintains based on usage patterns
contex --sourdough feed "ai-strategy"
# Ingests new content, updates summaries, prunes outdated info

# Use as regular context
contex -a "ai-strategy" | twig "What's our competitive position?"
```

### Tool Comparison Matrix

| Feature | contex | Twig | Siphon |
|---------|--------|------|--------|
| **Purpose** | Context injection | LLM querying | Universal ingestion |
| **Input sources** | Obsidian markdown | stdin, clipboard | 11+ types (PDF, audio, video, etc.) |
| **Output** | XML-tagged text | LLM responses | Cached ProcessedContent objects |
| **Search** | Fuzzy + vector (titles) | N/A | Vector (full content) |
| **Caching** | None (reads from Obsidian) | Conversation history | PostgreSQL + SQLite fallback |
| **Composition** | Pipes (stdin/stdout) | Pipes (receives stdin) | Pipes + Python API + FastAPI server |
| **Processing** | Minimal (read + wrap) | API calls to LLMs | Heavy (transcription, parsing, enrichment) |
| **Maintenance** | Manual (you edit markdown) | N/A | Auto-curation (future) |

### Recommended Workflows

#### Simple context + query
```bash
contex -a "linkedin" | twig "Summarize my experience"
```

#### Multi-context reasoning
```bash
contex -a "linkedin" | contex -a "mental-health" | \
  twig "How can I avoid burnout in my current role?"
```

#### External file + context
```bash
cat job_description.txt | contex -p "job-posting" | contex -a "linkedin" | \
  twig "Should I apply for this role?"
```

#### Siphon + contex + Twig pipeline
```bash
siphon competitor_earnings.mp3 -r c | \
  contex -p "earnings-transcript" | \
  contex -a "our-strategy" | \
  twig "Compare their strategy to ours"
```

#### Research synthesis across sources
```bash
# Use Siphon's research CLI for multi-document analysis
research_cli.py "competitive positioning" --dir ./intel/

# Then use contex to inject results into ongoing conversation
siphon research_results.json -r c | \
  contex -p "research-findings" | \
  twig "Based on this research, recommend next steps" --chat
```

---

## Roadmap

### v0.1: MVP (Ship This Weekend)
**Goal:** Make Obsidian context injection frictionless

**Features:**
- [x] Fuzzy matching with RapidFuzz
- [x] XML tag wrapping with kebab-case convention
- [x] Stdin passthrough and composition
- [x] Alias management (create, list, use, remove)
- [x] `-s` flag for match feedback
- [x] Basic error handling (no match, ambiguous match, file not found)

**Implementation:**
- Single Python package, `pip install -e .`
- Command-line entry point: `contex`
- Configuration via environment variables
- Aliases stored in `~/.config/contex/aliases.json`

**Testing priorities:**
- Fuzzy matching accuracy on real vault
- Stream composition with multiple pipes
- Alias CRUD operations
- Error messages are helpful

**What's NOT in v0.1:**
- Vector search (v0.2)
- Deduplication (v0.2)
- Usage analytics dashboard (v0.3)
- Siphon integration (v0.3)

### v0.2: Vector Search & Intelligence (2 Weeks After v0.1)
**Goal:** Enable semantic discovery and track usage patterns

**Features:**
- [ ] Vector similarity search via Chroma (`-v` flag)
- [ ] Index creation script for Obsidian titles
- [ ] Deduplication by content hash
- [ ] Usage statistics in alias file (last_used, use_count)
- [ ] `--stats` flag to show most-used contexts
- [ ] Improved error messages with suggestions

**Implementation:**
- Import your existing Chroma library for vector search
- Background script to maintain vector index: `contex-index-vault`
- Add deduplication logic to stream composition
- Track usage patterns in aliases.json

**Testing priorities:**
- Vector search accuracy vs. fuzzy matching
- Index freshness (how to handle new/updated files)
- Performance with 1000+ files in vault
