# Publication QA report

## Overall status: `IN_PROGRESS`

This working publication is not approved for publication. The PDF is a reproducible
pre-review build, not evidence that botanical claims, local planting timing, illustrations,
or editorial content are correct.

| Gate | Status | Evidence / remaining work |
|---|---|---|
| A — Source integrity | `PARTIAL` | Original supplied files retained; 137 plants and 359 calendar entries are count-checked. Calendar PDF authorship/history is unknown; transcription requires further comparison. |
| B — Botanical accuracy | `FAILED` | 0 independently verified taxonomy records and 0 individually reviewed horticultural profiles. |
| C — Local horticultural accuracy | `FAILED` | 8a/8b conflict unresolved; no independently sourced Errington frost normals or plant-specific local timings. |
| D — Illustration integrity | `PARTIAL — concept art complete, approval incomplete` | 137 concept candidates and 36 educational figures are present. 0 are human-botanical approved. The 70 historical branch images decode as 1024 × 1536 PNGs, but 68 are unique and cross-plant labels were found. |
| E — Editorial quality | `PARTIAL` | Source limitations and verification labels are included. Complete claim-level bibliography, index, and editorial sign-off remain outstanding. |
| F — Publication quality | `PARTIAL` | Current PDFs have 302, 10, 137, 138, and 37 pages. Concept plates and figures are embedded in dedicated PDFs and the encyclopedia supplement. Print-resolution review remains open. |
| G — Software quality | `PARTIAL` | `build_all.py`, data validation, and 43 tests pass locally. CI status is not claimed until a GitHub Actions run succeeds. |

## Latest build and visual scan — 2026-11-22

The regenerated products are `Errington_Gardening_Encyclopedia.pdf` (302 pages),
`Errington_Monthly_Gardening_Guide.pdf` (10 pages),
`Errington_Illustrated_Plant_Directory.pdf` (137 pages),
`Errington_Botanical_Illustration_Collection.pdf` (138 pages), and
`Errington_Educational_Figure_Collection.pdf` (37 pages). Every page must be rendered at the
pipeline's 1× scale and included in contact sheets. The overview scan found no obviously
blank or missing pages, but the body pages are text-dense in calendar sections and sparse
in the plant-directory layout. The 1× render and contact sheets are not adequate evidence
for print-size typography, clipping, or overlap; those checks remain pending.

The directory now contains every one of the 137 registry candidates with an explicit
“Concept Candidate — not botanically approved” status. Human approval remains separate;
no candidate or figure is represented as scientifically approved. The historical branch
candidates must not be used until their identity, visible labels, attribution, and licensing
are individually resolved.

Required human visual checklist:

- [x] Render every page of the final PDF and visually scan the complete set of contact sheets.
- [ ] Inspect every page at print-readable resolution; all rendered pages are currently at
  1× scale, and the contact-sheet scan is not a substitute.
- [ ] Check clipping, missing glyphs, blank pages, text/image overlap, page breaks, margins,
  running headers, and page numbers.
- [ ] Verify every table and every TOC page number/link against the rendered PDF.
- [ ] Inspect each illustration individually after its identity and rights are documented.
- [ ] Sign off editorial accuracy and confirm the climate-zone discrepancy is either
  authoritatively resolved or explicitly retained in the final edition.

No PDF is labeled `READY_FOR_REVIEW` or `APPROVED_FOR_PUBLICATION` by this report.
