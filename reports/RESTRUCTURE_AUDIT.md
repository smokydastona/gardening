# Repository restructuring baseline

- Main head: `037ced5e9d2b9f94cb830b41c5bc83be8062e3e0`.
- Illustration branch head: `c7bdbde9e5fc81c514a40decc7b9bfcdb1f00da5`.
- Merge base: `e39f16b7b05426e3d2c3731ee8843fead7f27b26`.
- Main-only commits since merge base: 38; illustration-branch-only commits: 9.
- Available tags: 0 (`none`).
- Pull request audit: PR #1 was the only pre-existing pull request found; it is merged into `main`.
- Main tree: 559 tracked files; illustration branch tree: 122 tracked files.
- Historical plant-image branch: 70 image files, 68 distinct SHA-256 payloads.
- The inventory includes inferred tracked directories, Git blob IDs, file sizes, SHA-256 hashes, duplicate-path candidates, and last modification dates visible in the locally fetched Git history. It excludes untracked files and ignored environments/build outputs.
- Perceptual-hash screening found 3 possible near-duplicate pairs at Hamming distance ≤5; these are not identity findings.

## Branch decision

`main` is the canonical implementation and is materially newer. The older `illustration-assets` branch diverges from the common ancestor and lacks current validation, evidence, and publication safeguards. It is not safe to merge wholesale.
Its 70 plant images remain on that branch. Existing per-image review records identify 68 unique payloads, duplicate pairs, nine filename/registry mismatches, and cross-plant labels. Because the image set is approximately 249 MB and remains unapproved, binary import is deferred; the branch and checksummed migration manifest preserve access without bloating `main` or bypassing review.

## Migration files

- `reports/REPOSITORY_INVENTORY.csv` — file and inferred-directory inventory by ref.
- `reports/REPOSITORY_MIGRATION_MANIFEST.csv` — per-path comparison, proposed destination, disposition, and human-review flag.
- `reports/ILLUSTRATION_BRANCH_REVIEW.csv` — existing per-image review record.
- `reports/ILLUSTRATION_SIMILARITY_AUDIT.csv` — per-image perceptual hash and near-duplicate candidates for human inspection.

The local repository was unshallowed before computing ancestry. No branch or tag was deleted, rebased, force-pushed, or rewritten.
