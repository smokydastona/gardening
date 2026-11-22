# Illustration audit

## Status: `IN_PROGRESS` — illustration review remains incomplete

The plant registry contains 137 records. 0 illustration associations have an approved manifest entry and valid human-review sidecar. The original audit found 70 images on the separate `illustration-assets` branch, without documented identity, creator, license, or review history.

The stable-ID manifest at `plant_illustrations/illustration_manifest.csv` does not associate any image based on a filename alone. The PDF builder requires both a stable plant ID and a valid hash-bound review sidecar.

The candidate-generation workflow can use optional OpenAI or Gemini backends. A generated candidate is not botanical evidence or an approved illustration.

Before approval, retrieve the external assets under controlled review, check identity, anatomy, resolution, duplicates, attribution, and license, then record reviewer notes against the stable plant ID. Preserve originals when rejecting an image.
