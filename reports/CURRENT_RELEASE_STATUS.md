# Current release status

**Release decision: NOT READY FOR PUBLICATION.** This report reads current source, verification, asset, and PDF records. It does not treat populated fields or generated artwork as independent verification or approval.

Regenerate with `python generate_release_status.py`.

## Source and scope

- Source checksum and authoritative registry validation: **PASS**.
- Registry validator: `{'plant_records': 137, 'calendar_entries': 359, 'claim_records': 2}`.
- Historical plan: 125 category entries map to 123 distinct registry records; 2 repeated category entries are retained.
- 4 explicit plural-form name matches are used; these are common-name inventory matches, not taxonomic conclusions.
- 137 registry records are retained; 14 are additional to the distinct historical-plan names. See `reports/PLANT_SCOPE_RECONCILIATION.csv`.
- Calendar source entries retained: 359; grouped entries still marked for review: 158.
- Profiles not explicitly verified: 137; taxonomy records explicitly marked `requires-resolution`: 15.
- Plants without any claim-source row: 136; claim rows not marked verified: 2.

## Research and human verification

- Plant verification records: 137; profile states: `{'pending-verification': 137}`; taxonomy states: `{'pending-verification': 122, 'requires-resolution': 15}`; timing states: `{'pending-verification': 94, 'source-record-exists-not-reviewed': 43}`.
- Records explicitly marked verified in the plant register: 0 profiles, 0 taxonomies, and 0 local timings.
- Claim-source rows: 2; evidence states: `{'conflicting-evidence': 2}`. A source row is not a verified profile.
- Climate zone and frost anchors remain disputed/unverified; external sources require direct review and local measurements/proxy limitations remain unresolved.
- Deterministic verification snapshot: **CURRENT**; decision **NOT_READY** for 137 plants and 359 calendar entries.
- Claim evidence extracts or source locations recorded: 0 of 2; current claim statuses: `{'CONFLICTING_EVIDENCE': 2}`.
- Verification audit blockers: 11; structural errors: 0. See `reports/VERIFICATION_AUDIT.json`.

## Assets and publications

- Plant concept candidates: 137 manifest rows; 137 hashes match; 0 missing or mismatched files/hashes; 0 repeated file hashes.
- Plant artwork manifest: 137 expected asset files are marked missing; 137 registry entries lack an approved illustration.
- Plant illustration assets explicitly marked approved in the asset manifest: 0.
- Educational figures: 36 manifest rows; 36 hashes match; 0 missing or mismatched files/hashes; 0 repeated file hashes; 0 marked approved.
- Educational figures without recorded source references: 36.
- Export-format completeness beyond the PNG files declared by current manifests is not assessable; required per-asset export formats are not recorded.

PDF publication-set structural validation: **PASS** (5 PDFs passed structural and metadata checks.)

| Publication PDF | Current file check |
|---|---|
| `Errington_Gardening_Encyclopedia.pdf` | Present; 219 pages |
| `Errington_Monthly_Gardening_Guide.pdf` | Present; 25 pages |
| `Errington_Illustrated_Plant_Directory.pdf` | Present; 25 pages |
| `Errington_Botanical_Illustration_Collection.pdf` | Present; 138 pages |
| `Errington_Educational_Figure_Collection.pdf` | Present; 37 pages |

## Outstanding release gates

- Independently verify the taxonomy, horticultural claims, local timing, and climate evidence for all applicable plants.
- Review calendar transcription and grouped recommendations against the source; keep source transcription separate from advice.
- Verify every image's identity, morphology, creator, license, checksum, and hash-bound independent approval; keep unapproved assets out of publications.
- Complete source-backed educational figures, accessibility review, and page-by-page print and visual QA.
- Broken-reference checking is limited to PDF table-of-contents destinations; manuscript cross-references are not checked by this report.
- Tests are not run by this report. Hosted CI is not queried; verify test and CI results for the current revision separately.
- Obtain qualified human botanical, horticultural, rights, and publication review.
