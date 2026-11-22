# Repository audit report

## Executive summary

The repository contains useful source documents, a full 89-page supplied calendar PDF,
chart images, a 137-record plant registry, 359 calendar transcriptions, several manuscripts,
and generated PDFs. The current content is not production-ready: the plant profile pipeline
used generic scaffolds and unverified bulk taxonomy, the 8a/8b conflict is unresolved,
calendar groups can be mistaken for individual advice, the illustration branch is not
reproducible from this checkout, and the existing PDF metadata names GitHub Copilot as its
author.

The implementation branch preserves the source records, adds independent provenance and
review registers, prevents source-registry mutation, builds an evidence-labeled calendar and
catalog, and makes PDF generation deterministic and source-local. Research and visual
editorial approval remain outstanding; the publication status is `IN_PROGRESS`, not
`APPROVED_FOR_PUBLICATION`.

## Repository architecture

```text
Supplied calendar PDF + chart images + project handoff
                 |
       source transcription CSV/Markdown
                 |
 plant_registry.csv + errington_calendar_entries.csv
                 |
 input validation -> provenance/review registers
                 |
 generated monthly reference + plant index + manuscript
                 |
       Markdown-aware ReportLab PDF
                 |
       PDF checks + human visual review
```

`extract_calendar_data.py` performs chart OCR and color sampling; its outputs are not
editorially verified and are not regenerated during the deterministic publication build.
`parse_errington_calendar.py` extracts text from the checked-in calendar PDF. Enrichment
joins names to calendar text. Report generation emits status registers. The final script
builds the publication PDF.

## Source inventory

| Source | Inventory and role | Limitation |
|---|---|---|
| `Errington BC Zone 8a Planting Calendar.pdf` | 89 pages; source for the local calendar transcription | Metadata identifies no author; source history/independence unknown |
| `Planting Calander-Crops.png` | Crop chart image | Visibly labeled Zone 8b; low-resolution text and chart marks need cell-by-cell review |
| `Planting Calander-Ornamentals.png` | Ornamental chart image | Visibly labeled Zone 8b; low-resolution text and chart marks need cell-by-cell review |
| `ERRINGTON_CALENDAR_FULL_TEXT.md` | 89-page text extraction | Derived from the supplied PDF; not independent evidence |
| `errington_calendar_entries.csv/.json` | 359 parsed calendar entries | Action columns and grouped names need review |
| `plant_registry.csv` | 137 retained common-name records | 122 labels had `bulk-taxonomy-populated`; none have claim-level citations here |
| `plant_registry_enriched.csv` | Derived calendar matches | Prior generation overwrote source values and appended repeated notes |
| Manuscripts and plan documents | Handbook, catalog, monthly reference, briefs, handoff, structure and plan | Some claims exceed citations currently available |
| Illustration assets | 70 image files exist on the separate `illustration-assets` branch | Not in this checkout; image identity, creator, license, and approval are unverified |
| PDFs | Calendar, general gardening reference, and prior generated encyclopedia | Prior encyclopedia has incorrect author metadata and a manually listed, non-paginated contents section |
| Tests/workflow/dependencies | 15 baseline tests; one GitHub Actions workflow; pinned Python requirements | No source-integrity checks or render/visual gate |

## Findings

### Botanical accuracy

- 137 records are present, including 15 already flagged for species/cultivar resolution.
- 122 entries marked `bulk-taxonomy-populated` are not independently verified. Existing
  Latin names and families have no claim-specific citations in the repository.
- Generic, category-level cultural descriptions were emitted for all records and can be
  mistaken for plant-specific profiles.
- Common names such as beans, roses, asters, ferns, and grasses do not identify a unique
  species or cultivar.

### Calendar accuracy

- 359 entries span all 12 months and 13 sections.
- No exact duplicate calendar entry keys were found in the baseline data.
- Slash/comma groups combine multiple plants in many entries; those schedules cannot be
  treated as individual recommendations without review.
- Action columns are source text, not typed or reviewed recommendations.
- The PDF identifies Zone 8a while both summary charts identify Zone 8b. The conflict is
  unresolved. April 15 and October 15 are source-reported approximate anchors only.

### Illustration findings

- No per-plant image files are present in the current checkout.
- The separate branch contains 70 image files but has no usable claim-level proof of
  identity, creator, license, visual review, or approval in this checkout.
- The previous renderer associated art by normalized filename and embedded images without
  an approval gate.

### Publication design

