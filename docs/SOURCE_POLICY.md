# Source and evidence policy

## Evidence hierarchy

Keep the following layers separate and preserve upstream files:

1. Supplied source artifacts, including PDFs and chart images.
2. Faithful source transcriptions with source ID and page or image location.
3. Normalized records that retain the original wording.
4. Independently researched botanical claims with claim-level citations.
5. Locally reviewed horticultural recommendations.
6. Edited reader-facing manuscript.
7. Illustrated assets with creator, license, review, and approval records.
8. Reproducibly generated publications and quality reports.

Never write editorial interpretations back into an original source file or replace source
wording with a normalized value. Generated records must retain their source ID, source path,
page or section where available, and a clear evidence type.

## Current source register

| Source ID | Repository path | Evidence and limits |
|---|---|---|
| `ERRINGTON-CALENDAR-PDF` | `Errington BC Zone 8a Planting Calendar.pdf` | Locally supplied 89-page calendar PDF. PDF metadata has no named author and a creation date of 2026-06-28. The source history and independence of this artifact are not established. |
| `ERRINGTON-CHART-IMAGES` | `Planting Calander-Crops.png`; `Planting Calander-Ornamentals.png` | Chart images visibly labeled Zone 8b. Their text and marks can be transcribed, but visual chart positions and color bands have not been independently reviewed plant by plant. |
| `CALENDAR-TRANSCRIPTION` | `ERRINGTON_CALENDAR_FULL_TEXT.md`; `errington_calendar_entries.csv` | Text transcription attributed to the supplied calendar PDF. It is not independent corroboration of that PDF. |
| `PROJECT-HANDOFF` | `ERRINGTON_ENCYCLOPEDIA_HANDOFF.md` | Project-scope and common-name inventory. Not a botanical authority. |
| `GENERAL-GARDENING-REFERENCE` | `Vegetable_Gardening_Encyclopedia_With_Sp.pdf` | Supplied general reference. Not Errington timing authority; copyright and reuse limits apply. |
| `USDA-HARDINESS-MAP` | <https://planthardiness.ars.usda.gov/> | Official U.S. hardiness-zone map; reference for the USDA system, not a local frost-date source. Accessed 2026-11-22. |
| `NRCan-HARDINESS-SITE` | <https://planthardiness.gc.ca/index.php?lang=en&m=17> | Natural Resources Canada explanation of Canadian and USDA hardiness-zone systems; the Canadian system uses multiple climate variables. Accessed 2026-11-22. |

Other sources mentioned in old project notes (including the Eastern Vancouver Island
pollinator guide and web references) are not checked into this repository. Do not treat
their statements as independently reverified here. Add a source artifact or a durable URL,
author/organization, publication date, access date, page/section, and the supported claim
before relying on them in a published profile.

## Climate and calendar policy

The supplied calendar PDF says Zone 8a; both chart images say Zone 8b. Keep both statements
with their source locations until an authoritative source resolves the discrepancy. USDA
hardiness zones describe average annual extreme minimum temperatures and are not Canadian
Plant Hardiness Zones, frost-date statistics, or a prediction for a particular garden.

The calendar's April 15 and October 15 dates are approximate expected frost anchors as
reported by the source. They are not guaranteed last/first frost dates. Do not present
them as observed local climate normals without a named, geographically relevant data source.
Recommendations must account for site exposure, elevation, cold-air drainage, wind, coastal
influence, drainage, and season-extension methods where evidence supports those details.

## Status vocabulary

Verification dimensions are independent. In particular, taxonomy verification never
validates cultivar identity, a profile, local timing, or an illustration. Use
`pending-verification` until the claim is supported by an identified source and an actual
review. Use `requires-resolution` when the name cannot be resolved at the current record
level. `bulk-taxonomy-populated` is historical pipeline metadata only and is not a
verification state.

Source matches, OCR output, generated prose, generated illustration prompts, and a
successful build are not independent verification. Record generated material as generated
and reviewed/approved material separately.
