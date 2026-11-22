# Illustration audit

## Status: `IN_PROGRESS` — no image approved for publication

The plant registry contains 137 records. The current checkout contains no per-plant image files. The `illustration-assets` branch has a separate collection of 70 image files, but the assets are not checked out by this deterministic build and their visual identities, creators, licenses, and review histories have not been independently established.

The stable-ID manifest at `plant_illustrations/illustration_manifest.csv` does not associate any image based on a filename alone. Every asset remains `pending` review and `not-approved`; no unreviewed plant art is embedded in the publication.

The repository includes an evidence-gated candidate generation and human-review workflow. Approval sidecars bind sign-off to image and evidence hashes; the publication builder also requires an explicit stable-ID manifest association. This is a review control, not a claim that any current plant or image has been independently verified.

The standard build does not retrieve assets from `illustration-assets`. Before reuse, bring an external asset into the review process under controlled conditions; check identity, anatomy, resolution, duplicates, attribution, and license, then record reviewer notes against the stable plant ID. Preserve originals when rejecting an image.
