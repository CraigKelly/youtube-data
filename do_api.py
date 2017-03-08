#!/usr/bin/env python3

"""Get basic statistics from You Tube API.

You need to get a YouTube API key from the Google Developer's Console. Then
you can run this script like so:

YT_KEY=your_key_here python3 ./do_api.py --csv some_csv_file.csv

The final file will api.json
"""

# pylama:ignore=E501,D213

import requests
import json
import os

from common import check_env_file, youtube_id_from_cmdline, log

check_env_file()
KEY = os.environ['YT_KEY']
if not KEY:
    raise ValueError("YT_KEY env variable not set")

# Make sure other scripts can import our target file
OUTPUT_FILE = "api.json"


class Getter(object):
    """Stateful ReST getter for YouTube."""

    def __init__(self):
        """Ctor."""
        self.buffer = set()

    def add(self, ytid):
        """Add ID to buffer."""
        self.buffer.add(ytid)
        if len(self.buffer) >= 10:
            self.get()

    def get(self):
        """"Get anything in the buffer."""
        if not self.buffer:
            return
        params = {
            'key': KEY,
            'part': 'statistics,snippet',
            'id': ','.join(list(self.buffer))
        }
        resp = requests.get(
            'https://www.googleapis.com/youtube/v3/videos',
            params=params
        )

        count = 0
        with open(OUTPUT_FILE, "a") as fh:
            for i in resp.json().get('items', []):
                fh.write(json.dumps(i) + '\n')
                count += 1

        self.buffer = set()
        log("Retrieved %d records", count)


def main():
    """Entry point."""
    getter = Getter()
    for ytid in youtube_id_from_cmdline():
        getter.add(ytid)
    getter.get()  # Final flush


if __name__ == '__main__':
    main()
