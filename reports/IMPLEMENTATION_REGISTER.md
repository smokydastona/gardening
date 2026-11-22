# Implementation register

## Status snapshot — 2026-11-22

This register distinguishes working software from completed research and human approval.
Passing a software test does not establish botanical accuracy or publication readiness.

| Requirement area | Deliverable and current status | Verification evidence | Remaining work |
|---|---|---|---|
| Source integrity | Original calendar PDF, two chart images, 137 registry records, and 359 calendar transcriptions are retained with SHA-256 snapshots. | `SOURCE_SHA256SUMS.txt`; `validate_pipeline.py`; `test_pipeline_validation.py`; `data_model.py` | Compare every transcription row to the source PDF/charts; establish source authorship. |
| Plant registry | 137 stable-ID records and 137 evidence templates. Historical master plan contains 125 target entries; the difference is unresolved, not deleted. | `validate_authoritative_registry`; `test_data_model_and_publications.py` | Reconcile identities, synonyms, cultivars, and categories; independently verify all claims. |
| Botanical research | 0 of 137 records have independently verified complete profiles; current statuses remain pending. | `PLANT_VERIFICATION_REPORT.md`; `plant_verification_register.csv` | Taxonomy and plant-specific morphology, cultivation, health, and regional evidence for every record. |
| Calendar and climate | 359 source-linked entries; 8a/8b disagreement and April 15/October 15 source anchors remain unresolved. | `calendar_review.csv`; `CALENDAR_REVIEW_REPORT.md`; calendar tests | Human review of all entries and groups; authoritative climate and frost analysis; separate recommendations from transcription. |
| Plant illustrations | 0 generated in this implementation run; 0 approved. Separate branch has 70 valid PNGs, 68 unique image payloads, and visible cross-plant labels. | `ILLUSTRATION_AUDIT.md`; `illustration_assets.py`; `test_illustration_pipeline.py` | Supply verified per-plant evidence, generation access or licensed source art, resolve identities and rights, and complete individual human review. |
| Educational figure library | No independently managed educational figure collection is present. | No figure collection tests exist. | Create original, informative, cited and accessible figures across the requested topic groups. |
| Worked instructions and complete chapters | Existing manuscript is a working editorial draft; it is not a complete encyclopedia with all requested worked examples. | Rendered encyclopedia PDF and manuscript inspection | Develop and fact-check chapter content and practical examples; integrate relevant figures. |
| Publications | Three reproducible PDFs: encyclopedia (101 pages), monthly guide (10 pages), and plant directory (23 pages). Directory embeds only approved stable-ID assets and is visibly marked pending while none are approved. | `build_all.py`; `validate_pipeline.py --publication`; `test_data_model_and_publications.py` | Complete the illustrated directory, standalone plate/figure collections, appendices, and reviewed editorial/index apparatus. |
| Visual QA | All 134 current PDF pages were rendered; contact sheets were overview-scanned. | `render_publication.py`; `PUBLICATION_QA_REPORT.md` | Inspect every page at print-readable resolution for clipping, legibility, overlap, and accessibility; complete human sign-off. |
| Build and CI | Local reproducible build and 41 tests pass. No GitHub Actions result was obtained for this revision. | `build_all.py`; `.github/workflows/build-encyclopedia.yml` | Confirm a successful hosted CI run; review dependency/action supply-chain risk. |

## Release status

**NOT READY FOR PUBLICATION.** The repository has a working data and PDF pipeline, but it
does not yet satisfy the botanical research, local calendar review, illustration, educational
figure, complete content, or print-approval requirements. No human review or approval is
claimed by this register.
