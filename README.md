# Simple Twitter Scraper

## Prereqs
- Python 3 (not sure if works with 2)

## Setup
### Install packages
```bash
pip install -r requirements.txt
```

### Set up API keys
Create a file named `config` in this directory, paste in the following skeleton, and fill out (no spaces, trailing characters): 
```
AccessToken=
AccessTokenSecret=
ApiKey=
ApiKeySecret=
```

## Usage

### Scrape

#### Run
```bash
python3 scrape.py (create|resume) --help
```
for more information about usage.

To summarize, the `create` command will start a new data set in directory `data/{SET_NAME}`. The `resume` command will reference an existing data set, pulling the existing cursors and resuming the original request when the set was created.

Note: Hashtags don't require `#` character as a prefix to make it easier in bash environments

#### Example
```bash
python3 scrape.py create mytestset TheKidFromAkron 3 # get tweets from the last 3 days including this hashtag
```

### Normalize

#### Run
```bash
python3 normalize to-csv --help
```

#### Example
```
python3 normalize to-csv data mytestset
```
