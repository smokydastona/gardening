# Changelog

## Unreleased

- Added the initial `src/gardening` package and unified `gardening` command for validation,
  calendar, illustration, figure, report, test, and publication workflows.
- Migrated calendar parsing/OCR, registry normalization, source validation, and the
  hash-bound illustration publication gate into focused package modules; retained root
  compatibility commands.
- Organized tests into unit and integration suites and added branch-tree and migration
  inventories with blob IDs, SHA-256, sizes, duplicate-path candidates, and timestamps.
- Added perceptual-hash screening that reports possible near-duplicate artwork without
  making automated identity or approval decisions.
- Audited the historical illustration branch without merging it; recorded the 70 reviewed
  plant candidates and deferred copying its roughly 249 MB unapproved image set.

## 0.2.1 — 2026-11-22

- Switched the encyclopedia, supporting PDFs, illustration annotations and generated
  educational assets to the bundled Reenie Beanie TTF.

- Added reproducible concept-art production: 137 stable-ID plant candidates, 36 educational
  figures, and 18 worked examples.
- Expanded publication output to five PDFs, including a botanical illustration collection
  and an educational figure collection.

- Added SHA-256 snapshots and build-time checks for supplied calendar documents, chart
  images, the registry, and calendar transcription records.
- Updated the plant-directory PDF to embed only approved stable-ID illustrations and to
  label the zero-approved output accurately.
- Tested all 70 external-branch PNGs for decoding and dimensions, identified duplicate
  bytes and cross-plant labels, and kept all candidates unapproved.
- Added an implementation register and refreshed source, illustration, and publication QA
  status with current counts and unresolved review gates.

## 0.2.0 — 2026-11-22

- Added source policy, data dictionary, audit, verification, calendar, illustration, and
  publication QA records.
- Preserved all 137 plant records and 359 calendar transcriptions while adding stable IDs,
  explicit provenance, independent verification states, and a manual calendar review list.
- Stopped enrichment from modifying the source registry or labeling bulk taxonomy as
  verified; removed generated filler from the reader-facing plant index.
- Reworked the PDF pipeline to render Markdown structure, embedded portable fonts, an
  automatically paginated table of contents, and project-appropriate metadata.
- Added a complete pinned dependency lock and rendering of every PDF page into review
  images/contact sheets.
- Added evidence templates, pending-candidate generation, human botanical/style review,
  hash-bound approval sidecars, and stable-ID manifest gating for illustrations.
- Added an optional Gemini image-generation backend and preserved illustration review
  records across rebuilds; approved images must match their plant and evidence identities.
- Added source-integrity validation and updated CI to build without the untracked
  illustration-assets branch.
- Kept botanical profiles, local timing, illustrations, and publication approval pending
  where evidence is not available.
