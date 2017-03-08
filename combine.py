#!/usr/bin/env python3

"""Extracting data from ytcrawl output dir and api.json file."""

# TODO: for API and ytcrawl, we might not have 100% ID overlap, so be sure to handle missing values
# TODO: read API Data
# TODO: join ytcrawl with API
# TODO: create a watch URL
# TODO: output everything as CSV

# pylama:ignore=E501,D213

import json
import os
import tarfile

from bs4 import BeautifulSoup

from common import log

# Get the location of the crawled data and the API JSON output
import do_crawl
import do_api

CRAWL_OUTPUT = os.path.join(do_crawl.OUTPUT_DIR, "data")
API_FILE = do_api.OUTPUT_FILE

# We track all brag bar labels from the crawled output for display later
ALL_BRAG_BAR = set()


def extract(buffer, start_tag, end_tag):
    """Extract the data bracketed by start_tag and end_tag."""
    start = buffer.find(start_tag)
    if start < 0:
        return ""
    end = buffer.find(end_tag, start + len(start_tag))
    if end < start:
        raise ValueError("Invalid buffer found - found '%s' but not '%s'" % (start_tag, end_tag))
    return buffer[start+len(start_tag):end].strip()


def process(tarinfo, reader):
    """Extract all data in single tar file."""
    ytid = os.path.split(tarinfo.name)[-1]
    data = str(reader.read()).strip()
    log("Processing: [%s] len=%12d %s", ytid, len(data), tarinfo.name)
    err_msg = extract(data, "<error_message><![CDATA[", "]]></error_message>")
    if err_msg:
        log("  Skipping: %s", err_msg)
        return False

    daily_stats = json.loads(extract(data, "<graph_data><![CDATA[", "]]></graph_data>"))
    brag_bar_html = extract(data, "<html_content><![CDATA[", "]]></html_content>")
    assert daily_stats
    assert brag_bar_html

    brag_bar = {}
    soup = BeautifulSoup(brag_bar_html, 'html.parser')
    for td in soup.find_all("td"):
        if "stats-bragbar" not in td.get('class'):
            continue
        label, value = "", ""
        for ch in td.children:
            if ch.name == "span" and "metric-label" in ch.get('class'):
                label = ch.text
            elif ch.name == "div" and "bragbar-metric" in ch.get('class'):
                value = ch.text
        if label and value:
            brag_bar[label] = value
            ALL_BRAG_BAR.add(label)

    daily_stats["YTID"] = ytid
    daily_stats["BragBar"] = brag_bar
    print(json.dumps(daily_stats))

    return True


def main():
    """Entry point."""
    skip_names = set(["key.done", "log"])

    count, processed = 0, 0

    with tarfile.open("ytcrawl.tar.gz") as tf:
        for tarinfo in tf:
            if not tarinfo.isfile() or tarinfo.size < 1:
                continue
            if tarinfo.name in skip_names or "data/" not in tarinfo.name:
                continue

            count += 1
            if process(tarinfo, tf.extractfile(tarinfo)):
                processed += 1

    log("Processed %d out of %d", processed, count)
    log("All brag bar labels: %s", repr(ALL_BRAG_BAR))


if __name__ == '__main__':
    main()
