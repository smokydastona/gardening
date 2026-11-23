# Publication QA report

## Overall status: `IN_PROGRESS`

This working publication is not approved for publication. The PDF is a reproducible
pre-review build, not evidence that botanical claims, local planting timing, illustrations,
or editorial content are correct.

## Current baseline — 2026-11-23

The current local suite passes 78 tests. `gardening build all` rebuilt and structurally
validated the five PDFs: 219, 25, 25, 138, and 37 pages respectively. The dimensioned
verification audit is `NOT_READY`; it records zero supported claim extracts/locations among
two conflicting claim-source rows, 36 figures without source references, and zero approved
plant illustrations or educational figures. This build did not rerender every page for visual
inspection. The full-resolution and human print-size review checklist below remains open.
No hosted CI result is reported for this local increment.

| Gate | Status | Evidence / remaining work |
|---|---|---|
| A — Source integrity | `PARTIAL` | Original supplied files retained; 137 plants and 359 calendar entries are count-checked. Calendar PDF authorship/history is unknown; transcription requires further comparison. |
| B — Botanical accuracy | `FAILED` | 0 independently verified taxonomy records and 0 individually reviewed horticultural profiles. |
| C — Local horticultural accuracy | `FAILED` | 8a/8b conflict unresolved; no independently sourced Errington frost normals or plant-specific local timings. |
| D — Illustration integrity | `PARTIAL — unapproved artwork withheld` | 0 botanical illustrations and 0 educational figures are approved. The owner confirms rights to the 70 branch images; they and the generated candidates are excluded from all PDFs pending identity, anatomy, and independent botanical review. Figure concept descriptions are listed in the encyclopedia, not presented as reviewed diagrams. |
| E — Editorial quality | `PARTIAL` | The core handbook includes expanded climate-risk, microclimate, planning, botany, soil, bed-building, propagation, irrigation, and diagnostic instruction. The plant index now cross-references exact calendar transcriptions and available claim research without treating them as recommendations. A complete claim-level bibliography, plant-specific research, and editorial sign-off remain outstanding. |
| F — Publication quality | `PARTIAL` | Current PDFs have 219, 25, 25, 138, and 37 pages. Only the encyclopedia cover image is embedded; all other PDFs contain no images. Body text uses Times-Roman. Full-publication print review remains open. |
| G — Software quality | `PARTIAL` | `gardening build all`, publication validation, and 78 tests pass locally. No hosted check is reported for this increment. |
| H — Pre-owned encyclopedia theme | `PARTIAL — release blocked` | The automated gate requires distributed editorial notes in three embedded handwriting fonts and at least three ink colors. Representative pages were inspected, but a full human print-size review of the theme and legibility remains mandatory. |

## Latest build and visual scan

The regenerated products are `Errington_Gardening_Encyclopedia.pdf` (219 pages),
`Errington_Monthly_Gardening_Guide.pdf` (25 pages),
`Errington_Illustrated_Plant_Directory.pdf` (25 pages),
`Errington_Botanical_Illustration_Collection.pdf` (138 pages), and
`Errington_Educational_Figure_Collection.pdf` (37 pages). The encyclopedia contains only its
cover image; the other PDFs contain no images. All 137 plant plates and 36 educational
figure images remain unapproved concepts and are withheld. The encyclopedia now includes
plant-by-plant calendar cross-references, available claim research, and text descriptions
of the educational figure concepts; none is represented as verified advice or reviewed
artwork. The botanical and educational review registers retain the detailed descriptions
and identify where artwork is pending. The monthly
guide uses wrapping table cells and separates months; extracted-text checks confirm long
calendar entries and the source-marked pea sowing action remain intact. The current rebuilt
PDFs have not received a full visual scan; publication review remains open. Earlier page
renders and contact sheets are historical artifacts and are not represented as a visual
inspection of this 219-page build.

The encyclopedia includes aged-paper styling and editorial handwritten-style notes in
Reenie Beanie, Indie Flower, and Architects Daughter, with several pen-ink colors. The
front matter identifies these as design additions, not historical annotations or
independent evidence. The theme is a mandatory release gate for every edition; automated
structural checks do not replace a complete human visual review.

The encyclopedia's plant field index lists all 137 registry records, links each to matching
calendar source rows and available claim research, and omits generic profile boilerplate.
Grouped calendar records remain explicitly grouped; the index does not convert them into
plant-specific recommendations. The 137 generated plant candidates, 36 generated figure images, and 70 historical branch
images are withheld from all PDFs. No candidate or figure is represented as scientifically
approved. The owner confirms rights to the branch assets, but each requires individual
identity and anatomical review before publication. `reports/ILLUSTRATION_BRANCH_REVIEW.csv` records the
visually plausible components and the specific structures to exclude or verify for each
of the 70 branch images; its crop suggestions are not approvals.

Required human visual checklist:

- [ ] Render every page of the final PDF and visually scan the complete set of contact sheets.
- [ ] Inspect every page at print-readable resolution.
- [ ] Check clipping, missing glyphs, blank pages, text/image overlap, page breaks, margins,
  running headers, and page numbers.
- [ ] Confirm the pre-owned-book appearance, varied handwritten notes and inks, contrast,
  and print-size readability throughout the encyclopedia.
- [ ] Verify every table and every TOC page number/link against the rendered PDF.
- [ ] Review each proposed illustration individually before approving or embedding it.
- [ ] Sign off editorial accuracy and confirm the climate-zone discrepancy is either
  authoritatively resolved or explicitly retained in the final edition.

No PDF is labeled `READY_FOR_REVIEW` or `APPROVED_FOR_PUBLICATION` by this report.
