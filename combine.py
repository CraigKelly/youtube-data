#!/usr/bin/env python3

"""Extracting data from ytcrawl output dir and api.json file."""

# pylama:ignore=E501,D213

import collections
import csv
import datetime
import json
import os

from bs4 import BeautifulSoup

from common import log, lines, rel_path

# Get the location of the crawled data and the API JSON output
import do_crawl
import do_api

CRAWL_INPUT = os.path.join(do_crawl.OUTPUT_DIR, "data")
API_FILE = do_api.OUTPUT_FILE

# We track all brag bar labels from the crawled output for display later
ALL_BRAG_BAR = set()

# Files that we write
OUTPUT_DATA = rel_path("output.csv")
OUTPUT_DAILIES = rel_path("dailies.csv")

DATA_COLS = [
    "YouTubeID",
    "WatchURL",
    # From API "snippet"
    "Title",
    "Channel",
    # From API statistics
    "StatsCommentCount",
    "StatsDislikeCount",
    "StatsFavoriteCount",
    "StatsLikeCount",
    "StatsViewCount",
    # From crawled brag bar
    "BBShares",
    "BBSubscriptions",
    "BBViews",
    "BBTimeWatched",
    # From API "snippet"
    "Description",
    "Tags",
]

DAILY_COLS = [
    "YouTubeID",
    "Day",
    "ViewCount"
]


def ints(s):
    """Return a coreced int from the string unless s is empty."""
    s = s.strip()
    if not s:
        return ""
    return int(s.replace(',', ''))


def normws(s):
    """Return the given string with normalized whitespace."""
    return ' '.join(s.strip().split())


def ts_to_day(ts):
    """Convert the JS-style timestamp to a year-month-day string."""
    dt = datetime.datetime.utcfromtimestamp(int(ts) / 1000)
    return dt.strftime("%Y-%m-%d")


def extract(buffer, start_tag, end_tag):
    """Extract the data bracketed by start_tag and end_tag."""
    start = buffer.find(start_tag)
    if start < 0:
        return ""
    end = buffer.find(end_tag, start + len(start_tag))
    if end < start:
        raise ValueError("Invalid buffer found - found '%s' but not '%s'" % (start_tag, end_tag))
    return buffer[start+len(start_tag):end].strip()


def process_crawled(data):
    """Extract all data from the single file contents.

    Return is tuple of 2 dictionaries: (daily_stats, brag_bar)
    """
    err_msg = extract(data, "<error_message><![CDATA[", "]]></error_message>")
    if err_msg:
        log("  Skipping: %s", err_msg)
        return None, None

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

    return daily_stats, brag_bar


def main():
    """Entry point."""
    # We store everything as a dict keyed on YouTube ID
    all_data = collections.defaultdict(dict)

    # Process crawled data
    log("Processing crawled data")
    count, processed = 0, 0
    for path, subdirs, files in os.walk(CRAWL_INPUT):
        for fn in files:
            count += 1
            # Remember, file name is also the youtube key in the crawl output
            with open(os.path.join(path, fn), "r") as fh:
                data = fh.read().strip()
            log("Processing crawled data: [%s] len=%12d", fn, len(data))
            daily_stats, brag_bar = process_crawled(data)
            if not daily_stats and not brag_bar:
                continue  # Nothing to do

            processed += 1
            all_data[fn]["daily_stats"] = daily_stats
            all_data[fn]["brag_bar"] = brag_bar

    log("Processed crawled data: %d out of %d", processed, count)
    log("All brag bar labels: %s", repr(ALL_BRAG_BAR))

    # Process API content
    log("Processing JSON retrieve from API")
    count, processed = 0, 0
    for line in lines(API_FILE):
        count += 1
        rec = json.loads(line)
        ytid = rec.get("id", "").strip()
        if not ytid:
            continue

        processed += 1
        all_data[ytid]["stats"] = rec.get("statistics", {})
        all_data[ytid]["snippet"] = rec.get("snippet", {})

    log("Processed API data: %d out of %d", processed, count)

    # Output final CSV files
    log("Writing output file:     %s", OUTPUT_DATA)
    log("Writing daily data file: %s", OUTPUT_DAILIES)
    data_count, daily_count = 0, 0
    with open(OUTPUT_DATA, "w") as data_fh, open(OUTPUT_DAILIES, "w") as daily_fh:
        data_csv = csv.writer(data_fh, quoting=csv.QUOTE_NONNUMERIC)
        data_csv.writerow(DATA_COLS)

        daily_csv = csv.writer(daily_fh, quoting=csv.QUOTE_NONNUMERIC)
        daily_csv.writerow(DAILY_COLS)

        for ytid, data in all_data.items():
            # From API
            stats = data.get("stats", {})
            snippet = data.get("snippet", {})
            # From crawl
            daily_stats = data.get("daily_stats", {})
            brag_bar = data.get("brag_bar", {})

            # Write out the main data record
            data_count += 1
            data_csv.writerow([
                ytid,                                            # YouTubeID
                "https://youtube.com/watch?v="+ytid,             # WatchURL
                normws(snippet.get("title", "")),                # Title
                snippet.get("channelTitle", ""),                 # Channel
                ints(stats.get("commentCount", "")),             # StatsCommentCount
                ints(stats.get("dislikeCount", "")),             # StatsDislikeCount
                ints(stats.get("favoriteCount", "")),            # StatsFavoriteCount
                ints(stats.get("likeCount", "")),                # StatsLikeCount
                ints(stats.get("viewCount", "")),                # StatsViewCount
                ints(brag_bar.get("Shares", "")),                # BBShares
                ints(brag_bar.get("Subscriptions driven", "")),  # BBSubscriptions
                ints(brag_bar.get("Views", "")),                 # BBViews
                ints(brag_bar.get("Time watched", "")),          # BBTimeWatched
                normws(snippet.get("description", "")),          # Description
                "|".join(snippet.get("tags", [])),               # Tags
            ])

            # Write out all the daily views
            days = daily_stats.get("day", {}).get("data", [])
            views = daily_stats.get("views", {}).get("daily", {}).get("data", [])
            for d, v in zip(days, views):
                daily_csv.writerow([ytid, ts_to_day(d), v])
                daily_count += 1

    log("Wrote %12d to %s", data_count, OUTPUT_DATA)
    log("Wrote %12d to %s", daily_count, OUTPUT_DAILIES)


if __name__ == '__main__':
    main()
