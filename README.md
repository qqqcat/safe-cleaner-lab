# safe-cleaner-lab

safe-cleaner-lab is a small Python command line utility for scanning folders, performing safe cleanup, reviewing duplicates, and running lightweight maintenance.

## Features

- Folder scanning with simple scan error classification.
- Cleanup execution with structured per-item reporting.
- Duplicate review by size + content hash, with resilient fallback hashing.
- Staging maintenance for fast-cleanup workflows.
- In-memory diagnostics and telemetry snapshots.

## Cleanup modes

- `recycle`: moves items into a local `.trash` folder.
- `fast`: stages items in `.staging` and then purges staged content.
- `permanent`: deletes items directly.

## Safety model

Safe Cleaner Lab prefers reversible cleanup for normal operations. Permanent deletion must be explicit. Cleanup execution reports foreground failures. Diagnostics expose scan and cleanup health.

## CLI usage

```bash
python -m safecleaner --help
python -m safecleaner demo
python -m safecleaner scan <path>
python -m safecleaner cleanup <path> --mode recycle|fast|permanent
python -m safecleaner duplicates <path>
python -m safecleaner maintenance <path>
python -m safecleaner report
```

## Demo and tests

Run the built-in demo:

```bash
python -m safecleaner demo
```

Run tests:

```bash
python -m pytest
```

## Known limitations


Diagnostics remain summary-oriented; some duplicate fallback and maintenance detail paths are still being unified.
