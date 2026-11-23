from __future__ import annotations

import hashlib
import json
import tempfile
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


GBIF_MATCH_ENDPOINT = "https://api.gbif.org/v1/species/match"
MAX_RESPONSE_BYTES = 1_000_000
RETRYABLE_HTTP_STATUSES = {429, 500, 502, 503, 504}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _retry_delay(header: str | None, attempt: int) -> float:
    if header:
        try:
            return min(30.0, max(1.0, float(header)))
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(header)
                return min(
                    30.0,
                    max(1.0, (retry_at - datetime.now(timezone.utc)).total_seconds()),
                )
            except (TypeError, ValueError, OverflowError):
                pass
    return min(30.0, float(2**attempt))


def _result(
    *,
    input_name: str,
    request_url: str,
    status: str,
    error: str = "",
    response: dict[str, Any] | None = None,
    response_bytes: bytes = b"",
    final_url: str = "",
    http_status: int | None = None,
    content_type: str = "",
) -> dict[str, Any]:
    response = response or {}
    return {
        "provider": "GBIF",
        "input_name": input_name,
        "request_url": request_url,
        "retrieved_at_utc": _utc_now(),
        "fetch_status": status,
        "final_url": final_url,
        "http_status": http_status,
        "content_type": content_type,
        "response_sha256": hashlib.sha256(response_bytes).hexdigest()
        if response_bytes
        else "",
        "match": {
            "usage_key": response.get("usageKey"),
            "scientific_name": response.get("scientificName"),
            "canonical_name": response.get("canonicalName"),
            "authorship": response.get("authorship"),
            "rank": response.get("rank"),
            "taxonomic_status": response.get("status"),
            "confidence": response.get("confidence"),
            "match_type": response.get("matchType"),
            "family": response.get("family"),
            "alternatives": response.get("alternatives", []),
            "diagnostics": response.get("diagnostics", {}),
        },
        "raw_response": response,
        "verification_status": "REQUIRES_HUMAN_REVIEW",
        "error": error,
    }


def fetch_gbif_candidate(
    scientific_name: str,
    *,
    timeout: float = 20.0,
    opener: Callable[..., Any] = urlopen,
    sleep: Callable[[float], None] = time.sleep,
    endpoint: str = GBIF_MATCH_ENDPOINT,
) -> dict[str, Any]:
    name = scientific_name.strip()
    if not name:
        raise ValueError("A non-empty recorded scientific name is required.")
    if timeout <= 0:
        raise ValueError("Timeout must be positive.")
    endpoint_parts = urlsplit(endpoint)
    if endpoint_parts.scheme != "https" or not endpoint_parts.netloc:
        raise ValueError("GBIF API endpoint must be an absolute HTTPS URL.")

    query = urlencode({"name": name, "strict": "false", "verbose": "true"})
    request_url = urlunsplit(
        (endpoint_parts.scheme, endpoint_parts.netloc, endpoint_parts.path, query, "")
    )
    request = Request(
        request_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Errington-Gardening-Encyclopedia/1.0 (research candidate lookup)",
        },
    )
    for attempt in range(3):
        try:
            with opener(request, timeout=timeout) as response:
                http_status = response.getcode()
                content_type = response.headers.get_content_type()
                final_url = response.geturl()
                body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                return _result(
                    input_name=name,
                    request_url=request_url,
                    status="UNKNOWN",
                    error=f"Response exceeds {MAX_RESPONSE_BYTES} bytes.",
                    response_bytes=body[:MAX_RESPONSE_BYTES],
                    final_url=final_url,
                    http_status=http_status,
                    content_type=content_type,
                )
            if content_type != "application/json":
                return _result(
                    input_name=name,
                    request_url=request_url,
                    status="UNKNOWN",
                    error=f"Expected application/json, received {content_type or 'unknown'}.",
                    response_bytes=body,
                    final_url=final_url,
                    http_status=http_status,
                    content_type=content_type,
                )
            try:
                payload = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                return _result(
                    input_name=name,
                    request_url=request_url,
                    status="UNKNOWN",
                    error=f"Invalid JSON response: {error}",
                    response_bytes=body,
                    final_url=final_url,
                    http_status=http_status,
                    content_type=content_type,
                )
            if not isinstance(payload, dict):
                return _result(
                    input_name=name,
                    request_url=request_url,
                    status="UNKNOWN",
                    error="GBIF response is not a JSON object.",
                    response_bytes=body,
                    final_url=final_url,
                    http_status=http_status,
                    content_type=content_type,
                )
            return _result(
                input_name=name,
                request_url=request_url,
                status="MATCHED" if payload.get("usageKey") else "NO_MATCH",
                response=payload,
                response_bytes=body,
                final_url=final_url,
                http_status=http_status,
                content_type=content_type,
            )
        except HTTPError as error:
            if error.code in RETRYABLE_HTTP_STATUSES and attempt < 2:
                delay = _retry_delay(error.headers.get("Retry-After"), attempt)
                error.close()
                sleep(delay)
                continue
            status = (
                "ACCESS_DENIED"
                if error.code in {401, 403}
                else "CONTENT_WITHDRAWN"
                if error.code == 410
                else "TEMPORARILY_UNAVAILABLE"
                if error.code in RETRYABLE_HTTP_STATUSES
                else "UNKNOWN"
            )
            return _result(
                input_name=name,
                request_url=request_url,
                status=status,
                error=f"GBIF returned HTTP {error.code}.",
                http_status=error.code,
            )
        except (OSError, URLError) as error:
            return _result(
                input_name=name,
                request_url=request_url,
                status="UNREACHABLE",
                error=f"GBIF request failed: {error}",
            )
    raise RuntimeError("GBIF retry loop exited unexpectedly.")