- The existing cover has a usable paper-and-botanical aesthetic.
- The existing 336-page PDF lists Contents without page numbers, uses line-by-line Markdown
  parsing, does not render real nested lists/tables/inline emphasis reliably, and identifies
  GitHub Copilot as author.
- The build searched machine-specific Windows font paths and could fall back to unembedded
  standard fonts.
- The prior output includes generated illustration prompts as if they were publication
  content.
- A complete index, fully reviewed glossary, and page-by-page visual approval are not
  evidenced.

### Software engineering, security, and dependencies

- The baseline test suite passed 15 tests, but did not check source counts, provenance,
  output integrity, or PDF contents/metadata.
- Runtime dependencies are now pinned in `requirements.lock.txt`; no vulnerability scan was
  run. GitHub Actions use major-version tags rather than immutable commit SHAs.
- `enrich_plant_registry.py` overwrote `plant_registry.csv`, violating source immutability,
  and could append bulk source notes repeatedly.
- The workflow checked out an external branch implicitly; the 70 assets were not in the
  main checkout, and absence was not clearly surfaced.
- Nine generated `.pyc` files were committed; there was no `.gitignore`.
- README links included absolute Windows paths. Build inputs otherwise require no network;
  the publication pipeline avoids runtime network access. The optional illustration
  generator has explicit OpenAI and Gemini backends that send user-selected evidence images
  to the selected provider; neither is invoked by CI or the publication build.
- The general reference PDF is treated as a topical source only; its contents are not
  copied into the generated publication.

## Defect register

| ID | Severity / priority | Finding | Resolution or limitation |
|---|---|---|---|
| A-01 | High / P1 | 8a text vs 8b charts | Preserved as unresolved in source policy and calendar reports; no arbitrary choice |
| A-02 | High / P1 | Frost anchors could read as guaranteed dates | Explicitly labeled approximate source anchors; no independent local normals available |
| A-03 | High / P1 | Bulk taxonomy appeared verified | Enrichment now downgrades bulk status; independent taxonomy register leaves all pending |
| A-04 | High / P1 | Generic profile filler | Removed from generated reader-facing plant index; evidence-based research still required |
| A-05 | High / P1 | Grouped calendar entries could imply same crop timing | Retained verbatim, explicitly flagged, and listed in `calendar_review.csv` |
| A-06 | High / P1 | No typed calendar action/provenance model | Added generated action register with source/page and mechanical classification status |
| A-07 | High / P1 | Enrichment overwrote source registry | `enrich_plant_registry.py` now writes only derived output |
| A-08 | High / P1 | Illustration assignment/approval conflated | Stable-ID manifest and hash-bound human-review sidecars gate publication; generation remains pending until explicit review |
| A-09 | High / P1 | External illustration branch dependency | Removed from deterministic build; branch assets remain separate and unapproved |
| A-10 | High / P1 | PDF author falsely identified | Rebuilt metadata credits the project, not Copilot |
| A-11 | High / P1 | Markdown parser and TOC inadequate | Markdown AST renderer, real headings/lists/tables, multi-pass page-numbered TOC implemented |
| A-12 | Medium / P2 | Machine-specific fonts | Switched to bundled ReportLab Vera fonts; font files embedded |
| A-13 | High / P1 | No record-loss gate | Added required-input, duplicate, page/month, and source-count validation |
| A-14 | Medium / P2 | Committed bytecode/no ignore file | Added `.gitignore` and removed tracked bytecode from version control |
| A-15 | Medium / P2 | Documentation used machine paths and mislabeled PDF as absent | README and source audit corrected; local PDF is present but source history remains unknown |
| A-16 | High / P1 | Human source verification unavailable | Recorded as limitation; no botanical/local timing claims marked verified |
| A-17 | High / P1 | Full visual QA and complete editorial apparatus unverified | Publication QA gate remains open; no publication-ready claim |
| A-18 | Medium / P2 | No dependency vulnerability scan; CI action references are major tags | Residual supply-chain risk documented; immutable action pins and a vulnerability scan remain operational follow-up |

## Remediation status

Implemented: source immutability, provenance registers, record-count validation, calendar
review export, stable plant IDs, separate illustration approval state, deterministic
Markdown/PDF rendering, an evidence-gated illustration candidate/review workflow, and CI
integration. Automated tests and PDF validation are run on
the implementation branch. Independently researched botanical profiles, local timing
review, asset licensing/identity review, complete index, and final human editorial/visual
approval remain outstanding.
