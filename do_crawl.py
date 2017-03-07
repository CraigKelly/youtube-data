#!/usr/bin/env python3

"""Somewhat automated crawler using the YTCrawl library."""

# pylama:ignore=E501

import argparse
import csv
import re
import sys

if sys.version_info[0] < 3:
    raise ValueError("Python 3 is required for this crawler")


def lines(filename):
    """Yield all non-empty lines in the file."""
    with open(filename) as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield line


def fields(filename):
    """Yield all non-empty fields in CSV records in the file."""
    with open(filename) as fh:
        for rec in csv.reader(fh):
            for fld in rec:
                fld = fld.strip()
                if fld:
                    yield fld


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input", help="input file with one YouTube ID per line", required=False)
    parser.add_argument("-c", "--csv", help="CSV input file with YouTube URL's like .../watch?v=youtube-id", required=False)
    args = parser.parse_args()

    def cmderror(msg):
        print(msg)
        parser.print_help()
        return 1

    if not args.input and not args.csv:
        return cmderror("You must specify either --input or --csv")
    if args.input and args.csv:
        return cmderror("You may only specify one of --input and --csv")

    yt_ids = set()

    if args.input:
        for line in lines(args.input):
            yt_ids.add(line)
    elif args.csv:
        ytid_re = re.compile(r'v=([A-Za-z0-9\-_]+)')
        for fld in fields(args.csv):
            match = ytid_re.findall(fld)
            if match and match[0]:
                yt_ids.add(match[0])

    if not yt_ids:
        print("Could not find any YouTube ID's")
        return 2

    print("Found %d YoutTube ID's" % len(yt_ids))

    batch_file = "batch_ytid.txt"
    output_dir = "output"

    print("Creating batch file: %s" % batch_file)
    with open(batch_file, "w") as fh:
        fh.write('\n'.join(list(sorted(yt_ids))))
        fh.write('\n')

    print("Will use output directory: %s" % output_dir)

    print("Starting batch process")
    from ytcrawl.crawler import Crawler
    c = Crawler()
    c._crawl_delay_time = 1
    c._cookie_update_delay_time = 1
    c.batch_crawl(batch_file, output_dir)
    print("COMPLETED")


if __name__ == '__main__':
    main()
