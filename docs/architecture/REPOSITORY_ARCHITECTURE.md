# Repository architecture and migration

## Current authoritative state

`main` is the canonical implementation branch. The current restructuring work is being
developed on `copilot/repository-restructure`; it is intended for review through a pull
request, not a direct write to `main`.

The immutable source layer remains at the repository root for now because checksums,
transcriptions, scripts, tests, and publication builders currently refer to those paths.
Do not move or rename a source artifact until its checksums, consumers, and provenance
references are migrated together.

| Existing location | Ownership | Intended destination |
|---|---|---|
| Root calendar PDF, chart images, source transcription | Original evidence / faithful transcription | `sources/original/` and `data/raw/` |
| Root plant and calendar CSV/JSON records | Authoritative source registries and derived records | `data/registries/`, `data/raw/`, `data/processed/` |
| Root `ERRINGTON_*` manuscript and guide files | Editorial source content | `content/encyclopedia/` and `content/monthly-guides/` |
| Root `plant_illustrations/`, `educational_figures/` | Candidate, review, and manifest records; publication is gated | `assets/botanical/` and `assets/educational-figures/` |
| Root publication PDFs | Generated, reproducible deliverables | `outputs/` or GitHub build artifacts |
| Root Python build/validation scripts | Existing pipeline implementations and compatibility commands | `src/gardening/` modules and `scripts/` |
| `tests/unit/`, `tests/integration/` | Unit and integration tests | Remain separated by test scope |
| `docs/`, root reports, and project audit records | Technical and historical documentation | `docs/` subdirectories |
| `.github/workflows/` | CI and automation definitions | Remains under `.github/workflows/` |

This table is a staged migration map, not a claim that those moves have already occurred.
`reports/REPOSITORY_MIGRATION_MANIFEST.csv` records the baseline paths, branch presence,
content identity, proposed destinations, and preservation decisions. The inventory includes
Git blob IDs and SHA-256 checksums for every file in each available ref.

## Data and evidence boundaries

The supplied calendar PDF and chart images, `plant_registry.csv`, and
`errington_calendar_entries.csv` remain protected source inputs. Derived registers,
claim-level research, editorial advice, and generated illustrations must remain separate
from those originals. A field being populated does not make it verified. An illustration is
publication-eligible only when the existing hash-bound approval gate accepts it.

`main` retains 137 plant records and 359 calendar entries. The source calendar's 8a/8b
disagreement is unresolved. Neither the old illustration branch nor a successful software
build can establish botanical accuracy, image rights, or independent approval.

## Python package and compatibility boundary

`src/gardening/` is the package entry point. Its `gardening` CLI currently provides a
unified interface over the tested legacy pipeline scripts. Stable plant registry validation,
source and publication validation, calendar parsing and OCR, registry normalization,
illustration eligibility, manuscript assembly, publication PDF builders, and project
reports are package modules. Root scripts for migrated modules are compatibility wrappers;
the full build orchestrator, release-status generator, research-link tools, PDF page-image
QA renderer, and illustration generation workflow remain to be migrated.

The CLI must fail with a non-zero status when a delegated command fails. It invokes
subprocesses without a shell. Review and audit commands report pending records but never
promote candidates to approved status.

## Branch and storage decision

`illustration-assets` is retained as historical source material, not merged wholesale. Its
latest reviewed tree contains 70 plant-image candidates (68 unique byte sequences), among
other files. The prior per-image review identifies duplicate filenames, unresolved plant
identity, and cross-plant labels. These images remain unapproved and are not copied into
the publication asset directory. Their branch, commit, image hashes, and review outcomes
are recorded in the migration manifest and `reports/ILLUSTRATION_BRANCH_REVIEW.csv`.

The old branch contains approximately 249 MB of image files, including its three cover and
calendar images. Importing all candidate bytes into `main` would enlarge ordinary clones
without making the images publishable. The source branch is preserved until a future asset
review and storage decision; selected assets can be imported as candidates after identity,
license, and size review. No force-push, branch deletion, or tag deletion is part of this
migration.

## Reproducible development commands

Install the project in editable mode with its supported Python 3.12 environment, then use
`gardening --help`. The existing canonical full build remains `gardening build all`;
`python build_all.py` remains available during the compatibility period.

## Migration completion policy

Moves are complete only when their checksums and provenance are preserved, all import and
build references work, tests pass from the new layout, and CI uses the new entry points.
The inventory is generated from Git refs and intentionally excludes ignored local
environments and temporary build output. Human decisions are required for botanical
identity, rights, asset approval, and publication sign-off.
