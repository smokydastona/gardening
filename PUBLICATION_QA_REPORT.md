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
| D — Illustration integrity | `PARTIAL — unapproved artwork withheld` | 0 botanical illustrations and 0 educational figures are approved. The owner confirms rights to the 70 branch images; they and the generated candidates are excluded from all PDFs pending identity, anatomy, and independent botanical review. |
| E — Editorial quality | `PARTIAL` | The core handbook now includes expanded climate-risk, microclimate, planning, botany, soil, bed-building, propagation, irrigation, and diagnostic instruction. Complete claim-level bibliography, plant-specific research, and editorial sign-off remain outstanding. |
| F — Publication quality | `PARTIAL` | Current PDFs have 305, 25, 25, 138, and 37 pages. Only the encyclopedia cover image is embedded; all other PDFs contain no images. Display headings use Reenie Beanie; body text uses Times-Roman. Full-publication print review remains open. |
| G — Software quality | `PARTIAL` | `build_all.py`, publication validation, and 49 tests pass locally. CI status is not claimed until a GitHub Actions run succeeds. |

## Latest build and visual scan

The regenerated products are `Errington_Gardening_Encyclopedia.pdf` (305 pages),
`Errington_Monthly_Gardening_Guide.pdf` (25 pages),
`Errington_Illustrated_Plant_Directory.pdf` (25 pages),
`Errington_Botanical_Illustration_Collection.pdf` (138 pages), and
`Errington_Educational_Figure_Collection.pdf` (37 pages). The encyclopedia contains only its
cover image; the other PDFs contain no images. All 137 plant plates and 36 educational
figures remain unapproved concepts and are withheld. The botanical and educational review
registers retain the text descriptions and identify where artwork is pending. The monthly
guide uses wrapping table cells and separates months; extracted-text checks confirm long
calendar entries and the source-marked pea sowing action remain intact. The current rebuilt
PDFs have not received a full visual scan; publication review remains open.

The directory lists all 137 registry records without displaying unapproved artwork. The 137
generated plant candidates, 36 generated figure concepts, and 70 historical branch images
are withheld from all PDFs. No candidate or figure is represented as scientifically
approved. The owner confirms rights to the branch assets, but each requires individual
identity and anatomical review before publication. `reports/ILLUSTRATION_BRANCH_REVIEW.csv` records the
visually plausible components and the specific structures to exclude or verify for each
of the 70 branch images; its crop suggestions are not approvals.

Required human visual checklist:

- [ ] Render every page of the final PDF and visually scan the complete set of contact sheets.
- [ ] Inspect every page at print-readable resolution.
- [ ] Check clipping, missing glyphs, blank pages, text/image overlap, page breaks, margins,
  running headers, and page numbers.
- [ ] Verify every table and every TOC page number/link against the rendered PDF.
- [ ] Review each proposed illustration individually before approving or embedding it.
- [ ] Sign off editorial accuracy and confirm the climate-zone discrepancy is either
  authoritatively resolved or explicitly retained in the final edition.

No PDF is labeled `READY_FOR_REVIEW` or `APPROVED_FOR_PUBLICATION` by this report.