def _load_registry(repository: Path) -> list[dict[str, str]]:
    import csv

    path = repository / "plant_registry.csv"
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not {"plant_id", "display_name", "latin_name"}.issubset(
                reader.fieldnames or ()
            ):
                raise ValueError("Plant registry is missing required taxonomy columns.")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as error:
        raise ValueError(f"Cannot read plant registry: {error}") from error
    identifiers = [row["plant_id"].strip() for row in rows]
    if any(not identifier for identifier in identifiers) or len(set(identifiers)) != len(identifiers):
        raise ValueError("Plant registry contains blank or duplicate plant IDs.")
    return rows


def _read_cache(path: Path, scientific_name: str, max_age_days: int) -> dict[str, Any] | None:
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
        retrieved = datetime.fromisoformat(cached["retrieved_at_utc"])
        age_seconds = (datetime.now(timezone.utc) - retrieved).total_seconds()
        if (
            cached.get("input_name") == scientific_name
            and cached.get("provider") == "GBIF"
            and 0 <= age_seconds <= max_age_days * 86400
        ):
            return cached
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return None


def _write_cache(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_name = stream.name
            stream.write(payload)
        Path(temporary_name).replace(path)
    except OSError:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
        raise


def collect_gbif_candidates(
    repository: Path,
    *,
    cache_directory: Path,
    plant_id: str | None = None,
    delay_seconds: float = 1.0,
    timeout: float = 20.0,
    max_cache_age_days: int = 90,
    fetcher: Callable[..., dict[str, Any]] = fetch_gbif_candidate,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    if delay_seconds < 0:
        raise ValueError("Delay must not be negative.")
    if max_cache_age_days < 0:
        raise ValueError("Cache age must not be negative.")
    registry = _load_registry(repository)
    selected = [row for row in registry if not plant_id or row["plant_id"] == plant_id]
    if plant_id and not selected:
        raise ValueError(f"Unknown plant ID: {plant_id}")

    results = []
    network_requests = 0
    for row in selected:
        name = row["latin_name"].strip()
        identifier = row["plant_id"].strip()
        if not name:
            candidate = _result(
                input_name="",
                request_url="",
                status="NO_NAME",
                error="Registry record has no recorded scientific name.",
            )
        else:
            cache_path = cache_directory / f"{hashlib.sha256(name.encode('utf-8')).hexdigest()}.json"
            candidate = _read_cache(cache_path, name, max_cache_age_days)
            if candidate is None:
                if network_requests:
                    sleep(delay_seconds)
                candidate = fetcher(name, timeout=timeout, sleep=sleep)
                network_requests += 1
                if candidate.get("fetch_status") in {"MATCHED", "NO_MATCH"}:
                    _write_cache(cache_path, candidate)
        results.append(
            {
                "plant_id": identifier,
                "display_name": row["display_name"].strip(),
                "recorded_scientific_name": name,
                "candidate": candidate,
            }
        )

    return {
        "schema_version": "1.0",
        "provider": "GBIF Species Match API",
        "api_endpoint": GBIF_MATCH_ENDPOINT,
        "retrieved_at_utc": _utc_now(),
        "candidate_only": True,
        "human_review_required": True,
        "registry_records_requested": len(selected),
        "network_requests": network_requests,
        "results": results,
    }


def write_candidate_report(report: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_name = stream.name
            stream.write(payload)
        Path(temporary_name).replace(output)
    except OSError:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
        raise
