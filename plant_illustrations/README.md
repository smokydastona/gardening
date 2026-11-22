# Plant illustrations

Per-plant illustration association is controlled by
[`illustration_manifest.csv`](illustration_manifest.csv). Use the stable plant ID, not a
loose filename match. The manifest separates image source, creator, license, generation,
review, and approval.

## Approval requirements

An image is not eligible for the publication PDF until its identity and botanical
plausibility have been checked, its creator and license are documented, and review notes
are recorded for the plant ID. Set `approval_status=approved` only after that review. The
PDF builder fails if an approved asset is missing or has an invalid filename; unapproved
images are never embedded.

The separate `illustration-assets` branch contains 70 image files, but those assets are not
retrieved by CI or the deterministic build. Their identity, attribution, and license remain
unverified. Do not copy or associate an asset until it has been reviewed.

## Generated manifests

- `illustration_manifest.csv` is the stable-ID source of truth.
- `illustration_asset_manifest.csv` and `.md` are legacy presence reports; they do not
  approve images.
- `missing_illustrations.txt` lists expected filenames not present in this checkout.
