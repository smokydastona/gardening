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
## Evidence preparation, generation, and review

### Style and review standards

The encyclopedia's hard visual standard is the portrait, warm-paper,
hand-drawn ink-and-watercolor botanical plate style of the
`illustration-assets` branch. Existing images are **style references, not
verified botanical evidence**. Never publish a generated or existing plate
without independent botanical and style review.

The PDF builder and the generated asset manifest accept only image files with
matching, approved JSON sidecars. The sidecar binds the approval to the image
bytes and an evidence snapshot. Missing, incomplete or changed assets are
skipped with a warning. A sign-off is a human attestation, not automatic
verification or a cryptographic signature. Existing PNGs without sidecars will
no longer appear in the PDF, including those restored from `illustration-assets`.

## Evidence and generation

From the repository root, install `requirements.txt` and, for the OpenAI
backend, install `openai` separately. Create templates:

```sh
python generate_illustrations.py templates
```

Complete `botanical_evidence/ARUGULA.json`: verify the exact accepted taxon
and cultivar, document diagnostic traits, give two distinct traceable sources
and at least two distinct local reference photographs with creator, source URL,
license and view. A named human must verify the record. Check that the licenses
permit the intended use and model processing; the script checks that license
fields are present, not that the rights or botanical claims are correct.
Templates contain registry candidates, not verified taxonomy.

Preview the prompt or produce a pending candidate:

```sh
python generate_illustrations.py generate --plant Arugula --dry-run
python generate_illustrations.py generate --plant Arugula --backend openai \
  --candidate openai-1 --style-reference /path/to/authorized-style-plate.png
```

Set `OPENAI_API_KEY` for OpenAI. The photographs and optional style plate are
sent to the provider; use only images you have permission to send. The style
reference is explicitly not botanical evidence. Output is a portrait PNG under
`plant_illustrations/pending_review/ARUGULA/`, never directly in the PDF
asset directory. The prompt deliberately omits generated lettering and borders;
add them before final review using the optional annotation step below. Style
conformity must be checked by the reviewer, not inferred from the prompt.

## Optional local backends

Install upstream dependencies and model checkpoints in separate environments.
They require CUDA-capable hardware and may require considerable GPU memory.
Review the exact checkpoint, dependency and data licenses before use. Point
`--backend-python` at the Python executable in the relevant environment.

```sh
python generate_illustrations.py generate --plant Arugula --backend o1 \
  --backend-dir /path/to/HiDream-O1-Image \
  --backend-python /path/to/o1-env/bin/python \
  --model /path/to/HiDream-O1-Image-checkpoint --model-type full \
  --candidate o1-32 --seed 32

python generate_illustrations.py generate --plant Arugula --backend i1 \
  --backend-python /path/to/i1-env/bin/python --candidate i1-32

python generate_illustrations.py generate --plant Arugula --backend kandinsky \
  --backend-dir /path/to/kandinsky-5 \
  --backend-python /path/to/kandinsky-env/bin/python --candidate k5-32
```

O1 uses the upstream multi-reference interface and supports `full` and `dev`.
I1 uses the upstream Diffusers full model and requires acceptance of its Llama
dependency license. Kandinsky uses the upstream T2I Lite configuration; verify
its checkpoint and component licenses independently. I1 and Kandinsky are
**text-only** here: they do not receive the photographs. Their outputs are
independent comparison candidates, not evidence or automated evaluators.

For O1 or OpenAI, optionally pass `--plantgen /path/to/plantc` after a human
has set `plantgen_species` in the evidence record to the exact supported
PlantGen species identifier. The tool renders a geometry aid and sends it
alongside the photographs; it is not evidence and can itself be inaccurate.
Inspect PlantGen's species traits and data source licenses before use. Generated
geometry is retained in the candidate directory for review.

## Title, border and labels

To match the reference plates without relying on generated text, add a title
and border and, optionally, manually positioned callouts. Create a JSON layout
with coordinates expressed as fractions of image width and height:

```json
{"labels": [{"text": "Leaf", "x": 0.08, "y": 0.50, "target_x": 0.35, "target_y": 0.60}]}
```

Use `{"labels": []}` for a title and border without callouts. Positions and
leader lines must be adjusted for the particular image; use only labels
supported by the evidence. The title and callouts use **The Girl Next Door**
by Kimberly Geswein by default. The bundled font is from
[Google Fonts](https://github.com/google/fonts/tree/90abd17b4f97671435798b6147b698aa9087612f/ofl/thegirlnextdoor)
and is licensed under the [SIL Open Font License 1.1](../fonts/OFL-TheGirlNextDoor.txt).

```sh
python generate_illustrations.py annotate --plant Arugula --candidate o1-32 \
  --output-candidate o1-32-plate --layout /path/to/layout.json
```

This creates a **new pending candidate**. Review the final composition,
legibility, line placement and factual correctness of every label, in addition
to the underlying botanical image. Annotation does not approve the candidate.
Override the default with `--font /path/to/font.ttf` only if that font's license
permits publication.

## Review and publication

To bring an existing portrait PNG into the same process, record its origin and
publication rights and import it against completed evidence:

```sh
python generate_illustrations.py import --plant Arugula --candidate legacy \
  --image /path/to/old-plate.png --provenance "Origin and publication rights"
```

Create a separate checklist for each candidate:

```sh
python generate_illustrations.py review-template --output /path/to/review.json
```

Inspect the *exact candidate* against the cited references. Set `style` to
`pass` only when it matches the established plate style; set `growth_habit`,
`leaves`, `stems`, `flowers`, `fruit_and_seed`, and `roots` to `pass` or
`not-depicted`. Growth habit and leaves must pass. Reject incorrect structures;
`not-depicted` is only for genuinely absent structures. Review scale,
proportions, relationships, and each visible inset as well. Notes must identify
what was compared and explain omissions or limitations.

```sh
python generate_illustrations.py approve --plant Arugula --candidate o1-32 \
  --checklist /path/to/review.json --reviewer "Reviewer name" \
  --notes "Compared visible organs and proportions against the cited sources."
```

Approval refuses changed candidates, evidence or reference photographs and
does not overwrite an existing asset. To replace a legacy image, explicitly
archive or remove the old file first. Commit the resulting `ARUGULA.png` and
`ARUGULA.json` together with the stable-ID manifest update. The
`illustration_manifest.csv` approval state controls publication; the legacy
`illustration_asset_manifest.csv` reports filename presence only. The standard
GitHub Actions build uses checked-in files and does not restore assets from
the separate `illustration-assets` branch.

Files use normalized catalog headings (for example `SWEET_PEA.png`), and the
builder also accepts approved JPEG, TIFF and WebP files with matching sidecars.
Do not treat the sidecars or checklist as an automated scientific guarantee.
