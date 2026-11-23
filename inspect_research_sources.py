#!/usr/bin/env python3
"""Record limited metadata from four priority research sources."""

import datetime
import hashlib
import io
import json
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from check_research_links import ADDITIONAL_URLS


class Headings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag = None
        self.text = {"title": [], "h1": []}

    def handle_starttag(self, tag, attrs):
        if tag in self.text:
            self.tag = tag

    def handle_endtag(self, tag):
        if tag == self.tag:
            self.tag = None

    def handle_data(self, data):
        if self.tag:
            self.text[self.tag].append(data)


def describe_content(kind, body):
    if kind == "pdf":
        pdf = PdfReader(io.BytesIO(body))
        metadata = pdf.metadata
        return {
            "pages": len(pdf.pages),
            "title": str(metadata.title) if metadata and metadata.title else None,
            "author": str(metadata.author) if metadata and metadata.author else None,
            "sha256": hashlib.sha256(body).hexdigest(),
        }
    if kind == "json":
        data = json.loads(body)
        return {key: data.get(key) for key in (
            "scientificName", "canonicalName", "status", "matchType", "confidence"
        )}
    headings = Headings()
    headings.feed(body.decode("utf-8", errors="replace"))
    return {key: " ".join(" ".join(value).split()) for key, value in headings.text.items()}


def inspect(url, kind):
    result = {"url": url}
    request = urllib.request.Request(
        url, headers={"User-Agent": "ErringtonEncyclopediaSourceCheck/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read(20 * 1024 * 1024 + 1)
            if len(body) > 20 * 1024 * 1024:
                raise ValueError("Source exceeds the 20 MiB inspection limit")
            result.update(
                status="inspected",
                final_url=response.geturl(),
                content_type=response.headers.get_content_type(),
                metadata=describe_content(kind, body),
            )
    except (urllib.error.URLError, OSError, ValueError, PdfReadError) as error:
        result.update(status="error", error=str(error))
    return result


def main():
    kinds = ("pdf", "html", "html", "json")
    results = [inspect(url, kind) for url, kind in zip(ADDITIONAL_URLS, kinds)]
    report = {
        "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "note": "Metadata inspection does not verify claims or grant reuse rights.",
        "results": results,
    }
    output = Path("build/research-source-metadata.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(any(result["status"] != "inspected" for result in results))


if __name__ == "__main__":
    sys.exit(main())
