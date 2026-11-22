# Errington Encyclopedia Source Audit

## Purpose and status

This inventory documents what the repository can and cannot support. See
[`docs/SOURCE_POLICY.md`](docs/SOURCE_POLICY.md) for the evidence hierarchy and
[`AUDIT_REPORT.md`](AUDIT_REPORT.md) for findings and remediation.

## Supplied Errington calendar PDF

File: [`Errington BC Zone 8a Planting Calendar.pdf`](Errington%20BC%20Zone%208a%20Planting%20Calendar.pdf)

The local PDF has 89 pages. Its metadata identifies no named author, contains a generic
title, and reports a 2026-06-28 creation date. The repository does not establish who created
it, whether it is an original source or a generated compilation, or whether the text
transcription was independently checked. The file is preserved as supplied source material;
its provenance remains unresolved.

The supplied PDF, both calendar images, `plant_registry.csv`, the parsed calendar CSV, and
the full-text transcription have SHA-256 snapshots in `SOURCE_SHA256SUMS.txt`. The build
fails if any protected source changes without an explicit checksum-manifest update.

The PDF text identifies Zone 8a and reports approximate April 15 and October 15 frost
anchors, approximately 183 frost-free days, approximately 1,200 mm annual rainfall, and
winter lows rarely below -12 C. These are source-reported claims, not independently
verified local observations or climate normals.

## Supplied crop and ornamental charts

Files: [`Planting Calander-Crops.png`](Planting%20Calander-Crops.png) and
[`Planting Calander-Ornamentals.png`](Planting%20Calander-Ornamentals.png).

Both images visibly identify Errington Zone 8b, conflicting with the PDF's 8a label. They
also show expected frost dates of April 15 and October 15. The crop chart uses red for
indoor sowing, yellow for transplanting, and green/teal for direct sowing or harvest. The
ornamental chart adds flowering and dormant/divide bands. These charts are preserved as
source artifacts, but their small text and cell boundaries have not been independently
transcribed and reviewed for every crop and month.

## Text extraction and normalized calendar

[`ERRINGTON_CALENDAR_FULL_TEXT.md`](ERRINGTON_CALENDAR_FULL_TEXT.md) is a text extraction
attributed to the local PDF. `errington_calendar_entries.csv` and `.json` are parsed
transcriptions. They contain 359 entries across all months. This derived information is not
independent confirmation of the PDF. Multiple plants in one source row remain grouped and
are flagged for editorial review rather than silently split into individual recommendations.

## Plant sources and taxonomy

`plant_registry.csv` preserves 137 source records. Some names come from the supplied local
chart images; the broader list is attributed to the project handoff. Existing taxonomy
values have no claim-level bibliography in the registry. In particular,
`bulk-taxonomy-populated` is historical pipeline metadata, not verification. The
`plant_verification_register.csv` makes taxonomy, cultivar, profile, timing, and
illustration states independent; no record is currently reported as independently
verified.

## Other supplied material

- `Vegetable_Gardening_Encyclopedia_With_Sp.pdf` is a general reference. It is not a local
  planting-time authority. Its text or artwork is not copied into the generated book.
- The Eastern Vancouver Island pollinator guide and web references mentioned in older notes
  are not checked into this repository; their contents have not been independently
  reverified in this build.
- Seventy image files were inspected on the separate `illustration-assets` branch at
  `c7bdbde9e5fc81c514a40decc7b9bfcdb1f00da5`. All decode as 1024 × 1536 PNGs, but only 68
  have unique content. Contact-sheet inspection found cross-plant labels; identity, creator,
  license, and publication approval remain unverified. The branch is not a build dependency.

## Source use

Retain supplied source artifacts unchanged. Every extracted or normalized record should
carry its source ID, repository path, page/section, evidence type, transcription, and
verification state. Editorial interpretation and locally reviewed advice must remain
separate. No unsupported source, license, botanical fact, or planting date should be
inferred from a filename or generated description.
