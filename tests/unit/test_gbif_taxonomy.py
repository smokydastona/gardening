import json
from datetime import datetime, timezone
from email.message import Message
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

import pytest

from gardening.research.gbif import (
    collect_gbif_candidates,
    fetch_gbif_candidate,
)


REPOSITORY = Path(__file__).resolve().parents[2]


class FakeResponse:
    def __init__(self, payload, *, content_type="application/json", final_url=None):
        self.body = json.dumps(payload).encode("utf-8")
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        self.final_url = final_url or "https://api.gbif.org/v1/species/match"

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def getcode(self):
        return 200

    def geturl(self):
        return self.final_url

    def read(self, _limit):
        return self.body


def test_gbif_match_is_recorded_as_candidate_not_verified():
    response = FakeResponse(
        {
            "usageKey": 123,
            "scientificName": "Eruca vesicaria (L.) Cav.",
            "canonicalName": "Eruca vesicaria",
            "rank": "SPECIES",
            "status": "ACCEPTED",
            "confidence": 96,
            "matchType": "EXACT",
            "family": "Brassicaceae",
            "alternatives": [{"usageKey": 456}],
        },
        final_url="https://api.gbif.org/v1/species/match",
    )
    requests = []

    def opener(request, timeout):
        requests.append((request, timeout))
        return response

    result = fetch_gbif_candidate(
        "Eruca vesicaria subsp. sativa",
        opener=opener,
        endpoint="https://api.gbif.org/v1/species/match",
    )

    assert result["fetch_status"] == "MATCHED"
    assert result["verification_status"] == "REQUIRES_HUMAN_REVIEW"
    assert result["match"]["usage_key"] == 123
    assert result["match"]["alternatives"] == [{"usageKey": 456}]
    assert parse_qs(urlsplit(requests[0][0].full_url).query)["name"] == [
        "Eruca vesicaria subsp. sativa"
    ]


def test_gbif_respects_retry_after_and_preserves_no_match():
    retry_headers = Message()
    retry_headers["Retry-After"] = "3"
    calls = []
    delays = []

    def opener(request, timeout):
        calls.append(request)
        if len(calls) == 1:
            raise HTTPError(request.full_url, 429, "rate limited", retry_headers, BytesIO())
        return FakeResponse({"confidence": 0, "alternatives": []})

    result = fetch_gbif_candidate(
        "Unknown example",
        opener=opener,
        sleep=delays.append,
    )

    assert result["fetch_status"] == "NO_MATCH"
    assert result["verification_status"] == "REQUIRES_HUMAN_REVIEW"
    assert delays == [3.0]
    assert len(calls) == 2


def test_gbif_access_denial_is_not_reported_as_a_missing_taxon():
    def opener(request, timeout):
        raise HTTPError(request.full_url, 403, "forbidden", Message(), BytesIO())

    result = fetch_gbif_candidate("Eruca vesicaria", opener=opener)

    assert result["fetch_status"] == "ACCESS_DENIED"
    assert result["http_status"] == 403
    assert result["match"]["usage_key"] is None


def test_gbif_candidate_cache_avoids_duplicate_network_requests(tmp_path):
    cache = tmp_path / "cache"
    calls = []

    def fetcher(name, *, timeout, sleep):
        calls.append(name)
        return {
            "provider": "GBIF",
            "input_name": name,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "fetch_status": "MATCHED",
            "verification_status": "REQUIRES_HUMAN_REVIEW",
        }

    first = collect_gbif_candidates(
        REPOSITORY,
        cache_directory=cache,
        plant_id="plant-arugula",
        fetcher=fetcher,
    )
    second = collect_gbif_candidates(
        REPOSITORY,
        cache_directory=cache,
        plant_id="plant-arugula",
        fetcher=fetcher,
    )

    assert first["network_requests"] == 1
    assert second["network_requests"] == 0
    assert len(calls) == 1
    assert second["candidate_only"] is True
    assert second["results"][0]["plant_id"] == "plant-arugula"
    with pytest.raises(ValueError, match="Unknown plant ID"):
        collect_gbif_candidates(
            REPOSITORY,
            cache_directory=cache,
            plant_id="plant-missing",
            fetcher=fetcher,
        )
