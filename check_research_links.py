#!/usr/bin/env python3
"""Check candidate research URLs from an independently networked runner."""

import concurrent.futures
import datetime
import json
import re
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path


LIBRARY = Path(__file__).parent / "docs" / "RESEARCH_LIBRARY.md"
ADDITIONAL_URLS = (
    "https://pollinatorpartnership.ca/assets/generalFiles/E.Vancouver.Isl.2017.pdf",
    "https://climate.weather.gc.ca/climate_normals/results_1981_2010_e.html?"
    "searchType=stnName&txtStationName=Nanaimo&searchMethod=contains"
    "&txtCentralLatMin=0&txtCentralLatSec=0&txtCentralLongMin=0"
    "&txtCentralLongSec=0&climate_id=1025370&dispBack=0",
    "https://open.canada.ca/data/en/dataset/adda404d-93e4-48e9-b6bf-5d1d3952ff22",
    "https://api.gbif.org/v1/species/match?name=Arugula",
)


def candidate_urls(text):
    urls = re.findall(r"https?://[^\s|<>)]+", text)
    return list(dict.fromkeys([*urls, *ADDITIONAL_URLS]))


def check_url(url):
    result = {"url": url}
    request = urllib.request.Request(
        url, headers={"User-Agent": "ErringtonEncyclopediaSourceCheck/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response.read(1)
            result.update(
                status="reachable",
                http_status=response.status,
                final_url=response.geturl(),
                content_type=response.headers.get_content_type(),
            )
    except urllib.error.HTTPError as error:
        result.update(
            status="http-error",
            http_status=error.code,
            final_url=error.geturl(),
            error=str(error),
        )
    except urllib.error.URLError as error:
        result.update(
            status="dns-error" if isinstance(error.reason, socket.gaierror) else "network-error",
            error=str(error.reason),
        )
    except (TimeoutError, OSError) as error:
        result.update(status="network-error", error=str(error))
    return result


def main():
    urls = candidate_urls(LIBRARY.read_text(encoding="utf-8"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(check_url, urls))
    report = {
        "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "note": "Reachability is not evidence that a source supports a claim.",
        "results": results,
    }
    output = Path("build/research-link-check.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for result in results:
        detail = result.get("http_status", result.get("error", ""))
        print(f"{result['status']}: {result['url']} ({detail})")
    print(f"Report: {output}")
    return int(any(result["status"] != "reachable" for result in results))


if __name__ == "__main__":
    sys.exit(main())
