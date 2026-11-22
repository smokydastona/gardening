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
| D — Illustration integrity | `FAILED` | 0 approved illustrations; 70 external-branch images have not been identity/license reviewed. |
| E — Editorial quality | `PARTIAL` | Source limitations and verification labels are included. Complete claim-level bibliography, index, and editorial sign-off remain outstanding. |
| F — Publication quality | `PARTIAL` | Rebuilt 101-page PDF passes automated metadata, embedded-font, text, page-count, and one-page TOC checks. All pages were rendered and contact sheets visually scanned at overview scale; full-resolution visual approval remains open. |
| G — Software quality | `PARTIAL` | Local build and automated tests pass (22 tests); reproducibility is tested. CI status is not claimed until a GitHub Actions run succeeds. |

Required human visual checklist:

- [x] Render every page of the final PDF and visually scan the complete set of contact sheets.
- [ ] Inspect every page at print-readable resolution; the contact-sheet scan is not a substitute.
- [ ] Check clipping, missing glyphs, blank pages, text/image overlap, page breaks, margins,
  running headers, and page numbers.
- [ ] Verify every table and every TOC page number/link against the rendered PDF.
- [ ] Inspect each illustration individually after its identity and rights are documented.
- [ ] Sign off editorial accuracy and confirm the climate-zone discrepancy is either
  authoritatively resolved or explicitly retained in the final edition.

No PDF is labeled `READY_FOR_REVIEW` or `APPROVED_FOR_PUBLICATION` by this report.
