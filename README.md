# Errington Gardening Encyclopedia

A source-led gardening reference for Errington, British Columbia, on Vancouver Island. The
repository preserves a supplied planting calendar, a plant inventory, editorial material,
and a reproducible PDF build. It is a working project and is **not approved for publication**:
botanical profiles, local timing, illustration identities and licenses, and final visual
review are still incomplete.

## Development setup

Python 3.12 is supported. From a clone, install the locked environment and the local command:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps -e .
```

The `gardening` command is the unified entry point for the existing tested pipeline:
`gardening --help`, `gardening validate`, `gardening test`, `gardening illustrations audit`,
`gardening figures validate`, `gardening reports generate`, and `gardening build all`.
Illustration generation remains a separate explicit candidate-generation command and never
approves its output. Calendar ingestion/parsing, registry normalization, authoritative
validation, illustration publication eligibility, manuscript assembly, PDF builders, and
project-report generation now live in package modules; root commands remain compatibility
wrappers. See the
[architecture and migration record](docs/architecture/REPOSITORY_ARCHITECTURE.md).
Existing source paths are intentionally unchanged while the build and provenance references
are migrated.

## Current status

| Area | Status |
|---|---|
| Plant inventory | 137 records preserved; taxonomy/profile verification pending |
| Calendar transcription | 359 entries across all 12 months; grouped rows and action meanings require review |
| Errington zone | Unresolved: calendar PDF says 8a; both chart images say 8b |
| Frost anchors | April 15 and October 15 are approximate source values, not guaranteed dates |
| Core handbook | Expanded foundations on climate risk, microclimates, planning, soil, raised beds, seed starting, watering, and plant-health diagnosis; plant-specific research remains pending |
| Grower's handbook | Working skills chapters, standardized plant-profile template, seasonal worksheets, calculations, and garden logs; external sources still need direct review |
| Illustrations | 0 approved; owner-confirmed 70-image branch set includes exact duplicates and visibly mismatched labels; taxonomic and anatomical review remains pending |
| PDF pipeline | One reproducible build command generates the working encyclopedia, monthly guide, plant directory, and two illustration review registers; only approved plant artwork is embedded |
| Encyclopedia design | Pre-owned-book styling with editorial handwritten-style notes in multiple fonts and ink colors; automated theme gate and human visual review are mandatory |
| Encyclopedia field index | 137 plant records are alphabetized within recorded categories and cross-referenced to verbatim calendar mentions and available claim research; growing profiles, taxonomy, and timing remain unverified |
| Learning aids | 18 practical worked examples and 36 figure concepts are included in the encyclopedia; unreviewed figure artwork is withheld |
| Publication approval | `IN_PROGRESS`; see [publication QA](PUBLICATION_QA_REPORT.md) |

## Key deliverables

- [Working encyclopedia PDF](Errington_Gardening_Encyclopedia.pdf)
- The single encyclopedia volume brings together the gardener-facing handbook, all 12 months of calendar transcriptions, the 137-plant index with calendar source cross-references, available claim research, and practical examples. Technical build files, audit records, raw evidence, and unapproved artwork remain separate so they are not mistaken for gardening advice.
- The current encyclopedia includes its cover image only. All 137 plant concept plates and 36 educational figure concepts are withheld from PDFs until independently reviewed and approved.
- Errington Monthly Gardening Guide PDF
- Errington Illustrated Plant Directory PDF
- [Errington Botanical Illustration Collection PDF](Errington_Botanical_Illustration_Collection.pdf)
- [Errington Educational Figure Collection PDF](Errington_Educational_Figure_Collection.pdf)
- [Plant field index, figure concepts, and worked examples](ERRINGTON_COMPLETE_SUPPLEMENT.md)
- [Editorial manuscript](ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md)
- [Grower's handbook and field reference](ERRINGTON_GROWER_HANDBOOK.md)
- [Monthly source calendar](ERRINGTON_MONTHLY_REFERENCE.md)
- [Plant registry index](ERRINGTON_PLANT_CATALOG.md)
- [Plant verification report](PLANT_VERIFICATION_REPORT.md)
- [Calendar review report](CALENDAR_REVIEW_REPORT.md)
- [Illustration audit](ILLUSTRATION_AUDIT.md)
- [Individual review of all 70 illustrations from the `illustration-assets` branch](reports/ILLUSTRATION_BRANCH_REVIEW.csv)
- [Repository audit](AUDIT_REPORT.md)
- [Publication quality report](PUBLICATION_QA_REPORT.md)
- [Implementation register](reports/IMPLEMENTATION_REGISTER.md)
- [Current generated release status](reports/CURRENT_RELEASE_STATUS.md)
- [125-entry plan to 137-record registry reconciliation](reports/PLANT_SCOPE_RECONCILIATION.csv)
- [Repository restructuring baseline](reports/RESTRUCTURE_AUDIT.md)
- [Git tree inventory](reports/REPOSITORY_INVENTORY.csv) and [migration manifest](reports/REPOSITORY_MIGRATION_MANIFEST.csv)
- [Historical illustration similarity candidates](reports/ILLUSTRATION_SIMILARITY_AUDIT.csv)
- [Source policy](docs/SOURCE_POLICY.md) and [data dictionary](docs/DATA_DICTIONARY.md)
- [Research and verification library](docs/RESEARCH_LIBRARY.md)

The encyclopedia's plant field index preserves recorded names, exact matched calendar
transcriptions, and available claim-level research while retaining verification status.
Grouped calendar rows remain visibly grouped and are not converted into plant-specific
recommendations. Generated candidates remain in the working source assets for review, but
unapproved artwork is not embedded in the encyclopedia. Approved assets remain separate
from candidates, and branch artwork is never embedded until identity, anatomy, rights, and
independent human review are complete.

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
| Root `*.py` entry points | Compatibility wrappers for the package and remaining legacy tools |
| `.github/workflows/build-encyclopedia.yml` | CI validation and publication artifact build |
| `src/gardening/` | Unified CLI, validation, ingestion, normalization, illustration gating, publication, and reporting modules |
| `tests/unit/`, `tests/integration/` | Automated unit and integration test suites |
| `scripts/migration/` | Reproducible branch and file inventory tooling |

## Common commands

```sh
.venv/bin/gardening validate
.venv/bin/gardening test
.venv/bin/gardening reports generate
.venv/bin/gardening build all
```

The source record-count snapshot intentionally checks 137 plant rows and 359 calendar rows.
For an authorized source update, change the data and corresponding snapshot/tests together;
do not bypass this guard to conceal data loss. The chart OCR script is an extraction aid,
not part of the reproducible publication build: OCR output must be reviewed before replacing
the checked-in transcription.

## Typography

The encyclopedia's aged-paper treatment and varied handwritten-style notes are a mandatory
design theme for every edition, not evidence of actual past owners or independent research.
Its notes use **Reenie Beanie**, **Indie Flower**, and **Architects Daughter** in distinct
ink colors; the bundled fonts and their SIL Open Font Licenses are in `fonts/`. Body text
uses Times-Roman for readability. The publication build checks note distribution, embedded
fonts, ink colors, and minimum size, and a human must review the full edition visually
before release. See [build and release](docs/BUILD_AND_RELEASE.md).

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
