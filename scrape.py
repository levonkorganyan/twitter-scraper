from datetime import datetime, timedelta
from email.utils import parsedate_tz

import base64
import pandas as pd
import numpy as np 
import requests
import tweepy
import argparse
import datetime
import json
import os
import pprint
import click


from api import Api
import pdb

# How many pages of tweets will go into one file. Each page is roughly 72 tweets per the twitter api limit
# So each scraped file will have PAGE_GROUP_SIZE * 72 tweets where each page is ~60-90KB
# A page size of a 200 will produce files of ~86k tweets that are ~15MB in size
PAGE_GROUP_SIZE = 200

def read_last_line(f):
    for line in f:
        pass
    last_line = line
    return last_line;

def twitter_date_to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime.datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])

def datetime_diff_days(a, b):
    return (a - b).dayss

@click.group()
def cli():
    pass

@click.command()
@click.argument('setname', type=str)
@click.argument('hashtag', type=str)
@click.argument('since_days_ago', type=int)
@click.option('--until_days_ago', type=int, default=0, help='0 means until today (default 0)')
def create(setname, hashtag, since_days_ago, until_days_ago):
    if since_days_ago < 0:
        since_days_ago = 1
    if until_days_ago < 0:
        until_days_ago = 0
    if not hashtag:
        raise Exception('Invalid hashtag {}', hashtag)
    if hashtag[0] != '#':
        hashtag = '#' + hashtag
    set_path = os.path.join('data', setname)
    if not os.path.exists(set_path):
        os.makedirs(set_path)
    else:
        raise Exception('Set "{}" already exists, use `resume` command'.format(setname))
    run(hashtag, since_days_ago, until_days_ago, set_path)

# Todo: fix bug where this assumes that twitter is scraping from oldest tweet to newest
@click.command()
@click.argument('setname')
def resume(setname):
    data_path = 'data'
    if not os.path.isdir(data_path):
        raise Exception('No data found')
    set_path = os.path.join(data_path, setname)
    if not os.path.isdir(set_path):
        raise Exception('Set {} not found', setname)
    files = os.listdir(set_path)
    if not files:
        raise Exception('No data found in set {}', setname)
    files.sort(reverse=True)

    hashtag = None
    since = None
    until = None
    for i in range(len(files)):
        last_file = os.path.join(set_path, files[i])
        with open(last_file, 'r') as inputfile:
            try:
                data = json.loads(read_last_line(inputfile))
                if not 'request' in data:
                    continue
                request = data['request']
                if not 'until' in request:
                    continue
                until = request['until']
                print(until)
                if not 'hashtag' in request:
                    continue
                hashtag = request['hashtag']
                if not 'items' in data:
                    continue
                items = data['items']
                if len(items) == 0:
                    continue
                first_item = items[0]
                since_datetime = twitter_date_to_datetime(first_item["created_at"])
                since = datetime_diff_days(datetime.datetime.now(), since_datetime) # assumes resume is running on same day create was ran
            except ValueError:
                continue
    if not hashtag or not since or not until:
        raise Exception('No valid data found in set {}, cannot resume', setname)
    run(hashtag, since, until, set_path)


cli.add_command(create)
cli.add_command(resume)


def write_page(cursor, request, items, path, mapper=lambda x: x):
    data = { 
        'cursor': cursor,
        'items': [mapper(item) for item in items],
        'request': request
    }
    print('Writing to location {}'.format(path))
    with open(path, 'a') as outputfile:
        json.dump(data, outputfile)
        outputfile.write("\n")

def create_file(path):
    filename = str(datetime.datetime.now().timestamp()).replace('.', '_') + '.json'
    full_path = os.path.join(path, filename)
    file = open(full_path, 'w')
    file.close();
    return full_path;


def run(hashtag, since, until, path):
    api = Api()
    request = {
        'hashtag': '#DontBelieveArmenia',
        'since': since,
        'until': until
    }
    days_since = datetime.datetime.now() - datetime.timedelta(since)
    days_until = datetime.datetime.now() - datetime.timedelta(until)

    group_index = 0;

    for page in api.get_tweets_for_hashtag(hashtag, days_since, days_until):
        if group_index % PAGE_GROUP_SIZE == 0:
            file_path = create_file(path)
            print("Created new file {}".format(file_path))
        if len(page) == 0:
            return
        page.reverse()
        start_time = page[0].created_at.timestamp()
        write_page(start_time, request, page, file_path, mapper=lambda s: s._json)
        group_index += 1 


if __name__ == '__main__':
    cli()