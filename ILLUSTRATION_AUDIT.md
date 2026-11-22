# Illustration audit

## Status: `IN_PROGRESS` — no image approved for publication

The plant registry contains 137 records. The current checkout contains no per-plant image files. The `illustration-assets` branch has a separate collection of 70 image files, but the assets are not checked out by this deterministic build and their visual identities, creators, licenses, and review histories have not been independently established.

The stable-ID manifest at `plant_illustrations/illustration_manifest.csv` does not associate any image based on a filename alone. Every asset remains `pending` review and `not-approved`; no unreviewed plant art is embedded in the publication.

Before approval, retrieve the external assets under controlled review, check identity, anatomy, resolution, duplicates, attribution, and license, then record reviewer notes against the stable plant ID. Preserve originals when rejecting an image.
