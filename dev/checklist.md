## Core Search & Retrieval

- [ ] **1. Implement similarity/vector search integration**
```bash
tap "burnout symptoms" --semantic
# Should use ChromaDB embeddings instead of fuzzy matching
```

- [ ] **2. Add passthrough mode for stdin**
```bash
cat resume.txt | tap -p "my-resume"
# Wraps arbitrary text in XML tags
```

- [ ] **3. Fix date range retrieval**
```bash
tap -d "2024-01-01:2024-01-31"
# Currently has validation but incomplete implementation
```

## Alias System

- [ ] **4. Implement complete alias management**
```bash
tap "LinkedIn Professional Context" -m "linkedin"  # create alias
tap -a "linkedin"                                   # use alias
tap --aliases                                       # list all aliases
tap --alias-rm "linkedin"                          # remove alias
```

- [ ] **5. Add alias usage tracking and statistics**
```bash
tap --stats
# Show which aliases are used most, suggest cleanup
```

## Context Composition & Pool

- [ ] **6. Implement the "pool" workspace system**
```bash
tap "mental health" --stow          # add to pool
tap "linkedin" --stow               # add another
tap --pool                          # show current pool
tap --pool-pour                     # output as XML, keep pool
tap --pool-drain                    # output as XML, clear pool
```

- [ ] **7. Add context chaining/composition**
```bash
tap "linkedin" | tap "mental health" | twig "career advice"
# Multiple contexts should combine into single XML output
```

## Search Refinement

- [ ] **8. Add search mode flags**
```bash
tap "exact title match" --exact     # only exact title matches
tap "fuzzy search" --fuzzy          # force fuzzy even if alias exists
```

- [ ] **9. Implement last search caching properly**
```bash
tap "linkedin"              # search
tap -l                      # show last results
tap -g 3                    # get item 3 from last search
```

## Output & Integration

- [ ] **10. Add XML context wrapping**
```bash
tap "linkedin"
# Should output: <context source="LinkedIn Professional Context.md">...</context>
```

- [ ] **11. Implement pipeline integration with "twig"**
```bash
tap "linkedin" | twig "help me write a bio"
# The twig command should accept context and send to AI
```

## Quality of Life

- [ ] **12. Add search result preview/summary**
```bash
tap "mental health" --preview
# Show first few lines of each result before selecting
```

- [ ] **13. Implement smart alias suggestions**
```bash
tap "LinkedIn Professional Context" --suggest-alias
# "Suggested alias: linkedin, prof, work"
```

The most critical missing pieces are: alias system (#4), passthrough mode (#2), and the pool workspace (#6). These form the core workflow described in your README but aren't implemented in the current codebase.

## Wilder ideas

Looking at the constraint of Obsidian notes + metadata only, here are some advanced functionality ideas:

## Temporal Intelligence

**14. Smart date-based context retrieval**
```bash
tap --context-for "2024-03-15"
# Finds notes created/modified around that date for temporal context
tap --recent 7d
# Notes from last 7 days (good for "what was I working on recently?")
```

**15. Time-pattern analysis**
```bash
tap --active-during "mornings"
# Notes you typically edit in morning hours (from file metadata)
tap --writing-bursts
# Identify periods of high note-creation activity
```

## Note Relationship Mining

**16. Wiki-link network traversal**
```bash
tap "project alpha" --connected
# Gets the note + all notes it links to (1-hop network)
tap "burnout" --network 2
# 2-hop network: note + its links + their links
```

**17. Reverse link discovery**
```bash
tap "meeting template" --referenced-by
# Find all notes that link TO this note
tap "john doe" --mentions
# Notes that mention this person/concept
```

**18. Orphan and hub detection**
```bash
tap --orphans
# Notes with no incoming/outgoing wiki-links
tap --hubs
# Notes with many incoming links (knowledge centers)
```

## Content Pattern Analysis

**19. Note similarity clustering**
```bash
tap --similar-to "daily note 2024-01-15"
# Find notes with similar content patterns
tap --content-clusters
# Group notes by content similarity
```

**20. Writing style evolution**
```bash
tap --style-like "early-2024"
# Notes matching your writing style from that period
tap --tone-shift
# Detect when your writing tone changed significantly
```

## Smart Context Assembly

**21. Automatic context building**
```bash
tap --build-context "project review"
# AI analyzes query, finds relevant notes, suggests context bundle
tap --context-recipe "work + health + recent"
# Saved combinations of search patterns
```

**22. Anti-patterns and filters**
```bash
tap "productivity" --exclude-daily-notes
# Search but filter out daily notes
tap "work" --not-after "2024-06-01"
# Temporal exclusion filters
```

## Note Quality & Maintenance

**23. Content gap detection**
```bash
tap --incomplete
# Notes with TODO items, empty sections, or [[broken links]]
tap --stale --older-than 6m
# Notes not modified in 6 months (potential cleanup candidates)
```

**24. Knowledge density analysis**
```bash
tap --dense
# Notes with high information density (lots of links, structured content)
tap --shallow
# Notes that might need more development
```

## Advanced Metadata Usage

**25. File system intelligence**
```bash
tap --folder-pattern "projects/"
# Notes in specific folder hierarchies
tap --size-range "1kb:10kb"
# Notes within certain file size ranges
```

**26. Edit pattern mining**
```bash
tap --frequently-edited
# Notes you return to edit often (high engagement)
tap --creation-burst "last-week"
# Notes created in rapid succession (project starts)
```

## Contextual Intelligence

**27. Seasonal/cyclical patterns**
```bash
tap --seasonal "Q4"
# Notes typically relevant during Q4 (from historical patterns)
tap --anniversary "project-starts"
# Notes created around same time in previous years
```

**28. Collaborative context**
```bash
tap --external-links
# Notes containing URLs (research, references)
tap --action-items
# Notes with TODO patterns, deadlines, action language
```

The key insight: even with just files + metadata, you can extract rich behavioral patterns, content relationships, and temporal intelligence that goes far beyond simple search. The metadata becomes a behavioral fingerprint of how you actually use your knowledge base.
