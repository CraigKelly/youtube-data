#!/usr/bin/env python3

"""Somewhat automated crawler using the YTCrawl library."""

# pylama:ignore=E501

# Note that the common import also checks for Python 3
from common import youtube_id_from_cmdline, log

# Make sure these parameters can be imported from another script
BATCH_FILE = "batch_ytid.txt"
OUTPUT_DIR = "output"


def main():
    """Entry point."""
    yt_ids = youtube_id_from_cmdline()

    log("Creating batch file: %s", BATCH_FILE)
    with open(BATCH_FILE, "w") as fh:
        fh.write('\n'.join(list(sorted(yt_ids))))
        fh.write('\n')

    log("Will use output directory: %s", OUTPUT_DIR)

    log("Starting batch process")
    from ytcrawl.crawler import Crawler
    c = Crawler()
    c._crawl_delay_time = 1
    c._cookie_update_delay_time = 1
    c.batch_crawl(BATCH_FILE, OUTPUT_DIR)
    log("COMPLETED")


if __name__ == '__main__':
    main()
