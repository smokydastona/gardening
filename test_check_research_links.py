import io
import socket
import urllib.error
from email.message import Message
from unittest.mock import patch

import check_research_links as links
import inspect_research_sources as sources


def test_candidate_urls_deduplicates_library_and_includes_blocked_sources():
    urls = links.candidate_urls(
        "| Source | https://example.org/page | use |\n"
        "[Source](https://example.org/page)\n"
    )
    assert urls.count("https://example.org/page") == 1
    assert set(links.ADDITIONAL_URLS).issubset(urls)


def test_success_records_redirect_and_content_type():
    headers = Message()
    headers["Content-Type"] = "application/json; charset=utf-8"

    class Response(io.BytesIO):
        status = 200

        def geturl(self):
            return "https://example.org/final"

    response = Response(b"{}")
    response.headers = headers
    with patch.object(links.urllib.request, "urlopen", return_value=response):
        result = links.check_url("https://example.org/start")
    assert result == {
        "url": "https://example.org/start",
        "status": "reachable",
        "http_status": 200,
        "final_url": "https://example.org/final",
        "content_type": "application/json",
    }


def test_dns_and_http_errors_are_distinct():
    with patch.object(
        links.urllib.request,
        "urlopen",
        side_effect=urllib.error.URLError(socket.gaierror("name resolution failed")),
    ):
        assert links.check_url("https://example.org")["status"] == "dns-error"
    with patch.object(
        links.urllib.request,
        "urlopen",
        side_effect=urllib.error.HTTPError(
            "https://example.org/final", 403, "Forbidden", {}, None
        ),
    ):
        result = links.check_url("https://example.org")
    assert result["status"] == "http-error"
    assert result["http_status"] == 403
    assert result["final_url"] == "https://example.org/final"


def test_source_metadata_extracts_headings_and_taxon_match():
    assert sources.describe_content("html", b"<title>Climate</title><h1>Nanaimo</h1>") == {
        "title": "Climate",
        "h1": "Nanaimo",
    }
    result = sources.describe_content(
        "json", b'{"scientificName":"Eruca vesicaria","matchType":"EXACT"}'
    )
    assert result["scientificName"] == "Eruca vesicaria"
    assert result["matchType"] == "EXACT"


def test_source_inspection_reports_fetch_errors():
    with patch.object(
        sources.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")
    ):
        result = sources.inspect("https://example.org", "html")
    assert result["status"] == "error"
    assert "offline" in result["error"]
