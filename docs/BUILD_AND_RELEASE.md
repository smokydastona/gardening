# Build and release

## Reproducible build

Create the locked Python environment and run:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python build_all.py
```

`build_all.py` validates source counts, rebuilds calendar and registry outputs, regenerates the
three PDFs, and validates all release PDFs. It fails on source, build, or publication validation
errors.

## Generated deliverables

- `Errington_Gardening_Encyclopedia.pdf`
- `Errington_Monthly_Gardening_Guide.pdf`
- `Errington_Illustrated_Plant_Directory.pdf`

Generated Markdown, CSV, reports, and PDFs are outputs. Source PDFs and chart images, the
plant registry, the calendar transcription, botanical evidence, claims, and release records
remain source or evidence inputs.

## Release gating

The project is release-gated by independent statuses:

- Software implementation
- Data integrity
- Botanical verification
- Horticultural verification
- Local climate verification
- Calendar verification
- Illustration approval
- Publication layout
- Reproducible build
- CI validation

Passing tests or generating PDFs does not change unresolved botanical or climate statuses to
verified.
