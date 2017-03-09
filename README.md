# youtube-data

Combining scraping with the YouTube API to get publicly available YouTube video data

## Setup and Requirements

You will need Python 3, BeautifulSoup 4, a Google API key, and a list of
YouTube video ID's. You can install BeautifulSoup 4 with pip:
`pip3 install beautifulsoup4`. Of course, you can also use your local package
manager, `conda` if you're using the Anaconda Python distribution, or whatever.
See below for details on a Google API key and creating a list of YouTube ID's

### Google API Key

If you don't already have one, you'll need to get a YouTube API key from the
[Google Developer Console](https://console.developers.google.com/).

You should either create a new project or select an existing one. Once you
have a project selected (it will be visible at the top-left of the window) you
need to enable the API and generate a key.

To enable the API, select "Library" from the left-hand column. A list of API's
will be displayed. Click on "YouTube Data API". The "YouTube Data API v3"
screen should be displayed. Next to the title there should be a link named
"Enable". Click it and answer the prompts. Note that if you have previously
enabled this API the link will say "Disable"; if that's the case you don't
need to do anything.

To generate an API key, select "Credentials" from the left-hand column. The
credential screen will include a button labeled "Create credentials" - click
it and select the "API Key" option. Follow the prompts to create a YouTube API
key. If you have previously created a YouTube API key, it will be displayed on
this screen under the section labeled "API keys". This is where you would copy
the key if ever lose it.

**The key you have created must be specified in an environment variable name
"YT_KEY".**

There are a few ways to do this:

1. Specify it globally or for all processes run by your user. _This is
   generally a bad idea_.
2. Specify it on the command line. For instance, `YT_KEY=foo python3 do_api.py`
3. Specify it in a file named `.env`

We recommend number 3 (using the `.env` file). Some notes:

* The file name is in .gitignore -- this is important. You don't want to check
  your YouTube API key into a source code control system.
* The file is in the format KEY=VALUE, so in this case it would look like this:

```
YT_KEY=my-youtube-api-key
```

### YouTube Video List

The two scripts that actually retrieve data from YouTube require an input file
listing the YouTube videos to target. YouTube videos have a unique identifier
that we use to track them (and that we need to know to download data). You can
extract the YouTube ID from a link to a video. For instance, the link
https://www.youtube.com/watch?v=jmcSzzN1gkc, the YouTube ID is `jmcSzzN1gkc`.

There are two ways to specify the YouTube ID's to be processed. The simplest is
a plain text file with a YouTube ID per line:

```
jmcSzzN1gkc
3Z5M7OzLNJs
L6BlpGnCYVg
```

The other way is a CSV file containing YouTube watch URL's. Every field of
every line is examined and if it matches a YouTube URL (`/watch?v=youtube-key-
here`) then the YouTube ID is extracted. An example CSV that would be sufficient
is:

```
Rating,Name,Link
0.99,Unknown,http://youtube.com/watch?v=jmcSzzN1gkc
0.91,Unknown,https://youtube.com/watch?v=3Z5M7OzLNJs
0.95,Unknown,/watch?v=L6BlpGnCYVg
```

Note that the URL's are in various formats.

## Running

Assuming that you have everything listed above, you're ready to begin.

Running manually is pretty easy. There are only three real steps:

1. Run the `do_crawl.py` script to crawl the public YouTube site. You will need
   to specify the input file on the command line (see below).
2. Run the `do_api.py` script to hit the public YouTube API (don't forget to
   specify the env variable YT_KEY). (The command line is the same as
   `do_crawl.py`.)
3. Run the `combine.py` script to combine the output from the above two scripts.

*Important!* The `do_crawl.py` script can be run multiple times; it is "smart"
enough to skip previously scraped videos. There is no restart capability for
`do_api.py` because it runs so fast. However, all of the above assumes that you
are working on one list of YouTube API's at a time.

### Crawling YouTube

The `do_crawl.py` script expects one of two command line parameters:

* `--input` (can be abbreviated `-f`) accepts a file of YouTube ID's, one on each
  line.
* `--csv` (can be abbreviated `-c`) accepts a CSV file.

Both of these options correspond to the two kinds of files described above in
"YouTube Video List".

The input file is process and the YouTube ID's to crawl are written to a file
named `batch_ytid.txt`. A directory named `output` is created where log files
and the raw crawled data is stored. See `combine.py` for how the raw data is
processed

### Using the YouTube API

The script `do_api.py` expected the same command line parameters as
`do_crawl.py`. It will read the input file, call the YouTube API, and write
all results to `api.json`. As mentioned above, the environment variable YT_KEY
must be correctly defined.

### Combining outputs

The script `combine.py` doesn't require any command line parameters. It reads
the output of `do_crawl.py` and `do_api.py`. It creates two CSV files:
youtube-data.csv and youtube-daily-views.csv.

*youtube-data.csv* has a line per YouTube video and the following columns:

* YouTubeID
* WatchURL
* Title
* Channel
* StatsCommentCount
* StatsDislikeCount
* StatsFavoriteCount
* StatsLikeCount
* StatsViewCount
* BBShares
* BBSubscriptions
* BBViews
* BBTimeWatched
* Description
* Tags

They are mostly self-describing. Integer-valued fields are empty (and so not
zero) if they weren't found. A zero value means that YouTube actually returned 0.
"Tags" is a pipe ("|") delimited list of the tags specified for the video.

*youtube-daily-views.csv* has a line for every video/day combination found when
crawling YouTube. It has three columns:

* YouTubeID
* Day
* ViewCount

Day is in year-month-day format.


## Automating the process

The process isn't complicated, but it would be easy to automate. Other repositories
(like our [TED data collection](https://github.com/CraigKelly/ted-youtube-data))
use a tool named `dmk`. Rather than

## Credits

The YouTube crawling code in the ytcrawl package was cloned from
https://github.com/yuhonglin/YTCrawl, converted to Python 3, and changed for
this project. The original code is release under the BSD 3 clause license,
as is this repository.

## License

The code in this repository is licensed under the BSD 3 clause license.
