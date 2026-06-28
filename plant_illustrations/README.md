# Plant Illustration Assets

Place one scientifically accurate plant illustration file in this folder for each plant that should appear in the encyclopedia PDF.

The PDF builder automatically looks for image files here when rendering the `Plant Catalog` section.

## Supported Formats

1. `.png`
2. `.jpg`
3. `.jpeg`
4. `.tif`
5. `.tiff`
6. `.webp`

## Naming Rule

Name each file after the plant heading used in the catalog, normalized to letters, numbers, and underscores.

Examples:

1. `Allium.png`
2. `Sweet_Pea.png`
3. `Brussels_Sprouts.png`
4. `Red_Flowering_Currant.png`
5. `Clematis_Group_3.png`

The builder normalizes names case-insensitively, so `allium.png` and `Allium.png` both resolve to the same catalog heading.

## Generated Tracking Files

The workspace now generates these files in this folder:

1. `illustration_asset_manifest.csv` - one row per plant with the expected filename and current presence status.
2. `illustration_asset_manifest.md` - a quick readable checklist version of the manifest.
3. `missing_illustrations.txt` - the exact filenames still missing from this folder.

## GitHub Actions Asset Source

The GitHub Actions build restores committed plant illustration PNG files from the `illustration-assets` branch before rebuilding the PDF.

That means the current checkout can remove those PNG files after they are safely committed to `illustration-assets`, while the remote workflow still has a canonical source for rebuilding the illustrated encyclopedia.

## Current Limitation

The workspace does not yet contain the required per-plant illustration image files. Until they are added here, the PDF can only include the cover image and the reused reference-book plates.