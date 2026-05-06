PRD: Safe Cleaner Lab
1. Project Goal

Build a small but realistic Python CLI project named safe-cleaner-lab.

The project simulates a local cleanup assistant with four subsystems:

scan
cleanup execution
duplicate review
staging maintenance

The project must be fully runnable and testable. It should intentionally include realistic design inconsistencies in failure reporting and telemetry, but it must not contain syntax errors, broken imports, failing tests, or intentionally unusable code.

The purpose is to create a realistic codebase for codebase deep-research evaluation. The code should be understandable but not overly simplified.

2. Non-goals

Do not build a real destructive disk cleaner.

Do not delete files outside the project’s controlled demo workspace.

Do not use external services, cloud APIs, databases, or network requests.

Do not add intentionally broken code.

Do not make the inconsistencies obvious in filenames like buggy.py or wrong.py.

Do not make README explicitly reveal every hidden inconsistency. README should be partial, like a real project.

3. Tech Stack

Use:

Python 3.10+
standard library
pytest

No runtime dependencies beyond the Python standard library.

Dev dependency:

pytest

Use either pyproject.toml or requirements-dev.txt.

Recommended:

pyproject.toml
src/safecleaner/
tests/
4. Required Repository Structure

Create this structure:

safe-cleaner-lab/
  README.md
  pyproject.toml
  src/
    safecleaner/
      __init__.py
      __main__.py
      app.py
      models.py
      scanner.py
      cleanup.py
      duplicate_review.py
      staging.py
      telemetry.py
      reports.py
      diagnostics.py
      legacy.py
  tests/
    test_cleanup.py
    test_duplicate_review.py
    test_diagnostics.py
    test_staging.py

Optional:

  examples/
    sample_tree/

But tests should generate temp directories dynamically, not depend on committed binary fixtures.

5. Domain Model

Use dataclasses in models.py.

Required models:

CleanupMode
FailureKind
Visibility
ScanError
CleanupTarget
CleanupResultItem
CleanupReport
TelemetryEvent
DuplicateGroup
MaintenanceResult
DiagnosticSnapshot

Required enums:

CleanupMode:
  RECYCLE
  FAST
  PERMANENT

FailureKind:
  MISSING
  PERMISSION
  IO
  UNSUPPORTED
  VERIFY_FAILED
  HASH_FALLBACK
  FINALIZE
  UNKNOWN

Visibility:
  USER_VISIBLE
  REPORT_ONLY
  TELEMETRY_ONLY
  IGNORED

Important: not every subsystem should use these enums consistently. Cleanup should use them well. Duplicate review and maintenance should be intentionally less consistent, but still functional.

6. CLI Requirements

python -m safecleaner --help should work.

Commands:

python -m safecleaner demo
python -m safecleaner scan <path>
python -m safecleaner cleanup <path> --mode recycle|fast|permanent
python -m safecleaner duplicates <path>
python -m safecleaner maintenance <path>
python -m safecleaner report

Behavior:

demo

Creates a temporary demo workspace with:

cache/
downloads/
logs/
duplicates/
staging/

Runs:

scan
cleanup fast on cache item
duplicate review
maintenance purge
diagnostic report

Prints a readable summary.

scan

Walks a directory and classifies errors as user/system/transient. Store errors in a session-level scan result.

cleanup

Supports three modes:

recycle
fast
permanent

No real OS recycle bin integration is needed. Simulate recycle by moving files into .trash/.

Fast cleanup should stage files into .staging/ first, mark foreground result as success, then run background purge simulation synchronously for tests but through a separate function that records telemetry only.

Permanent cleanup deletes directly.

duplicates

Finds duplicate candidates by file size and hash.

Important intended inconsistency:

If hashing a file fails, silently fallback to hashing the path string and record no user-visible error. Optionally record no telemetry for this fallback, or record only a coarse counter. This mirrors a real-world observability gap.

maintenance

Purges .staging/.

Important intended inconsistency:

Maintenance should return only (message, success) style feedback to the CLI/UI layer, not structured FailureKind.

If individual staged file purge fails, maintenance may continue and only report a coarse summary.

report

Prints a diagnostic snapshot:

scan error count
cleanup attempted/failed count
telemetry event count
last action audit entries
duplicate groups count
maintenance feedback
7. Required Subsystem Behavior
7.1 Scan

File: scanner.py

Responsibilities:

Walk a directory.
Build a list of files.
Record scan errors.
Classify scan errors into:
user
transient
system

Example behavior:

def classify_scan_error(exc: OSError) -> str:
    if isinstance(exc, PermissionError):
        return "user"
    if isinstance(exc, FileNotFoundError):
        return "transient"
    return "system"

Scan errors should be:

