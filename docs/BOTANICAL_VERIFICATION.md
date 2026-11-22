# Botanical verification

## Identity hierarchy

The registry distinguishes a `display_name` from an accepted botanical name. `plant_id` is the
permanent primary identifier. Recorded Latin names and families are candidates until examined
against claim-level evidence.

## Verification dimensions

- **Taxonomy:** accepted name, authority, source URL, date checked.
- **Cultivar:** cultivar or group identity and applicable source.
- **Profile:** botanical description and growth characteristics.
- **Horticultural:** propagation, soil, water, spacing, pests, and management.
- **Timing:** plant-specific or regional timing.
- **Illustration:** subject, provenance, license, human botanical review.

Valid states are `unreviewed`, `research_required`, `partially_verified`, `verified`,
`conflicting_evidence`, `insufficient_evidence`, and `not_applicable`.

## Claim evidence

Substantive claims use `claims/CLAIM_SOURCES.csv`. A source in the repository or the web
does not support a claim until the relevant record is examined and linked to the exact claim.
The Arugula pair of POWO and WFO records is retained as `conflicting-evidence`, not resolved
by preference.
