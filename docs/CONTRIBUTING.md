# Contributing

Keep source artifacts immutable. Add or correct records in `plant_registry.csv`,
`errington_calendar_entries.csv`, or the appropriate evidence file; do not manually edit
generated PDFs or reports.

Every stable plant ID must derive from `display_name` and remain unique. Claim-level evidence
goes in `claims/CLAIM_SOURCES.csv`. Botanical or horticultural verification must identify a
reviewer and retain the relevant source URL or source artifact.

Run `.venv/bin/python build_all.py` and `.venv/bin/python -m pytest -q` before review.
