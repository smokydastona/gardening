# Errington Gardening Encyclopedia — Implementation Final Report

**Report date:** 2026-11-22
**Final repository branch:** `main`

## 1. Executive summary

The reproducible build and data safeguards were implemented. The repository now generates
three PDFs from shared plant and calendar data, has stable plant IDs, claim-source scaffolding,
climate-evidence documentation, and an evidence-gated illustration workflow.

**Release decision: NOT READY.** Software, data-model structure, and publication generation
are substantially complete, but botanical identities/profiles, local climate numbers,
calendar interpretation, illustrations, and human print review remain external requirements.

## 2. Repository changes

Important additions:

- `data_model.py`, `build_all.py`, and `build_publications.py`
- Stable `plant_id` fields in plant registry and derived registry files
- `claims/CLAIM_SOURCES.csv`
- `data/local_climate_evidence.json`
- Three reproducible PDF products
- Required methodology, build, botanical, illustration, calendar, and contribution documentation
- Expanded pytest coverage for data and publication products

The original PDF, chart images, calendar transcription, and registry source files were preserved.

## 3. Data corrections

- 137 plant records retained.
- 137 stable plant IDs added.
- 359 original calendar entries retained.
- 359 entries remain source transcriptions.
- 158 grouped calendar entries remain identified for review.
- 137 botanical evidence templates remain unverified.
- 2 claim-source rows document Arugula identity authorities.

No unsupported fact was converted into a verified value.

## 4. Botanical research

POWO and WFO Arugula records were recorded:

- POWO: <https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:2798761-4>
- WFO: <https://www.worldfloraonline.org/taxon/wfo-0000677418>

They are retained as conflicting/evaluative evidence rather than silently selecting a name.
All 137 plant taxonomy/profile states remain independently unverified unless a later record
explicitly changes that state.

## 5. Local climate research

The supplied 8a PDF label and 8b chart labels remain unresolved. Canadian and USDA zone
systems are documented as distinct. April 15 and October 15 remain source anchors rather than
verified Errington normals. Nanaimo A is recorded only as a candidate regional proxy:
<https://climate.weather.gc.ca/climate_normals/results_1981_2010_e.html?searchType=stnProv&lstProvince=BC&climate_id=1025370&dispBack=0>

## 6. Calendar reconciliation

All 359 transcription rows remain present. Mechanical action classifications and grouped-entry
review fields remain. No new individual planting dates were invented.

## 7. Illustration review

Approved assets: 0.
Pending candidates: 0.
Unapproved/untouched external assets: 70 separate-branch images remain outside the build.
No botanical accuracy or license was fabricated or approved.

## 8. Publication improvements

Generated and rendered:

- Complete encyclopedia: 265 pages
- Monthly guide: 10 pages
- Illustrated directory: 137 pages
- Botanical illustration collection: 138 pages
- Educational figure collection: 37 pages

The three products were built from shared source data. Contact sheets were rendered for every
page and overview-scanned. Print-readable full-resolution page and content sign-off remains
external human work.

## 9. Engineering validation

Executed:

- `python build_all.py`
- `python -m pytest -q`
- `python validate_pipeline.py --publication`
- Rendered all pages for all three PDFs

Actual test result: 43 passed.
Actual PDF validation: all three PDFs are present, non-empty, and have intentional author metadata.

## 10. CI results

The workflow file was updated to build all three products and run tests. No actual GitHub Actions
run was available for the final implementation revision at report time.

## 11. Remaining blockers

- Human botanical identity review for 137 records.
- Claim-level horticultural source review.
- Authoritative Errington climate data and zone reconciliation.
- Human calendar review, especially grouped entries.
- Licensed, identity-reviewed illustration assets.
- Full-resolution print and accessibility sign-off.

## 12. Release decision

**NOT READY**: critical botanical, climate, calendar, illustration, and human publication
review requirements remain unsatisfied. The software implementation and reproducible build
are complete enough to support subsequent review.

## 13. Follow-up implementation check

The current working tree adds SHA-256 snapshots for the supplied calendar PDF, chart images,
plant registry, calendar transcription, and full-text transcription. `validate_pipeline.py`
now rejects modifications to those files unless the source-hash register is explicitly
updated. The plant-directory builder includes all stable-ID concept candidates and labels
them as unapproved. Separate approval sidecars remain required for approved assets. A
focused test covers both the zero-approved state and embedding a valid approved asset.

The separate `illustration-assets` branch was inspected at
`c7bdbde9e5fc81c514a40decc7b9bfcdb1f00da5`: 70 valid 1024 × 1536 PNG files contain 68
unique image byte sequences. Contact-sheet review found visible cross-plant labels, so the
assets remain unapproved. 137 local concept candidates and 36 educational concept figures
were generated in this implementation run; they are not species-specific evidence or
approved publication assets. Provider credentials were unavailable, and fully researched
plant profiles and claim-level citations remain to be produced.

Current build and test commands are recorded in `reports/IMPLEMENTATION_REGISTER.md` and
`PUBLICATION_QA_REPORT.md`; the current local suite passes 44 tests. All outstanding
scientific and human review gates remain open.

## 14. Asset completion follow-up

The implementation now generates and embeds 137 concept plant candidates, 36 educational
figure concepts and 18 worked examples. Reenie Beanie is used throughout the publication
and generated assets. The complete supplement is included in the 265-page encyclopedia,
and standalone botanical and figure collections contain 138 and
37 pages respectively. None of these concepts is human-botanical approved. They are
production assets for review, not evidence of accepted taxonomy or cultivation.
