# youtube-data

Combining scraping with the YouTube API to get publicly available YouTube video data

## Setup and Requirements

You will need Python 3, a few libraries, a Google API key, and a list of
YouTube video ID's

### Libraries

TODO

### Google API Key

TODO: getting one

You must specify the Google API in an environment variable name "YT_KEY".
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

TODO

## Running

Assuming that you have everything listed above, you're ready to begin.

Running manually is pretty easy. There are only three real steps:

1. Run the `do_crawl.py` script to crawl the public YouTube site.
2. Run the `do_api.py` script to hit the public YouTube API (don't forget to
   specify the env variable YT_KEY)
3. Run the `combine.py` script to combine the output from the above two scripts.

*Important!* The `do_crawl.py` script can be run multiple times; it is "smart"
enough to skip previously scraped videos. There is no restart capability for
`do_api.py` because it runs so fast. However, all of the above assumes that you
are working on one list of YouTube API's at a time.

## Automating the process

If you don't want to run manually and you are running in an environment with
bash available, you can use `dmk` to automate the process.
You'll need to make sure that the `dmk` binary is on your path by building it
or downloading a binary. See https://github.com/CraigKelly/dmk. There is already
a `pipline.yaml` specified, so all you need to do is run `dmk`:

```
$ YT_KEY=your_key_here dmk
```

## Credits

The YouTube crawling code in the ytcrawl package was cloned from
https://github.com/yuhonglin/YTCrawl, converted to Python 3, and changed for
this project. The original code is release under the BSD 3 clause license,
as is this repository.

## License

The code in this repository is licensed under the BSD 3 clause license.
