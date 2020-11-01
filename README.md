# Simple Twitter Scraper

## Prereqs
- Python 3 (not sure if works with 2)

## Setup
### Install packages
```
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
Run
```
python3 scrape.py (create|resume) --help
```
for more information about usage.

To summarize, the `create` command will start a new data set in directory `data/{SET_NAME}`. The `resume` command will reference an existing data set, pulling the existing cursors and resuming the original request when the set was created.