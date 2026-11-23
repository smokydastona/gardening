# Errington Gardening Encyclopedia

A source-led gardening reference for Errington, British Columbia, on Vancouver Island. The
repository preserves a supplied planting calendar, a plant inventory, editorial material,
and a reproducible PDF build. It is a working project and is **not approved for publication**:
botanical profiles, local timing, illustration identities and licenses, and final visual
review are still incomplete.

## Current status

| Area | Status |
|---|---|
| Plant inventory | 137 records preserved; taxonomy/profile verification pending |
| Calendar transcription | 359 entries across all 12 months; grouped rows and action meanings require review |
| Errington zone | Unresolved: calendar PDF says 8a; both chart images say 8b |
| Frost anchors | April 15 and October 15 are approximate source values, not guaranteed dates |
| Core handbook | Expanded foundations on climate risk, microclimates, planning, soil, raised beds, seed starting, watering, and plant-health diagnosis; plant-specific research remains pending |
| Illustrations | 0 approved; 70 image files on the separate `illustration-assets` branch passed PNG/dimension checks but contain duplicate content and visibly misattributed labels; identity/license review remains pending |
| PDF pipeline | One reproducible build command generates the working encyclopedia, monthly guide, plant directory, and two illustration review registers; only approved plant artwork is embedded |
| Generated supplement | 137 plant concept plates, 36 educational figure concepts, and 18 worked examples are retained as working assets; all unapproved artwork is withheld from PDFs |
| Publication approval | `IN_PROGRESS`; see [publication QA](PUBLICATION_QA_REPORT.md) |

## Key deliverables

- [Working encyclopedia PDF](Errington_Gardening_Encyclopedia.pdf)
- The current encyclopedia includes its cover image only. All 137 plant concept plates and 36 educational figure concepts are withheld from PDFs until independently reviewed and approved.
- Errington Monthly Gardening Guide PDF
- Errington Illustrated Plant Directory PDF
- [Errington Botanical Illustration Collection PDF](Errington_Botanical_Illustration_Collection.pdf)
- [Errington Educational Figure Collection PDF](Errington_Educational_Figure_Collection.pdf)
- [Complete plant, figure, and worked-example supplement](ERRINGTON_COMPLETE_SUPPLEMENT.md)
- [Editorial manuscript](ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md)
- [Monthly source calendar](ERRINGTON_MONTHLY_REFERENCE.md)
- [Plant registry index](ERRINGTON_PLANT_CATALOG.md)
- [Plant verification report](PLANT_VERIFICATION_REPORT.md)
- [Calendar review report](CALENDAR_REVIEW_REPORT.md)
- [Illustration audit](ILLUSTRATION_AUDIT.md)
- [Repository audit](AUDIT_REPORT.md)
- [Publication quality report](PUBLICATION_QA_REPORT.md)
- [Implementation register](reports/IMPLEMENTATION_REGISTER.md)
- [Source policy](docs/SOURCE_POLICY.md) and [data dictionary](docs/DATA_DICTIONARY.md)
- [Research and verification library](docs/RESEARCH_LIBRARY.md)

The plant directory lists all 137 stable-ID records without displaying unapproved candidate
art. Generated candidates remain in the working source assets for review, but are not
embedded in any PDF. Approved plant assets remain separate from candidates, and branch
artwork is never embedded until identity, anatomy, licensing and human review are complete.

## Repository map

| Path | Purpose |
|---|---|
| `Errington BC Zone 8a Planting Calendar.pdf`, chart PNGs | Supplied local calendar artifacts; source history not established |
| `ERRINGTON_CALENDAR_FULL_TEXT.md`, `errington_calendar_entries.csv/.json` | Source transcription and parsed records |
| `plant_registry.csv` | Retained plant inventory; do not overwrite with generated data |
| `SOURCE_SHA256SUMS.txt` | SHA-256 snapshots for protected source records and supplied calendar assets |
| `plant_registry_enriched.csv` | Derived registry/calendar join |
| `calendar_actions.csv`, `calendar_review.csv` | Source-linked action classification and review queue |
| `plant_verification_register.csv` | Stable IDs, source attribution, and independent verification states |
| `plant_illustrations/` | Illustration manifest and review state; no image is approved |
| `ERRINGTON_*MANUSCRIPT*.md`, `ENCYCLOPEDIA_STRUCTURE.md` | Editorial manuscript and project structure |
| `build_*.py`, `extract_calendar_data.py`, `parse_errington_calendar.py` | Extraction, validation, report, and publication code |
| `test_*.py` | Automated tests |
| `.github/workflows/build-encyclopedia.yml` | CI validation and publication artifact build |

## Install

Python 3.12 is supported. Use an isolated environment:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.lock.txt
```

PowerShell activation: `.venv\Scripts\Activate.ps1`.

## Validate and build

```sh
python build_all.py
python -m pytest
```

The source record-count snapshot intentionally checks 137 plant rows and 359 calendar rows.
For an authorized source update, change the data and corresponding snapshot/tests together;
do not bypass this guard to conceal data loss. The chart OCR script is an extraction aid,
not part of the reproducible publication build: OCR output must be reviewed before replacing
the checked-in transcription.

## Typography

Display headings and generated illustration text use **Reenie Beanie**, from
[Google Fonts](https://fonts.google.com/specimen/Reenie+Beanie). The bundled TTF and
SIL Open Font License are stored in `fonts/`. Publication body text uses Times-Roman for
readability.

## Evidence and accuracy limitations

Original/source files, transcriptions, structured records, editorial interpretation, and
generated outputs are separate layers. A calendar transcription or filename match does not
verify an individual recommendation or illustration. The calendar's 8a/8b label conflict
remains unresolved. The source-reported frost anchors are approximate. Existing bulk-filled
taxonomy and cultural notes are retained as recorded but not treated as verified.

See [source policy](docs/SOURCE_POLICY.md), [data dictionary](docs/DATA_DICTIONARY.md),
[source audit](SOURCE_AUDIT.md), and [verification report](PLANT_VERIFICATION_REPORT.md)
before using any record as gardening advice.

## Illustration policy

Generated prompts are not images, and generated images are not automatically approved.
Approval requires a stable plant ID, correct identity, documented creator and license,
visual review, and reviewer notes. The separate `illustration-assets` branch is not a
runtime build dependency; assets from it must be reviewed and explicitly added to the
manifest before embedding.

See the [botanical illustration workflow](plant_illustrations/README.md) for evidence
requirements, generation, review, and approval. The workflow build uses only checked-in
files; it does not fetch assets from another branch. Approved image files and their JSON
sidecars must be committed with the stable-ID manifest.

## Contributions

Keep source evidence immutable, cite claims at the record level, and update the
corresponding tests and reports when changing data. Do not mark taxonomy, timing, profile,
or illustration status verified without the relevant independent review. Changes to source
record counts require an explicit snapshot update and a documented explanation.
