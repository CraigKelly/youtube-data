#!/usr/bin/env python3

"""Get basic statistics from You Tube API.

You need to get a YouTube API key from the Google Developer's Console. Then
you can run this script like so:

YT_KEY=your_key_here python3 ./basics.py < ../ted_joined.csv | tee basics.json

Note that you'll need to have already created the ted_joined.csv file in the
parent directory.
"""

# pylama:ignore=E501,D213

import csv
import requests
import json
import os
import sys
import inspect


KEY = os.environ['YT_KEY']
if not KEY:
    raise ValueError("YT_KEY env variable not set")


def log(msg, *args):
    """Log to stderr with optional formatting."""
    if args:
        msg = msg % args
    pre = inspect.getfile(sys._getframe(1)) + ": "
    sys.stderr.write(pre + msg + "\n")
    sys.stderr.flush()
    sys.stdout.flush()


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
        for i in resp.json().get('items', []):
            print(json.dumps(i))
            count += 1

        self.buffer = set()
        log("Retrieved %d records", count)


def main():
    """Entry point."""
    getter = Getter()
    for r in csv.DictReader(sys.stdin):
        getter.add(r['youtube_id'])
    getter.get()


if __name__ == '__main__':
    main()
