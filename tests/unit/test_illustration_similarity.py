from __future__ import annotations

import io

from PIL import Image, ImageDraw

from scripts.migration.audit_illustration_similarity import _distance, _phash


def _png(draw: bool) -> bytes:
    image = Image.new("RGB", (128, 128), "white")
    if draw:
        ImageDraw.Draw(image).ellipse((35, 25, 95, 105), fill="darkgreen")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_perceptual_hash_is_stable_and_separates_distinct_shapes() -> None:
    plain_hash, _, _ = _phash(_png(False))
    same_hash, _, _ = _phash(_png(False))
    drawn_hash, _, _ = _phash(_png(True))

    assert _distance(plain_hash, same_hash) == 0
    assert _distance(plain_hash, drawn_hash) > 0
