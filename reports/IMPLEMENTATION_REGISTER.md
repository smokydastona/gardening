# Implementation register

## Status snapshot — 2026-11-23

This register distinguishes working software from completed research and human approval.
Passing a software test does not establish botanical accuracy or publication readiness.

| Requirement area | Deliverable and current status | Verification evidence | Remaining work |
|---|---|---|---|
| Source integrity | Original calendar PDF, two chart images, 137 registry records, and 359 calendar transcriptions are retained with SHA-256 snapshots. | `SOURCE_SHA256SUMS.txt`; `validate_pipeline.py`; `test_pipeline_validation.py`; `data_model.py` | Compare every transcription row to the source PDF/charts; establish source authorship. |
| Plant registry | 137 stable-ID records and 137 evidence templates. Historical master plan contains 125 target entries; the difference is unresolved, not deleted. | `validate_authoritative_registry`; `test_data_model_and_publications.py` | Reconcile identities, synonyms, cultivars, and categories; independently verify all claims. |
| Botanical research | 0 of 137 records have independently verified complete profiles; current statuses remain pending. | `PLANT_VERIFICATION_REPORT.md`; `plant_verification_register.csv` | Taxonomy and plant-specific morphology, cultivation, health, and regional evidence for every record. |
| Dimensioned verification | `gardening verify audit` emits deterministic JSON with separate plant and project statuses; current snapshot covers all 137 plants, 359 calendar entries, 2 claim-source records, and 36 figures. | `reports/VERIFICATION_AUDIT.json`; `tests/unit/test_verification_engine.py` | Add provider-specific taxonomy and source-monitoring integrations; capture claim excerpts, review events, climate evidence, and human decisions. |
| Taxonomy provider | Opt-in GBIF Species Match adapter supports per-plant or registry-wide candidate collection, bounded retries, rate limiting, 90-day caching, raw responses, alternatives, and response hashes. No new live query ran because DNS resolution is unavailable here. | `gardening research taxonomy --provider gbif`; `tests/unit/test_gbif_taxonomy.py`; `docs/RESEARCH_LIBRARY.md` | Run on an authorized network; review API terms, match alternatives, and every candidate against independent taxonomy authorities before recording evidence. |
| Calendar and climate | 359 source-linked entries; 8a/8b disagreement and April 15/October 15 source anchors remain unresolved. | `calendar_review.csv`; `CALENDAR_REVIEW_REPORT.md`; calendar tests | Human review of all entries and groups; authoritative climate and frost analysis; separate recommendations from transcription. |
| Plant illustrations | 137 local concept candidates generated; 0 approved. Separate branch has 70 valid PNGs, 68 unique image payloads, and visible cross-plant labels. | `ILLUSTRATION_AUDIT.md`; `plant_illustrations/concept_candidates/`; `test_illustration_pipeline.py` | Replace category concepts with species-specific evidence-reviewed art, resolve identities and rights, and complete individual human review. |
| Educational figure library | 36 concept figures generated with stable IDs, captions and accessibility text. | `educational_figures/figure_manifest.csv`; `Errington_Educational_Figure_Collection.pdf` | Attach authoritative sources and complete botanical/horticultural human review. |
| Worked instructions and complete chapters | 137 plant field entries and 18 worked examples are included in the supplement. | `ERRINGTON_COMPLETE_SUPPLEMENT.md`; rendered encyclopedia PDF | Fact-check profiles and examples, and complete all claim-level citations. |
| Publications | Five PDFs structurally validate: encyclopedia (219 pages), monthly guide (25), plant directory (25), botanical collection (138), and figure collection (37). | `gardening build all`; `reports/CURRENT_RELEASE_STATUS.md` | Complete botanical approval and editorial/print approval. |
| Visual QA | Current build passed structural PDF checks; page-by-page rendering and human print-size review were not rerun in this snapshot. | `render_publication.py`; `PUBLICATION_QA_REPORT.md` | Render every page and inspect clipping, legibility, overlap, accessibility, and design; complete human sign-off. |
| Build and CI | Current local run: 78 tests passed; all five PDFs rebuilt and structurally validated. No hosted CI result is available for this increment. | `gardening test`; `gardening build all`; `.github/workflows/build-encyclopedia.yml` | Obtain a successful hosted CI run after push; review dependency/action supply-chain risk. |

## Release status

**NOT READY FOR PUBLICATION.** The repository has a working data and PDF pipeline, but it
does not yet satisfy the botanical research, local calendar review, illustration, educational
figure, complete content, or print-approval requirements. No human review or approval is
claimed by this register.
