# contex: System Design

**A POSIX-compliant CLI tool for injecting Obsidian knowledge artifacts into LLM pipelines**

---

## System Overview

`contex` is a lightweight command-line tool that bridges Obsidian vaults and LLM workflows. It retrieves markdown files through fuzzy matching or semantic search, wraps them in XML tags, and outputs to stdout for composition with other CLI tools.

### Core Design Principles

**Single Responsibility**: Context injection only. No LLM interaction, no complex preprocessing, no caching layer.

**POSIX Composition**: Pure stdin/stdout interface. Chains with pipes. Composes with any tool.

**Local-First**: Reads directly from Obsidian vault. No cloud dependencies for core functionality.

**Orthogonal Features**: Fuzzy matching and vector search are independent. Either works without the other.

---

## System Components

### 1. Obsidian Vault (Source of Truth)

**What it is**: User's existing Obsidian markdown files on local filesystem.

**Relationship to contex**: Read-only data source. `contex` never modifies vault contents.

**No local caching**: Files are small (5-50KB), SSD reads are fast (~30ms for directory scan), caching adds complexity without meaningful performance gain.

### 2. Fuzzy Matching Engine (RapidFuzz)

**Purpose**: Fast, deterministic title matching for interactive queries.

**Scope**: Filename stems only (not full content).

**Performance**: ~100ms for 5000 files (dominated by string matching, not I/O).

**Independence**: Works without any external services. Always available.

### 3. Vector Search System (ChromaDB)

**Purpose**: Semantic similarity search for conceptual queries.

**Architecture**:
- **ChromaDB instance**: Runs locally on laptop, stores embeddings and metadata
- **SiphonServer**: Remote GPU rig (RTX 5090) handling embedding generation
- **Indexing script**: Scheduled job that detects vault changes and updates ChromaDB

**Data flow**:
```
Vault changes → Indexing script → SiphonServer (embed) → ChromaDB (store)
                                      ↓
User query → contex -v → ChromaDB (similarity search) → Results
```

**Update schedule**:
- Daily incremental (2am): Only changed files, ~5-20 files typical
- Weekly full reindex (Sunday 3am): Verify consistency, all files

**Embedding scope**:
- v0.1: Title embeddings only
- v0.2+: Full document content embeddings

**Fallback**: Vector search failure degrades gracefully—user can retry with fuzzy matching.

### 4. Alias System

**Purpose**: Predefined shortcuts for frequently accessed contexts.

**Storage**: `~/.config/contex/aliases.json` (local JSON file)

**Structure**:
```json
{
  "alias-name": {
    "file": "Exact Filename.md",
    "tag": "xml-tag-name",
    "description": "Human-readable description",
    "last_used": "ISO8601 timestamp",
    "use_count": integer
  }
}
```

**Usage tracking**: Automatically records access patterns (frequency, recency) for future analytics and Siphon integration.

### 5. SiphonServer (Remote GPU Service)

**What it is**: Existing FastAPI service running on RTX 5090 machine, shared across multiple projects (Chain, Siphon, contex).

**Role in contex**: Embedding generation endpoint.

**API contract**:
```
POST /embed
Body: ["text1", "text2", ...]
Response: [[0.1, 0.2, ...], [0.3, 0.4, ...]]
```

**Benefits**:
- Offloads compute from laptop
- Batch processing (256+ documents per request)
- Shared infrastructure across projects
- Easy model upgrades (change server config, no client changes)

