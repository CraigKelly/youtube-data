"""Some common utilities used by all the scripts in this directory."""

# pylama:ignore=D213

import argparse
import csv
import inspect
import os
import re
import sys

import os.path as pth

if sys.version_info[0] < 3:
    raise ValueError("Python 3 is required for this crawler")


FILE_PATH = inspect.getabsfile(lambda i: i)
SCRIPT_DIR = pth.dirname(FILE_PATH)


def rel_path(*parts):
    """Return a path relative to this script's dir using the parts given."""
    return pth.abspath(pth.join(SCRIPT_DIR, *parts))


def log(msg, *args):
    """Log to stderr with optional formatting."""
    if args:
        msg = msg % args
    pre = inspect.getfile(sys._getframe(1)) + ": "
    sys.stderr.write(pre + msg + "\n")
    sys.stderr.flush()
    sys.stdout.flush()


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


def check_env_file():
    """Check for existence of env file and process it."""
    if pth.isfile(".env"):
        log("Reading environment variables from .env")
        with open(".env", "r") as fh:
            for line in fh:
                line = line.strip().split('=')
                if len(line) < 2:
                    continue
                key = line[0].strip()
                val = ' '.join(line[1:]).strip()
                log("Setting env variable %s", key)
                os.environ[key] = val


def youtube_id_from_cmdline():
    """Parse the command line and then parse the indicated file for YT id's.

    Assumes a CLI script, so if an error is found the process is exited.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--input",
        help="input file with one YouTube ID per line",
        required=False
    )
    parser.add_argument(
        "-c", "--csv",
        help="CSV input file with YouTube URL's like .../watch?v=youtube-id",
        required=False
    )
    args = parser.parse_args()

    def cmderror(msg):
        log(msg)
        parser.print_help()
        sys.exit(1)

    if not args.input and not args.csv:
        cmderror("You must specify either --input or --csv")
    if args.input and args.csv:
        cmderror("You may only specify one of --input and --csv")

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
        log("Could not find any YouTube ID's")
        sys.exit(2)

    log("Found %d YoutTube ID's", len(yt_ids))

    return yt_ids
