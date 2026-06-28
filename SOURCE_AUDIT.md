# Errington Encyclopedia Source Audit

## Purpose

This file records the current source set, what each source can support, and where uncertainty still remains.

## Source Priority

1. Direct local Errington calendar PDF in this workspace.
2. Local Errington calendar images in this workspace.
3. User-provided Errington calendar details preserved in the shared Copilot plan.
4. Local generic vegetable encyclopedia PDF for structure and general non-local reference.
5. External authoritative botanical and horticultural references for later verification.

## Local Sources

### Direct Errington Calendar PDF

File: [Errington BC Zone 8a Planting Calendar.pdf](/c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Errington%20BC%20Zone%208a%20Planting%20Calendar.pdf)

Supports:

1. Direct local climate summary for Errington, BC, Zone 8a.
2. Monthly edible crop tables.
3. Monthly flower and ornamental tables.
4. Local frost guidance and monthly tips.
5. Structured timing entries that are substantially richer than the summary chart images.

Verified facts:

1. The PDF is 89 pages long.
2. It extracts readable text with `pypdf`.
3. It explicitly states: Zone 8a, last frost approximately April 15, first frost approximately October 15, frost-free period approximately 183 days, annual rainfall approximately 1,200 mm, winter lows rarely below -12 C.
4. It is organized as monthly two-page spreads with Page A for edible crops and Page B for flowers and ornamentals.

Derived workspace artifacts:

1. [ERRINGTON_CALENDAR_FULL_TEXT.md](/c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/ERRINGTON_CALENDAR_FULL_TEXT.md) is a searchable full-text extraction of the PDF.

Limitations:

1. Page text is readable but still imperfect in formatting after extraction.
2. The PDF does not remove the need for later botanical verification of Latin names and families.

### Errington Crop Calendar Image

File: [Planting Calander-Crops.png](/c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Planting%20Calander-Crops.png)

Supports:

1. Frost anchor dates of April 15 and October 15.
2. Crop list visible on the chart.
3. Color legend for indoor sow, transplant, and direct sow or harvest.
4. A partial set of day counts and note fragments.

Limitations:

1. Several plant names are visibly misspelled.
2. Fine timing detail is not clean enough to treat every cell as authoritative without further extraction.
3. Right-column notes are not fully legible.

### Errington Ornamental Calendar Image

File: [Planting Calander-Ornamentals.png](/c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Planting%20Calander-Ornamentals.png)

Supports:

1. Frost anchor dates of April 15 and October 15.
2. Annual, perennial, bulb, and ornamental plant lists visible on the chart.
3. Color legend for indoor sow, transplant, direct sow, bloom, and dormant or divide.
4. A partial set of cultural note fragments.

Limitations:

1. The image appears to be a summary chart rather than a full worksheet.
2. Several notes are only partly legible.
3. Not all likely ornamental scope from the broader plan is visible here.

### Generic Vegetable Encyclopedia PDF

File: [Vegetable_Gardening_Encyclopedia_With_Sp.pdf](/c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Vegetable_Gardening_Encyclopedia_With_Sp.pdf)

Verified facts:

1. The file is locally readable with Python and `pypdf`.
2. It is 261 pages long.
3. It appears to be a general vegetable gardening encyclopedia rather than an Errington-local document.
4. It includes usable PDF bookmarks that expose its high-level structure.

Recovered bookmark structure:

1. Planning Your Garden
2. Spadework - the Essential
3. Planting Your Garden
4. Caring for the Garden
5. Keeping the Garden Healthy
6. The Plants - Vegetables
7. Herbs
8. How to Store Vegetables
9. How to Freeze Vegetables
10. How to Dry Vegetables
11. How to Sprout Vegetables
12. Storing Herbs

How to use it:

1. Use it as a structural and topical backbone for general vegetable-gardening chapters.
2. Do not use it as the timing authority when it conflicts with Errington-local calendars.
3. Use it as a likely source for categories such as planning, soil prep, care, health, vegetables, herbs, and storage.

Limitations:

1. It is not localized to Errington.
2. Its extracted text is noisy in places due to PDF quality.
3. It does not cover the ornamental scope implied by the Errington project.

## Current Evidence Model

Use these labels in working files:

1. `verified-local` for facts directly visible in local workspace sources.
2. `shared-plan` for information recovered from the shared Copilot conversation but not yet re-verified locally.
3. `backbone-generic` for structure or general guidance taken from the PDF.
4. `pending-verification` for anything that still needs direct confirmation.

## Immediate Next Work

1. Parse the direct Errington PDF into structured monthly and per-plant timing data.
2. Populate [plant_registry.csv](/c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/plant_registry.csv) from the direct local PDF before relying on the summary images.
3. Use the summary images as cross-checks rather than as the main timing source.
4. Continue drafting the encyclopedia from direct local text instead of image inference wherever possible.