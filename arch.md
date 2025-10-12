contex/
├── cli/
│   ├── __init__.py
│   ├── parser.py          # create_parser() only
│   ├── router.py          # route_command() only
│   └── commands/          # One file per command group
│       ├── __init__.py
│       ├── search.py      # handle_search, handle_get, handle_last
│       ├── stow.py        # handle_stow
│       ├── pool.py        # handle_pool_* functions
│       └── alias.py       # handle_alias_* functions
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── search_service.py  # SearchService class
│   ├── pool_service.py    # PoolService class
│   └── alias_service.py   # AliasService class
├── storage/               # Persistence layer
│   ├── __init__.py
│   ├── config.py          # Path constants, file I/O
│   └── models.py          # Pydantic models for JSON schemas
└── query/                 # Existing query logic
    ├── fuzzy.py
    └── similarity.py
