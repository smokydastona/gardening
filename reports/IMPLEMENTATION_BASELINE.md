# Errington Gardening Encyclopedia — Implementation Baseline

**Baseline date:** 2026-11-22
**Repository revision at baseline:** `a634118`
**Baseline release state:** **NOT READY**

## Repository structure

The repository contains source PDFs and chart images, generated Markdown and CSV records,
Python build and validation scripts, a 101-page working PDF, reportlab fonts, pytest tests,
GitHub Actions workflows, botanical evidence templates, and an illustration review system.

## Existing deliverables

| Deliverable | Actual state |
|---|---|
| `Errington_Gardening_Encyclopedia.pdf` | 101-page working/pre-review build |
| `ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md` | Editorial manuscript |
| `ERRINGTON_MONTHLY_REFERENCE.md` | Month-grouped source transcription |
| `ERRINGTON_PLANT_CATALOG.md` | 137 registry records |
| `plant_registry.csv` | Initially lacked stable IDs; now gains `plant_id` |
| `errington_calendar_entries.csv` | 359 source-transcription rows |
| `botanical_evidence/` | 137 unverified templates |
| `plant_illustrations/` | 0 approved images; pending workflow only |

## Record and verification counts

| Measure | Count |
|---|---:|
| Plant records | 137 |
| Calendar entries | 359 |
| Calendar months | 12 |
| Approved illustrations | 0 |
| Verified taxonomy records | 0 |
| Individually reviewed profiles | 0 |
| Claim-level source records | 2 for Arugula identity; all other claims remain unreconciled |

No duplicate stable IDs or duplicate plant display names were present at baseline.
No duplicate calendar entry keys were present.

## Build and test baseline

The repository initially used two main workflows and 37 pytest tests. The baseline
`validate_pipeline.py` and test suite passed using `.venv/bin/python` with the pinned
dependencies. It was not sufficient to establish botanical, horticultural, or publication
correctness.

Initial discrepancies:

1. The README and reports described a working/publication system, but botanical and local
   evidence remained unverified.
2. The build generated only the complete encyclopedia PDF.
3. Stable plant IDs were generated mechanically and did not exist as a first-class registry field.
4. Claim-level evidence and an explicit climate evidence model were absent.
5. The illustration branch assets were not deterministic build dependencies.
6. The 8a/8b zone conflict and April 15/October 15 frost anchors were not independently resolved.
7. No automated release decision separated software, data, botanical, climate, calendar,
   illustration, layout, build, and CI states.

## Critical unresolved evidence

- 137 plant identities and profiles lack independent claim-level review.
- 359 calendar rows remain source transcriptions, not verified recommendations.
- 8a and 8b refer to source/chart statements that require local evidence resolution.
- Frost dates and 183-day frost-free period were not independently established.
- 70 separate-branch images lack verified subject, license, attribution, and review history.
- Human visual sign-off for every PDF page is still external.
