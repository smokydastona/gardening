# Errington Encyclopedia Source Audit

## Purpose

This file records the current source set, what each source can support, and where uncertainty still remains.

## Source Priority

1. Errington calendar text extraction and the checked-in crop and ornamental images. Preserve the images' Zone 8b label and the text extraction's Zone 8a label as an unresolved conflict.
2. The 2017 Eastern Vancouver Island pollinator guide for regional ecology and pollinator-habitat guidance, not Errington-specific timing.
3. The user-supplied plant reference books for plant facts, with exact edition and page citations verified before publication.
4. The Reader's Digest gardening PDF for general practices, not local climate or planting dates.
5. Authoritative botanical and horticultural references for verification where the supplied sources do not resolve a plant-level fact.

## Local Sources

### Errington Calendar Text Extraction

File: [ERRINGTON_CALENDAR_FULL_TEXT.md](ERRINGTON_CALENDAR_FULL_TEXT.md). The original 89-page calendar PDF referred to in project records is not checked into this workspace; the extraction has 89 page headings.

The extraction reports Zone 8a, approximate last and first frost dates of April 15 and October 15, approximately 183 frost-free days, approximately 1,200 mm annual rainfall, and winter lows rarely below -12 C. It contains monthly edible and ornamental timing records. These are source-reported values; extraction formatting and the absent original PDF limit direct re-verification.

The summary images independently show the April 15 and October 15 frost anchors but are branded Zone 8b. Preserve the Zone 8a/8b discrepancy; do not silently select one label.

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

### Eastern Vancouver Island Pollinator Guide

File: session-provided `E.Vancouver.Isl.2017.ver6.pdf`, titled *Selecting Plants for Pollinators: A Guide for Gardeners, Farmers, and Land Managers in the Eastern Vancouver Island Ecoregion*. PDF metadata dates its creation to 2017; the guide credits Pollinator Partnership Canada and the North American Pollinator Protection Campaign.

Supports regional ecoregion context, pollinator food/shelter/water needs, home-landscape practices, nesting habitat, and a regional plant table with flowering periods (pp. 3, 6, 10, 12-21).

Limitations:

1. The Eastern Vancouver Island ecoregion is broader than Errington; its climate ranges and bloom periods are not Errington-specific measurements.
2. The uploaded PDF is outside the repository and is not included in CI builds. The encyclopedia contains an attributed original summary of selected guidance, not a transcription of the guide.

### User-Provided Plant Reference Books

1. *Encyclopedia of Plants and Flowers*: https://archive.org/details/encyclopediaofplantsandflowers
2. *Trees, Leaves, Flowers and Seeds: A Visual Encyclopedia of the Plant Kingdom* (DK, 2019): https://archive.org/details/trees-leaves-flowers-and-seeds-a-visual-encyclopedia-of-the-plant-kingdom-dk-2019/mode/2up
3. *Illustrated Encyclopedia*: https://archive.org/details/illustratedencyc00wrig/page/38/mode/2up

Use these as reference sources for plant entries. Confirm the exact title, edition, and page for each claim before citing it in the encyclopedia. Do not copy their prose or illustrations into the compiled work.

### Reader's Digest Gardening Reference PDF

File: [Vegetable_Gardening_Encyclopedia_With_Sp.pdf](/c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Vegetable_Gardening_Encyclopedia_With_Sp.pdf)

Verified facts:

1. The file is locally readable with Python and `pypdf`.
2. It is 261 pages long.
3. It appears to be a general vegetable gardening encyclopedia rather than an Errington-local document.
4. It includes PDF bookmarks that expose its high-level structure. The file metadata does not identify a title, author, or publication details.

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

For new material, record the source and page alongside the claim. Keep ecoregion-level facts separate from Errington observations, and keep source wording and artwork out of the encyclopedia unless reuse permission is established.

## Immediate Next Work

1. Recover or obtain the original Errington calendar PDF so the extracted monthly data can be checked against its pages.
2. Resolve the 8a/8b label discrepancy only if a source establishes which label applies; otherwise keep both claims.
3. The 137-record registry now has bulk taxonomy and cultural profiles. Resolve the entries marked `taxonomy-requires-species-or-cultivar-resolution` and add cultivar-specific values.
4. Keep pollinator guide climate and bloom data labeled as Eastern Vancouver Island ecoregion-wide rather than Errington-specific.