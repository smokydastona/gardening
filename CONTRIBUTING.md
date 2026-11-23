# Contributing

## Development

Use Python 3.12 and the pinned dependency set:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/gardening validate
.venv/bin/gardening test
```

Use `gardening --help` for supported commands. The package CLI currently wraps established
root-level pipeline programs; keep those adapters working until a replacement is migrated,
tested, and adopted by CI.

## Evidence and data changes

- Never edit supplied evidence or transcription layers to make derived material look verified.
- Preserve the 137 plant IDs and 359 calendar entries unless the change includes documented,
  independently reviewed evidence and updates the data-integrity checks.
- Add claim-level citations and keep source transcription, research, editorial interpretation,
  and recommendations distinguishable.
- Do not infer a local planting date from the supplied calendar alone.
- Keep the unresolved Zone 8a/8b disagreement explicit.

## Illustration changes

- Treat generated and imported art as a candidate.
- Preserve source URL, creator, license, method, evidence links, and SHA-256.
- Never infer identity from a filename or appearance alone.
- Only the existing hash-bound human approval process can make an asset publication-eligible.
- Preserve rejected assets and their reasons; do not overwrite originals.

## Pull requests

Keep changes focused and run the relevant tests plus the publication validation when applicable:

```sh
.venv/bin/gardening test
.venv/bin/gardening build all
```

Do not claim hosted CI passed until a successful run exists for the exact revision. A software
test pass is not botanical, rights, or publication approval. Include the current release status
and known review requirements in the pull-request description.

See [repository architecture](docs/architecture/REPOSITORY_ARCHITECTURE.md) and
[build and release](docs/BUILD_AND_RELEASE.md) for ownership and publication gates.