stored in ScanError list
counted in telemetry
visible in diagnostics as a count
optionally visible as details through report

This subsystem should be relatively well-structured.

7.2 Cleanup Execution

File: cleanup.py

Responsibilities:

Build a cleanup plan.
Validate targets.
Execute cleanup by mode.
Return CleanupReport with per-item CleanupResultItem.
Record telemetry audit entries.

Mode behavior:

recycle

Move target into .trash/.

If move fails:

CleanupResultItem.success = False
failure_kind = FailureKind.IO or FailureKind.PERMISSION
visibility = USER_VISIBLE
telemetry audit entry recorded
permanent

Delete file or directory.

If delete fails:

structured failure item
user-visible
telemetry audit entry recorded
fast

Stage file into .staging/.

Foreground staging failure:

structured failure
user-visible
telemetry audit entry recorded

Background purge failure after staging:

do not add to CleanupReport
record telemetry audit only
leave a TODO comment noting the missing user-visible path

This is an intentional realistic inconsistency.

Important: tests should pass. The inconsistency is semantic, not test failure.

7.3 Duplicate Review

File: duplicate_review.py

Responsibilities:

Find duplicate groups by size and content hash.
Recommend one file to keep.
Return DuplicateGroup list.

Intentional inconsistency:

If file hashing fails:

try:
    return hash_file(path)
except OSError:
    return hash_path_string(path)

This means the duplicate review remains functional, but failures are silently degraded and not surfaced through ScanError, CleanupReport, or diagnostic details.

Add a TODO comment:

# TODO: wire duplicate hash fallback into telemetry and diagnostics.

Do not make this comment too loud in README.

7.4 Staging Maintenance

File: staging.py

Responsibilities:

Create staging directory.
Stage paths.
Purge staged paths.
Maintenance command clears .staging/.

Intentional inconsistency:

purge_staging_area() should return a MaintenanceResult(message: str, success: bool) but not per-file structured failures.

If one staged item fails, continue processing and return a coarse warning.

No per-item audit by default.

Add TODO:

# TODO: replace coarse maintenance feedback with structured FailureKind records.
7.5 Telemetry

File: telemetry.py

Responsibilities:

Store in-memory counters.
Store last N audit events.
Provide snapshot.

Telemetry should include:

scan_errors
cleanup_attempted
cleanup_failed
action_audit_tail
duplicate_hash_fallbacks optional counter
maintenance_attempts

Important intended inconsistency:

Cleanup should write detailed audit entries.

Staging maintenance should only increment a coarse counter.

Duplicate review should have either no detailed audit or only a fallback counter. Prefer making this partially wired, not fully absent, to feel realistic.

7.6 Diagnostics

File: diagnostics.py

Responsibilities:

Build DiagnosticSnapshot.
Combine scan, cleanup, telemetry, duplicate, maintenance state.

Diagnostics should show:

current scan error count
cleanup attempt/failure counters
last cleanup report summary
duplicate group count
maintenance last feedback
telemetry audit tail

Do not include full duplicate hashing fallback details.

Do not include per-file staging purge failures.

This creates a realistic observability gap.

7.7 Legacy Module

File: legacy.py

Include a small unused legacy function:

def delete_direct_legacy(path: Path) -> bool:
    ...

It should be real code but not used by the main CLI flow.

Purpose: realistic old code residue.

Do not name it unused_trap or anything artificial.

8. README Requirements

README should be partial and realistic.

Include:

- what the project does
- how to run demo
- how to run tests
- safety model
- cleanup modes
- diagnostics overview
- known limitations

README safety model should say:

Safe Cleaner Lab prefers reversible cleanup for normal operations.
Permanent deletion must be explicit.
Cleanup execution reports foreground failures.
Diagnostics expose scan and cleanup health.

Do not explicitly list every intentional inconsistency in README.

Known limitations section may mention:

Some maintenance and duplicate-review diagnostics are still being unified.

Do not say:

This repo is designed to trick AI models.
9. Tests

Add tests that pass.

Required tests:

test_cleanup_recycle_moves_file_to_trash
test_cleanup_permanent_deletes_file
test_cleanup_fast_stages_then_purges
test_cleanup_missing_target_is_reported
test_duplicate_review_finds_duplicates
test_duplicate_hash_fallback_does_not_crash
test_diagnostics_contains_cleanup_counters
test_staging_maintenance_returns_coarse_feedback

Tests should validate functionality but not “fix” the intended inconsistencies.

The test suite must pass with:

python -m pytest
10. Acceptance Criteria

The project is complete when:

python -m pytest
python -m safecleaner --help
python -m safecleaner demo

all work.

Codebase size target:

8–12 source files
8–15 tests
600–1500 lines total

Project should look like a realistic small tool, not a toy script.

The final commit should include all files.
