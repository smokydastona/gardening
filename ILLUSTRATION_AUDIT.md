# Illustration audit

## Status: `IN_PROGRESS` — illustration review remains incomplete

The plant registry contains 137 records. 0 illustration associations have an approved manifest entry and valid human-review sidecar.

The separate `illustration-assets` branch was inspected at commit `c7bdbde9e5fc81c514a40decc7b9bfcdb1f00da5`. Its 70 image files are valid 1024 × 1536 PNGs, but contain only 68 unique byte sequences. The duplicate pairs are `Hellebore.png` / `hellebores.png` and `Ranunculus.png` / `ranunculus.png`. Nine filenames do not exactly match a registry display name and require explicit identity reconciliation.

Contact-sheet inspection found cross-plant text in at least two plates: `Hyacinth.png` labels its seed inset as “Gladiolus Seeds,” and `Tulip.png` labels its seed inset as “Camassia Seeds.” This is sufficient to reject filename-based association or automatic approval; the remaining candidates also require individual botanical, licensing, and attribution review.

The stable-ID manifest at `plant_illustrations/illustration_manifest.csv` does not associate any image based on a filename alone. The PDF builder requires both a stable plant ID and a valid hash-bound review sidecar.

The candidate-generation workflow can use optional OpenAI or Gemini backends. No candidate was generated in this implementation run: neither `OPENAI_API_KEY` nor `GEMINI_API_KEY` was configured in the execution environment. A generated candidate would still require human botanical, attribution, and license review before publication.

Before approval, retrieve the external assets under controlled review, check identity, anatomy, resolution, duplicates, attribution, and license, then record reviewer notes against the stable plant ID. Preserve originals when rejecting an image.