**Failure mode**: If unavailable, indexing script logs warning and skips update (doesn't crash). Vector search continues using stale index.

---

## Data Flow Patterns

### Basic Query (Fuzzy Matching)
```
User: contex "mental health"
  ↓
Scan vault directory (30ms)
  ↓
RapidFuzz match on filenames (80ms)
  ↓
Read matched file (0.3ms)
  ↓
Generate XML tag (from filename or -t flag)
  ↓
Output: <mental-health-context>file content</mental-health-context>
```

### Vector Search Query
```
User: contex -v "emotional triggers and work avoidance"
  ↓
Query ChromaDB (cosine similarity on embeddings)
  ↓
Retrieve top match (with confidence score)
  ↓
Read file from vault
  ↓
Generate XML tag
  ↓
Output: <matched-file>file content</matched-file>
```

### Stream Composition
```
User: contex -a "linkedin" | contex "mental health" | twig "..."
  ↓
contex (first call):
  - Load "linkedin" alias from JSON
  - Read file from vault
  - Output: <linkedin>content1</linkedin>
  ↓
contex (second call):
  - Read stdin: <linkedin>content1</linkedin>
  - Fuzzy match "mental health"
  - Read matched file
  - Concatenate: stdin + <mental-health-context>content2</mental-health-context>
  - Output combined stream
  ↓
twig receives: <linkedin>content1</linkedin><mental-health-context>content2</mental-health-context>
```

### Passthrough Mode (Tagging Arbitrary Content)
```
User: cat data.csv | contex -p "product-catalog" | twig "..."
  ↓
contex:
  - Read stdin (CSV content)
  - No vault lookup (passthrough mode)
  - Wrap in <product-catalog>stdin</product-catalog>
  - Output to twig
```

### ChromaDB Indexing (Background Process)
```
Cron triggers: contex-index-vault --incremental
  ↓
Detect changes:
  - Compare current vault mtimes to last indexed state
  - Identify: new files, modified files, deleted files
  ↓
If changes found:
  - Read file contents
  - Batch send to SiphonServer (/embed endpoint)
  - Receive embeddings
  - Upsert to ChromaDB (ids=filepaths, embeddings, metadata)
  - Update index metadata file
  ↓
If no changes:
  - Log "no changes" and exit
```

---

## System Integration Points

### With Twig (LLM CLI)
**Relationship**: `contex` provides context, `twig` handles LLM interaction.

**Pattern**: `contex ... | twig "query" -a "additional instructions"`

**Separation**: `contex` never talks to LLMs. `twig` never reads Obsidian directly.

### With Siphon (Content Ingestion)
**Current (v0.1)**: Independent tools that compose via pipes:
```
siphon file.pptx -r c | contex -p "presentation" | twig "..."
```

**Future (v0.3)**: `contex` can query Siphon's cache as alternative backend:
```
contex -v "query" --backend siphon
```
Falls back to Siphon's ProcessedContent cache if not found in Obsidian.

### With SiphonServer (GPU Service)
**Usage**: Only for embedding generation during indexing.

**Interaction**: HTTP POST from indexing script to SiphonServer, response contains embeddings.

**Failure handling**: If server unreachable, indexing script logs warning and exits gracefully. Does not block `contex` CLI usage.

---

## Key Architectural Decisions

### No Local Caching
**Rationale**: Files are small, reads are fast, caching adds staleness risk without meaningful performance benefit. Obsidian vault is source of truth.

**Exception**: ChromaDB maintains embeddings (expensive to regenerate) but not file contents.

### Cold Start on Every CLI Invocation
**Tradeoff**: No persistent daemon means ~100ms startup overhead, but zero deployment complexity (no systemd, no socket management, no lifecycle issues).

**Verdict**: 100ms is imperceptible for interactive use. Daemon would be premature optimization.

### Independent Query Methods
**Design**: Fuzzy matching and vector search are separate code paths with no shared dependencies.

**Benefit**: Fuzzy matching works even if ChromaDB is down. Vector search works even if fuzzy matching is slow.

**User experience**: `-v` flag switches modes cleanly.

### Scheduled Indexing, Not Real-Time
**Rationale**: Filesystem watchers add complexity (daemon management, system-specific APIs, battery drain).

**Solution**: Cron jobs with incremental updates. Handles 99% of cases with simple, predictable behavior.

**Staleness tolerance**: User warned if index >24h old, but search proceeds with stale data (better than blocking).

### XML Tag Generation from Filenames
**Convention**: Lowercase, kebab-case, strip "Context" suffix.

**Override**: `-t` flag or alias definition provides explicit tag name.

**Why XML tags**: Clear document boundaries, LLM-friendly, easy to parse/validate in downstream tools.

### Alias Usage Tracking
**Purpose**: Not for current functionality, but for future Siphon integration.

**Data collected**: Access count, last used timestamp.

**Future use**: Identify high-value contexts for auto-curation, inform "Sourdough" maintenance strategies.

---

## Failure Modes and Degradation

### ChromaDB Unavailable
**Impact**: Vector search (`-v` flag) fails.

**Degradation**: User can retry with fuzzy matching (no `-v` flag). Functionality preserved.

### SiphonServer Unavailable
**Impact**: Cannot update ChromaDB index.

**Degradation**: Vector search continues using stale index. User warned but not blocked.

### Fuzzy Match Ambiguity
**Impact**: Multiple files score equally.

**Handling**: Error message lists candidates, suggests using `-v` for semantic search or creating alias.

### No Match Found
**Impact**: Query returns no results.

**Handling**: Helpful error message suggests alternatives (vector search, check spelling, list aliases).

### Vault Directory Missing
**Impact**: Cannot read any files.

**Handling**: Fatal error with clear message about `$OBSIDIAN_VAULT` configuration.

---

## Performance Characteristics

### Fuzzy Matching
- Directory scan (5000 files): ~30ms
- RapidFuzz matching: ~80ms
- File read: ~0.3ms
- **Total: ~110ms** (acceptable for interactive CLI)

### Vector Search
- ChromaDB query: ~50-100ms
- File read: ~0.3ms
- **Total: ~100ms** (comparable to fuzzy matching)

### Indexing
- Incremental (5-20 files): ~10 seconds (network + GPU embedding)
- Full reindex (5000 files): ~10-15 minutes (batched GPU processing)

### Stream Composition
- Additional overhead per piped `contex` call: ~2ms (stdin read + concatenation)
- Multiple contexts: negligible performance impact

---

## Security and Privacy

### Local-First Data
All file content remains on local machine. ChromaDB stores embeddings (mathematical representations) not raw text.

### SiphonServer Communication
- Sends file text for embedding generation
- User controls which files get indexed
- No automatic cloud upload

### Alias File
Contains file paths and metadata. Stored in user home directory with standard filesystem permissions.

---

## Future Integration Path

### v0.1 → v0.2
Add deduplication, usage analytics, improved error messages. No architectural changes.

### v0.2 → v0.3
`contex` becomes Siphon's CLI interface:
- `--backend siphon` flag queries Siphon's cache
- Unified vector index (Obsidian + Siphon content)
- Automatic source selection (Obsidian first, Siphon fallback)

### v0.3 → "Sourdough"
Auto-maintained knowledge bases:
- Track context co-occurrence patterns
- Suggest context updates based on usage
- Integrate with Siphon's continuous ingestion
- AI-powered curation and pruning

---

## Conclusion

`contex` is a minimal, composable tool that solves one problem well: injecting Obsidian content into LLM workflows. It maintains independence from heavyweight infrastructure while enabling future integration with Siphon. The architecture prioritizes simplicity, reliability, and POSIX composition over feature complexity.
