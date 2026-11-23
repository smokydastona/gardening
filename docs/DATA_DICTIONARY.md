# Data dictionary

## Source records

### `claims/CLAIM_SOURCES.csv`

Claim-level source evidence, with separate rows for individual sources. Record the exact
claim, source and access details, geographic applicability, confidence, review and status.
Use notes to connect cross-checks and record agreement, conflicts, limitations and
publication suitability. See [research library](RESEARCH_LIBRARY.md); a listed candidate
source is not itself a verified claim. Each row must align with the CSV header; the
data-model validator rejects rows with missing or extra cells.

### `plant_registry.csv`

The 137-row working plant inventory. Existing names, taxonomy values, and notes are retained
as recorded. `display_name` is the current human-readable label; it is not guaranteed to be
a resolved taxon. Existing `verification_status` values are historical and must not be used
to infer verification.

### `errington_calendar_entries.csv`

The 359-row transcription of calendar content. `month`, `page_type`, `section`,
`page_number`, `plant_text`, `plant_normalized`, and `row_text` identify the source
transcription. `indoor_sow`, `direct_sow_or_transplant`, and `harvest_bloom_action` are
transcribed text columns, not normalized gardening advice.

## Derived registers

### `plant_verification_register.csv`

One row per stable `plant_id` (`plant-` plus a normalized common-name slug). Source
attribution and review states are independent. `botanical_name_as_recorded` and
`family_as_recorded` preserve existing values but are unverified. `source_status`,
`taxonomy_status`, `cultivar_status`, `profile_status`, `timing_status`, and
`illustration_status` must not be collapsed into one status.

### `calendar_actions.csv`

One row per source calendar entry. It records source ID/title/path, author and publication
date status, access date, page, evidence type, verbatim row, editorial interpretation,
confidence, and verification state. `source_transcription` preserves the full source row;
`action_types` is a mechanical keyword classification and may be `unclassified`.
`interpretation_status` explicitly distinguishes the transcription from a recommendation.
`grouped_plant_text=true` means the source row names more than one plant; it is not mapped to
individual plant timing.

Action vocabulary: `indoor-sowing`, `direct-sowing`, `transplanting`,
`succession-sowing`, `harvesting`, `flowering`, `pruning`, `dividing`,
`propagation`, and `seasonal-maintenance`. Action classification is generated and remains
unreviewed.

### `calendar_review.csv`

Rows requiring editorial review because a name is grouped, no exact single-plant ID exists,
an action could not be classified, or a required section is absent. `page_number` points to
the locally supplied calendar PDF.

### `plant_illustrations/illustration_manifest.csv`

One row per stable plant ID. A filename is a naming suggestion only; it is not an
image-to-plant association. Creator, license, generation, review, and approval are recorded
independently. No image may be embedded as approved unless `approval_status=approved` and
the exact asset exists, its plant identity matches the stable ID, and its hash-bound
human-review sidecar passes validation. Builds preserve existing manifest entries; an
orphaned ID or unexpected manifest columns cause an error rather than discarding review data.

## Generated files

`plant_registry_enriched.csv`, `ERRINGTON_MONTHLY_REFERENCE.md`,
`ERRINGTON_PLANT_CATALOG.md`, `calendar_actions.csv`, verification reports, and PDFs are
derived outputs. Regenerate them from retained sources and scripts; never edit generated
outputs as the sole location of a source correction.
