# Errington Gardening Encyclopedia Workspace

This workspace contains the local source material, extraction scripts, tests, structured data outputs, and generated encyclopedia artifacts for the Errington gardening encyclopedia project.

## Source Files

Primary local source:

1. [Errington BC Zone 8a Planting Calendar.pdf](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Errington%20BC%20Zone%208a%20Planting%20Calendar.pdf)

Supporting local sources:

1. [Planting Calander-Crops.png](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Planting%20Calander-Crops.png)
2. [Planting Calander-Ornamentals.png](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Planting%20Calander-Ornamentals.png)
3. [Vegetable_Gardening_Encyclopedia_With_Sp.pdf](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Vegetable_Gardening_Encyclopedia_With_Sp.pdf)

## Python Environment

Tested with Python 3.12 on Windows.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Validation

Run the automated tests:

```powershell
python -m pytest test_parse_errington_calendar.py test_enrich_plant_registry.py
```

## Build Pipeline

Run the full local pipeline:

```powershell
python extract_calendar_data.py
python parse_errington_calendar.py
python enrich_plant_registry.py
python build_encyclopedia_outputs.py
python build_final_encyclopedia_pdf.py
```

## GitHub Actions Build

The canonical release build can run entirely on GitHub from the checked-in source files and illustration assets.

Workflow:

1. [.github/workflows/build-encyclopedia.yml](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/.github/workflows/build-encyclopedia.yml)

Behavior:

1. Triggers on `workflow_dispatch`, pushes to `main`, and pull requests that touch the build inputs.
2. Checks out the repository on GitHub-hosted runners, so it uses the assets committed to the repo rather than local-only files.
3. Installs dependencies, runs the full test suite, rebuilds the encyclopedia outputs, and uploads the PDF and generated artifacts as a workflow artifact named `encyclopedia-build`.

If you want the build to include plant illustrations, add the actual image files to [plant_illustrations](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/plant_illustrations) and push them. The workflow runner will use those committed assets automatically.

## Generated Artifacts

Structured source outputs:

1. [ERRINGTON_CALENDAR_FULL_TEXT.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/ERRINGTON_CALENDAR_FULL_TEXT.md)
2. [errington_calendar_entries.csv](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/errington_calendar_entries.csv)
3. [errington_calendar_entries.json](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/errington_calendar_entries.json)
4. [errington_calendar_plant_summary.csv](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/errington_calendar_plant_summary.csv)
5. [plant_registry_enriched.csv](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/plant_registry_enriched.csv)

Reader-facing outputs:

1. [ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md)
2. [ERRINGTON_MONTHLY_REFERENCE.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/ERRINGTON_MONTHLY_REFERENCE.md)
3. [ERRINGTON_PLANT_CATALOG.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/ERRINGTON_PLANT_CATALOG.md)
4. [ERRINGTON_ILLUSTRATION_BRIEFS_AND_PROMPTS.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/ERRINGTON_ILLUSTRATION_BRIEFS_AND_PROMPTS.md)
5. [errington_illustration_briefs.csv](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/errington_illustration_briefs.csv)
6. [Errington_Gardening_Encyclopedia_Compiled.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Errington_Gardening_Encyclopedia_Compiled.md)
7. [Errington_Gardening_Encyclopedia.pdf](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/Errington_Gardening_Encyclopedia.pdf)

Working project records:

1. [ERRINGTON_ENCYCLOPEDIA_HANDOFF.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/ERRINGTON_ENCYCLOPEDIA_HANDOFF.md)
2. [SOURCE_AUDIT.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/SOURCE_AUDIT.md)
3. [ENCYCLOPEDIA_STRUCTURE.md](c:/Users/smoky/OneDrive/Desktop/Homemade%20Mods/My%20Gardening%20Encyclopedia/ENCYCLOPEDIA_STRUCTURE.md)

## Implementation Notes

1. The direct Errington PDF is the authoritative local timing source in this workspace.
2. The chart images are retained as cross-checks and for OCR-based extraction artifacts.
3. The original vegetable encyclopedia PDF is used for structure, illustration plates, and general gardening guidance, but it does not override Errington-specific timing.