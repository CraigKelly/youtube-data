"""The logger class supporting the crawler."""

# pylama:ignore=D212,D213,E501

# Author: Honglin Yu <yuhonglin1986@gmail.com>
# License: BSD 3 clause


import time
import os
from os.path import join


class Logger(object):
    """record the crawling status, error and warnings."""

    def __init__(self, outputDir=""):
        """init."""
        self._output_dir = outputDir
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)

        log_name = join(self._output_dir, 'log')
        self._log_file_dict = {'log': open(log_name, 'a+')}
        self._log_name_dict = {'log': log_name}

        self._done_name = join(self._output_dir, 'key.done')
        self._done_file = open(self._done_name, 'a+')

    def add_log(self, d):
        """Add a log file."""
        for i, j in d.items():
            fn = join(self._output_dir, j)
            self._log_name_dict[i] = fn
            self._log_file_dict[i] = open(fn, 'a+')

    def _read_done_keys(self):
        with open(self._done_name, "r") as fh:
            return set([i.strip() for i in fh.read().split() if i.strip()])

    def _read_logged_keys(self, name):
        with open(self._log_name_dict[name], "r") as fh:
            return set([line.split(',')[1] for line in fh if line.strip()])

    def get_key_done(self, lognames=[]):
        """Get the keys that have been crawled."""
        ks = self._read_done_keys() | self._read_logged_keys('log')
        for name in lognames:
            ks = ks | self._read_logged_keys(name)
        return ks

    def log_done(self, k):
        """Thread safe finalizer for logs."""
        # self._mutex_done.acquire()
        self._done_file.write('%s\n' % k)
        self._done_file.flush()
        # self._mutex_done.release()

    def log_warn(self, k, m, lfk='log'):
        """Log message as warning.

        Arguments:
        - `k` : the key
        - `m`: the message
        - `lfk`: log_file_key
        """
        # self._mutex_log.acquire()
        msg = ','.join([
            time.strftime('%Y-%m-%d %m:%H:%M'),
            k,
            m
        ])
        outp = self._log_file_dict[lfk]
        outp.write(msg + '\n')
        outp.flush()
        # self._mutex_log.release()
