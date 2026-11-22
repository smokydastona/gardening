# Errington Gardening Encyclopedia Workspace

This workspace contains the local source material, extraction scripts, tests, structured data outputs, and generated encyclopedia artifacts for the Errington gardening encyclopedia project.

## Source Files

Primary local calendar evidence:

1. [ERRINGTON_CALENDAR_FULL_TEXT.md](ERRINGTON_CALENDAR_FULL_TEXT.md), a text extraction; the original calendar PDF is not checked into this workspace.

Supporting local sources:

1. [Planting Calander-Crops.png](Planting%20Calander-Crops.png)
2. [Planting Calander-Ornamentals.png](Planting%20Calander-Ornamentals.png)
3. [Vegetable_Gardening_Encyclopedia_With_Sp.pdf](Vegetable_Gardening_Encyclopedia_With_Sp.pdf), the supplied Reader's Digest gardening reference.
4. The user-provided 2017 Eastern Vancouver Island pollinator guide and Internet Archive plant references are documented in [ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md](ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md); they are not checked into this repository.

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
3. Restores illustration PNG assets and approval sidecars from the dedicated `illustration-assets` branch. Only human-reviewed assets whose image and evidence hashes match are included; legacy assets without approval are skipped.
4. Installs dependencies, runs the full test suite, rebuilds the encyclopedia outputs, and uploads the PDF and generated artifacts as a workflow artifact named `encyclopedia-build`.

For evidence preparation, generation, review and publication, see [the illustration workflow](plant_illustrations/README.md). Commit approved images and their JSON sidecars together on the asset branch.

The current workflow restores plant illustration assets from `origin/illustration-assets`.

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

1. The available calendar text extraction supplies detailed monthly entries; its source PDF is absent, so transcription accuracy remains a limitation.
2. The chart images independently support the frost dates and plant lists, and label the calendar Zone 8b. The text extraction labels it Zone 8a; retain this conflict.
3. The Reader's Digest PDF can inform general gardening topics but does not override local timing. Do not copy its prose or illustrations into the encyclopedia.