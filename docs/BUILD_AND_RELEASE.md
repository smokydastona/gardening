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

## Mandatory encyclopedia design gate

Every edition of the encyclopedia must retain the pre-owned-book theme: aged-paper styling
and readable editorial handwritten-style notes and additions distributed throughout the
volume, using multiple distinct handwriting fonts and pen-ink colors. These are designed
editorial notes, not claims that real previous owners wrote them or independent evidence.
Keep source warnings and body text legible; never use the theme to imply a claim was verified.

`validate_pipeline.py --publication` blocks the publication build if the encyclopedia has
too few notes or too few annotated pages (at least one note per ten pages and one annotated
page per twenty pages, with minimums of five notes and three pages), does not spread notes
near both ends, lacks five different note texts, or does not render them at 10 points or
larger in all three embedded handwriting fonts and at least three ink colors. This is a
minimum structural gate, not a judgment of appearance, legibility, or print accessibility.
Before any release, a human must review the complete PDF at print size and confirm the
pre-owned visual theme, varied handwriting and inks, contrast, readability, and absence of
overlaps or clipping. Failed or incomplete automated or human review blocks release; do not
silently disable or weaken this gate in future versions.
